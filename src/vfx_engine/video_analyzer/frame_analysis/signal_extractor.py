"""Per-frame visual, color, sharpness, chromatic aberration, and optical flow signal extractor."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

import cv2
import numpy as np

from ...schemas.video_schema import FrameSignalEntry
from ..decoder.ffprobe_decoder import DecodedFrame
from ..motion_analysis.optical_flow import compute_optical_flow_metrics


def _compute_structure_tensor_anisotropy(gray_f32: np.ndarray) -> tuple[float, float]:
    """Compute gradient orientation coherence (directional motion blur cue) and dominant angle."""
    gx = cv2.Sobel(gray_f32, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_f32, cv2.CV_32F, 0, 1, ksize=3)

    jxx = float(np.mean(gx * gx))
    jyy = float(np.mean(gy * gy))
    jxy = float(np.mean(gx * gy))

    trace = jxx + jyy
    if trace < 1e-3:
        return 0.0, 0.0

    diff = jxx - jyy
    disc = float(np.hypot(diff, 2.0 * jxy))
    coherence = float(np.clip(disc / (trace + 1e-6), 0.0, 1.0))
    angle_rad = 0.5 * float(np.arctan2(2.0 * jxy, diff))
    angle_deg = float(np.degrees(angle_rad))
    return round(coherence, 4), round(angle_deg, 2)


def _compute_chromatic_aberration_metrics(bgr: np.ndarray) -> tuple[float, float, float]:
    """Measure R-G and R-B spatial edge offset and high-contrast color fringe score."""
    b = bgr[..., 0].astype(np.float32)
    g = bgr[..., 1].astype(np.float32)
    r = bgr[..., 2].astype(np.float32)

    # Edge magnitude per channel
    er = np.hypot(
        cv2.Sobel(r, cv2.CV_32F, 1, 0, ksize=3),
        cv2.Sobel(r, cv2.CV_32F, 0, 1, ksize=3),
    )
    eg = np.hypot(
        cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3),
        cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3),
    )
    eb = np.hypot(
        cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3),
        cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3),
    )

    edge_sum = er + eg + eb
    max_edge = float(np.max(edge_sum))
    if max_edge < 15.0:
        return 0.0, 0.0, 0.0

    # Phase correlation on channel edge maps to measure spatial RGB split shift in pixels
    try:
        (dx_rg, dy_rg), resp_rg = cv2.phaseCorrelate(eg, er)
        rg_shift = float(np.hypot(dx_rg, dy_rg)) if resp_rg > 0.05 else 0.0
    except cv2.error:
        rg_shift = 0.0

    try:
        (dx_rb, dy_rb), resp_rb = cv2.phaseCorrelate(eb, er)
        rb_shift = float(np.hypot(dx_rb, dy_rb)) if resp_rb > 0.05 else 0.0
    except cv2.error:
        rb_shift = 0.0

    # Chromatic fringe score: normalized divergence of R/G/B edge maps where edges are strong
    mask = edge_sum > float(np.percentile(edge_sum, 85))
    if np.any(mask):
        diff_rg = np.abs(er[mask] - eg[mask])
        diff_rb = np.abs(er[mask] - eb[mask])
        denom = (er[mask] + eg[mask] + eb[mask]) / 3.0 + 10.0
        fringe = float(np.mean((diff_rg + diff_rb) / (2.0 * denom)))
    else:
        fringe = 0.0

    return round(rg_shift, 4), round(rb_shift, 4), round(float(np.clip(fringe, 0.0, 1.0)), 4)


def _compute_bloom_halo_energy(gray_f32: np.ndarray) -> float:
    """Measure bright glow/bloom halo spread around high-luminance regions."""
    bright_mask = (gray_f32 > 220.0).astype(np.float32)
    bright_ratio = float(np.mean(bright_mask))
    if bright_ratio < 0.001 or bright_ratio > 0.85:
        return 0.0

    # Dilate bright core to inspect surrounding halo zone
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    core = cv2.dilate(bright_mask, kernel, iterations=1)
    outer = cv2.dilate(bright_mask, kernel, iterations=3)
    halo_ring = np.clip(outer - core, 0.0, 1.0)
    ring_pixels = float(np.sum(halo_ring))
    if ring_pixels < 10.0:
        return 0.0

    blurred = cv2.GaussianBlur(gray_f32, (21, 21), 6.0)
    halo_luma = float(np.sum(blurred * halo_ring) / ring_pixels)
    bg_mask = 1.0 - outer
    bg_luma = float(np.sum(gray_f32 * bg_mask) / (float(np.sum(bg_mask)) + 1.0))

    halo_excess = max(0.0, halo_luma - bg_luma) / 255.0
    return round(float(np.clip(halo_excess, 0.0, 1.0)), 4)


def _compute_scanline_tear_score(prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
    """Detect horizontal scanline tearing / displacement jumps typical of glitch effects."""
    diff = np.abs(curr_gray.astype(np.float32) - prev_gray.astype(np.float32))
    row_means = np.mean(diff, axis=1)
    if float(np.mean(row_means)) < 1.5:
        return 0.0
    row_jumps = np.abs(np.diff(row_means))
    p98 = float(np.percentile(row_jumps, 98))
    median_jump = float(np.median(row_jumps)) + 1.0
    ratio = (p98 / median_jump - 1.0) / 12.0
    return round(float(np.clip(ratio, 0.0, 1.0)), 4)


def _compute_particle_speckles(prev_gray: np.ndarray, curr_gray: np.ndarray) -> int:
    """Count small isolated high-contrast moving bright speckles (particles/sparks/dust)."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    tophat = cv2.morphologyEx(curr_gray, cv2.MORPH_TOPHAT, kernel)
    temp_diff = cv2.absdiff(curr_gray, prev_gray)
    combined = cv2.bitwise_and(tophat, temp_diff)
    _, thresh = cv2.threshold(combined, 28, 255, cv2.THRESH_BINARY)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    count = 0
    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if 2 <= area <= 45:
            count += 1
    return count


