"""Exact timestamps must never silently fall back to nominal FPS."""

import json
import subprocess

import pytest
from typer.testing import CliRunner

from vfx_engine.cli.main import app
from vfx_engine.core.safety import compute_sha256
from vfx_engine.video_analyzer.decoder.ffprobe_decoder import (
    iter_decoded_frames,
    probe_video_metadata_and_timestamps,
)


@pytest.fixture(scope="module")
def vfr_clip(tmp_path_factory):
    path = tmp_path_factory.mktemp("timestamps") / "variable.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=red:s=32x32:r=10:d=1",
        "-vf", "select='not(eq(mod(n,4),2))'", "-fps_mode", "vfr", "-c:v", "libx264",
        str(path),
    ], check=True)
    return path


def test_probe_and_decoder_preserve_measured_vfr_timestamps(vfr_clip):
    metadata, timestamps = probe_video_metadata_and_timestamps(vfr_clip)
    expected = [0.0, 0.1, 0.3, 0.4, 0.5, 0.7, 0.8, 0.9]
    assert timestamps == pytest.approx(expected)
    assert metadata.is_vfr
    assert [frame.timestamp for frame in iter_decoded_frames(vfr_clip, timestamps, metadata.nominal_fps)] == pytest.approx(expected)


@pytest.mark.parametrize("probe_failure", [
    subprocess.CompletedProcess([], 1, "", "injected PTS failure"),
    subprocess.CompletedProcess([], 0, '{"frames": []}', ""),
    subprocess.CompletedProcess([], 0, "invalid JSON", ""),
    subprocess.CompletedProcess([], 0, json.dumps({"frames": [{"pts_time": "0"}, {}]}), ""),
    subprocess.CompletedProcess([], 0, json.dumps({"frames": [{"pts_time": "N/A"}]}), ""),
    subprocess.CompletedProcess([], 0, json.dumps({"frames": [{"pts_time": "NaN"}]}), ""),
    subprocess.TimeoutExpired("ffprobe", 1),
])
def test_probe_refuses_missing_or_invalid_exact_timestamps(vfr_clip, monkeypatch, probe_failure):
    real_run = subprocess.run

    def run(args, *positional, **kwargs):
        if "-show_entries" in args:
            if isinstance(probe_failure, Exception):
                raise probe_failure
            return probe_failure
        return real_run(args, *positional, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(ValueError, match="(?i)timestamp"):
        probe_video_metadata_and_timestamps(vfr_clip)


def test_decoder_refuses_to_invent_timestamps_after_probe_coverage(vfr_clip):
    metadata, timestamps = probe_video_metadata_and_timestamps(vfr_clip)
    with pytest.raises(ValueError, match="(?i)timestamp"):
        list(iter_decoded_frames(vfr_clip, timestamps[:2], metadata.nominal_fps))


def test_cli_returns_error_without_reports_when_pts_probe_fails(vfr_clip, monkeypatch, tmp_path):
    real_run = subprocess.run
    before = compute_sha256(vfr_clip)

    def run(args, *positional, **kwargs):
        if "-show_entries" in args:
            return subprocess.CompletedProcess(args, 1, "", "injected PTS failure")
        return real_run(args, *positional, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    result = CliRunner().invoke(app, ["analyze-video", str(vfr_clip), "--output", str(tmp_path)])
    assert result.exit_code == 1, result.output
    assert "timestamp" in result.output.lower()
    assert not list(tmp_path.iterdir())
    assert compute_sha256(vfr_clip) == before
