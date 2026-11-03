"""Offline After Effects (.aep) parser built on `py_aep` + raw RIFX chunk auditing."""

from __future__ import annotations

import io
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import py_aep
from py_aep.binary.chunk import ListChunk, read_aep
from py_aep.models import (
    CameraLayer,
    CompItem,
    FileSource,
    FolderItem,
    FootageItem,
    Layer,
    LightLayer,
    ParametricMeshLayer,
    PlaceholderSource,
    Property,
    PropertyGroup,
    Shape,
    ShapeLayer,
    SolidSource,
    TextDocument,
    TextLayer,
    ThreeDModelLayer,
)

from ...core.logging import get_logger
from ...core.safety import readonly_file_guard, validate_project_file_safety
from ...schemas.common import AnalysisWarning, DataAvailabilityStatus, FieldProvenance
from ...schemas.project_schema import (
    CompositionGraphEdgeSchema,
    CompositionSchema,
    EffectInstanceSchema,
    EffectParameterSchema,
    FootageDependencySchema,
    KeyframeEasingSchema,
    KeyframeSchema,
    LayerRelationshipEdgeSchema,
    LayerSchema,
    MaskSchema,
    PluginInventoryItemSchema,
    ProjectAnalysisResult,
    ProjectMetadataSchema,
    PropertySchema,
    TextAnimatorSchema,
    TextLayerDetailSchema,
    TransformSchema,
)
from ..effect_extractor.plugin_registry import classify_effect

logger = get_logger("project_analyzer.py_aep_parser")


def _enum_name(val: Any) -> str | None:
    if val is None:
        return None
    if hasattr(val, "name"):
        return str(val.name)
    return str(val)


def _safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def _serialize_value(val: Any) -> Any:
    """Convert `py_aep` property/keyframe values into JSON-serializable structures."""
    if val is None or isinstance(val, (bool, int, str)):
        return val
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(val, 6)
    if isinstance(val, (list, tuple)):
        return [_serialize_value(v) for v in val]
    if isinstance(val, dict):
        return {str(k): _serialize_value(v) for k, v in val.items()}
    if isinstance(val, Shape):
        return {
            "_type": "Shape",
            "closed": _safe_getattr(val, "closed", True),
            "vertices_count": len(_safe_getattr(val, "vertices", []) or []),
            "vertices": _serialize_value(_safe_getattr(val, "vertices", [])),
            "in_tangents": _serialize_value(_safe_getattr(val, "in_tangents", [])),
            "out_tangents": _serialize_value(_safe_getattr(val, "out_tangents", [])),
            "feather_points_count": len(_safe_getattr(val, "feather_points", []) or []),
        }
    if isinstance(val, TextDocument):
        return {
            "_type": "TextDocument",
            "text": _safe_getattr(val, "text", ""),
            "font": _safe_getattr(val, "font", None),
            "font_size": _serialize_value(_safe_getattr(val, "font_size", None)),
            "fill_color": _serialize_value(_safe_getattr(val, "fill_color", None)),
            "stroke_color": _serialize_value(_safe_getattr(val, "stroke_color", None)),
            "stroke_width": _serialize_value(_safe_getattr(val, "stroke_width", None)),
            "apply_fill": _safe_getattr(val, "apply_fill", None),
            "apply_stroke": _safe_getattr(val, "apply_stroke", None),
            "justification": _enum_name(_safe_getattr(val, "justification", None)),
            "tracking": _serialize_value(_safe_getattr(val, "tracking", None)),
            "leading": _serialize_value(_safe_getattr(val, "leading", None)),
        }
    if hasattr(val, "comment") and hasattr(val, "duration"):
        # MarkerValue
        return {
            "_type": "MarkerValue",
            "comment": _safe_getattr(val, "comment", ""),
            "chapter": _safe_getattr(val, "chapter", ""),
            "url": _safe_getattr(val, "url", ""),
            "duration": _serialize_value(_safe_getattr(val, "duration", 0.0)),
            "cue_point_name": _safe_getattr(val, "cue_point_name", ""),
            "params": _serialize_value(_safe_getattr(val, "params", {})),
        }
    if hasattr(val, "color_stops") and hasattr(val, "opacity_stops"):
        # Gradient
        return {
            "_type": "Gradient",
            "color_stops": [
                {
                    "location": _serialize_value(_safe_getattr(s, "location", 0.0)),
                    "midpoint": _serialize_value(_safe_getattr(s, "midpoint", 0.5)),
                    "color": _serialize_value(_safe_getattr(s, "color", [])),
                }
                for s in (_safe_getattr(val, "color_stops", []) or [])
            ],
            "opacity_stops": [
                {
                    "location": _serialize_value(_safe_getattr(s, "location", 0.0)),
                    "midpoint": _serialize_value(_safe_getattr(s, "midpoint", 0.5)),
                    "opacity": _serialize_value(_safe_getattr(s, "opacity", 1.0)),
                }
                for s in (_safe_getattr(val, "opacity_stops", []) or [])
            ],
        }
    if hasattr(val, "name"):
        return str(val.name)
    return str(val)


def _extract_keyframes(prop: Property, comp_fps: float) -> list[KeyframeSchema]:
    """Extract all keyframes with timing, values, interpolation, and easing."""
    kfs_raw = _safe_getattr(prop, "keyframes", None)
    if not kfs_raw:
        return []
    result: list[KeyframeSchema] = []
    for idx, kf in enumerate(kfs_raw, start=1):
        t = float(_safe_getattr(kf, "time", 0.0) or 0.0)
        frame_time = _safe_getattr(kf, "frame_time", None)
        if frame_time is None and comp_fps > 0:
            frame_time = round(t * comp_fps, 3)

        in_interp = _enum_name(_safe_getattr(kf, "in_interpolation_type", None)) or "LINEAR"
        out_interp = _enum_name(_safe_getattr(kf, "out_interpolation_type", None)) or "LINEAR"

        in_ease_raw = _safe_getattr(kf, "in_temporal_ease", None) or []
        out_ease_raw = _safe_getattr(kf, "out_temporal_ease", None) or []
        in_ease = [
            KeyframeEasingSchema(
                speed=round(float(_safe_getattr(e, "speed", 0.0) or 0.0), 6),
                influence=round(float(_safe_getattr(e, "influence", 0.0) or 0.0), 6),
            )
            for e in in_ease_raw
        ]
        out_ease = [
            KeyframeEasingSchema(
                speed=round(float(_safe_getattr(e, "speed", 0.0) or 0.0), 6),
                influence=round(float(_safe_getattr(e, "influence", 0.0) or 0.0), 6),
            )
            for e in out_ease_raw
        ]

        in_spatial = _serialize_value(_safe_getattr(kf, "in_spatial_tangent", None))
        out_spatial = _serialize_value(_safe_getattr(kf, "out_spatial_tangent", None))

        result.append(
            KeyframeSchema(
                index=idx,
                time=round(t, 6),
                frame=round(float(frame_time), 3) if frame_time is not None else None,
                value=_serialize_value(_safe_getattr(kf, "value", None)),
                in_interpolation=in_interp,
                out_interpolation=out_interp,
                in_temporal_ease=in_ease,
                out_temporal_ease=out_ease,
                in_spatial_tangent=in_spatial if isinstance(in_spatial, list) else None,
                out_spatial_tangent=out_spatial if isinstance(out_spatial, list) else None,
                temporal_continuous=_safe_getattr(kf, "temporal_continuous", None),
                temporal_auto_bezier=_safe_getattr(kf, "temporal_auto_bezier", None),
                spatial_continuous=_safe_getattr(kf, "spatial_continuous", None),
                spatial_auto_bezier=_safe_getattr(kf, "spatial_auto_bezier", None),
                roving=_safe_getattr(kf, "roving", None),
                label=_enum_name(_safe_getattr(kf, "label", None)),
            )
        )
    return result