def extract_frame_signals(
    decoded_frames: Iterable[DecodedFrame],
    dense_frame_indices: set[int] | None = None,
    dense_frame_stride: int | None = None,
) -> list[FrameSignalEntry]:
    """Compute per-frame visual, motion, chromatic, sharpness, and activity signals."""
    signals: list[FrameSignalEntry] = []
    prev_small_bgr: np.ndarray | None = None
    prev_small_gray: np.ndarray | None = None
    prev_luma: float | None = None
    prev_ts: float | None = None
    edge_history: deque[np.ndarray] = deque(maxlen=4)

    for stream_pos, item in enumerate(decoded_frames):
        bgr = item.bgr
        h, w = bgr.shape[:2]
        # Resize to standardized analysis resolution (max width 320) for consistent, fast metrics
        target_w = min(320, w)
        target_h = max(36, int(round(h * (target_w / max(1, w)))))
        small_bgr = cv2.resize(bgr, (target_w, target_h), interpolation=cv2.INTER_AREA)
        del bgr
        small_gray = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2GRAY)
        small_gray_f32 = small_gray.astype(np.float32)

        delta_t = 0.0 if prev_ts is None else max(1e-5, item.timestamp - prev_ts)
        mean_luma = float(np.mean(small_gray_f32))
        luma_std = float(np.std(small_gray_f32))
        luma_delta = 0.0 if prev_luma is None else (mean_luma - prev_luma)
        highlight_ratio = float(np.mean(small_gray_f32 > 235.0))

        # Sharpness via variance of Laplacian
        lap = cv2.Laplacian(small_gray_f32, cv2.CV_32F, ksize=3)
        lap_sharpness = float(np.var(lap))

        coherence, dom_angle = _compute_structure_tensor_anisotropy(small_gray_f32)
        bloom_energy = _compute_bloom_halo_energy(small_gray_f32)
        rg_shift, rb_shift, fringe_score = _compute_chromatic_aberration_metrics(small_bgr)

        max_ch_diff = 0.0
        changed_cell_area = 0.0
        flow_metrics_mag = 0.0
        flow_metrics_p95 = 0.0
        flow_dx = 0.0
        flow_dy = 0.0
        flow_scale = 0.0
        flow_rot = 0.0
        flow_res = 0.0
        flow_depth = 0.0
        trail_corr = 0.0
        particle_count = 0
        tear_score = 0.0

        if dense_frame_indices is not None:
            is_dense = item.frame_index in dense_frame_indices
        elif dense_frame_stride is not None and dense_frame_stride > 1:
            is_dense = (stream_pos % dense_frame_stride) == 0
        else:
            is_dense = True

        curr_edges = cv2.Canny(small_gray, 60, 150).astype(np.float32) / 255.0

        if prev_small_bgr is not None and prev_small_gray is not None:
            # 12x9 grid change detection inspired by video-effect-reel + mimic-mcp
            ch_diff = np.max(
                np.abs(small_bgr.astype(np.float32) - prev_small_bgr.astype(np.float32)),
                axis=2,
            )
            max_ch_diff = float(np.mean(ch_diff) * (100.0 / 255.0))
            grid = cv2.resize(ch_diff, (12, 9), interpolation=cv2.INTER_AREA)
            changed_cell_area = float(np.mean(grid > 18.0))

            if is_dense:
                flow = compute_optical_flow_metrics(prev_small_gray, small_gray)
                flow_metrics_mag = flow.magnitude_mean
                flow_metrics_p95 = flow.magnitude_p95
                flow_dx = flow.dx
                flow_dy = flow.dy
                flow_scale = flow.scale_rate
                flow_rot = flow.rotation_deg
                flow_res = flow.residual_mean
                flow_depth = flow.depth_layers_score

                tear_score = _compute_scanline_tear_score(prev_small_gray, small_gray)
                particle_count = _compute_particle_speckles(prev_small_gray, small_gray)

                # Motion trail / ghost echo correlation: check if frame difference aligns with lagged edges
                if len(edge_history) >= 2:
                    residual_frame = np.abs(small_gray_f32 - prev_small_gray.astype(np.float32)) / 255.0
                    lagged_edge = edge_history[0]
                    # Exclude current frame's primary edges to isolate trailing ghost edges
                    ghost_zone = np.clip(residual_frame * (1.0 - curr_edges), 0.0, 1.0)
                    denom = float(np.sqrt(np.sum(ghost_zone**2) * np.sum(lagged_edge**2))) + 1e-6
                    if denom > 1e-3:
                        trail_corr = float(np.clip(np.sum(ghost_zone * lagged_edge) / denom, 0.0, 1.0))

        edge_history.append(curr_edges)

        # Composite visual activity score (0..100) for adaptive window detection
        activity = (
            max_ch_diff * 0.45
            + changed_cell_area * 25.0
            + min(25.0, abs(luma_delta) * 0.5)
            + min(25.0, flow_metrics_mag * 2.5)
        )

        signals.append(
            FrameSignalEntry(
                frame_index=item.frame_index,
                timestamp=round(item.timestamp, 5),
                delta_t=round(delta_t, 5),
                mean_luma=round(mean_luma, 3),
                luma_delta=round(luma_delta, 3),
                luma_std=round(luma_std, 3),
                highlight_ratio=round(highlight_ratio, 4),
                bloom_halo_energy=bloom_energy,
                max_channel_diff=round(max_ch_diff, 3),
                changed_cell_area=round(changed_cell_area, 4),
                laplacian_sharpness=round(lap_sharpness, 3),
                gradient_anisotropy=coherence,
                dominant_gradient_angle_deg=dom_angle,
                rg_edge_shift_px=rg_shift,
                rb_edge_shift_px=rb_shift,
                chromatic_fringe_score=fringe_score,
                flow_magnitude_mean=flow_metrics_mag,
                flow_magnitude_p95=flow_metrics_p95,
                flow_dx=flow_dx,
                flow_dy=flow_dy,
                flow_scale_rate=flow_scale,
                flow_rotation_deg=flow_rot,
                flow_residual=flow_res,
                flow_depth_layers_score=flow_depth,
                trail_echo_correlation=round(trail_corr, 4),
                particle_speckle_count=particle_count,
                scanline_tear_score=tear_score,
                activity_score=round(float(np.clip(activity, 0.0, 100.0)), 3),
                is_dense_sampled=is_dense,
            )
        )

        prev_small_bgr = small_bgr
        prev_small_gray = small_gray
        prev_luma = mean_luma
        prev_ts = item.timestamp

    return signals


