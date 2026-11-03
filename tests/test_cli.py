"""CLI smoke and integration tests for `vfx` commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from vfx_engine.cli.main import app

runner = CliRunner()


def test_cli_doctor_json() -> None:
    """Verify `vfx doctor --json` outputs valid environment diagnostics."""
    res = runner.invoke(app, ["doctor", "--json"])
    assert res.exit_code == 0
    payload = json.loads(res.stdout)
    assert payload["ready"] is True
    assert payload["ffmpeg"]["available"] is True
    assert payload["ffprobe"]["available"] is True


def test_cli_analyze_project_and_inspect(
    complex_vfx_aep_and_aepx: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    """Verify `vfx analyze-project` and `vfx inspect` end-to-end."""
    aep_path, _ = complex_vfx_aep_and_aepx
    out_dir = tmp_path / "cli_proj_out"

    res = runner.invoke(app, ["analyze-project", str(aep_path), "--output", str(out_dir)])
    assert res.exit_code == 0

    json_file = out_dir / "project-analysis.json"
    md_file = out_dir / "project-report.md"
    assert json_file.exists()
    assert md_file.exists()

    insp = runner.invoke(app, ["inspect", str(json_file)])
    assert insp.exit_code == 0
    assert "S_Shake" in insp.stdout
    assert "Deep Glow" in insp.stdout


def test_cli_refuses_aex_with_exit_code_2(fake_aex_plugin_path: Path, tmp_path: Path) -> None:
    """Verify `vfx analyze-project` exits with code 2 when given an `.aex` binary plugin."""
    res = runner.invoke(app, ["analyze-project", str(fake_aex_plugin_path), "--output", str(tmp_path / "aex_out")])
    assert res.exit_code == 2
    assert "Safety Refusal" in res.stdout


def test_cli_analyze_video_and_inspect(
    synthetic_fast_vfx_video: Path,
    tmp_path: Path,
) -> None:
    """Verify `vfx analyze-video` and `vfx inspect` end-to-end."""
    out_dir = tmp_path / "cli_vid_out"
    res = runner.invoke(app, ["analyze-video", str(synthetic_fast_vfx_video), "--output", str(out_dir)])
    assert res.exit_code == 0

    json_file = out_dir / "video-analysis.json"
    tl_file = out_dir / "timeline.json"
    md_file = out_dir / "video-report.md"
    cs_file = out_dir / "contact-sheet.jpg"

    assert json_file.exists()
    assert tl_file.exists()
    assert md_file.exists()
    assert cs_file.exists()

    insp = runner.invoke(app, ["inspect", str(json_file)])
    assert insp.exit_code == 0
    assert "Detected VFX Events" in insp.stdout


def test_cli_analyze_folder_recursive(
    fixtures_dir: Path,
    complex_vfx_aep_and_aepx: tuple[Path, Path],
    synthetic_fast_vfx_video: Path,
    fake_aex_plugin_path: Path,
    tmp_path: Path,
) -> None:
    """Verify `vfx analyze-folder --recursive` processes projects and videos while skipping `.aex` plugins."""
    batch_out = tmp_path / "cli_batch_out"
    res = runner.invoke(app, ["analyze-folder", str(fixtures_dir), "--recursive", "--output", str(batch_out)])
    assert res.exit_code == 0

    summary_path = batch_out / "batch-summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert len(summary["projects_analyzed"]) >= 2
    assert len(summary["videos_analyzed"]) >= 1
    assert len(summary["skipped_aex_plugins"]) >= 1
