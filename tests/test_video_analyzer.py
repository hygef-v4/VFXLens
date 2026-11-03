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


def test_video_frame_memory_is_bounded_not_proportional_to_frame_count(
    synthetic_fast_vfx_video: Path,
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    """Regression for Task 1: retained full-resolution frames must remain bounded O(1), not O(N)."""
    import gc
    import weakref

    import pytest

    import vfx_engine.video_analyzer.analyzer as analyzer_mod
    from vfx_engine.video_analyzer.decoder.ffprobe_decoder import iter_decoded_frames as real_iter

    def measure_peak_live_frames(frame_cap: int) -> int:
        live_refs: list[weakref.ReferenceType[object]] = []
        peak_live = 0

        def instrumented_iter(*args: object, **kwargs: object):
            nonlocal peak_live
            for idx, df in enumerate(real_iter(*args, **kwargs)):
                if idx % 20 == 0:
                    gc.collect()
                alive_now = sum(1 for r in live_refs if r() is not None)
                live_refs.append(weakref.ref(df.image_bgr))
                peak_live = max(peak_live, alive_now + 1)
                yield df

        monkeypatch.setattr(analyzer_mod, "iter_decoded_frames", instrumented_iter)
        out_dir = tmp_path / f"mem_bound_{frame_cap}"
        analyzer = VideoVFXAnalyzer()
        analyzer.analyze(synthetic_fast_vfx_video, output_dir=out_dir, max_frames=frame_cap)
        gc.collect()
        return peak_live

    peak_40 = measure_peak_live_frames(40)
    peak_120 = measure_peak_live_frames(120)

    # Full-resolution frame retention must be bounded (at most a few frames in flight),
    # never growing proportionally with clip length (40 vs 120).
    assert peak_40 <= 4, f"Expected <=4 live full-res frames for 40-frame run, got {peak_40}"
    assert peak_120 <= 4, f"Expected <=4 live full-res frames for 120-frame run, got {peak_120}"

    # Verify empty decode raises a clear ValueError
    monkeypatch.setattr(analyzer_mod, "iter_decoded_frames", lambda *a, **kw: iter([]))
    with pytest.raises(ValueError, match="No decodable video frames"):
        VideoVFXAnalyzer().analyze(synthetic_fast_vfx_video, output_dir=tmp_path / "empty_decode")


def test_capped_and_incomplete_video_analysis_preserves_source_totals(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    """Regression for Task 4: max_frames cap and incomplete decode must preserve source totals and report partial coverage."""
    import subprocess

    import cv2
    import numpy as np
    import pytest
    from typer.testing import CliRunner

    import vfx_engine.video_analyzer.analyzer as analyzer_mod
    from vfx_engine.cli.main import app
    from vfx_engine.video_analyzer.decoder.ffprobe_decoder import iter_decoded_frames as real_iter

    # Synthesize a 10-frame, 1.0-second (10 fps) video
    raw_avi = tmp_path / "ten_frames.avi"
    ten_mp4 = tmp_path / "ten_frames.mp4"
    writer = cv2.VideoWriter(str(raw_avi), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (320, 180))
    for i in range(10):
        img = np.full((180, 320, 3), i * 20, dtype=np.uint8)
        writer.write(img)
    writer.release()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "quiet",
            "-i",
            str(raw_avi),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(ten_mp4),
        ],
        check=True,
    )

    # 1. Capped at max_frames=3
    analyzer = VideoVFXAnalyzer()
    res_capped, tl_capped = analyzer.analyze(ten_mp4, output_dir=tmp_path / "capped_3", max_frames=3)
    assert res_capped.metadata.frame_count == 10
    assert res_capped.sampling.total_video_frames == 10
    assert res_capped.sampling.decoded_frames_count == 3
    assert res_capped.sampling.analyzed_frames_count == 3
    assert res_capped.sampling.is_partial is True
    assert res_capped.sampling.coverage_ratio == pytest.approx(0.3, abs=1e-3)
    assert "--max-frames 3" in res_capped.rerun_command
    assert any("MAX_FRAMES" in w.code or "PARTIAL" in w.code for w in res_capped.warnings)
    assert len(tl_capped.frames) == 3

    # 2. Zero and negative max_frames rejected programmatically and via CLI
    with pytest.raises(ValueError, match="max_frames"):
        analyzer.analyze(ten_mp4, output_dir=tmp_path / "cap_zero", max_frames=0)
    with pytest.raises(ValueError, match="max_frames"):
        analyzer.analyze(ten_mp4, output_dir=tmp_path / "cap_neg", max_frames=-2)

    runner = CliRunner()
    cli_zero = runner.invoke(app, ["analyze-video", str(ten_mp4), "--max-frames", "0", "--output", str(tmp_path / "cli_zero")])
    assert cli_zero.exit_code != 0
    cli_neg = runner.invoke(app, ["analyze-video", str(ten_mp4), "--max-frames", "-3", "--output", str(tmp_path / "cli_neg")])
    assert cli_neg.exit_code != 0

    # 3. Incomplete decoder output (decoder yields only 6 of 10 frames without max_frames cap)
    def truncated_iter(*args: object, **kwargs: object):
        for idx, df in enumerate(real_iter(*args, **kwargs)):
            if idx >= 6:
                break
            yield df

    monkeypatch.setattr(analyzer_mod, "iter_decoded_frames", truncated_iter)
    res_inc, tl_inc = analyzer.analyze(ten_mp4, output_dir=tmp_path / "incomplete_6")
    assert res_inc.metadata.frame_count == 10
    assert res_inc.sampling.total_video_frames == 10
    assert res_inc.sampling.decoded_frames_count == 6
    assert res_inc.sampling.analyzed_frames_count == 6
    assert res_inc.sampling.is_partial is True
    assert res_inc.sampling.coverage_ratio == pytest.approx(0.6, abs=1e-3)
    assert any("INCOMPLETE" in w.code or "PARTIAL" in w.code for w in res_inc.warnings)
    assert len(tl_inc.frames) == 6