def _extract_property_tree(
    prop_or_group: Property | PropertyGroup,
    parent_path: str,
    comp_fps: float,
    expressions_acc: list[dict[str, Any]],
    animated_acc: list[str],
    comp_name: str,
    layer_name: str,
    layer_index: int,
    max_depth: int = 8,
    current_depth: int = 0,
) -> PropertySchema:
    """Recursively extract a Property or PropertyGroup into `PropertySchema`."""
    name = str(_safe_getattr(prop_or_group, "name", "") or "")
    match_name = str(_safe_getattr(prop_or_group, "match_name", "") or name)
    prop_path = f"{parent_path}/{name or match_name}"
    prop_type = _enum_name(_safe_getattr(prop_or_group, "property_type", None)) or "PROPERTY"
    enabled = bool(_safe_getattr(prop_or_group, "enabled", True))
    is_modified = bool(_safe_getattr(prop_or_group, "is_modified", False))

    if isinstance(prop_or_group, Property):
        pvt = _enum_name(_safe_getattr(prop_or_group, "property_value_type", None))
        ctrl_type = _enum_name(_safe_getattr(prop_or_group, "property_control_type", None))
        is_time_varying = bool(_safe_getattr(prop_or_group, "is_time_varying", False))
        val = _serialize_value(_safe_getattr(prop_or_group, "value", None))
        default_val = _serialize_value(_safe_getattr(prop_or_group, "default_value", None))
        min_val = _serialize_value(_safe_getattr(prop_or_group, "min_value", None))
        max_val = _serialize_value(_safe_getattr(prop_or_group, "max_value", None))
        units = _safe_getattr(prop_or_group, "units_text", None)
        prop_params = _safe_getattr(prop_or_group, "property_parameters", None)
        expr_enabled = bool(_safe_getattr(prop_or_group, "expression_enabled", False))
        expr_str = _safe_getattr(prop_or_group, "expression", "") or None
        dims_sep = bool(_safe_getattr(prop_or_group, "dimensions_separated", False))
        is_spatial = bool(_safe_getattr(prop_or_group, "is_spatial", False))

        keyframes = _extract_keyframes(prop_or_group, comp_fps) if is_time_varying else []
        if is_time_varying or keyframes:
            animated_acc.append(f"{prop_path} ({len(keyframes)} keyframes)")

        if expr_str:
            expressions_acc.append(
                {
                    "composition": comp_name,
                    "layer_index": layer_index,
                    "layer_name": layer_name,
                    "property_path": prop_path,
                    "match_name": match_name,
                    "expression_enabled": expr_enabled,
                    "expression": expr_str,
                    "pre_expression_value": val,
                    "evaluated_value_status": DataAvailabilityStatus.UNAVAILABLE.value,
                }
            )

        return PropertySchema(
            name=name,
            match_name=match_name,
            property_path=prop_path,
            property_type=prop_type,
            property_value_type=pvt,
            control_type=ctrl_type,
            enabled=enabled,
            is_modified=is_modified,
            is_time_varying=is_time_varying,
            value=val,
            default_value=default_val,
            min_value=min_val,
            max_value=max_val,
            units_text=str(units) if units else None,
            property_parameters=[str(x) for x in prop_params] if prop_params else None,
            keyframes_count=len(keyframes),
            keyframes=keyframes,
            expression_enabled=expr_enabled,
            expression=expr_str,
            expression_error=None,
            expression_evaluated_value_status=(
                DataAvailabilityStatus.UNAVAILABLE
                if expr_enabled
                else DataAvailabilityStatus.OBSERVED
            ),
            dimensions_separated=dims_sep,
            is_spatial=is_spatial,
            status=DataAvailabilityStatus.OBSERVED,
            children=[],
        )

    # PropertyGroup
    children: list[PropertySchema] = []
    if current_depth < max_depth:
        raw_children = _safe_getattr(prop_or_group, "properties", None)
        if raw_children is None:
            try:
                raw_children = list(prop_or_group)
            except Exception:
                raw_children = []
        for child in raw_children or []:
            children.append(
                _extract_property_tree(
                    child,
                    prop_path,
                    comp_fps,
                    expressions_acc,
                    animated_acc,
                    comp_name,
                    layer_name,
                    layer_index,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                )
            )

    return PropertySchema(
        name=name,
        match_name=match_name,
        property_path=prop_path,
        property_type=prop_type,
        enabled=enabled,
        is_modified=is_modified,
        status=DataAvailabilityStatus.OBSERVED,
        children=children,
    )


