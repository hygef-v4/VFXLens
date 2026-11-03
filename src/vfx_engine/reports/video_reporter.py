"""Report writers for Video VFX Analyzer (`video-analysis.json`, `timeline.json`, `video-report.md`)."""

from __future__ import annotations

import json
from pathlib import Path

from ..schemas.video_schema import VideoAnalysisResult, VideoTimelineSchema


def write_video_reports(
    result: VideoAnalysisResult,
    timeline: VideoTimelineSchema,
    output_dir: str | Path,
) -> tuple[Path, Path, Path]:
    """Write `video-analysis.json`, `timeline.json`, and `video-report.md` into `output_dir`."""
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    analysis_json_path = out / "video-analysis.json"
    timeline_json_path = out / "timeline.json"
    report_md_path = out / "video-report.md"

    analysis_json_path.write_text(
        json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    timeline_json_path.write_text(
        json.dumps(timeline.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    report_md_path.write_text(render_video_markdown(result), encoding="utf-8")
    return analysis_json_path, timeline_json_path, report_md_path


def render_video_markdown(result: VideoAnalysisResult) -> str:
    """Render a comprehensive Markdown report from a `VideoAnalysisResult`."""
    m = result.metadata
    s = result.sampling
    lines: list[str] = [
        f"# Video VFX Analysis Report: `{m.file_name}`",
        "",
        "## 1. Executive Summary & Provenance",
        f"- **Analysis ID**: `{result.analysis_id}`",
        f"- **Analyzed At**: `{result.analyzed_at}`",
        (
            f"- **Sampling Strategy**: `{s.strategy}` "
            f"(`{s.analyzed_frames_count}` dense-analyzed / `{s.decoded_frames_count}` decoded / "
            f"`{s.total_video_frames}` total source frames, coverage `{s.coverage_ratio * 100:.1f}%`, "
            f"partial=`{s.is_partial}`"
            + (f", max_frames_cap=`{s.max_frames_cap}`)" if s.max_frames_cap is not None else ")")
        ),
        f"- **Contact Sheet**: `{s.contact_sheet_path}`",
        f"- **Evidence Frames Directory**: `{s.evidence_frames_dir}/` (`{len(s.evidence_frame_files)}` frames exported)",
        f"- **Re-run Command**: `{result.rerun_command}`",
        "",
    ]

    if result.warnings:
        lines.append("### Analysis Warnings")
        for w in result.warnings:
            lines.append(f"- ⚠️ **`[{w.code}]`**: {w.message}")
        lines.append("")

    lines.extend(
        [
            "## 2. Stream & Timing Metadata",
            "| Property | Value |",
            "| :--- | :--- |",
            f"| **File Path** | `{m.file_path}` |",
            f"| **Container / Codec** | `{m.container_format}` / `{m.video_codec}` (`{m.pixel_format or 'unknown'}`) |",
            f"| **Resolution** | `{m.width}x{m.height}` |",
            f"| **Duration** | `{m.duration_seconds:.3f}s` (`{m.frame_count}` source frames, `{s.decoded_frames_count}` decoded) |",
            f"| **Frame Rate** | Nominal `{m.nominal_fps:.3f}` fps / Average `{m.average_fps:.3f}` fps |",
            f"| **Variable Frame Rate (VFR)** | `{m.is_vfr}` (PTS jitter std = `{m.vfr_jitter_ms:.3f} ms`) |",
            f"| **Audio Track** | `{m.has_audio}` ({m.audio_codec or 'none'}, {m.audio_sample_rate or 0} Hz) |",
            "",
            "## 3. Scene Segmentation",
            "| Scene # | Start Time | End Time | Duration | Frames | Transition Type | Cut Score |",
            "| :---: | :---: | :---: | :---: | :---: | :--- | :---: |",
        ]
    )

    for sc in result.scenes:
        lines.append(
            f"| {sc.scene_index} | `{sc.start_time:.3f}s` | `{sc.end_time:.3f}s` | "
            f"`{sc.duration:.3f}s` | `{sc.start_frame}..{sc.end_frame}` | `{sc.transition_type}` | `{sc.cut_score:.1f}` |"
        )
    lines.append("")

    # High-activity windows
    lines.append("## 4. High-Activity Visual/Motion Windows")
    if not s.high_activity_windows:
        lines.append("_Uniform visual activity across timeline._\n")
    else:
        for idx, win in enumerate(s.high_activity_windows, start=1):
            lines.append(
                f"- **Window #{idx}**: `{win['start_time']:.3f}s - {win['end_time']:.3f}s` "
                f"(frames `{win['start_frame']}..{win['end_frame']}`, peak frame `#{win['peak_frame']}`, "
                f"peak activity `{win['peak_activity_score']}`)"
            )
        lines.append("")

    # Detected VFX Events
    lines.append("## 5. Detected VFX & Motion Events")
    lines.append(
        "> **Important Epistemic Note**: Direct pixel/motion measurements (`observations`) are separated from "
        "plausible After Effects recreation workflows (`possible_ae_techniques`) and candidate plugins (`possible_plugins`). "
        "Plugin names are **never claimed with certainty** from rendered video pixels alone.\n"
    )

    if not result.effect_events:
        lines.append("_No distinct VFX candidate events exceeded signal thresholds._\n")
    else:
        for ev in result.effect_events:
            lines.extend(
                [
                    f"### `{ev.event_id}` — `{ev.effect_type}` (`{ev.start_time:.3f}s` -> `{ev.end_time:.3f}s`, frames `{ev.start_frame}..{ev.end_frame}`)",
                    f"- **Peak Frame**: `#{ev.peak_frame}` (`{ev.peak_time:.3f}s`)",
                    f"- **Confidence**: `{ev.confidence:.2f}` ({ev.confidence_explanation})",
                    f"- **Extraction Method**: `{ev.extraction_method}` | **Source**: `{ev.source.value}` | **Verified vs .aep**: `{ev.verified}`",
                    "- **Direct Visual Observations (Measured)**:",
                ]
            )
            for obs in ev.observations:
                lines.append(f"  - {obs}")
            lines.append(f"- **Measured Signals**: `{json.dumps(ev.measured_signals, ensure_ascii=False)}`")
            if ev.possible_ae_techniques:
                lines.append("- **Possible After Effects Techniques**:")
                for tech in ev.possible_ae_techniques:
                    lines.append(f"  - {tech}")
            if ev.possible_plugins:
                lines.append("- **Suspected AE Plugins (Candidates Only, Unverified)**:")
                for plug in ev.possible_plugins:
                    lines.append(f"  - `{plug}`")
            if ev.undetermined_parameters:
                lines.append("- **Parameters Undetermined from Video Alone**:")
                for up in ev.undetermined_parameters:
                    lines.append(f"  - {up}")
            if ev.evidence_frames:
                lines.append("- **Evidence Frames**: " + ", ".join(f"`{ef}`" for ef in ev.evidence_frames))
            lines.append("")

    # AI Vision Summary
    v = result.vision_analysis
    lines.extend(
        [
            "## 6. AI Vision Adapter Status",
            f"- **Provider**: `{v.provider}` | **Model**: `{v.model or 'none'}`",
            f"- **Status**: `{v.status.value}` | **Analyzed**: `{v.analyzed}`",
            f"- **Note**: {v.note}",
            "",
            "## 7. Global Undetermined Video Aspects",
        ]
    )
    for item in result.undetermined_video_aspects:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
