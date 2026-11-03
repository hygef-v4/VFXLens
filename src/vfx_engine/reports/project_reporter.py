"""Report writers for After Effects Project Analyzer (`project-analysis.json` and `project-report.md`)."""

from __future__ import annotations

import json
from pathlib import Path

from ..schemas.project_schema import ProjectAnalysisResult


def write_project_reports(
    result: ProjectAnalysisResult,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """Write `project-analysis.json` and `project-report.md` into `output_dir`."""
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "project-analysis.json"
    md_path = out / "project-report.md"

    json_path.write_text(
        json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md_content = render_project_markdown(result)
    md_path.write_text(md_content, encoding="utf-8")
    return json_path, md_path


def render_project_markdown(result: ProjectAnalysisResult) -> str:
    """Render a comprehensive Markdown report from a `ProjectAnalysisResult`."""
    m = result.metadata
    lines: list[str] = [
        f"# After Effects Project Analysis Report: `{m.file_name}`",
        "",
        "## 1. Executive Summary & Provenance",
        f"- **Analysis ID**: `{result.analysis_id}`",
        f"- **Analyzed At**: `{result.analyzed_at}`",
        f"- **Extraction Method**: `{result.extraction_method}`",
        f"- **Live AE Bridge Tested**: `{result.live_bridge_tested}` ({result.live_bridge_status_note})",
        f"- **Re-run Command**: `{result.rerun_command}`",
        "",
        "## 2. Project Metadata",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **File Path** | `{m.file_path}` |",
        f"| **Format** | `{m.file_format.upper()}` ({m.file_size_bytes:,} bytes) |",
        f"| **SHA-256** | `{m.sha256}` |",
        f"| **AE Version** | `{m.ae_version or 'unknown'}` |",
        f"| **Color Depth (bpc)** | `{m.bits_per_channel or 'unknown'}` |",
        f"| **Working Space** | `{m.working_space or 'None'}` |",
        f"| **Expression Engine** | `{m.expression_engine or 'unknown'}` |",
        f"| **Compositions (Main / Precomp)** | `{m.total_compositions}` total (`{m.total_precompositions}` precomps) |",
        f"| **Footage / Solid Items** | `{m.total_footage_items}` |",
        f"| **Folders** | `{m.total_folders}` |",
        "",
    ]

    # Plugin Inventory
    lines.append("## 3. Plugin & Effect Inventory")
    if not result.plugin_inventory:
        lines.append("_No effects or plugins detected in this project._\n")
    else:
        third_party = [p for p in result.plugin_inventory if p.is_third_party]
        builtin = [p for p in result.plugin_inventory if not p.is_third_party]
        lines.append(
            f"- **Third-Party Plugins Used**: `{len(third_party)}` distinct effect types\n"
            f"- **Built-in AE Effects Used**: `{len(builtin)}` distinct effect types\n"
        )
        lines.extend(
            [
                "| Match Name | Display Name | Vendor / Package | Category | 3rd Party | Count | Compositions |",
                "| :--- | :--- | :--- | :--- | :---: | :---: | :--- |",
            ]
        )
        for p in result.plugin_inventory:
            tp_badge = "YES" if p.is_third_party else "No"
            comps_str = ", ".join(p.used_in_compositions[:4])
            if len(p.used_in_compositions) > 4:
                comps_str += f" (+{len(p.used_in_compositions) - 4})"
            lines.append(
                f"| `{p.match_name}` | {p.display_name} | {p.plugin_vendor} ({p.plugin_package}) | "
                f"{p.category} | **{tp_badge}** | {p.occurrences_count} | {comps_str} |"
            )
        lines.append("")

    # Composition Hierarchy
    lines.append("## 4. Composition & Precomposition Hierarchy")
    if result.composition_hierarchy:
        lines.append("| Parent Composition | Referenced Precomp | Via Layer |")
        lines.append("| :--- | :--- | :--- |")
        for edge in result.composition_hierarchy:
            lines.append(
                f"| `{edge.parent_comp}` | `{edge.child_comp}` | `#{edge.layer_index} {edge.layer_name}` |"
            )
        lines.append("")
    else:
        lines.append("_No nested precomposition dependencies found._\n")

    # Detailed Composition & Layer Breakdown
    lines.append("## 5. Detailed Composition & Layer Effect Stacks")
    for comp in result.compositions:
        role = "Precomposition" if comp.is_precomp else "Root / Main Composition"
        res_str = (
            f"{comp.width}x{comp.height}"
            if (comp.width is not None and comp.height is not None)
            else "unavailable"
        )
        fps_str = f"{comp.frame_rate:.3f}" if comp.frame_rate is not None else "unavailable"
        dur_str = f"{comp.duration:.3f}s" if comp.duration is not None else "unavailable"
        lines.extend(
            [
                f"### Composition: `{comp.name}` ({role})",
                f"- **Resolution**: `{res_str}` (PAR `{comp.pixel_aspect}`) @ `{fps_str}` fps",
                f"- **Duration**: `{dur_str}` | **Motion Blur**: `{comp.motion_blur}` (Shutter `{comp.shutter_angle}` deg, Phase `{comp.shutter_phase}`)",
                f"- **Layers Count**: `{comp.layers_count}`",
                "",
            ]
        )

        if not comp.layers:
            lines.append("_Empty composition (0 layers)._\n")
            continue

        lines.extend(
            [
                "| # | Layer Name | Type | Blend / Matte | Parent | Flags | Effects Count |",
                "| :---: | :--- | :--- | :--- | :--- | :--- | :---: |",
            ]
        )
        for lyr in comp.layers:
            flags: list[str] = []
            if lyr.is_adjustment_layer:
                flags.append("ADJ")
            if lyr.is_three_d:
                flags.append("3D")
            if lyr.motion_blur:
                flags.append("MBlur")
            if lyr.time_remapping_enabled:
                flags.append("TimeRemap")
            if lyr.collapse_transformation:
                flags.append("Collapse")
            if lyr.expressions_summary:
                flags.append(f"Expr({len(lyr.expressions_summary)})")
            if lyr.masks:
                flags.append(f"Masks({len(lyr.masks)})")

            blend_str = lyr.blending_mode or "NORMAL"
            if lyr.has_track_matte and lyr.track_matte_type:
                blend_str += f" + Matte({lyr.track_matte_type})"
            parent_str = f"#{lyr.parent_index} {lyr.parent_name}" if lyr.parent_index else "-"
            lines.append(
                f"| {lyr.index} | `{lyr.name}` | `{lyr.layer_type}` | `{blend_str}` | "
                f"`{parent_str}` | {', '.join(flags) or '-'} | {len(lyr.effects)} |"
            )
        lines.append("")

        # Layer details for layers with effects, expressions, masks, or animated transforms
        for lyr in comp.layers:
            if not (
                lyr.effects
                or lyr.expressions_summary
                or lyr.masks
                or lyr.animated_properties_summary
                or lyr.text_detail
            ):
                continue

            lines.append(f"#### Layer #{lyr.index}: `{lyr.name}` (`{lyr.layer_type}`)")
            lines.append(
                f"- **Timing**: in=`{lyr.in_point:.3f}s`, out=`{lyr.out_point:.3f}s`, start=`{lyr.start_time:.3f}s`, stretch=`{lyr.stretch}%`"
            )
            if lyr.animated_properties_summary:
                lines.append(
                    f"- **Animated Properties ({len(lyr.animated_properties_summary)})**: "
                    + ", ".join(f"`{p}`" for p in lyr.animated_properties_summary[:10])
                )
            if lyr.masks:
                mask_desc = ", ".join(
                    f"`{mk.name}` (mode={mk.mask_mode}, animated={mk.is_path_animated})"
                    for mk in lyr.masks
                )
                lines.append(f"- **Masks ({len(lyr.masks)})**: {mask_desc}")
            if lyr.text_detail and lyr.text_detail.source_text is not None:
                lines.append(
                    f"- **Text**: `{lyr.text_detail.source_text}` (Font: `{lyr.text_detail.font}`, Size: `{lyr.text_detail.font_size}`, Animators: `{len(lyr.text_detail.animators)}`)"
                )

            if lyr.effects:
                lines.append("- **Effect Stack (Ordered)**:")
                for eff in lyr.effects:
                    vendor_tag = f"[{eff.plugin_package}]" if eff.plugin_package else ""
                    lines.append(
                        f"  {eff.index}. **`{eff.name}`** (`matchName: {eff.match_name}`) {vendor_tag} — "
                        f"Enabled: `{eff.enabled}`, Params: `{eff.parameters_count}` "
                        f"(`{eff.modified_parameters_count}` modified, `{eff.animated_parameters_count}` animated)"
                    )
                    for param in eff.parameters:
                        if param.is_modified or param.is_time_varying or param.expression_enabled:
                            kf_info = f", {param.keyframes_count} keyframes" if param.keyframes_count else ""
                            expr_info = f", expr=`{param.expression}`" if param.expression_enabled else ""
                            lines.append(
                                f"     - `{param.name}` (`{param.match_name}`): value=`{param.value}`{kf_info}{expr_info}"
                            )
            lines.append("")

    # Expressions Inventory
    lines.append("## 6. Expressions Inventory")
    if not result.expressions_inventory:
        lines.append("_No active expressions found in this project._\n")
    else:
        for expr in result.expressions_inventory:
            lines.extend(
                [
                    f"- **Comp `{expr['composition']}` > Layer #{expr['layer_index']} `{expr['layer_name']}` > `{expr['property_path']}`**:",
                    "  ```javascript",
                    f"  {expr['expression']}",
                    "  ```",
                ]
            )
        lines.append("")

    # Missing Assets & Warnings
    lines.append("## 7. Dependencies, Missing Assets & Limitations")
    lines.append(f"- **Total Footage/Solid Dependencies**: `{len(result.dependencies)}`")
    lines.append(f"- **Missing Footage Files on Local Disk**: `{len(result.missing_assets)}`")
    for ma in result.missing_assets[:15]:
        lines.append(f"  - `{ma.name}` -> `{ma.missing_footage_path}`")
    if result.unsupported_fields:
        lines.append("\n### Unavailable / Unsupported Fields")
        for uf in result.unsupported_fields:
            lines.append(f"- `{uf.field_path}` (`{uf.status.value}` via `{uf.source_method}`): {uf.reason}")
    if result.warnings:
        lines.append("\n### Warnings")
        for w in result.warnings:
            loc_str = f" ({w.location})" if w.location else ""
            lines.append(f"- **[{w.status.value.upper()}] `{w.code}`**{loc_str}: {w.message}")
    lines.append("")
    return "\n".join(lines)