def _extract_layer_effects(
    layer: Layer,
    comp_name: str,
    comp_fps: float,
    layer_index: int,
    expressions_acc: list[dict[str, Any]],
    animated_acc: list[str],
    layer_relationships_acc: list[LayerRelationshipEdgeSchema],
    comp_layers_by_index: dict[int, str],
) -> list[EffectInstanceSchema]:
    """Extract the full Effect Stack (`ADBE Effect Parade`) on a layer."""
    effects_group = _safe_getattr(layer, "effects", None)
    if effects_group is None:
        return []

    try:
        effect_groups = list(effects_group)
    except Exception:
        effect_groups = _safe_getattr(effects_group, "properties", []) or []

    extracted_effects: list[EffectInstanceSchema] = []
    for eff_idx, eff_group in enumerate(effect_groups, start=1):
        eff_name = str(_safe_getattr(eff_group, "name", "") or f"Effect {eff_idx}")
        eff_match_name = str(_safe_getattr(eff_group, "match_name", "") or eff_name)
        eff_auto_name = str(_safe_getattr(eff_group, "_auto_name", "") or eff_name)
        eff_enabled = bool(_safe_getattr(eff_group, "enabled", True))

        classification = classify_effect(eff_match_name, eff_auto_name)

        params_list: list[EffectParameterSchema] = []
        modified_count = 0
        animated_count = 0

        try:
            raw_params = list(eff_group)
        except Exception:
            raw_params = _safe_getattr(eff_group, "properties", []) or []

        for p_idx, param in enumerate(raw_params, start=1):
            p_name = str(_safe_getattr(param, "name", "") or f"Param {p_idx}")
            p_match_name = str(_safe_getattr(param, "match_name", "") or p_name)
            p_path = f"Effects/{eff_name}/{p_name}"

            if isinstance(param, Property):
                ctrl_type = _enum_name(_safe_getattr(param, "property_control_type", None))
                pvt = _enum_name(_safe_getattr(param, "property_value_type", None))
                val = _serialize_value(_safe_getattr(param, "value", None))
                def_val = _serialize_value(_safe_getattr(param, "default_value", None))
                min_val = _serialize_value(_safe_getattr(param, "min_value", None))
                max_val = _serialize_value(_safe_getattr(param, "max_value", None))
                units = _safe_getattr(param, "units_text", None)
                dropdown_opts = _safe_getattr(param, "property_parameters", None)
                is_mod = bool(_safe_getattr(param, "is_modified", False))
                is_tv = bool(_safe_getattr(param, "is_time_varying", False))
                expr_en = bool(_safe_getattr(param, "expression_enabled", False))
                expr_str = _safe_getattr(param, "expression", "") or None

                kfs = _extract_keyframes(param, comp_fps) if is_tv else []
                if is_mod:
                    modified_count += 1
                if is_tv or kfs:
                    animated_count += 1
                    animated_acc.append(f"{p_path} ({len(kfs)} keyframes)")

                if expr_str:
                    expressions_acc.append(
                        {
                            "composition": comp_name,
                            "layer_index": layer_index,
                            "layer_name": layer.name,
                            "property_path": p_path,
                            "match_name": p_match_name,
                            "expression_enabled": expr_en,
                            "expression": expr_str,
                            "pre_expression_value": val,
                            "evaluated_value_status": DataAvailabilityStatus.UNAVAILABLE.value,
                        }
                    )

                # Detect layer-reference effect parameters (e.g. Set Matte, Displacement Map)
                if ctrl_type == "LAYER" and isinstance(val, int) and val > 0:
                    target_name = comp_layers_by_index.get(val, f"Layer #{val}")
                    layer_relationships_acc.append(
                        LayerRelationshipEdgeSchema(
                            composition_name=comp_name,
                            source_layer_index=layer_index,
                            source_layer_name=layer.name,
                            target_layer_index=val,
                            target_layer_name=target_name,
                            relationship_type="effect_layer_param",
                            detail=f"{eff_name} ({eff_match_name}) -> {p_name}",
                        )
                    )

                params_list.append(
                    EffectParameterSchema(
                        index=p_idx,
                        name=p_name,
                        match_name=p_match_name,
                        property_path=p_path,
                        control_type=ctrl_type,
                        property_value_type=pvt,
                        value=val,
                        default_value=def_val,
                        min_value=min_val,
                        max_value=max_val,
                        units_text=str(units) if units else None,
                        dropdown_options=[str(o) for o in dropdown_opts] if dropdown_opts else None,
                        is_modified=is_mod,
                        is_time_varying=is_tv,
                        keyframes_count=len(kfs),
                        keyframes=kfs,
                        expression_enabled=expr_en,
                        expression=expr_str,
                        status=DataAvailabilityStatus.OBSERVED,
                    )
                )
            else:
                # Sub-group inside effect (e.g. Compositing Options or Group Separator)
                params_list.append(
                    EffectParameterSchema(
                        index=p_idx,
                        name=p_name,
                        match_name=p_match_name,
                        property_path=p_path,
                        control_type="GROUP",
                        property_value_type="NO_VALUE",
                        status=DataAvailabilityStatus.OBSERVED,
                    )
                )

        extracted_effects.append(
            EffectInstanceSchema(
                index=eff_idx,
                name=eff_name,
                match_name=eff_match_name,
                display_name=classification.display_name,
                enabled=eff_enabled,
                is_third_party=classification.is_third_party,
                plugin_vendor=classification.plugin_vendor,
                plugin_package=classification.plugin_package,
                category=classification.category,
                parameters_count=len(params_list),
                modified_parameters_count=modified_count,
                animated_parameters_count=animated_count,
                parameters=params_list,
                status=DataAvailabilityStatus.OBSERVED,
            )
        )

    return extracted_effects


def _extract_layer_masks(
    layer: Layer,
    comp_name: str,
    comp_fps: float,
    layer_index: int,
    expressions_acc: list[dict[str, Any]],
    animated_acc: list[str],
) -> list[MaskSchema]:
    """Extract all Masks (`ADBE Mask Parade`) on an AVLayer."""
    masks_group = _safe_getattr(layer, "masks", None)
    if masks_group is None:
        return []
    try:
        mask_atoms = list(masks_group)
    except Exception:
        mask_atoms = _safe_getattr(masks_group, "properties", []) or []

    masks: list[MaskSchema] = []
    for m_idx, mask_atom in enumerate(mask_atoms, start=1):
        m_name = str(_safe_getattr(mask_atom, "name", "") or f"Mask {m_idx}")
        m_match_name = str(_safe_getattr(mask_atom, "match_name", "ADBE Mask Atom"))
        enabled = bool(_safe_getattr(mask_atom, "enabled", True))
        inverted = bool(_safe_getattr(mask_atom, "inverted", False))
        locked = bool(_safe_getattr(mask_atom, "locked", False))
        roto_bezier = bool(_safe_getattr(mask_atom, "roto_bezier", False))
        mask_mode = _enum_name(_safe_getattr(mask_atom, "mask_mode", None))
        mask_mb = _enum_name(_safe_getattr(mask_atom, "mask_motion_blur", None))
        color = _serialize_value(_safe_getattr(mask_atom, "color", None))

        # Extract child properties (Mask Path, Mask Feather, Mask Opacity, Mask Expansion)
        props: list[PropertySchema] = []
        is_path_anim = False
        vertices_cnt: int | None = None
        closed: bool | None = None
        feather_val: Any = None
        opacity_val: Any = None
        expansion_val: Any = None

        try:
            raw_m_props = list(mask_atom)
        except Exception:
            raw_m_props = _safe_getattr(mask_atom, "properties", []) or []

        for mp in raw_m_props:
            ps = _extract_property_tree(
                mp,
                f"Masks/{m_name}",
                comp_fps,
                expressions_acc,
                animated_acc,
                comp_name,
                layer.name,
                layer_index,
            )
            props.append(ps)
            if ps.match_name == "ADBE Mask Shape":
                is_path_anim = ps.is_time_varying
                if isinstance(ps.value, dict) and ps.value.get("_type") == "Shape":
                    vertices_cnt = ps.value.get("vertices_count")
                    closed = ps.value.get("closed")
                elif ps.keyframes and isinstance(ps.keyframes[0].value, dict):
                    vertices_cnt = ps.keyframes[0].value.get("vertices_count")
                    closed = ps.keyframes[0].value.get("closed")
            elif ps.match_name == "ADBE Mask Feather":
                feather_val = ps.value
            elif ps.match_name == "ADBE Mask Opacity":
                opacity_val = ps.value
            elif ps.match_name == "ADBE Mask Offset":
                expansion_val = ps.value

        masks.append(
            MaskSchema(
                index=m_idx,
                name=m_name,
                match_name=m_match_name,
                enabled=enabled,
                inverted=inverted,
                locked=locked,
                roto_bezier=roto_bezier,
                mask_mode=mask_mode,
                mask_motion_blur=mask_mb,
                color=color if isinstance(color, list) else None,
                is_path_animated=is_path_anim,
                vertices_count=vertices_cnt,
                closed=closed,
                feather=feather_val,
                opacity=opacity_val,
                expansion=expansion_val,
                properties=props,
            )
        )

    return masks


