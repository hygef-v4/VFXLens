"""Pydantic schemas for Video VFX Analyzer (`video-analysis.json` and `timeline.json`)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import AnalysisWarning, DataAvailabilityStatus


class VideoMetadataSchema(BaseModel):
    """Decoded video stream and container metadata."""

    file_path: str
    file_name: str
    file_size_bytes: int
    sha256: str
    container_format: str
    video_codec: str
    codec_profile: str | None = None
    pixel_format: str | None = None
    width: int
    height: int
    aspect_ratio: str | None = None
    nominal_fps: float
    average_fps: float
    r_frame_rate: str | None = None
    avg_frame_rate: str | None = None
    is_vfr: bool = Field(default=False, description="True if Variable Frame Rate is detected")
    vfr_jitter_ms: float = Field(default=0.0, description="Std dev of inter-frame PTS deltas in ms")
    duration_seconds: float
    frame_count: int
    bit_rate: int | None = None
    has_audio: bool = False
    audio_codec: str | None = None
    audio_sample_rate: int | None = None
    audio_channels: int | None = None


class FrameSignalEntry(BaseModel):
    """Per-frame measured visual, color, sharpness, chromatic, and optical flow signals."""

    frame_index: int
    timestamp: float = Field(..., description="Exact presentation timestamp in seconds")
    delta_t: float = Field(..., description="Time elapsed since previous frame in seconds")
    mean_luma: float = Field(..., description="Mean luminance (0..255)")
    luma_delta: float = Field(default=0.0, description="Signed luminance change from previous frame")
    luma_std: float = Field(..., description="Luminance standard deviation (contrast)")
    highlight_ratio: float = Field(..., description="Fraction of pixels with luma > 235 (0..1)")
    bloom_halo_energy: float = Field(default=0.0, description="Low-frequency glow halo energy around bright areas")
    max_channel_diff: float = Field(default=0.0, description="Mean of per-pixel max(|dR|,|dG|,|dB|) scaled 0..100")
    changed_cell_area: float = Field(default=0.0, description="Fraction of 12x9 grid cells that changed significantly (0..1)")
    laplacian_sharpness: float = Field(default=0.0, description="Variance of Laplacian (edge sharpness)")
    gradient_anisotropy: float = Field(default=0.0, description="Directional blur/gradient orientation coherence (0..1)")
    dominant_gradient_angle_deg: float = Field(default=0.0, description="Dominant edge/blur angle in degrees")
    rg_edge_shift_px: float = Field(default=0.0, description="Estimated subpixel/pixel shift between Red and Green edges")
    rb_edge_shift_px: float = Field(default=0.0, description="Estimated subpixel/pixel shift between Red and Blue edges")
    chromatic_fringe_score: float = Field(default=0.0, description="Normalized high-contrast edge color channel divergence")
    flow_magnitude_mean: float = Field(default=0.0, description="Mean optical flow magnitude (px/frame)")
    flow_magnitude_p95: float = Field(default=0.0, description="95th percentile optical flow magnitude (px/frame)")
    flow_dx: float = Field(default=0.0, description="Global horizontal translation (px/frame)")
    flow_dy: float = Field(default=0.0, description="Global vertical translation (px/frame)")
    flow_scale_rate: float = Field(default=0.0, description="Global radial zoom rate per frame (>0 zoom in, <0 zoom out)")
    flow_rotation_deg: float = Field(default=0.0, description="Global in-plane rotation per frame in degrees")
    flow_residual: float = Field(default=0.0, description="Non-affine optical flow residual (distortion/parallax/local motion)")
    flow_depth_layers_score: float = Field(default=0.0, description="Bimodal/multi-layer flow velocity separation (parallax cue)")
    trail_echo_correlation: float = Field(default=0.0, description="Correlation of current residual with lagged frame edges")
    particle_speckle_count: int = Field(default=0, description="Count of isolated high-contrast small moving blobs/particles")
    scanline_tear_score: float = Field(default=0.0, description="Horizontal row-to-row displacement discontinuity (glitch cue)")
    activity_score: float = Field(default=0.0, description="Composite visual change score used for adaptive sampling")
    is_dense_sampled: bool = True


class SceneBoundarySchema(BaseModel):
    """Detected scene segment bounded by cuts, flashes, or transitions."""

    scene_index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    cut_score: float = 0.0
    transition_type: str = Field(
        default="hard_cut",
        description="initial_scene, hard_cut, flash_cut, dissolve_fade, or whip_zoom_cut",
    )


class VideoEffectEventSchema(BaseModel):
    """Detected VFX/motion event with separated observations, AE techniques, and plugin candidates."""

    event_id: str
    effect_type: str = Field(
        ...,
        description=(
            "scene_cut, flash_frame, camera_shake, zoom_punch_transition, speed_ramp, "
            "motion_blur, rgb_split_chromatic_aberration, glow_bloom, distortion_displacement, "
            "motion_trail_echo, masking_reveal, particles_overlay, kinetic_typography_candidate, "
            "camera_3d_parallax, or compositing_overlay"
        ),
    )
    start_time: float
    end_time: float
    start_frame: int
    end_frame: int
    peak_frame: int
    peak_time: float
    observations: list[str] = Field(
        default_factory=list,
        description="Direct visual/signal observations measured from the video frames",
    )
    measured_signals: dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative measurements backing the detection",
    )
    possible_ae_techniques: list[str] = Field(
        default_factory=list,
        description="Plausible After Effects workflows/techniques that could produce this effect",
    )
    possible_plugins: list[str] = Field(
        default_factory=list,
        description="Suspected third-party or built-in AE plugins (never claimed with certainty from pixels alone)",
    )
    undetermined_parameters: list[str] = Field(
        default_factory=list,
        description="Exact AE parameters that cannot be recovered from rendered MP4/MOV pixels",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score (0.0 to 1.0)")
    confidence_explanation: str = Field(
        ...,
        description="Deterministic explanation of how the confidence score was derived from measured signals",
    )
    extraction_method: str = Field(
        ...,
        description="Name of the signal detector, optical flow estimator, or vision adapter that produced this event",
    )
    evidence_frames: list[str] = Field(
        default_factory=list,
        description="Relative paths to extracted evidence PNG/JPG frames for this event",
    )
    source: DataAvailabilityStatus = Field(
        default=DataAvailabilityStatus.INFERRED,
        description="OBSERVED for direct signal measurements (e.g. luminance spike, cut) or INFERRED for technique candidates",
    )
    verified: bool = Field(
        default=False,
        description="False when analyzed from rendered video alone without matching .aep ground truth",
    )


class VisionAnalysisSummarySchema(BaseModel):
    """Status and output of the optional AI Vision adapter."""

    provider: str = "none"
    model: str | None = None
    status: DataAvailabilityStatus = DataAvailabilityStatus.UNAVAILABLE
    analyzed: bool = False
    semantic_observations: list[dict[str, Any]] = Field(default_factory=list)
    note: str = (
        "AI Vision provider not configured; computer-vision signal detectors ran locally "
        "and semantic-only judgements are marked as unavailable."
    )


class SamplingSummarySchema(BaseModel):
    """Summary of frame decoding and adaptive sampling."""

    strategy: str = Field(
        ...,
        description="full_frame_with_adaptive_windows or adaptive_two_pass",
    )
    total_video_frames: int
    analyzed_frames_count: int
    coverage_ratio: float
    high_activity_windows: list[dict[str, float | int]] = Field(default_factory=list)
    contact_sheet_path: str
    evidence_frames_dir: str
    evidence_frame_files: list[str] = Field(default_factory=list)


class VideoTimelineSchema(BaseModel):
    """Schema for `timeline.json` containing the full frame-by-frame signal timeline."""

    analysis_id: str
    video_file: str
    nominal_fps: float
    is_vfr: bool
    frame_count: int
    duration_seconds: float
    high_activity_windows: list[dict[str, float | int]] = Field(default_factory=list)
    scenes: list[SceneBoundarySchema] = Field(default_factory=list)
    events_summary: list[dict[str, Any]] = Field(default_factory=list)
    frames: list[FrameSignalEntry] = Field(default_factory=list)


class VideoAnalysisResult(BaseModel):
    """Top-level normalized output schema for `video-analysis.json`."""

    schema_version: str = "1.0.0"
    analysis_id: str
    analyzed_at: str
    rerun_command: str
    metadata: VideoMetadataSchema
    sampling: SamplingSummarySchema
    scenes: list[SceneBoundarySchema] = Field(default_factory=list)
    effect_events: list[VideoEffectEventSchema] = Field(default_factory=list)
    vision_analysis: VisionAnalysisSummarySchema
    undetermined_video_aspects: list[str] = Field(default_factory=list)
    warnings: list[AnalysisWarning] = Field(default_factory=list)
