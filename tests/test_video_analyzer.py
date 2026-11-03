"""Unit and integration tests for Video VFX Analyzer."""

from __future__ import annotations

from pathlib import Path

from vfx_engine.core.safety import compute_sha256
from vfx_engine.reports.video_reporter import write_video_reports
from vfx_engine.schemas.common import DataAvailabilityStatus
from vfx_engine.video_analyzer.analyzer import VideoVFXAnalyzer


def test_video_vfx_analyzer_detects_fast_vfx_events_and_writes_outputs(
    synthetic_fast_vfx_video: Path,
    tmp_path: Path,
) -> None:
    """Verify full-frame decoding, signal extraction, scene cuts, and VFX candidates on a fast VFX video."""
    out_dir = tmp_path / "video_run1"
    before_sha = compute_sha256(synthetic_fast_vfx_video)

    analyzer = VideoVFXAnalyzer()
    result, timeline = analyzer.analyze(synthetic_fast_vfx_video, output_dir=out_dir)
    json_path, tl_path, md_path = write_video_reports(result, timeline, out_dir)

    after_sha = compute_sha256(synthetic_fast_vfx_video)
    assert before_sha == after_sha, "Source video file must never be mutated!"

    # 1. Verify metadata and full-frame sampling
    assert result.metadata.width == 640
    assert result.metadata.height == 360
    assert result.metadata.frame_count == 150
    assert result.sampling.strategy == "full_frame_with_adaptive_windows"
    assert result.sampling.analyzed_frames_count == 150
    assert result.sampling.coverage_ratio == 1.0
    assert len(timeline.frames) == 150

    # 2. Verify scene cuts and VFX candidate types detected
    assert len(result.scenes) >= 2
    detected_types = {ev.effect_type for ev in result.effect_events}

    # Our synthetic video contains cuts, flash, shake, zoom punch, motion blur, RGB split, glow/bloom, speed ramp, particles, distortion
    expected_core_effects = {
        "scene_cut",
        "flash_frame",
        "camera_shake",
        "zoom_punch_transition",
        "motion_blur",
        "rgb_split_chromatic_aberration",
        "glow_bloom",
        "particles_overlay",
        "distortion_displacement",
    }
    missing = expected_core_effects - detected_types
    assert not missing, f"Expected VFX detectors did not fire for: {missing} (got {detected_types})"

    # 3. Verify epistemic separation (observations vs techniques vs unverified plugins)
    for ev in result.effect_events:
        assert len(ev.observations) >= 1
        assert len(ev.possible_ae_techniques) >= 1
        assert len(ev.undetermined_parameters) >= 1
        assert 0.0 < ev.confidence <= 1.0
        assert ev.confidence_explanation
        assert ev.verified is False
        assert len(ev.evidence_frames) >= 1

    # 4. Verify AI Vision adapter defaults to honest NoOpVisionAnalyzer
    assert result.vision_analysis.analyzed is False
    assert result.vision_analysis.status == DataAvailabilityStatus.UNAVAILABLE

    # 5. Verify output artifacts on disk
    assert json_path.exists()
    assert tl_path.exists()
    assert md_path.exists()
    assert (out_dir / result.sampling.contact_sheet_path).exists()
    assert (out_dir / result.sampling.evidence_frames_dir).is_dir()
    assert len(result.sampling.evidence_frame_files) >= 5


def test_video_vfx_analyzer_detects_vfr_timestamps(
    synthetic_vfr_video: Path,
    tmp_path: Path,
) -> None:
    """Verify Variable Frame Rate (VFR) detection via ffprobe per-frame PTS jitter."""
    out_dir = tmp_path / "video_vfr"
    analyzer = VideoVFXAnalyzer()
    result, timeline = analyzer.analyze(synthetic_vfr_video, output_dir=out_dir)

    assert result.metadata.is_vfr is True
    assert result.metadata.vfr_jitter_ms > 1.5
    assert len(timeline.frames) == result.metadata.frame_count