def _extract_transform(
    layer: Layer,
    comp_name: str,
    comp_fps: float,
    layer_index: int,
    expressions_acc: list[dict[str, Any]],
    animated_acc: list[str],
) -> TransformSchema | None:
    transform_group = _safe_getattr(layer, "transform", None)
    if transform_group is None:
        return None

    props_map: dict[str, PropertySchema] = {}
    try:
        children = list(transform_group)
    except Exception:
        children = _safe_getattr(transform_group, "properties", []) or []

    for child in children:
        ps = _extract_property_tree(
            child,
            "Transform",
            comp_fps,
            expressions_acc,
            animated_acc,
            comp_name,
            layer.name,
            layer_index,
        )
        props_map[ps.match_name] = ps

    pos_prop = props_map.get("ADBE Position")
    dims_sep = pos_prop.dimensions_separated if pos_prop else False

    return TransformSchema(
        anchor_point=props_map.get("ADBE Anchor Point").value if "ADBE Anchor Point" in props_map else None,
        position=pos_prop.value if pos_prop else None,
        x_position=props_map.get("ADBE Position_0").value if "ADBE Position_0" in props_map else None,
        y_position=props_map.get("ADBE Position_1").value if "ADBE Position_1" in props_map else None,
        z_position=props_map.get("ADBE Position_2").value if "ADBE Position_2" in props_map else None,
        dimensions_separated=dims_sep,
        scale=props_map.get("ADBE Scale").value if "ADBE Scale" in props_map else None,
        orientation=props_map.get("ADBE Orientation").value if "ADBE Orientation" in props_map else None,
        rotation=props_map.get("ADBE Rotate Z").value if "ADBE Rotate Z" in props_map else None,
        x_rotation=props_map.get("ADBE Rotate X").value if "ADBE Rotate X" in props_map else None,
        y_rotation=props_map.get("ADBE Rotate Y").value if "ADBE Rotate Y" in props_map else None,
        z_rotation=props_map.get("ADBE Rotate Z").value if "ADBE Rotate Z" in props_map else None,
        opacity=props_map.get("ADBE Opacity").value if "ADBE Opacity" in props_map else None,
        properties=props_map,
    )


def _extract_text_layer_detail(
    layer: TextLayer,
    comp_name: str,
    comp_fps: float,
    layer_index: int,
    expressions_acc: list[dict[str, Any]],
    animated_acc: list[str],
) -> TextLayerDetailSchema | None:
    text_group = _safe_getattr(layer, "text", None)
    if text_group is None:
        return None

    source_text_prop = _safe_getattr(text_group, "source_text", None)
    doc = _safe_getattr(source_text_prop, "value", None) if source_text_prop else None

    src_kfs: list[KeyframeSchema] = []
    is_src_anim = False
    if isinstance(source_text_prop, Property):
        is_src_anim = bool(_safe_getattr(source_text_prop, "is_time_varying", False))
        if is_src_anim:
            src_kfs = _extract_keyframes(source_text_prop, comp_fps)
            animated_acc.append(f"Text/Source Text ({len(src_kfs)} keyframes)")
        expr_str = _safe_getattr(source_text_prop, "expression", "") or None
        if expr_str:
            expressions_acc.append(
                {
                    "composition": comp_name,
                    "layer_index": layer_index,
                    "layer_name": layer.name,
                    "property_path": "Text/Source Text",
                    "match_name": "ADBE Text Document",
                    "expression_enabled": bool(_safe_getattr(source_text_prop, "expression_enabled", False)),
                    "expression": expr_str,
                    "pre_expression_value": _serialize_value(doc),
                    "evaluated_value_status": DataAvailabilityStatus.UNAVAILABLE.value,
                }
            )

    animators_list: list[TextAnimatorSchema] = []
    animators_group = None
    try:
        animators_group = text_group["ADBE Text Animators"]
    except Exception:
        pass

    if animators_group is not None:
        try:
            raw_animators = list(animators_group)
        except Exception:
            raw_animators = _safe_getattr(animators_group, "properties", []) or []
        for anim in raw_animators:
            a_name = str(_safe_getattr(anim, "name", "Animator"))
            a_mn = str(_safe_getattr(anim, "match_name", "ADBE Text Animator"))
            selectors_out: list[PropertySchema] = []
            props_out: list[PropertySchema] = []
            try:
                sel_group = anim["ADBE Text Selectors"]
                for s in list(sel_group):
                    selectors_out.append(
                        _extract_property_tree(
                            s,
                            f"Text/Animators/{a_name}/Selectors",
                            comp_fps,
                            expressions_acc,
                            animated_acc,
                            comp_name,
                            layer.name,
                            layer_index,
                        )
                    )
            except Exception:
                pass
            try:
                ap_group = anim["ADBE Text Animator Properties"]
                for ap in list(ap_group):
                    ps = _extract_property_tree(
                        ap,
                        f"Text/Animators/{a_name}/Properties",
                        comp_fps,
                        expressions_acc,
                        animated_acc,
                        comp_name,
                        layer.name,
                        layer_index,
                    )
                    if ps.is_modified or ps.is_time_varying or ps.expression:
                        props_out.append(ps)
            except Exception:
                pass
            animators_list.append(
                TextAnimatorSchema(
                    name=a_name,
                    match_name=a_mn,
                    selectors=selectors_out,
                    animator_properties=props_out,
                )
            )

    return TextLayerDetailSchema(
        source_text=_safe_getattr(doc, "text", None) if doc else None,
        font=_safe_getattr(doc, "font", None) if doc else None,
        font_family=None,  # Resolved by OS font server at runtime
        font_style=None,
        font_size=_serialize_value(_safe_getattr(doc, "font_size", None)) if doc else None,
        fill_color=_serialize_value(_safe_getattr(doc, "fill_color", None)) if doc else None,
        stroke_color=_serialize_value(_safe_getattr(doc, "stroke_color", None)) if doc else None,
        stroke_width=_serialize_value(_safe_getattr(doc, "stroke_width", None)) if doc else None,
        apply_fill=_safe_getattr(doc, "apply_fill", None) if doc else None,
        apply_stroke=_safe_getattr(doc, "apply_stroke", None) if doc else None,
        justification=_enum_name(_safe_getattr(doc, "justification", None)) if doc else None,
        tracking=_serialize_value(_safe_getattr(doc, "tracking", None)) if doc else None,
        leading=_serialize_value(_safe_getattr(doc, "leading", None)) if doc else None,
        is_box_text=_safe_getattr(doc, "box_text", None) if doc else None,
        three_d_per_char=bool(_safe_getattr(layer, "three_d_per_char", False)),
        is_source_text_animated=is_src_anim,
        source_text_keyframes=src_kfs,
        animators=animators_list,
        status=DataAvailabilityStatus.OBSERVED,
    )