def detect_high_activity_windows(
    signals: list[FrameSignalEntry],
    padding_frames: int = 4,
) -> list[dict[str, float | int]]:
    """Identify contiguous intervals of high visual/motion variation using adaptive MAD thresholding."""
    if not signals:
        return []

    scores = np.array([s.activity_score for s in signals], dtype=np.float32)
    median = float(np.median(scores))
    mad = float(np.median(np.abs(scores - median))) + 1e-3
    threshold = max(12.0, median + 1.8 * mad)

    active_mask = scores >= threshold
    # Dilate active mask by padding_frames to capture full entry/exit of fast transitions
    dilated = np.zeros_like(active_mask, dtype=bool)
    n = len(signals)
    for idx, is_active in enumerate(active_mask):
        if is_active:
            lo = max(0, idx - padding_frames)
            hi = min(n, idx + padding_frames + 1)
            dilated[lo:hi] = True

    windows: list[dict[str, float | int]] = []
    in_win = False
    start_idx = 0
    for idx, val in enumerate(dilated):
        if val and not in_win:
            in_win = True
            start_idx = idx
        elif not val and in_win:
            in_win = False
            end_idx = idx - 1
            peak_idx = start_idx + int(np.argmax(scores[start_idx : end_idx + 1]))
            windows.append(
                {
                    "start_frame": signals[start_idx].frame_index,
                    "end_frame": signals[end_idx].frame_index,
                    "start_time": signals[start_idx].timestamp,
                    "end_time": signals[end_idx].timestamp,
                    "peak_frame": signals[peak_idx].frame_index,
                    "peak_activity_score": float(round(scores[peak_idx], 3)),
                }
            )
    if in_win:
        end_idx = n - 1
        peak_idx = start_idx + int(np.argmax(scores[start_idx : end_idx + 1]))
        windows.append(
            {
                "start_frame": signals[start_idx].frame_index,
                "end_frame": signals[end_idx].frame_index,
                "start_time": signals[start_idx].timestamp,
                "end_time": signals[end_idx].timestamp,
                "peak_frame": signals[peak_idx].frame_index,
                "peak_activity_score": float(round(scores[peak_idx], 3)),
            }
        )
    return windows
