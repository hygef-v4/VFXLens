"""Signal-driven VFX event detectors with strict separation of observation vs. AE technique inference."""

from __future__ import annotations

import numpy as np

from ...schemas.common import DataAvailabilityStatus
from ...schemas.video_schema import (
    FrameSignalEntry,
    SceneBoundarySchema,
    VideoEffectEventSchema,
)


def _group_contiguous_indices(indices: list[int], max_gap: int = 2) -> list[list[int]]:
    """Group sorted frame list positions into contiguous spans allowing small gaps."""
    if not indices:
        return []
    groups: list[list[int]] = [[indices[0]]]
    for idx in indices[1:]:
        if idx - groups[-1][-1] <= max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


def detect_video_effect_candidates(
    signals: list[FrameSignalEntry],
    scenes: list[SceneBoundarySchema],
) -> list[VideoEffectEventSchema]:
    """Run all deterministic computer-vision VFX detectors over the frame signal timeline."""
    if len(signals) < 2:
        return []

    events: list[VideoEffectEventSchema] = []
    event_counter = 0

    def next_id(prefix: str) -> str:
        nonlocal event_counter
        event_counter += 1
        return f"evt_{event_counter:03d}_{prefix}"

    n = len(signals)
    cut_frame_set = {sc.start_frame for sc in scenes if sc.scene_index > 0}

    # -------------------------------------------------------------------------
    # 1. Scene Cuts
    # -------------------------------------------------------------------------
    sig_by_frame = {s.frame_index: (i, s) for i, s in enumerate(signals)}
    for sc in scenes:
        if sc.scene_index == 0:
            continue
        pos_sig = sig_by_frame.get(sc.start_frame)
        if not pos_sig:
            continue
        pos, sig = pos_sig
        prev_sig = signals[max(0, pos - 1)]
        conf = float(np.clip(0.55 + (sc.cut_score / 180.0), 0.55, 0.98))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("scene_cut"),
                effect_type="scene_cut",
                start_time=prev_sig.timestamp,
                end_time=sig.timestamp,
                start_frame=prev_sig.frame_index,
                end_frame=sig.frame_index,
                peak_frame=sig.frame_index,
                peak_time=sig.timestamp,
                observations=[
                    f"Abrupt inter-frame visual discontinuity at {sig.timestamp:.3f}s (frame #{sig.frame_index}).",
                    f"Mean per-pixel max RGB channel delta = {sig.max_channel_diff:.1f}% across {sig.changed_cell_area * 100:.1f}% of 12x9 grid cells.",
                ],
                measured_signals={
                    "cut_score": sc.cut_score,
                    "transition_type": sc.transition_type,
                    "max_channel_diff": sig.max_channel_diff,
                    "changed_cell_area": sig.changed_cell_area,
                    "luma_delta": sig.luma_delta,
                },
                possible_ae_techniques=[
                    "Hard layer split (Ctrl+Shift+D) or sequential footage layer cut in timeline",
                    "Precomp boundary cut or adjustment layer transition cut",
                ],
                possible_plugins=[],
                undetermined_parameters=[
                    "Whether the cut occurs between two separate layers, inside a precomp, or from an imported pre-edited clip",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Derived from hybrid PySceneDetect + frame-level max_channel_diff ({sig.max_channel_diff:.1f}) "
                    f"and changed_cell_area ({sig.changed_cell_area:.2f})."
                ),
                extraction_method="hybrid_pyscenedetect_and_grid_delta",
                source=DataAvailabilityStatus.OBSERVED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 2. Flash Frames (Luminance / Exposure Impact Flashes)
    # -------------------------------------------------------------------------
    lumas = np.array([s.mean_luma for s in signals], dtype=np.float32)
    med_luma = float(np.median(lumas))
    flash_positions: list[int] = []
    for i, s in enumerate(signals):
        # Detect sharp positive luminance spikes or sudden full-frame highlight saturation
        local_lo = max(0, i - 5)
        local_hi = min(n, i + 6)
        local_med = float(np.median(lumas[local_lo:local_hi]))
        if (s.mean_luma - local_med > 32.0 and s.highlight_ratio > 0.25) or (
            abs(s.luma_delta) > 42.0 and s.highlight_ratio > 0.35
        ):
            flash_positions.append(i)

    for grp in _group_contiguous_indices(flash_positions, max_gap=2):
        if len(grp) > 10:
            # Sustained bright scene rather than transient flash impact
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].mean_luma + abs(signals[idx].luma_delta))
        peak_s = signals[peak_pos]
        conf = float(
            np.clip(
                0.55 + min(0.25, abs(peak_s.luma_delta) / 220.0) + min(0.18, peak_s.highlight_ratio * 0.3),
                0.55,
                0.96,
            )
        )
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("flash"),
                effect_type="flash_frame",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Transient luminance spike peaking at {peak_s.mean_luma:.1f}/255 (luma delta {peak_s.luma_delta:+.1f}).",
                    f"High-luminance pixel ratio (>235) reached {peak_s.highlight_ratio * 100:.1f}% over {len(grp)} frame(s).",
                ],
                measured_signals={
                    "peak_mean_luma": peak_s.mean_luma,
                    "peak_luma_delta": peak_s.luma_delta,
                    "peak_highlight_ratio": peak_s.highlight_ratio,
                    "duration_frames": len(grp),
                    "baseline_median_luma": round(med_luma, 2),
                },
                possible_ae_techniques=[
                    "Keyframed Exposure / Brightness & Contrast on an Adjustment Layer across 2-6 frames",
                    "White Solid layer with Add/Screen/Overlay blending mode and fast Opacity decay",
                    "Luma fade / impact flash transition between shots",
                ],
                possible_plugins=[
                    "ADBE Exposure2 (Built-in Exposure)",
                    "S_Glow / S_Flashbulbs (Boris FX Sapphire)",
                    "Deep Glow (Plugin Everything - threshold/exposure spike)",
                    "BCC+ Light Leaks / Dissolve (Boris FX Continuum)",
                ],
                undetermined_parameters=[
                    "Exact Exposure EV stop value vs. White Solid Opacity percentage",
                    "Exact graph editor Bezier decay handles",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Transient luminance spike ({peak_s.luma_delta:+.1f}) and highlight saturation "
                    f"({peak_s.highlight_ratio:.2f}) returning to baseline within {len(grp)} frames."
                ),
                extraction_method="luminance_impulse_detector",
                source=DataAvailabilityStatus.OBSERVED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 3. Camera Shake (High-frequency oscillatory global translation/rotation)
    # -------------------------------------------------------------------------
    shake_positions: list[int] = []
    for i in range(1, n - 1):
        s_prev = signals[i - 1]
        s_curr = signals[i]
        s_next = signals[i + 1]
        speed_curr = float(np.hypot(s_curr.flow_dx, s_curr.flow_dy))
        speed_prev = float(np.hypot(s_prev.flow_dx, s_prev.flow_dy))
        if speed_curr < 1.2 and abs(s_curr.flow_rotation_deg) < 0.25:
            continue
        # Direction reversal (negative dot product between consecutive velocity vectors) or high jerk
        dot = s_curr.flow_dx * s_prev.flow_dx + s_curr.flow_dy * s_prev.flow_dy
        dot_next = s_curr.flow_dx * s_next.flow_dx + s_curr.flow_dy * s_next.flow_dy
        jerk = float(np.hypot(s_curr.flow_dx - s_prev.flow_dx, s_curr.flow_dy - s_prev.flow_dy))
        if (dot < -0.5 or dot_next < -0.5) and (speed_curr > 1.4 or speed_prev > 1.4 or jerk > 2.2):
            shake_positions.append(i)

    for grp in _group_contiguous_indices(shake_positions, max_gap=3):
        if len(grp) < 2:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: float(np.hypot(signals[idx].flow_dx, signals[idx].flow_dy)))
        peak_s = signals[peak_pos]
        amp_px = float(max(np.hypot(signals[idx].flow_dx, signals[idx].flow_dy) for idx in grp))
        rot_amp = float(max(abs(signals[idx].flow_rotation_deg) for idx in grp))
        conf = float(np.clip(0.52 + min(0.32, amp_px / 18.0) + min(0.10, len(grp) * 0.025), 0.52, 0.94))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("camera_shake"),
                effect_type="camera_shake",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Rapid oscillatory global translation reversals over {len(grp)} frames ({start_s.timestamp:.3f}s - {end_s.timestamp:.3f}s).",
                    f"Peak global displacement velocity = {amp_px:.2f} px/frame, peak rotational jitter = {rot_amp:.2f} deg/frame.",
                ],
                measured_signals={
                    "peak_displacement_px_per_frame": round(amp_px, 3),
                    "peak_rotation_deg_per_frame": round(rot_amp, 3),
                    "oscillation_frames": len(grp),
                },
                possible_ae_techniques=[
                    "Position/Rotation `wiggle(freq, amp)` expression damped by a Slider Control envelope",
                    "Adjustment Layer with Transform effect + Motion Tile (Mirrored Edges) for impact shake",
                    "Procedural camera shake plugin on an adjustment layer at cut impact",
                ],
                possible_plugins=[
                    "S_Shake (Boris FX Sapphire)",
                    "BCC Camera Shake (Boris FX Continuum)",
                    "Universe Camera Shake (Maxon Red Giant)",
                    "ADBE Geometry2 + ADBE Tile (Transform + Motion Tile workflow)",
                ],
                undetermined_parameters=[
                    "Exact random seed / phase of procedural shake generator",
                    "Whether edge compensation used Motion Tile mirror vs. underlying layer scale >100%",
                    "Whether Z-axis shake was enabled vs. 2D X/Y shake + scale",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"High-frequency global velocity vector sign reversals across {len(grp)} frames "
                    f"with peak amplitude {amp_px:.2f} px/frame."
                ),
                extraction_method="optical_flow_oscillation_detector",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 4. Zoom / Punch Transitions
    # -------------------------------------------------------------------------
    zoom_positions = [
        i
        for i, s in enumerate(signals)
        if abs(s.flow_scale_rate) >= 0.015 and s.flow_magnitude_p95 >= 1.8
    ]
    for grp in _group_contiguous_indices(zoom_positions, max_gap=2):
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: abs(signals[idx].flow_scale_rate))
        peak_s = signals[peak_pos]
        direction = "zoom_in" if peak_s.flow_scale_rate > 0 else "zoom_out"
        near_cut = any(abs(signals[idx].frame_index - cf) <= 4 for idx in grp for cf in cut_frame_set)
        conf = float(
            np.clip(
                0.55 + min(0.28, abs(peak_s.flow_scale_rate) * 4.5) + (0.08 if near_cut else 0.0),
                0.55,
                0.95,
            )
        )
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("zoom_punch"),
                effect_type="zoom_punch_transition",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Radial optical flow divergence ({direction}) peaking at scale rate {peak_s.flow_scale_rate:+.4f}/frame.",
                    f"95th-percentile optical flow speed reached {peak_s.flow_magnitude_p95:.2f} px/frame"
                    + (" coinciding with a scene cut boundary." if near_cut else "."),
                ],
                measured_signals={
                    "direction": direction,
                    "peak_scale_rate": peak_s.flow_scale_rate,
                    "peak_flow_p95": peak_s.flow_magnitude_p95,
                    "near_scene_cut": near_cut,
                    "duration_frames": len(grp),
                },
                possible_ae_techniques=[
                    "Adjustment Layer with Transform Scale keyframes (exponential speed graph peak at cut) + Motion Tile",
                    "Parented Null Object scale punch with native shutter angle motion blur (180-360 deg)",
                    "3D Camera Z-position push-in/pull-out across two sequential layers",
                ],
                possible_plugins=[
                    "ADBE Geometry2 + ADBE Tile (Built-in Transform + Motion Tile)",
                    "S_BlurMoCurves (Boris FX Sapphire Z-dist/zoom transition)",
                    "BCC Swish Pan / Zoom (Boris FX Continuum)",
                ],
                undetermined_parameters=[
                    "Exact Bezier speed curve handles in AE Graph Editor",
                    "Whether zoom was achieved via 2D Scale, S_BlurMoCurves Z Dist, or 3D Camera Z-translation",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Radial flow expansion/contraction ({peak_s.flow_scale_rate:+.4f}) "
                    f"with p95 flow {peak_s.flow_magnitude_p95:.2f} px/frame."
                ),
                extraction_method="radial_optical_flow_divergence",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 5. Speed Ramp / Time-Remap Velocity Envelope
    # -------------------------------------------------------------------------
    for sc in scenes:
        sc_signals = [
            s for s in signals if sc.start_frame < s.frame_index <= sc.end_frame and s.is_dense_sampled
        ]
        if len(sc_signals) < 6:
            continue
        mags = np.array([s.flow_magnitude_mean for s in sc_signals], dtype=np.float32)
        p85 = float(np.percentile(mags, 85))
        p25 = float(np.percentile(mags, 25))
        max_mag = float(np.max(mags))
        # Speed ramp signature: strong smooth dynamic range between fast burst and slow-mo plateau within one scene
        if max_mag >= 3.2 and (p85 / max(0.35, p25)) >= 2.8:
            peak_idx = int(np.argmax(mags))
            peak_s = sc_signals[peak_idx]
            start_s = sc_signals[0]
            end_s = sc_signals[-1]
            ratio = round(p85 / max(0.35, p25), 2)
            conf = float(np.clip(0.50 + min(0.35, (ratio - 2.5) * 0.08), 0.50, 0.88))
            events.append(
                VideoEffectEventSchema(
                    event_id=next_id("speed_ramp"),
                    effect_type="speed_ramp",
                    start_time=start_s.timestamp,
                    end_time=end_s.timestamp,
                    start_frame=start_s.frame_index,
                    end_frame=end_s.frame_index,
                    peak_frame=peak_s.frame_index,
                    peak_time=peak_s.timestamp,
                    observations=[
                        f"Intra-scene motion velocity surges {ratio:.1f}x from slow plateau ({p25:.2f} px/frame) to burst peak ({max_mag:.2f} px/frame).",
                        f"Peak motion velocity occurs at {peak_s.timestamp:.3f}s (frame #{peak_s.frame_index}).",
                    ],
                    measured_signals={
                        "scene_index": sc.scene_index,
                        "velocity_p25_px": round(p25, 3),
                        "velocity_p85_px": round(p85, 3),
                        "velocity_max_px": round(max_mag, 3),
                        "velocity_dynamic_ratio": ratio,
                    },
                    possible_ae_techniques=[
                        "Time Remapping (`Ctrl+Alt+T`) with Easy Ease speed graph spike/valley",
                        "Timewarp effect with keyframed Speed percentage and Pixel Motion frame blending",
                    ],
                    possible_plugins=[
                        "RE:Vision Effects Twixtor / Twixtor Pro",
                        "ADBE Timewarp (Built-in Timewarp)",
                        "Boris FX Continuum Optical Flow",
                    ],
                    undetermined_parameters=[
                        "Original source footage framerate (e.g. 60/120fps slowed down vs. 24fps optical-flow interpolated)",
                        "Exact Time Remap curve vs. real physical camera/subject acceleration",
                    ],
                    confidence=round(conf, 3),
                    confidence_explanation=(
                        f"Intra-scene optical flow velocity dynamic ratio of {ratio:.2f}x "
                        f"(p85={p85:.2f} vs p25={p25:.2f} px/frame)."
                    ),
                    extraction_method="intra_scene_velocity_envelope",
                    source=DataAvailabilityStatus.INFERRED,
                    verified=False,
                )
            )

    # -------------------------------------------------------------------------
    # 6. Directional Motion Blur
    # -------------------------------------------------------------------------
    sharp_vals = np.array([s.laplacian_sharpness for s in signals], dtype=np.float32)
    med_sharp = float(np.median(sharp_vals)) + 1e-3
    mblur_positions = [
        i
        for i, s in enumerate(signals)
        if (
            s.gradient_anisotropy >= 0.32
            and (s.laplacian_sharpness < med_sharp * 0.72 or s.flow_magnitude_p95 >= 3.5)
            and (s.flow_magnitude_mean >= 1.5 or s.laplacian_sharpness < med_sharp * 0.55)
        )
    ]
    for grp in _group_contiguous_indices(mblur_positions, max_gap=2):
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(
            grp,
            key=lambda idx: signals[idx].gradient_anisotropy * (1.0 + signals[idx].flow_magnitude_mean * 0.1),
        )
        peak_s = signals[peak_pos]
        sharp_drop_pct = max(0.0, (1.0 - peak_s.laplacian_sharpness / med_sharp) * 100.0)
        conf = float(
            np.clip(
                0.52 + min(0.25, peak_s.gradient_anisotropy * 0.5) + min(0.18, sharp_drop_pct / 250.0),
                0.52,
                0.92,
            )
        )
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("motion_blur"),
                effect_type="motion_blur",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Directional gradient anisotropy = {peak_s.gradient_anisotropy:.3f} oriented along {peak_s.dominant_gradient_angle_deg:.1f} deg.",
                    f"High-frequency Laplacian sharpness dropped {sharp_drop_pct:.1f}% below video median ({peak_s.laplacian_sharpness:.1f} vs {med_sharp:.1f}).",
                ],
                measured_signals={
                    "peak_gradient_anisotropy": peak_s.gradient_anisotropy,
                    "dominant_angle_deg": peak_s.dominant_gradient_angle_deg,
                    "laplacian_sharpness": peak_s.laplacian_sharpness,
                    "median_sharpness": round(med_sharp, 2),
                    "flow_magnitude_mean": peak_s.flow_magnitude_mean,
                },
                possible_ae_techniques=[
                    "Native AE Layer Motion Blur switch enabled with Comp Shutter Angle (180-360 deg)",
                    "Directional Blur or Vector Motion Blur applied during fast transition",
                ],
                possible_plugins=[
                    "RE:Vision Effects RSMB (ReelSmart Motion Blur)",
                    "ADBE Motion Blur (Built-in Directional Blur)",
                    "ADBE Force Motion Blur (CC Force Motion Blur)",
                    "S_BlurMotion / S_BlurMoCurves (Boris FX Sapphire)",
                ],
                undetermined_parameters=[
                    "Exact composition Shutter Angle and Shutter Phase settings",
                    "Whether motion blur was rendered natively by AE transform, RSMB optical flow, or in-camera shutter",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Combined structure-tensor anisotropy ({peak_s.gradient_anisotropy:.2f}) "
                    f"and Laplacian sharpness drop ({sharp_drop_pct:.1f}%)."
                ),
                extraction_method="structure_tensor_and_laplacian_blur_detector",
                source=DataAvailabilityStatus.OBSERVED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 7. RGB Split / Chromatic Aberration
    # -------------------------------------------------------------------------
    chroma_positions = [
        i
        for i, s in enumerate(signals)
        if (
            max(s.rg_edge_shift_px, s.rb_edge_shift_px) >= 0.85
            or s.chromatic_fringe_score >= 0.22
        )
    ]
    for grp in _group_contiguous_indices(chroma_positions, max_gap=2):
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(
            grp,
            key=lambda idx: max(signals[idx].rg_edge_shift_px, signals[idx].rb_edge_shift_px)
            + signals[idx].chromatic_fringe_score * 3.0,
        )
        peak_s = signals[peak_pos]
        max_shift = max(peak_s.rg_edge_shift_px, peak_s.rb_edge_shift_px)
        conf = float(
            np.clip(
                0.55 + min(0.25, max_shift * 0.08) + min(0.16, peak_s.chromatic_fringe_score * 0.4),
                0.55,
                0.95,
            )
        )
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("rgb_split"),
                effect_type="rgb_split_chromatic_aberration",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Spatial edge divergence between color channels: R-G shift = {peak_s.rg_edge_shift_px:.2f} px, R-B shift = {peak_s.rb_edge_shift_px:.2f} px.",
                    f"High-contrast edge chromatic fringe score = {peak_s.chromatic_fringe_score:.3f}.",
                ],
                measured_signals={
                    "rg_edge_shift_px": peak_s.rg_edge_shift_px,
                    "rb_edge_shift_px": peak_s.rb_edge_shift_px,
                    "chromatic_fringe_score": peak_s.chromatic_fringe_score,
                },
                possible_ae_techniques=[
                    "3 duplicated layers or Adjustment Layers isolated to Red/Green/Blue via Shift Channels (`ADBE Shift Channels`) with Screen/Add blending and offset Position/Scale",
                    "Chromatic aberration / RGB displacement plugin applied on an adjustment layer",
                ],
                possible_plugins=[
                    "S_WarpChroma (Boris FX Sapphire)",
                    "Universe Chromatic Aberration / RGB Separation (Maxon Red Giant)",
                    "BCC+ Chromatic Aberration (Boris FX Continuum)",
                    "ADBE Shift Channels + Optics Compensation (Built-in AE workflow)",
                ],
                undetermined_parameters=[
                    "Whether channels were split manually via 3 Shift Channels layers or a single shader plugin",
                    "Exact radial center vs. linear directional offset vector",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Measured R/G/B edge phase-correlation shift ({max_shift:.2f} px) and "
                    f"edge chromatic fringe score ({peak_s.chromatic_fringe_score:.3f})."
                ),
                extraction_method="rgb_edge_phase_correlation_and_fringe",
                source=DataAvailabilityStatus.OBSERVED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 8. Glow / Bloom
    # -------------------------------------------------------------------------
    glow_positions = [
        i
        for i, s in enumerate(signals)
        if s.bloom_halo_energy >= 0.14 and s.highlight_ratio >= 0.015
    ]
    for grp in _group_contiguous_indices(glow_positions, max_gap=3):
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].bloom_halo_energy)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.54 + min(0.36, peak_s.bloom_halo_energy * 1.2), 0.54, 0.93))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("glow_bloom"),
                effect_type="glow_bloom",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Soft luminance halo surrounding bright highlights (bloom halo energy = {peak_s.bloom_halo_energy:.3f}).",
                    f"Bright core pixel ratio (>235) = {peak_s.highlight_ratio * 100:.2f}%.",
                ],
                measured_signals={
                    "peak_bloom_halo_energy": peak_s.bloom_halo_energy,
                    "peak_highlight_ratio": peak_s.highlight_ratio,
                    "mean_luma": peak_s.mean_luma,
                },
                possible_ae_techniques=[
                    "Physically based inverse-square falloff glow plugin on layer or adjustment layer",
                    "Stacked built-in Glow effects with ascending Glow Radius (e.g., 20, 80, 250) in 16/32-bpc color",
                ],
                possible_plugins=[
                    "Deep Glow / Deep Glow 2 (Plugin Everything)",
                    "S_Glow / S_Glint (Boris FX Sapphire)",
                    "ADBE Glo2 (Built-in Stylized Glow)",
                    "Universe Glow (Maxon Red Giant)",
                ],
                undetermined_parameters=[
                    "Whether project color depth was 8-bpc, 16-bpc, or 32-bpc linear float",
                    "Exact glow threshold, radius octave spread, and chromatic tint settings",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Measured annular halo luminance excess ({peak_s.bloom_halo_energy:.3f}) "
                    f"around bright highlight cores ({peak_s.highlight_ratio:.3f})."
                ),
                extraction_method="annular_highlight_halo_detector",
                source=DataAvailabilityStatus.OBSERVED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 9. Distortion / Displacement / Glitch
    # -------------------------------------------------------------------------
    distort_positions = [
        i
        for i, s in enumerate(signals)
        if (
            s.scanline_tear_score >= 0.30
            or (s.flow_residual >= 1.6 and s.flow_residual > float(np.hypot(s.flow_dx, s.flow_dy)) * 1.15)
        )
        and s.frame_index not in cut_frame_set
    ]
    for grp in _group_contiguous_indices(distort_positions, max_gap=2):
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(
            grp,
            key=lambda idx: signals[idx].scanline_tear_score * 2.0 + signals[idx].flow_residual,
        )
        peak_s = signals[peak_pos]
        conf = float(
            np.clip(
                0.52 + min(0.25, peak_s.scanline_tear_score * 0.45) + min(0.18, peak_s.flow_residual * 0.06),
                0.52,
                0.90,
            )
        )
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("distortion"),
                effect_type="distortion_displacement",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Non-rigid spatial warp / scanline displacement detected (flow residual = {peak_s.flow_residual:.2f} px, scanline tear score = {peak_s.scanline_tear_score:.3f}).",
                ],
                measured_signals={
                    "peak_flow_residual": peak_s.flow_residual,
                    "peak_scanline_tear_score": peak_s.scanline_tear_score,
                },
                possible_ae_techniques=[
                    "Displacement Map driven by a precomped Fractal Noise / glitch block map",
                    "Turbulent Displace, Optics Compensation, or Wave Warp on an adjustment layer",
                ],
                possible_plugins=[
                    "ADBE Displacement Map / ADBE Turbulent Displace (Built-in Distort)",
                    "S_Distort / S_Zap / S_TVDamage (Boris FX Sapphire)",
                    "Universe Glitch / Holomatrix (Maxon Red Giant)",
                ],
                undetermined_parameters=[
                    "Structure of the underlying luma/chroma displacement map precomp",
                    "Exact Max Horizontal / Vertical Displacement pixel amounts",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Elevated non-affine optical flow residual ({peak_s.flow_residual:.2f}) and "
                    f"row-to-row scanline tear discontinuity ({peak_s.scanline_tear_score:.3f})."
                ),
                extraction_method="non_affine_residual_and_scanline_tear",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 10. Motion Trails / Echo
    # -------------------------------------------------------------------------
    trail_positions = [
        i
        for i, s in enumerate(signals)
        if s.trail_echo_correlation >= 0.24 and s.flow_magnitude_mean >= 0.8
    ]
    for grp in _group_contiguous_indices(trail_positions, max_gap=2):
        if len(grp) < 2:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].trail_echo_correlation)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.50 + min(0.38, peak_s.trail_echo_correlation * 0.85), 0.50, 0.88))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("motion_trail"),
                effect_type="motion_trail_echo",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Lagged edge ghosting correlation = {peak_s.trail_echo_correlation:.3f} across moving edges.",
                ],
                measured_signals={
                    "peak_trail_echo_correlation": peak_s.trail_echo_correlation,
                    "flow_magnitude_mean": peak_s.flow_magnitude_mean,
                },
                possible_ae_techniques=[
                    "Built-in Echo effect (`ADBE Echo`) with decaying Decay and negative Echo Time",
                    "CC Wide Time or time-offset duplicated layers with Screen/Add blending",
                ],
                possible_plugins=[
                    "ADBE Echo (Built-in Time > Echo)",
                    "S_TimeSlice / S_Feedback (Boris FX Sapphire)",
                    "BCC Motion Key / Stage Light (Boris FX Continuum)",
                ],
                undetermined_parameters=[
                    "Exact number of echoes, Echo Time offset in seconds, and Decay factor",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Correlation ({peak_s.trail_echo_correlation:.3f}) between current non-primary residual "
                    f"and lagged frame edge contours."
                ),
                extraction_method="lagged_edge_echo_correlation",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 11. Masking / Wipe Reveal
    # -------------------------------------------------------------------------
    mask_positions = [
        i
        for i, s in enumerate(signals)
        if 0.20 <= s.changed_cell_area <= 0.60
        and s.max_channel_diff >= 8.0
        and s.frame_index not in cut_frame_set
    ]
    for grp in _group_contiguous_indices(mask_positions, max_gap=2):
        if len(grp) < 3:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].changed_cell_area)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.50 + min(0.30, len(grp) * 0.03), 0.50, 0.84))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("mask_reveal"),
                effect_type="masking_reveal",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Partial-frame progressive transition covering {peak_s.changed_cell_area * 100:.1f}% of grid cells over {len(grp)} frames.",
                ],
                measured_signals={
                    "peak_changed_cell_area": peak_s.changed_cell_area,
                    "duration_frames": len(grp),
                },
                possible_ae_techniques=[
                    "Animated Bezier Mask Path reveal or Track Matte (Alpha / Luma Matte) wipe",
                    "Linear Wipe / Radial Wipe / Venetian Blinds transition effect",
                ],
                possible_plugins=[
                    "Native AE Mask Path / Track Matte",
                    "ADBE Linear Wipe / ADBE Radial Wipe",
                    "S_Wipe* (Boris FX Sapphire Wipe transitions)",
                ],
                undetermined_parameters=[
                    "Exact Mask Feather pixel value and whether mask was hand-rotoscoped (Roto Brush) vs. geometric matte",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Sustained partial-frame grid progression ({peak_s.changed_cell_area:.2f} cell area) "
                    f"over {len(grp)} consecutive frames."
                ),
                extraction_method="partial_grid_progression_detector",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 12. Particles Overlay
    # -------------------------------------------------------------------------
    particle_positions = [i for i, s in enumerate(signals) if s.particle_speckle_count >= 14]
    for grp in _group_contiguous_indices(particle_positions, max_gap=3):
        if len(grp) < 2:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].particle_speckle_count)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.50 + min(0.35, peak_s.particle_speckle_count / 80.0), 0.50, 0.86))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("particles"),
                effect_type="particles_overlay",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Detected {peak_s.particle_speckle_count} isolated small moving high-contrast speckles/particles at peak frame #{peak_s.frame_index}.",
                ],
                measured_signals={
                    "peak_particle_speckle_count": peak_s.particle_speckle_count,
                    "duration_frames": len(grp),
                },
                possible_ae_techniques=[
                    "3D particle emitter system on a solid layer",
                    "Pre-rendered dust/sparks/debris stock footage overlay with Screen/Add blending mode",
                ],
                possible_plugins=[
                    "RG Trapcode Particular (Maxon Red Giant)",
                    "CC Particle World / CC Particle Systems II (Built-in Simulation)",
                    "Video Copilot Orb / Stardust",
                ],
                undetermined_parameters=[
                    "Whether particles are procedural (Trapcode Particular) vs. pre-rendered stock video overlay",
                    "Exact emitter physics (Birth Rate, Velocity, Air Resistance, Turbulence Field)",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Morphological Top-Hat + temporal motion filter counted {peak_s.particle_speckle_count} "
                    f"small moving bright blobs."
                ),
                extraction_method="morphological_tophat_speckle_tracker",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 13. Kinetic Typography / Sharp Graphic Overlay Candidate
    # -------------------------------------------------------------------------
    typo_positions = [
        i
        for i, s in enumerate(signals)
        if s.laplacian_sharpness >= med_sharp * 1.35
        and s.luma_std >= 48.0
        and 0.08 <= s.changed_cell_area <= 0.55
    ]
    for grp in _group_contiguous_indices(typo_positions, max_gap=3):
        if len(grp) < 2:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].laplacian_sharpness)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.45 + min(0.28, (peak_s.laplacian_sharpness / med_sharp - 1.0) * 0.25), 0.45, 0.76))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("kinetic_typography_candidate"),
                effect_type="kinetic_typography_candidate",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"High-contrast sharp graphic/text edge candidate (Laplacian sharpness = {peak_s.laplacian_sharpness:.1f}, luma std = {peak_s.luma_std:.1f}) with localized motion.",
                    "Semantic text content requires AI Vision verification (marked as candidate).",
                ],
                measured_signals={
                    "peak_laplacian_sharpness": peak_s.laplacian_sharpness,
                    "luma_std": peak_s.luma_std,
                    "changed_cell_area": peak_s.changed_cell_area,
                },
                possible_ae_techniques=[
                    "AE Text Layer with Range Selector Animators (Position, Scale, Opacity, Tracking, Blur)",
                    "Shape Layer / vector graphic callout animated with Trim Paths",
                ],
                possible_plugins=[
                    "Native AE Text Animator Engine (`ADBE Text Animators`)",
                    "Animation Composer (Mister Horse)",
                ],
                undetermined_parameters=[
                    "Exact font family, character tracking, and Range Selector Ramp Up/Down easing",
                    "Semantic text string (requires OCR / AI Vision)",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Sharp high-contrast edge spike ({peak_s.laplacian_sharpness:.1f} vs median {med_sharp:.1f}) "
                    f"with localized cell activity; capped below 0.76 without OCR/Vision confirmation."
                ),
                extraction_method="sharp_contrast_graphic_candidate_detector",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    # -------------------------------------------------------------------------
    # 14. 3D Camera Motion & Multi-plane Parallax
    # -------------------------------------------------------------------------
    parallax_positions = [
        i for i, s in enumerate(signals) if s.flow_depth_layers_score >= 0.42
    ]
    for grp in _group_contiguous_indices(parallax_positions, max_gap=3):
        if len(grp) < 3:
            continue
        start_s = signals[grp[0]]
        end_s = signals[grp[-1]]
        peak_pos = max(grp, key=lambda idx: signals[idx].flow_depth_layers_score)
        peak_s = signals[peak_pos]
        conf = float(np.clip(0.50 + min(0.35, peak_s.flow_depth_layers_score * 0.45), 0.50, 0.85))
        events.append(
            VideoEffectEventSchema(
                event_id=next_id("camera_3d_parallax"),
                effect_type="camera_3d_parallax",
                start_time=start_s.timestamp,
                end_time=end_s.timestamp,
                start_frame=start_s.frame_index,
                end_frame=end_s.frame_index,
                peak_frame=peak_s.frame_index,
                peak_time=peak_s.timestamp,
                observations=[
                    f"Sustained global camera translation with multi-layer velocity separation (depth parallax score = {peak_s.flow_depth_layers_score:.3f}).",
                ],
                measured_signals={
                    "peak_depth_layers_score": peak_s.flow_depth_layers_score,
                    "flow_dx": peak_s.flow_dx,
                    "flow_dy": peak_s.flow_dy,
                    "duration_frames": len(grp),
                },
                possible_ae_techniques=[
                    "3D Layers arranged at different Z-depths with an animated Two-Node 3D Camera + Orbit Null",
                    "3D Camera Tracker (`ADBE 3D Tracker`) compositing or Element 3D object pass",
                ],
                possible_plugins=[
                    "Native AE 3D Camera + 3D Layer Space",
                    "Video Copilot Element 3D (`VIDEOCOPILOT 3DArray`)",
                ],
                undetermined_parameters=[
                    "Exact Camera Focal Length (mm), Film Size, Depth of Field Aperture, and layer Z-coordinates",
                    "Whether parallax originates from AE 2.5D layers, Element 3D, or real physical camera movement",
                ],
                confidence=round(conf, 3),
                confidence_explanation=(
                    f"Multi-modal optical flow velocity distribution ({peak_s.flow_depth_layers_score:.3f}) "
                    f"during sustained camera translation."
                ),
                extraction_method="multi_plane_optical_flow_parallax",
                source=DataAvailabilityStatus.INFERRED,
                verified=False,
            )
        )

    events.sort(key=lambda e: (e.start_time, -e.confidence))
    return events
