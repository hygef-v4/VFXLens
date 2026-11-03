"""Normalizer and comparator between Offline Parser output and Live AE Bridge output."""

from __future__ import annotations

from typing import Any

from ...schemas.common import DataAvailabilityStatus
from ...schemas.project_schema import ProjectAnalysisResult, ProjectComparisonDiffSchema


def compare_offline_and_live(
    offline_result: ProjectAnalysisResult,
    live_payload: dict[str, Any],
) -> list[ProjectComparisonDiffSchema]:
    """Compare normalized Offline Parser output against Live AE Bridge output.

    Distinguishes:
    - `matched`: Identical values between offline parser and live AE
    - `value_mismatch`: Divergent values for a static property
    - `expected_runtime_difference`: Differences caused by live expression evaluation or runtime state
    - `only_in_offline`: Present in offline parse but omitted in live payload
    - `only_in_live`: Present only in live AE (e.g., runtime expression errors or evaluated values)
    """
    diffs: list[ProjectComparisonDiffSchema] = []

    # 1. Compare project-level bits_per_channel
    live_bpc = live_payload.get("bits_per_channel")
    if live_bpc is not None:
        off_bpc = offline_result.metadata.bits_per_channel
        diffs.append(
            ProjectComparisonDiffSchema(
                field_path="project.bits_per_channel",
                offline_value=off_bpc,
                live_value=live_bpc,
                offline_status=DataAvailabilityStatus.OBSERVED,
                live_status=DataAvailabilityStatus.OBSERVED,
                comparison_result="matched" if off_bpc == live_bpc else "value_mismatch",
                explanation="Project color bit depth comparison.",
            )
        )

    # 2. Index compositions by name
    off_comps = {c.name: c for c in offline_result.compositions}
    live_comps = {
        str(c.get("name", "")): c
        for c in (live_payload.get("compositions") or [])
        if isinstance(c, dict) and c.get("name")
    }

    for c_name, off_comp in off_comps.items():
        if c_name not in live_comps:
            diffs.append(
                ProjectComparisonDiffSchema(
                    field_path=f"compositions[{c_name}]",
                    offline_value={"width": off_comp.width, "height": off_comp.height},
                    live_value=None,
                    offline_status=DataAvailabilityStatus.OBSERVED,
                    live_status=DataAvailabilityStatus.UNAVAILABLE,
                    comparison_result="only_in_offline",
                    explanation=f"Composition '{c_name}' parsed offline but missing from live bridge snapshot.",
                )
            )
            continue

        l_comp = live_comps[c_name]
        # Compare dimensions & FPS
        dim_match = (
            off_comp.width is not None
            and off_comp.height is not None
            and off_comp.width == l_comp.get("width")
            and off_comp.height == l_comp.get("height")
        )
        off_dim_status = (
            DataAvailabilityStatus.OBSERVED
            if (off_comp.width is not None and off_comp.height is not None)
            else DataAvailabilityStatus.UNAVAILABLE
        )
        diffs.append(
            ProjectComparisonDiffSchema(
                field_path=f"compositions[{c_name}].dimensions",
                offline_value=[off_comp.width, off_comp.height],
                live_value=[l_comp.get("width"), l_comp.get("height")],
                offline_status=off_dim_status,
                live_status=DataAvailabilityStatus.OBSERVED,
                comparison_result="matched" if dim_match else "value_mismatch",
                explanation="Composition resolution (width x height).",
            )
        )

        # Compare layer counts and effect stacks
        live_layers = l_comp.get("layers") or []
        diffs.append(
            ProjectComparisonDiffSchema(
                field_path=f"compositions[{c_name}].layers_count",
                offline_value=off_comp.layers_count,
                live_value=len(live_layers),
                offline_status=DataAvailabilityStatus.OBSERVED,
                live_status=DataAvailabilityStatus.OBSERVED,
                comparison_result="matched" if off_comp.layers_count == len(live_layers) else "value_mismatch",
                explanation="Layer count in composition.",
            )
        )

        live_layers_by_idx = {
            int(ll.get("index", idx + 1)): ll for idx, ll in enumerate(live_layers) if isinstance(ll, dict)
        }
        for off_layer in off_comp.layers:
            ll = live_layers_by_idx.get(off_layer.index)
            if not ll:
                continue
            off_eff_mns = [e.match_name for e in off_layer.effects]
            live_eff_mns = [
                str(le.get("match_name") if "match_name" in le else le.get("matchName", ""))
                for le in (ll.get("effects") or [])
                if isinstance(le, dict)
            ]
            diffs.append(
                ProjectComparisonDiffSchema(
                    field_path=f"compositions[{c_name}].layers[{off_layer.index}:{off_layer.name}].effect_stack",
                    offline_value=off_eff_mns,
                    live_value=live_eff_mns,
                    offline_status=DataAvailabilityStatus.OBSERVED,
                    live_status=DataAvailabilityStatus.OBSERVED,
                    comparison_result="matched" if off_eff_mns == live_eff_mns else "value_mismatch",
                    explanation="Effect stack order and matchNames on layer.",
                )
            )

            # Check if layer has active expressions where runtime value is expected to differ
            for expr_item in off_layer.expressions_summary:
                if expr_item.get("expression_enabled"):
                    diffs.append(
                        ProjectComparisonDiffSchema(
                            field_path=(
                                f"compositions[{c_name}].layers[{off_layer.index}:{off_layer.name}]."
                                f"{expr_item.get('property_path')}.evaluated_value"
                            ),
                            offline_value=expr_item.get("pre_expression_value"),
                            live_value="<evaluated_by_ae_expression_engine>",
                            offline_status=DataAvailabilityStatus.UNAVAILABLE,
                            live_status=DataAvailabilityStatus.OBSERVED,
                            comparison_result="expected_runtime_difference",
                            explanation=(
                                "Property has an active expression; offline parser reports pre-expression "
                                "stored value while live AE evaluates the expression at runtime."
                            ),
                        )
                    )

    for c_name in live_comps:
        if c_name not in off_comps:
            diffs.append(
                ProjectComparisonDiffSchema(
                    field_path=f"compositions[{c_name}]",
                    offline_value=None,
                    live_value=live_comps[c_name].get("name"),
                    offline_status=DataAvailabilityStatus.UNAVAILABLE,
                    live_status=DataAvailabilityStatus.OBSERVED,
                    comparison_result="only_in_live",
                    explanation=f"Composition '{c_name}' present in live AE session only.",
                )
            )

    return diffs