def test_export_evidence_frames_and_contact_sheet_raises_on_failed_imwrite(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    """Regression for Follow-up Task 2: failed cv2.imwrite for evidence JPEG or contact sheet must raise OSError with path."""
    import cv2
    import numpy as np
    import pytest

    from vfx_engine.schemas.video_schema import VideoEffectEventSchema
    from vfx_engine.video_analyzer.decoder.ffprobe_decoder import DecodedFrame
    from vfx_engine.video_analyzer.frame_analysis.contact_sheet import (
        export_evidence_frames_and_contact_sheet,
    )

    real_imwrite = cv2.imwrite

    for failure_target in ("evidence_jpeg", "contact_sheet"):
        frames = [
            DecodedFrame(
                frame_index=i,
                timestamp=i / 30.0,
                delta_t=1.0 / 30.0,
                image_bgr=np.full((180, 320, 3), 40 + i * 20, dtype=np.uint8),
            )
            for i in range(3)
        ]
        event = VideoEffectEventSchema(
            event_id="ev_001",
            effect_type="flash_frame",
            start_time=0.0,
            end_time=0.066,
            start_frame=0,
            end_frame=2,
            peak_frame=1,
            peak_time=0.033,
            confidence=0.9,
            confidence_explanation="test",
            extraction_method="test",
        )
        out_sub = tmp_path / f"fail_{failure_target}"

        def fake_imwrite(filename: str, img: object, params: object = None, _target: str = failure_target) -> bool:
            if _target == "evidence_jpeg" and "evidence-frames" in str(filename):
                return False
            if _target == "contact_sheet" and str(filename).endswith("contact-sheet.jpg"):
                return False
            return bool(real_imwrite(filename, img, params))  # type: ignore[arg-type]

        monkeypatch.setattr(cv2, "imwrite", fake_imwrite)

        expected_substr = "evidence-frames" if failure_target == "evidence_jpeg" else "contact-sheet.jpg"
        with pytest.raises(OSError, match=expected_substr):
            export_evidence_frames_and_contact_sheet(
                decoded_frames=iter(frames),
                events=[event],
                output_dir=out_sub,
            )
        if failure_target == "evidence_jpeg":
            assert event.evidence_frames == []


def test_contact_sheet_bounds_thumbnail_allocations_while_preserving_all_event_evidence(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    """Regression for Follow-up Task 4: 60 event peaks with max_sheet_tiles=25 must allocate at most 25 thumbnails while saving all 60 event evidence JPEGs."""
    import cv2
    import numpy as np

    from vfx_engine.schemas.video_schema import VideoEffectEventSchema
    from vfx_engine.video_analyzer.decoder.ffprobe_decoder import DecodedFrame
    from vfx_engine.video_analyzer.frame_analysis.contact_sheet import (
        export_evidence_frames_and_contact_sheet,
    )

    real_resize = cv2.resize

    for mode in ("with_frame_indices", "generator_without_frame_indices"):
        resize_calls = 0

        def counting_resize(*args: object, **kwargs: object) -> object:
            nonlocal resize_calls
            resize_calls += 1
            return real_resize(*args, **kwargs)  # type: ignore[arg-type]

        monkeypatch.setattr(cv2, "resize", counting_resize)

        def make_frame_stream():
            for i in range(60):
                yield DecodedFrame(
                    frame_index=i,
                    timestamp=i / 30.0,
                    delta_t=1.0 / 30.0,
                    image_bgr=np.full((180, 320, 3), (i * 4) % 255, dtype=np.uint8),
                )

        events = [
            VideoEffectEventSchema(
                event_id=f"ev_{i:03d}",
                effect_type="flash_frame",
                start_time=i / 30.0,
                end_time=i / 30.0,
                start_frame=i,
                end_frame=i,
                peak_frame=i,
                peak_time=i / 30.0,
                confidence=0.85,
                confidence_explanation="synthetic peak",
                extraction_method="test",
            )
            for i in range(60)
        ]

        out_sub = tmp_path / f"thumb_bound_{mode}"
        supplied_indices = list(range(60)) if mode == "with_frame_indices" else None

        cs_rel, ev_dir_rel, ev_files = export_evidence_frames_and_contact_sheet(
            decoded_frames=make_frame_stream(),
            events=events,
            output_dir=out_sub,
            max_sheet_tiles=25,
            frame_indices=supplied_indices,
        )

        assert resize_calls <= 25, f"Mode {mode}: expected <=25 thumbnail resize calls, got {resize_calls}"
        assert (out_sub / cs_rel).exists()
        assert len(ev_files) == 60
        for ev in events:
            assert len(ev.evidence_frames) == 1
            assert (out_sub / ev.evidence_frames[0]).exists()




