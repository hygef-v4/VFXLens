"""Output aliases must never mutate reference files."""

import json

import cv2
import numpy as np
import pytest
from typer.testing import CliRunner

from vfx_engine.cli.main import app
from vfx_engine.core.safety import UnsafeFileError, compute_sha256
from vfx_engine.reports.project_reporter import write_project_reports
from vfx_engine.reports.video_reporter import write_video_reports
from vfx_engine.schemas.project_schema import ProjectAnalysisResult, ProjectMetadataSchema
from vfx_engine.video_analyzer.analyzer import VideoVFXAnalyzer
from vfx_engine.video_analyzer.decoder.ffprobe_decoder import DecodedFrame
from vfx_engine.video_analyzer.frame_analysis.contact_sheet import (
    export_evidence_frames_and_contact_sheet,
)


@pytest.fixture
def analyzed_clip(tmp_path_factory):
    root = tmp_path_factory.mktemp("output_safety")
    source = root / "source.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 10, (32, 32))
    assert writer.isOpened()
    for index in range(4):
        writer.write(np.full((32, 32, 3), index * 30, dtype=np.uint8))
    writer.release()
    result, timeline = VideoVFXAnalyzer().analyze(source, root / "initial")
    return source, result, timeline


@pytest.mark.parametrize("artifact", ["video-analysis.json", "timeline.json", "video-report.md"])
def test_video_report_rejects_source_hard_link_before_writing(analyzed_clip, tmp_path, artifact):
    source, result, timeline = analyzed_clip
    before = compute_sha256(source)
    (tmp_path / artifact).hardlink_to(source)
    with pytest.raises(UnsafeFileError):
        write_video_reports(result, timeline, tmp_path)
    assert compute_sha256(source) == before
    assert {p.name for p in tmp_path.iterdir()} == {artifact}


@pytest.mark.parametrize("artifact", ["project-analysis.json", "project-report.md"])
def test_project_report_rejects_source_hard_link_before_writing(tmp_path, artifact):
    source = tmp_path / "original.aepx"
    source.write_text("<AfterEffectsProject />", encoding="utf-8")
    before = compute_sha256(source)
    result = ProjectAnalysisResult(
        analysis_id="safety", analyzed_at="2026-11-15", extraction_method="offline_aepx",
        rerun_command="", metadata=ProjectMetadataSchema(
            file_path=str(source), file_name=source.name, file_format="aepx",
            file_size_bytes=source.stat().st_size, sha256=before,
        ),
    )
    out = tmp_path / "reports"
    out.mkdir()
    (out / artifact).hardlink_to(source)
    with pytest.raises(UnsafeFileError):
        write_project_reports(result, out)
    assert compute_sha256(source) == before
    assert {p.name for p in out.iterdir()} == {artifact}


@pytest.mark.parametrize("artifact", ["contact-sheet.jpg", "evidence-frames/frame_00000_0.000s.jpg"])
def test_evidence_export_rejects_source_hard_link(tmp_path, artifact):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"generated reference bytes")
    before = compute_sha256(source)
    destination = tmp_path / "outputs" / artifact
    destination.parent.mkdir(parents=True)
    destination.hardlink_to(source)
    frame = DecodedFrame(0, 0.0, 0.1, np.zeros((32, 32, 3), dtype=np.uint8))
    with pytest.raises(UnsafeFileError):
        export_evidence_frames_and_contact_sheet([frame], [], tmp_path / "outputs", frame_indices=[0])
    assert compute_sha256(source) == before


def test_video_cli_refuses_linked_report(analyzed_clip, tmp_path):
    source, _, _ = analyzed_clip
    before = compute_sha256(source)
    (tmp_path / "video-analysis.json").hardlink_to(source)
    result = CliRunner().invoke(app, ["analyze-video", str(source), "--output", str(tmp_path)])
    assert result.exit_code == 2, result.output
    assert compute_sha256(source) == before


def test_video_report_refuses_source_symlink(analyzed_clip, tmp_path):
    source, result, timeline = analyzed_clip
    before = compute_sha256(source)
    (tmp_path / "video-analysis.json").symlink_to(source)
    with pytest.raises(UnsafeFileError):
        write_video_reports(result, timeline, tmp_path)
    assert compute_sha256(source) == before


def test_video_reports_can_replace_regular_outputs(analyzed_clip, tmp_path):
    _, result, timeline = analyzed_clip
    write_video_reports(result, timeline, tmp_path)
    result = result.model_copy(update={"analysis_id": "second-analysis"})
    timeline = timeline.model_copy(update={"analysis_id": "second-analysis"})
    json_path, _, _ = write_video_reports(result, timeline, tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["analysis_id"] == "second-analysis"


def test_batch_summary_cannot_overwrite_reference(tmp_path):
    source = tmp_path / "broken.aep"
    source.write_bytes(b"generated invalid project")
    before = compute_sha256(source)
    out = tmp_path / "reports"
    out.mkdir()
    (out / "batch-summary.json").hardlink_to(source)
    result = CliRunner().invoke(app, ["analyze-folder", str(tmp_path), "--output", str(out)])
    assert result.exit_code != 0
    assert compute_sha256(source) == before
