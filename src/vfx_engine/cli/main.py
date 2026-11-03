"""Typer CLI entrypoint for VFX Learning Engine (`vfx`)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from ..core.config import EngineConfig
from ..core.doctor import run_environment_doctor
from ..core.logging import console, setup_logging
from ..core.safety import SUPPORTED_VIDEO_EXTENSIONS, UnsafeFileError
from ..project_analyzer.analyzer import analyze_ae_project
from ..reports.project_reporter import write_project_reports
from ..reports.video_reporter import write_video_reports
from ..video_analyzer.analyzer import VideoVFXAnalyzer

app = typer.Typer(
    name="vfx",
    help="VFX Learning Engine — Phase 1: After Effects Project Analyzer (.aep/.aepx) & Video VFX Analyzer.",
    no_args_is_help=True,
    add_completion=False,
)


def _default_output_dir(base: Path, prefix: str, target_path: Path) -> Path:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", target_path.stem).strip("_")[:28] or "item"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return base / f"{prefix}_{slug}_{ts}"


@app.command("analyze-project")
def cmd_analyze_project(
    project_path: Annotated[
        Path,
        typer.Argument(help="Path to the .aep or .aepx After Effects project file."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for project-analysis.json and project-report.md."),
    ] = None,
    use_ae_bridge: Annotated[
        bool,
        typer.Option(
            "--use-ae-bridge",
            help="Attempt read-only comparison with a running After Effects MCP bridge if available.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose debug logging."),
    ] = False,
) -> None:
    """Analyze an After Effects `.aep` or `.aepx` project (read-only) and export JSON + Markdown reports."""
    setup_logging("DEBUG" if verbose else "INFO")
    cfg = EngineConfig()
    out_dir = (output or _default_output_dir(cfg.outputs_dir, "proj", project_path)).resolve()

    try:
        result = analyze_ae_project(
            project_path=project_path,
            config=cfg,
            use_ae_bridge=use_ae_bridge,
        )
        result.rerun_command = (
            f'vfx analyze-project "{project_path.resolve()}" --output "{out_dir}"'
            + (" --use-ae-bridge" if use_ae_bridge else "")
        )
        json_path, md_path = write_project_reports(result, out_dir)
    except UnsafeFileError as exc:
        console.print(f"[bold red]Safety Refusal:[/bold red] {exc}")
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        console.print(f"[bold red]Project Analysis Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    m = result.metadata
    third_party_count = sum(1 for p in result.plugin_inventory if p.is_third_party)

    table = Table(title=f"Project Analysis Summary: {m.file_name}", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Analysis ID", result.analysis_id)
    table.add_row("Format / Version", f"{m.file_format.upper()} / {m.ae_version or 'unknown'}")
    table.add_row("Extraction Method", result.extraction_method)
    table.add_row("Live Bridge Tested", str(result.live_bridge_tested))
    table.add_row("Compositions (Precomps)", f"{m.total_compositions} ({m.total_precompositions} precomps)")
    table.add_row("Distinct Plugins (3rd Party)", f"{len(result.plugin_inventory)} ({third_party_count} third-party)")
    table.add_row("Active Expressions", str(len(result.expressions_inventory)))
    table.add_row("Output JSON", str(json_path))
    table.add_row("Output Markdown", str(md_path))
    console.print(table)


@app.command("analyze-video")
def cmd_analyze_video(
    video_path: Annotated[
        Path,
        typer.Argument(help="Path to the MP4, MOV, or FFmpeg-supported video file."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for video-analysis.json, timeline.json, and contact-sheet.jpg."),
    ] = None,
    max_frames: Annotated[
        int | None,
        typer.Option("--max-frames", help="Optional cap on decoded frames."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose debug logging."),
    ] = False,
) -> None:
    """Analyze a VFX video for cuts, flashes, camera shake, zoom punches, speed ramps, glow, RGB split, and blur."""
    setup_logging("DEBUG" if verbose else "INFO")
    cfg = EngineConfig()
    out_dir = (output or _default_output_dir(cfg.outputs_dir, "vid", video_path)).resolve()

    try:
        analyzer = VideoVFXAnalyzer(config=cfg)
        result, timeline = analyzer.analyze(
            video_path=video_path,
            output_dir=out_dir,
            max_frames=max_frames,
        )
        json_path, timeline_path, md_path = write_video_reports(result, timeline, out_dir)
    except UnsafeFileError as exc:
        console.print(f"[bold red]Safety Refusal:[/bold red] {exc}")
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        console.print(f"[bold red]Video Analysis Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    m = result.metadata
    s = result.sampling
    frames_summary = (
        f"{m.duration_seconds:.3f}s / {s.decoded_frames_count}/{m.frame_count} decoded frames"
        if s.is_partial
        else f"{m.duration_seconds:.3f}s / {m.frame_count} frames"
    )
    table = Table(title=f"Video VFX Analysis Summary: {m.file_name}", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Analysis ID", result.analysis_id)
    table.add_row("Resolution / Codec", f"{m.width}x{m.height} / {m.video_codec}")
    table.add_row("Duration / Frames", frames_summary)
    table.add_row("FPS / VFR", f"{m.nominal_fps:.2f} fps (VFR={m.is_vfr}, jitter={m.vfr_jitter_ms:.2f}ms)")
    table.add_row(
        "Sampling Strategy",
        f"{s.strategy} ({s.coverage_ratio * 100:.1f}% source coverage, partial={s.is_partial})",
    )
    table.add_row("Scenes Detected", str(len(result.scenes)))
    table.add_row("VFX Events Detected", str(len(result.effect_events)))
    table.add_row("Output JSON", str(json_path))
    table.add_row("Timeline JSON", str(timeline_path))
    table.add_row("Report Markdown", str(md_path))
    table.add_row("Contact Sheet", str(out_dir / s.contact_sheet_path))
    console.print(table)


@app.command("analyze-folder")
def cmd_analyze_folder(
    folder_path: Annotated[
        Path,
        typer.Argument(help="Folder containing .aep, .aepx, or video files."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for batch analysis."),
    ] = None,
    recursive: Annotated[
        bool,
        typer.Option("--recursive/--no-recursive", "-r", help="Recursively scan subdirectories."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose debug logging."),
    ] = False,
) -> None:
    """Batch-analyze all `.aep`, `.aepx`, and video files in a folder (skipping `.aex` plugins safely)."""
    setup_logging("DEBUG" if verbose else "INFO")
    cfg = EngineConfig()
    root = folder_path.resolve()
    if not root.exists() or not root.is_dir():
        console.print(f"[bold red]Folder does not exist:[/bold red] {root}")
        raise typer.Exit(code=1)

    out_dir = (output or _default_output_dir(cfg.outputs_dir, "batch", root)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    iterator = root.rglob("*") if recursive else root.glob("*")
    project_files: list[Path] = []
    video_files: list[Path] = []
    skipped_aex: list[str] = []

    for p in sorted(iterator):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext == ".aex":
            skipped_aex.append(str(p))
        elif ext in (".aep", ".aepx"):
            project_files.append(p)
        elif ext in SUPPORTED_VIDEO_EXTENSIONS:
            video_files.append(p)

    batch_summary: dict[str, object] = {
        "scanned_folder": str(root),
        "recursive": recursive,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "projects_analyzed": [],
        "videos_analyzed": [],
        "skipped_aex_plugins": skipped_aex,
        "errors": [],
    }

    proj_list: list[dict[str, object]] = []
    vid_list: list[dict[str, object]] = []
    err_list: list[dict[str, str]] = []

    for idx, pfile in enumerate(project_files, start=1):
        sub_out = out_dir / f"project_{idx:03d}_{pfile.stem}"
        try:
            res = analyze_ae_project(pfile, config=cfg)
            j_path, m_path = write_project_reports(res, sub_out)
            proj_list.append(
                {
                    "file": str(pfile),
                    "analysis_id": res.analysis_id,
                    "compositions": res.metadata.total_compositions,
                    "plugins": len(res.plugin_inventory),
                    "json_report": str(j_path),
                    "markdown_report": str(m_path),
                }
            )
        except Exception as exc:
            err_list.append({"file": str(pfile), "error": str(exc)})

    video_analyzer = VideoVFXAnalyzer(config=cfg)
    for idx, vfile in enumerate(video_files, start=1):
        sub_out = out_dir / f"video_{idx:03d}_{vfile.stem}"
        try:
            v_res, v_tl = video_analyzer.analyze(vfile, output_dir=sub_out)
            j_path, tl_path, m_path = write_video_reports(v_res, v_tl, sub_out)
            vid_list.append(
                {
                    "file": str(vfile),
                    "analysis_id": v_res.analysis_id,
                    "scenes": len(v_res.scenes),
                    "effect_events": len(v_res.effect_events),
                    "json_report": str(j_path),
                    "timeline_json": str(tl_path),
                    "markdown_report": str(m_path),
                }
            )
        except Exception as exc:
            err_list.append({"file": str(vfile), "error": str(exc)})

    batch_summary["projects_analyzed"] = proj_list
    batch_summary["videos_analyzed"] = vid_list
    batch_summary["errors"] = err_list

    summary_path = out_dir / "batch-summary.json"
    summary_path.write_text(json.dumps(batch_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    console.print(
        Panel(
            f"Scanned: [cyan]{root}[/cyan]\n"
            f"Projects Analyzed: [green]{len(proj_list)}[/green]\n"
            f"Videos Analyzed: [green]{len(vid_list)}[/green]\n"
            f"Skipped .aex Binary Plugins: [yellow]{len(skipped_aex)}[/yellow]\n"
            f"Errors: [red]{len(err_list)}[/red]\n"
            f"Batch Summary JSON: [bold]{summary_path}[/bold]",
            title="Batch Analysis Complete",
        )
    )


@app.command("inspect")
def cmd_inspect(
    json_file: Annotated[
        Path,
        typer.Argument(help="Path to project-analysis.json, video-analysis.json, or timeline.json."),
    ],
) -> None:
    """Inspect a generated analysis JSON artifact with formatted summary tables."""
    target = json_file.resolve()
    if not target.exists():
        console.print(f"[bold red]File not found:[/bold red] {target}")
        raise typer.Exit(code=1)

    data = json.loads(target.read_text(encoding="utf-8"))

    if "compositions" in data and "plugin_inventory" in data:
        meta = data.get("metadata", {})
        console.print(
            Panel(
                f"[bold cyan]Project:[/bold cyan] {meta.get('file_name')} ({meta.get('file_format', '').upper()})\n"
                f"[bold cyan]AE Version:[/bold cyan] {meta.get('ae_version')}\n"
                f"[bold cyan]Extraction Method:[/bold cyan] {data.get('extraction_method')} "
                f"(Live Bridge Tested: {data.get('live_bridge_tested')})\n"
                f"[bold cyan]Compositions:[/bold cyan] {meta.get('total_compositions')} "
                f"(Precomps: {meta.get('total_precompositions')})\n"
                f"[bold cyan]Plugins Used:[/bold cyan] {len(data.get('plugin_inventory', []))}\n"
                f"[bold cyan]Expressions:[/bold cyan] {len(data.get('expressions_inventory', []))}",
                title=f"Inspecting Project Analysis: {data.get('analysis_id')}",
            )
        )
        plug_table = Table(title="Plugin Inventory", show_header=True)
        plug_table.add_column("Match Name", style="cyan")
        plug_table.add_column("Display Name")
        plug_table.add_column("Package / Vendor", style="magenta")
        plug_table.add_column("3rd Party", justify="center")
        plug_table.add_column("Count", justify="right", style="green")
        for p in data.get("plugin_inventory", []):
            plug_table.add_row(
                str(p.get("match_name")),
                str(p.get("display_name")),
                f"{p.get('plugin_package')} ({p.get('plugin_vendor')})",
                "YES" if p.get("is_third_party") else "No",
                str(p.get("occurrences_count")),
            )
        console.print(plug_table)

    elif "effect_events" in data and "sampling" in data:
        meta = data.get("metadata", {})
        samp = data.get("sampling", {})
        console.print(
            Panel(
                f"[bold cyan]Video:[/bold cyan] {meta.get('file_name')} ({meta.get('width')}x{meta.get('height')})\n"
                f"[bold cyan]Duration / Frames:[/bold cyan] {meta.get('duration_seconds')}s / {meta.get('frame_count')} frames @ {meta.get('nominal_fps')} fps (VFR={meta.get('is_vfr')})\n"
                f"[bold cyan]Sampling:[/bold cyan] {samp.get('strategy')} (Coverage: {samp.get('coverage_ratio', 0) * 100:.1f}%)\n"
                f"[bold cyan]Scenes:[/bold cyan] {len(data.get('scenes', []))} | "
                f"[bold cyan]VFX Events:[/bold cyan] {len(data.get('effect_events', []))}",
                title=f"Inspecting Video Analysis: {data.get('analysis_id')}",
            )
        )
        ev_table = Table(title="Detected VFX Events", show_header=True)
        ev_table.add_column("ID", style="cyan")
        ev_table.add_column("Effect Type", style="yellow")
        ev_table.add_column("Time Range (s)")
        ev_table.add_column("Frames")
        ev_table.add_column("Confidence", justify="right", style="green")
        ev_table.add_column("Suspected Plugins (Candidates)")
        for ev in data.get("effect_events", []):
            ev_table.add_row(
                str(ev.get("event_id")),
                str(ev.get("effect_type")),
                f"{ev.get('start_time'):.3f}s - {ev.get('end_time'):.3f}s",
                f"{ev.get('start_frame')}..{ev.get('end_frame')}",
                f"{ev.get('confidence'):.2f}",
                ", ".join(ev.get("possible_plugins", [])[:2]) or "-",
            )
        console.print(ev_table)
    else:
        console.print_json(data=data)


@app.command("doctor")
def cmd_doctor(
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output environment diagnostics as raw JSON."),
    ] = False,
) -> None:
    """Check Python, FFmpeg/FFprobe, OpenCV, PySceneDetect, GPU/CUDA, After Effects, and Vision configuration."""
    report = run_environment_doctor()
    if as_json:
        console.print_json(data=report)
        return

    table = Table(title="VFX Learning Engine — Environment Doctor", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    py = report["python"]
    table.add_row("Python Runtime", "OK", f"{py['version']} ({py['platform']})")

    ff = report["ffmpeg"]
    table.add_row("FFmpeg", "OK" if ff["available"] else "MISSING", ff["version"] or ff["binary"])

    fp = report["ffprobe"]
    table.add_row("FFprobe", "OK" if fp["available"] else "MISSING", fp["version"] or fp["binary"])

    gpu = report["gpu"]
    table.add_row("GPU / NVIDIA", "OK" if gpu["available"] else "CPU FALLBACK", str(gpu["details"]))

    for pkg_name, pkg_ver in report["packages"].items():
        table.add_row(f"Package: {pkg_name}", "OK" if pkg_ver != "MISSING" else "MISSING", pkg_ver)

    ae = report["after_effects"]
    installs = ae["installed_versions"]
    ae_desc = ", ".join(i["name"] for i in installs) if installs else "Not installed (Offline parser active)"
    table.add_row("After Effects Install", "FOUND" if installs else "OFFLINE ONLY", ae_desc)

    bridges = ae["live_bridges"]
    bridge_online = bridges.get("any_live_bridge_online", False)
    jd_state = "Online" if bridges.get("junkdoge_ae_mcp", {}).get("reachable") else "Offline"
    sol_state = "Online" if bridges.get("solomon_ae_bridge", {}).get("reachable") else "Offline"
    table.add_row(
        "Live AE MCP Bridge",
        "ONLINE" if bridge_online else "OFFLINE (Read-only offline parser active)",
        f"JUNKDOGE(:11488)={jd_state}, Solomon(:7788)={sol_state}",
    )

    vis = report["vision"]
    table.add_row("AI Vision Adapter", "CONFIGURED" if vis["configured"] else "LOCAL CV ONLY", vis["note"])

    console.print(table)


if __name__ == "__main__":
    app()