def _classify_layer_type(layer: Layer) -> str:
    if isinstance(layer, TextLayer):
        return "TextLayer"
    if isinstance(layer, ShapeLayer):
        return "ShapeLayer"
    if isinstance(layer, CameraLayer):
        return "CameraLayer"
    if isinstance(layer, LightLayer):
        return "LightLayer"
    if isinstance(layer, ThreeDModelLayer):
        return "ThreeDModelLayer"
    if isinstance(layer, ParametricMeshLayer):
        return "ParametricMeshLayer"
    if bool(_safe_getattr(layer, "adjustment_layer", False)):
        return "AdjustmentLayer"
    if bool(_safe_getattr(layer, "null_layer", False)):
        return "NullLayer"
    src = _safe_getattr(layer, "source", None)
    if isinstance(src, CompItem):
        return "PrecompLayer"
    if isinstance(src, FootageItem):
        ms = _safe_getattr(src, "main_source", None)
        if isinstance(ms, SolidSource):
            return "SolidLayer"
        return "FootageLayer"
    return type(layer).__name__


def _extract_raw_efdg_definitions(rifx: Any) -> list[dict[str, str]]:
    """Extract global effect definitions (`LIST:EfdG` -> `LIST:EfDf`) from the raw RIFX chunk tree."""
    ef_defs: list[dict[str, str]] = []
    try:
        for chunk in getattr(rifx, "chunks", []):
            if isinstance(chunk, ListChunk) and chunk.list_type == "Fold":
                for sub in chunk.chunks:
                    if isinstance(sub, ListChunk) and sub.list_type == "EfdG":
                        for efdf in sub.chunks:
                            if isinstance(efdf, ListChunk) and efdf.list_type == "EfDf":
                                mn = ""
                                dn = ""
                                for c in efdf.chunks:
                                    if getattr(c, "header", "") == "tdmn":
                                        mn = str(getattr(c, "value", "") or "").rstrip("\x00")
                                    elif isinstance(c, ListChunk) and c.list_type == "sspc":
                                        for sc in c.chunks:
                                            if getattr(sc, "header", "") == "fnam" or (
                                                isinstance(sc, ListChunk) and sc.list_type == "fnam"
                                            ):
                                                for u in getattr(sc, "chunks", []):
                                                    if getattr(u, "header", "") == "Utf8":
                                                        dn = str(getattr(u, "value", "") or "")
                                if mn:
                                    ef_defs.append({"match_name": mn, "display_name": dn or mn})
    except Exception as exc:
        logger.debug("Could not extract raw EfdG definitions: %s", exc)
    return ef_defs


def parse_aep_with_py_aep(
    project_path: Path,
    analysis_id: str,
    rerun_command: str,
    rifx_bytes_override: bytes | None = None,
    file_format_override: str | None = None,
) -> ProjectAnalysisResult:
    """Parse an After Effects `.aep` (or transcoded `.aepx`) file using `py_aep`."""
    fmt, size_bytes, sha256_hex = validate_project_file_safety(project_path)
    actual_format = file_format_override or fmt

    warnings: list[AnalysisWarning] = []
    unsupported_fields: list[FieldProvenance] = [
        FieldProvenance(
            field_path="Property.value (when expression_enabled=true)",
            status=DataAvailabilityStatus.UNAVAILABLE,
            source_method="offline_py_aep",
            reason=(
                "After Effects evaluates JavaScript/ExtendScript expressions at runtime. "
                "Offline parsing extracts the full expression source string and the pre-expression "
                "stored value/keyframes, while runtime expression evaluation results require Live AE Bridge."
            ),
        ),
        FieldProvenance(
            field_path="Property.expression_error",
            status=DataAvailabilityStatus.UNAVAILABLE,
            source_method="offline_py_aep",
            reason="Expression syntax/runtime errors are computed by the live AE expression engine.",
        ),
        FieldProvenance(
            field_path="Application.effects / Application.fonts",
            status=DataAvailabilityStatus.UNAVAILABLE,
            source_method="offline_py_aep",
            reason="System-installed plugins and OS font tables are runtime machine state, not stored in .aep.",
        ),
    ]

    with readonly_file_guard(project_path):
        raw_bytes = rifx_bytes_override if rifx_bytes_override is not None else project_path.read_bytes()
        rifx_chunk, _ = read_aep(io.BytesIO(raw_bytes))
        raw_efdg = _extract_raw_efdg_definitions(rifx_chunk)

        if rifx_bytes_override is not None:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".aep", delete=False) as tmp:
                tmp.write(rifx_bytes_override)
                tmp_path = Path(tmp.name)
            try:
                app = py_aep.parse(tmp_path)
            finally:
                tmp_path.unlink(missing_ok=True)
        else:
            app = py_aep.parse(project_path)

    proj = app.project

    # Build folder path helper
    def _folder_path(item: Any) -> str:
        parts: list[str] = []
        curr = _safe_getattr(item, "parent_folder", None)
        visited = 0
        while curr is not None and visited < 32:
            visited += 1
            cname = _safe_getattr(curr, "name", "")
            if cname and cname != "Root":
                parts.append(str(cname))
            curr = _safe_getattr(curr, "parent_folder", None)
        return "/" + "/".join(reversed(parts)) if parts else "/"

    # Track composition & precomp usage
    comp_items: list[CompItem] = list(_safe_getattr(proj, "compositions", []) or [])
    footage_items: list[FootageItem] = list(_safe_getattr(proj, "footages", []) or [])
    folder_items: list[FolderItem] = list(_safe_getattr(proj, "folders", []) or [])
    all_items_dict: dict[int, Any] = _safe_getattr(proj, "items", {}) or {}

    comp_hierarchy: list[CompositionGraphEdgeSchema] = []
    layer_relationships: list[LayerRelationshipEdgeSchema] = []
    expressions_inventory: list[dict[str, Any]] = []
    plugin_map: dict[str, PluginInventoryItemSchema] = {}

    # Pre-populate plugin map with global EfdG definitions found in the binary
    for ef_def in raw_efdg:
        mn = ef_def["match_name"]
        dn = ef_def["display_name"]
        c_info = classify_effect(mn, dn)
        if mn not in plugin_map:
            plugin_map[mn] = PluginInventoryItemSchema(
                match_name=mn,
                display_name=c_info.display_name,
                plugin_vendor=c_info.plugin_vendor,
                plugin_package=c_info.plugin_package,
                category=c_info.category,
                is_third_party=c_info.is_third_party,
                is_builtin=c_info.is_builtin,
                occurrences_count=0,
                status=DataAvailabilityStatus.OBSERVED,
            )

    compositions_out: list[CompositionSchema] = []
    precomp_names_set: set[str] = set()

    for comp in comp_items:
        c_name = str(_safe_getattr(comp, "name", "Composition"))
        c_id = _safe_getattr(comp, "id", None)
        c_fps = float(_safe_getattr(comp, "frame_rate", 30.0) or 30.0)
        used_in_comps = [
            str(_safe_getattr(uc, "name", ""))
            for uc in (_safe_getattr(comp, "used_in", []) or [])
            if _safe_getattr(uc, "name", "")
        ]
        is_precomp = len(used_in_comps) > 0
        if is_precomp:
            precomp_names_set.add(c_name)

        raw_layers: list[Layer] = list(_safe_getattr(comp, "layers", []) or [])
        comp_layers_by_1idx: dict[int, str] = {
            idx: str(_safe_getattr(lyr_item, "name", f"Layer {idx}"))
            for idx, lyr_item in enumerate(raw_layers, start=1)
        }

        referenced_precomps: list[str] = []
        layers_out: list[LayerSchema] = []

        for l_1idx, layer in enumerate(raw_layers, start=1):
            l_name = str(_safe_getattr(layer, "name", f"Layer {l_1idx}"))
            l_id = _safe_getattr(layer, "id", None)
            l_type = _classify_layer_type(layer)

            parent_layer = _safe_getattr(layer, "parent", None)
            parent_1idx: int | None = None
            parent_name: str | None = None
            if parent_layer is not None:
                p_0idx = _safe_getattr(parent_layer, "index", None)
                if isinstance(p_0idx, int):
                    parent_1idx = p_0idx + 1
                parent_name = str(_safe_getattr(parent_layer, "name", ""))
                layer_relationships.append(
                    LayerRelationshipEdgeSchema(
                        composition_name=c_name,
                        source_layer_index=l_1idx,
                        source_layer_name=l_name,
                        target_layer_index=parent_1idx,
                        target_layer_name=parent_name or f"Layer #{parent_1idx}",
                        relationship_type="parenting",
                        detail="Layer parent transform link",
                    )
                )

            has_tm = bool(_safe_getattr(layer, "has_track_matte", False))
            is_tm = bool(_safe_getattr(layer, "is_track_matte", False))
            tm_type = _enum_name(_safe_getattr(layer, "track_matte_type", None))
            tm_layer = _safe_getattr(layer, "track_matte_layer", None)
            tm_1idx: int | None = None
            tm_name: str | None = None
            if tm_layer is not None:
                tm_0idx = _safe_getattr(tm_layer, "index", None)
                if isinstance(tm_0idx, int):
                    tm_1idx = tm_0idx + 1
                tm_name = str(_safe_getattr(tm_layer, "name", ""))
                layer_relationships.append(
                    LayerRelationshipEdgeSchema(
                        composition_name=c_name,
                        source_layer_index=l_1idx,
                        source_layer_name=l_name,
                        target_layer_index=tm_1idx,
                        target_layer_name=tm_name or f"Layer #{tm_1idx}",
                        relationship_type="track_matte",
                        detail=f"Track Matte ({tm_type or 'ALPHA'})",
                    )
                )

            src_item = _safe_getattr(layer, "source", None)
            src_id = _safe_getattr(src_item, "id", None) if src_item is not None else None
            src_name = str(_safe_getattr(src_item, "name", "")) if src_item is not None else None
            src_comp_name: str | None = None
            if isinstance(src_item, CompItem):
                src_comp_name = src_name
                if src_comp_name and src_comp_name not in referenced_precomps:
                    referenced_precomps.append(src_comp_name)
                if src_comp_name:
                    comp_hierarchy.append(
                        CompositionGraphEdgeSchema(
                            parent_comp=c_name,
                            child_comp=src_comp_name,
                            layer_index=l_1idx,
                            layer_name=l_name,
                        )
                    )
                    layer_relationships.append(
                        LayerRelationshipEdgeSchema(
                            composition_name=c_name,
                            source_layer_index=l_1idx,
                            source_layer_name=l_name,
                            target_layer_index=None,
                            target_layer_name=src_comp_name,
                            relationship_type="precomp_source",
                            detail=f"Nested composition '{src_comp_name}'",
                        )
                    )

            layer_exprs: list[dict[str, Any]] = []
            layer_animated: list[str] = []

            # Transform
            transform_schema = _extract_transform(
                layer, c_name, c_fps, l_1idx, layer_exprs, layer_animated
            )

            # Time Remapping
            tr_enabled = bool(_safe_getattr(layer, "time_remapping_enabled", False))
            tr_prop_schema: PropertySchema | None = None
            tr_raw = _safe_getattr(layer, "time_remap", None)
            if isinstance(tr_raw, Property) and (tr_enabled or _safe_getattr(tr_raw, "is_time_varying", False)):
                tr_prop_schema = _extract_property_tree(
                    tr_raw,
                    "Time Remap",
                    c_fps,
                    layer_exprs,
                    layer_animated,
                    c_name,
                    l_name,
                    l_1idx,
                )

            # Masks
            masks_out = _extract_layer_masks(
                layer, c_name, c_fps, l_1idx, layer_exprs, layer_animated
            )

            # Effects
            effects_out = _extract_layer_effects(
                layer,
                c_name,
                c_fps,
                l_1idx,
                layer_exprs,
                layer_animated,
                layer_relationships,
                comp_layers_by_1idx,
            )
            for eff in effects_out:
                if eff.match_name not in plugin_map:
                    plugin_map[eff.match_name] = PluginInventoryItemSchema(
                        match_name=eff.match_name,
                        display_name=eff.display_name or eff.name,
                        plugin_vendor=eff.plugin_vendor or "Unknown",
                        plugin_package=eff.plugin_package or eff.name,
                        category=eff.category or "Effect",
                        is_third_party=eff.is_third_party,
                        is_builtin=not eff.is_third_party,
                        occurrences_count=0,
                        status=DataAvailabilityStatus.OBSERVED,
                    )
                p_entry = plugin_map[eff.match_name]
                p_entry.occurrences_count += 1
                if c_name not in p_entry.used_in_compositions:
                    p_entry.used_in_compositions.append(c_name)
                layer_ref_label = f"{c_name} > [{l_1idx}] {l_name} ({eff.name})"
                if layer_ref_label not in p_entry.used_on_layers:
                    p_entry.used_on_layers.append(layer_ref_label)

            # Text Layer Detail
            text_detail: TextLayerDetailSchema | None = None
            if isinstance(layer, TextLayer):
                text_detail = _extract_text_layer_detail(
                    layer, c_name, c_fps, l_1idx, layer_exprs, layer_animated
                )

            # Shape Layer Contents
            shape_contents: list[PropertySchema] = []
            if isinstance(layer, ShapeLayer):
                root_vec = _safe_getattr(layer, "content", None)
                if root_vec is None:
                    try:
                        root_vec = layer["ADBE Root Vectors Group"]
                    except Exception:
                        root_vec = None
                if root_vec is not None:
                    try:
                        for sc in list(root_vec):
                            shape_contents.append(
                                _extract_property_tree(
                                    sc,
                                    "Contents",
                                    c_fps,
                                    layer_exprs,
                                    layer_animated,
                                    c_name,
                                    l_name,
                                    l_1idx,
                                )
                            )
                    except Exception:
                        pass

            # Camera Options
            camera_opts: list[PropertySchema] = []
            if isinstance(layer, CameraLayer):
                cam_group = _safe_getattr(layer, "camera_options", None)
                if cam_group is not None:
                    try:
                        for co in list(cam_group):
                            camera_opts.append(
                                _extract_property_tree(
                                    co,
                                    "Camera Options",
                                    c_fps,
                                    layer_exprs,
                                    layer_animated,
                                    c_name,
                                    l_name,
                                    l_1idx,
                                )
                            )
                    except Exception:
                        pass

            # Light Options
            light_opts: list[PropertySchema] = []
            if isinstance(layer, LightLayer):
                lgt_group = _safe_getattr(layer, "light_options", None)
                if lgt_group is not None:
                    try:
                        for lo in list(lgt_group):
                            light_opts.append(
                                _extract_property_tree(
                                    lo,
                                    "Light Options",
                                    c_fps,
                                    layer_exprs,
                                    layer_animated,
                                    c_name,
                                    l_name,
                                    l_1idx,
                                )
                            )
                    except Exception:
                        pass

            # Layer Styles (only include enabled sub-styles to keep output clean and accurate)
            layer_styles_out: list[PropertySchema] = []
            ls_group = _safe_getattr(layer, "layer_style", None)
            if ls_group is not None and bool(_safe_getattr(ls_group, "enabled", False)):
                try:
                    for ls_child in list(ls_group):
                        if bool(_safe_getattr(ls_child, "enabled", False)):
                            layer_styles_out.append(
                                _extract_property_tree(
                                    ls_child,
                                    "Layer Styles",
                                    c_fps,
                                    layer_exprs,
                                    layer_animated,
                                    c_name,
                                    l_name,
                                    l_1idx,
                                )
                            )
                except Exception:
                    pass

            # Layer Markers
            layer_markers: list[KeyframeSchema] = []
            marker_prop = _safe_getattr(layer, "marker", None)
            if isinstance(marker_prop, Property):
                layer_markers = _extract_keyframes(marker_prop, c_fps)

            expressions_inventory.extend(layer_exprs)

            layers_out.append(
                LayerSchema(
                    index=l_1idx,
                    id=l_id,
                    name=l_name,
                    layer_type=l_type,
                    enabled=bool(_safe_getattr(layer, "enabled", True)),
                    solo=bool(_safe_getattr(layer, "solo", False)),
                    shy=bool(_safe_getattr(layer, "shy", False)),
                    locked=bool(_safe_getattr(layer, "locked", False)),
                    is_null=bool(_safe_getattr(layer, "null_layer", False)),
                    is_adjustment_layer=bool(_safe_getattr(layer, "adjustment_layer", False)),
                    is_three_d=bool(_safe_getattr(layer, "three_d_layer", False)),
                    is_guide_layer=bool(_safe_getattr(layer, "guide_layer", False)),
                    collapse_transformation=bool(_safe_getattr(layer, "collapse_transformation", False)),
                    motion_blur=bool(_safe_getattr(layer, "motion_blur", False)),
                    effects_active=bool(_safe_getattr(layer, "effects_active", True)),
                    frame_blending_type=_enum_name(_safe_getattr(layer, "frame_blending_type", None)),
                    quality=_enum_name(_safe_getattr(layer, "quality", None)),
                    sampling_quality=_enum_name(_safe_getattr(layer, "sampling_quality", None)),
                    blending_mode=_enum_name(_safe_getattr(layer, "blending_mode", None)),
                    preserve_transparency=bool(_safe_getattr(layer, "preserve_transparency", False)),
                    auto_orient=_enum_name(_safe_getattr(layer, "auto_orient", None)),
                    label=_enum_name(_safe_getattr(layer, "label", None)),
                    comment=_safe_getattr(layer, "comment", None) or None,
                    parent_index=parent_1idx,
                    parent_name=parent_name,
                    has_track_matte=has_tm,
                    is_track_matte=is_tm,
                    track_matte_type=tm_type,
                    track_matte_layer_index=tm_1idx,
                    track_matte_layer_name=tm_name,
                    in_point=round(float(_safe_getattr(layer, "in_point", 0.0) or 0.0), 6),
                    out_point=round(float(_safe_getattr(layer, "out_point", 0.0) or 0.0), 6),
                    start_time=round(float(_safe_getattr(layer, "start_time", 0.0) or 0.0), 6),
                    stretch=round(float(_safe_getattr(layer, "stretch", 100.0) or 100.0), 4),
                    source_item_id=src_id,
                    source_item_name=src_name,
                    source_comp_name=src_comp_name,
                    time_remapping_enabled=tr_enabled,
                    time_remap_property=tr_prop_schema,
                    transform=transform_schema,
                    masks=masks_out,
                    effects=effects_out,
                    text_detail=text_detail,
                    shape_contents=shape_contents,
                    camera_options=camera_opts,
                    light_options=light_opts,
                    layer_styles=layer_styles_out,
                    markers=layer_markers,
                    expressions_summary=layer_exprs,
                    animated_properties_summary=layer_animated,
                    status=DataAvailabilityStatus.OBSERVED,
                )
            )

        # Composition markers
        comp_markers: list[KeyframeSchema] = []
        c_marker_prop = _safe_getattr(comp, "marker_property", None)
        if isinstance(c_marker_prop, Property):
            comp_markers = _extract_keyframes(c_marker_prop, c_fps)

        compositions_out.append(
            CompositionSchema(
                item_id=c_id,
                name=c_name,
                comment=_safe_getattr(comp, "comment", None) or None,
                parent_folder_path=_folder_path(comp),
                width=int(_safe_getattr(comp, "width", 0) or 0),
                height=int(_safe_getattr(comp, "height", 0) or 0),
                pixel_aspect=round(float(_safe_getattr(comp, "pixel_aspect", 1.0) or 1.0), 6),
                frame_rate=round(c_fps, 6),
                duration=round(float(_safe_getattr(comp, "duration", 0.0) or 0.0), 6),
                work_area_start=round(float(_safe_getattr(comp, "work_area_start", 0.0) or 0.0), 6),
                work_area_duration=round(float(_safe_getattr(comp, "work_area_duration", 0.0) or 0.0), 6),
                bg_color=_serialize_value(_safe_getattr(comp, "bg_color", [])) or [],
                shutter_angle=_safe_getattr(comp, "shutter_angle", None),
                shutter_phase=_safe_getattr(comp, "shutter_phase", None),
                motion_blur=bool(_safe_getattr(comp, "motion_blur", False)),
                motion_blur_samples_per_frame=_safe_getattr(comp, "motion_blur_samples_per_frame", None),
                motion_blur_adaptive_sample_limit=_safe_getattr(
                    comp, "motion_blur_adaptive_sample_limit", None
                ),
                frame_blending=bool(_safe_getattr(comp, "frame_blending", False)),
                preserve_nested_frame_rate=bool(_safe_getattr(comp, "preserve_nested_frame_rate", False)),
                preserve_nested_resolution=bool(_safe_getattr(comp, "preserve_nested_resolution", False)),
                drop_frame=bool(_safe_getattr(comp, "drop_frame", False)),
                hide_shy_layers=bool(_safe_getattr(comp, "hide_shy_layers", False)),
                renderer=_safe_getattr(comp, "renderer", None),
                is_precomp=is_precomp,
                used_in_compositions=used_in_comps,
                referenced_precomps=referenced_precomps,
                layers_count=len(layers_out),
                layers=layers_out,
                markers=comp_markers,
            )
        )

    # Extract Footage Dependencies & Missing Assets
    dependencies_out: list[FootageDependencySchema] = []
    missing_assets_out: list[FootageDependencySchema] = []

    for ftg in footage_items:
        f_id = _safe_getattr(ftg, "id", None)
        f_name = str(_safe_getattr(ftg, "name", "Footage"))
        ms = _safe_getattr(ftg, "main_source", None)
        asset_type = str(_safe_getattr(ftg, "asset_type", "file") or "file")
        file_path_str: str | None = None
        exists_on_disk: bool | None = None
        is_missing = bool(_safe_getattr(ftg, "footage_missing", False))
        missing_path = _safe_getattr(ms, "missing_footage_path", None) if ms else None
        solid_color: list[float] | None = None

        if isinstance(ms, FileSource):
            f_obj = _safe_getattr(ms, "file", None)
            if f_obj is not None:
                file_path_str = str(f_obj)
                try:
                    exists_on_disk = Path(file_path_str).exists()
                except OSError:
                    exists_on_disk = False
                if not exists_on_disk:
                    is_missing = True
        elif isinstance(ms, SolidSource):
            asset_type = "solid"
            solid_color = _serialize_value(_safe_getattr(ms, "color", None))
        elif isinstance(ms, PlaceholderSource):
            asset_type = "placeholder"
            is_missing = True

        used_in = [
            str(_safe_getattr(uc, "name", ""))
            for uc in (_safe_getattr(ftg, "used_in", []) or [])
            if _safe_getattr(uc, "name", "")
        ]

        dep = FootageDependencySchema(
            item_id=f_id,
            name=f_name,
            parent_folder_path=_folder_path(ftg),
            asset_type=asset_type,
            file_path=file_path_str,
            exists_on_disk=exists_on_disk,
            is_missing=is_missing,
            missing_footage_path=str(missing_path) if missing_path else None,
            width=_safe_getattr(ftg, "width", None),
            height=_safe_getattr(ftg, "height", None),
            duration=_serialize_value(_safe_getattr(ftg, "duration", None)),
            frame_rate=_serialize_value(_safe_getattr(ftg, "frame_rate", None)),
            has_alpha=_safe_getattr(ms, "has_alpha", None) if ms else None,
            solid_color=solid_color if isinstance(solid_color, list) else None,
            used_in_compositions=used_in,
        )
        dependencies_out.append(dep)
        if is_missing and asset_type != "solid":
            missing_assets_out.append(dep)

    # Identify third-party plugins that may require external installation in AE
    third_party_plugins = [
        f"{p.display_name} ({p.match_name}) — {p.plugin_vendor} [{p.plugin_package}]"
        for p in plugin_map.values()
        if p.is_third_party
    ]
    if third_party_plugins:
        warnings.append(
            AnalysisWarning(
                code="THIRD_PARTY_PLUGINS_DETECTED",
                message=(
                    f"Project references {len(third_party_plugins)} third-party plugin(s). "
                    "Offline parser extracted their stored parameter trees from binary parT/tdgp chunks; "
                    "opening in After Effects requires those .aex plugins installed."
                ),
                status=DataAvailabilityStatus.OBSERVED,
            )
        )

    rq = _safe_getattr(proj, "render_queue", None)
    rq_count = len(list(rq)) if rq is not None else 0

    metadata = ProjectMetadataSchema(
        file_path=str(project_path.resolve()),
        file_name=project_path.name,
        file_format=actual_format,
        file_size_bytes=size_bytes,
        sha256=sha256_hex,
        ae_version=str(_safe_getattr(app, "version", "") or ""),
        bits_per_channel=_enum_name(_safe_getattr(proj, "bits_per_channel", None))
        if not isinstance(_safe_getattr(proj, "bits_per_channel", None), int)
        else int(_safe_getattr(proj, "bits_per_channel", 8)),
        working_space=_safe_getattr(proj, "working_space", None),
        working_gamma=_serialize_value(_safe_getattr(proj, "working_gamma", None)),
        linearize_working_space=_safe_getattr(proj, "linearize_working_space", None),
        compensate_for_scene_referred_profiles=_safe_getattr(
            proj, "compensate_for_scene_referred_profiles", None
        ),
        time_display_type=_enum_name(_safe_getattr(proj, "time_display_type", None)),
        frames_count_type=_enum_name(_safe_getattr(proj, "frames_count_type", None)),
        feet_frames_film_type=_enum_name(_safe_getattr(proj, "feet_frames_film_type", None)),
        audio_sample_rate=_serialize_value(_safe_getattr(proj, "audio_sample_rate", None)),
        expression_engine=_safe_getattr(proj, "expression_engine", None),
        gpu_accel_type=_enum_name(_safe_getattr(proj, "gpu_accel_type", None)),
        total_items=len(all_items_dict),
        total_compositions=len(compositions_out),
        total_precompositions=len(precomp_names_set),
        total_footage_items=len(footage_items),
        total_folders=len(folder_items),
        render_queue_items_count=rq_count,
        field_status={
            "ae_version": DataAvailabilityStatus.OBSERVED,
            "compositions": DataAvailabilityStatus.OBSERVED,
            "layers": DataAvailabilityStatus.OBSERVED,
            "effect_stack": DataAvailabilityStatus.OBSERVED,
            "keyframes": DataAvailabilityStatus.OBSERVED,
            "expressions_source": DataAvailabilityStatus.OBSERVED,
            "expressions_evaluated_value": DataAvailabilityStatus.UNAVAILABLE,
            "installed_system_effects": DataAvailabilityStatus.UNAVAILABLE,
        },
    )

    raw_summary = {
        "rifx_header": getattr(rifx_chunk, "header", "RIFX"),
        "rifx_list_type": getattr(rifx_chunk, "list_type", "Egg!"),
        "top_level_chunks_count": len(getattr(rifx_chunk, "chunks", [])),
        "global_efdg_definitions_count": len(raw_efdg),
        "global_efdg_definitions": raw_efdg,
        "total_layers_across_compositions": sum(c.layers_count for c in compositions_out),
        "total_effects_applied": sum(
            len(lyr.effects) for c in compositions_out for lyr in c.layers
        ),
        "total_expressions": len(expressions_inventory),
    }

    return ProjectAnalysisResult(
        analysis_id=analysis_id,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        extraction_method="offline_aepx" if actual_format == "aepx" else "offline_py_aep",
        live_bridge_tested=False,
        live_bridge_status_note=(
            "Offline parsing completed without opening After Effects. "
            "Pass --use-ae-bridge to query or compare with a live After Effects instance."
        ),
        rerun_command=rerun_command,
        metadata=metadata,
        compositions=compositions_out,
        composition_hierarchy=comp_hierarchy,
        layer_relationships=layer_relationships,
        plugin_inventory=sorted(
            plugin_map.values(),
            key=lambda x: (not x.is_third_party, -x.occurrences_count, x.match_name),
        ),
        dependencies=dependencies_out,
        missing_assets=missing_assets_out,
        missing_effects=third_party_plugins,
        expressions_inventory=expressions_inventory,
        warnings=warnings,
        unsupported_fields=unsupported_fields,
        raw_summary=raw_summary,
        comparison_with_live=None,
    )
