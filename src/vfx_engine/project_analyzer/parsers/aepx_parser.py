"""Clean-room After Effects XML Project (.aepx) parser and RIFX transcoder."""

from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...core.logging import get_logger
from ...core.safety import readonly_file_guard, validate_project_file_safety
from ...schemas.common import AnalysisWarning, DataAvailabilityStatus, FieldProvenance
from ...schemas.project_schema import (
    CompositionGraphEdgeSchema,
    CompositionSchema,
    EffectInstanceSchema,
    FootageDependencySchema,
    LayerSchema,
    PluginInventoryItemSchema,
    ProjectAnalysisResult,
    ProjectMetadataSchema,
)
from ..effect_extractor.plugin_registry import classify_effect
from .py_aep_parser import parse_aep_with_py_aep

logger = get_logger("project_analyzer.aepx_parser")

# Non-LIST container chunks in RIFX that hold sub-chunks without a 4-byte list_type prefix
_NON_LIST_CONTAINERS = {"tdsn", "fnam", "pdnm"}


def _fourcc(tag: str) -> bytes:
    """Convert an XML tag name to a 4-byte ASCII FourCC."""
    if tag == "Pin":
        return b"Pin "
    if tag == "AfterEffectsProject":
        return b"Egg!"
    raw = tag.encode("latin1", errors="replace")
    if len(raw) < 4:
        return raw.ljust(4, b" ")
    return raw[:4]


def _serialize_aepx_elem_to_rifx(elem: ET.Element) -> bytes:
    """Recursively serialize an AEPX XML element into big-endian RIFX chunk bytes."""
    tag = elem.tag.split("}")[-1]  # Strip XML namespace if present

    # Case 1: Leaf chunk with hex binary payload (`bdata="..."`)
    bdata = elem.get("bdata")
    if bdata is not None:
        clean_hex = "".join(bdata.split())
        payload = bytes.fromhex(clean_hex) if clean_hex else b""
        if tag == "btdk":
            # In RIFX binary, btdk is stored as `LIST <size> btdk <payload>`
            list_size = 4 + len(payload)
            out = b"LIST" + struct.pack(">I", list_size) + b"btdk" + payload
            if len(payload) % 2 == 1:
                out += b"\x00"
            return out
        header = _fourcc(tag)
        out = header + struct.pack(">I", len(payload)) + payload
        if len(payload) % 2 == 1:
            out += b"\x00"
        return out

    # Case 2: `<string>...</string>` inside `<Utf8>` or standalone
    if tag == "string":
        text_bytes = (elem.text or "").encode("utf-8")
        out = b"Utf8" + struct.pack(">I", len(text_bytes)) + text_bytes
        if len(text_bytes) % 2 == 1:
            out += b"\x00"
        return out

    # Case 3: `<Utf8>` containing `<string>` or direct text
    if tag == "Utf8" and len(elem) == 1 and elem[0].tag.split("}")[-1] == "string":
        text_bytes = (elem[0].text or "").encode("utf-8")
        out = b"Utf8" + struct.pack(">I", len(text_bytes)) + text_bytes
        if len(text_bytes) % 2 == 1:
            out += b"\x00"
        return out

    # Case 4: `<fileReference fullpath="..." ... />` inside `<Als2>`
    if tag == "fileReference":
        ref: dict[str, Any] = {}
        for k, v in elem.attrib.items():
            if k == "target_is_folder":
                ref[k] = v in ("1", "true", "True")
            else:
                ref[k] = v
        payload = json.dumps(ref).encode("utf-8")
        out = b"alas" + struct.pack(">I", len(payload)) + payload
        if len(payload) % 2 == 1:
            out += b"\x00"
        return out

    # Case 5: Container chunk
    children_bytes = b"".join(_serialize_aepx_elem_to_rifx(child) for child in elem)

    if tag == "AfterEffectsProject":
        # Root RIFX container: `RIFX <size> Egg! <children>`
        total_size = 4 + len(children_bytes)
        return b"RIFX" + struct.pack(">I", total_size) + b"Egg!" + children_bytes

    if tag in _NON_LIST_CONTAINERS:
        header = _fourcc(tag)
        out = header + struct.pack(">I", len(children_bytes)) + children_bytes
        if len(children_bytes) % 2 == 1:
            out += b"\x00"
        return out

    # Standard LIST chunk: `LIST <size> <list_type> <children>`
    list_type = _fourcc(tag)
    list_size = 4 + len(children_bytes)
    out = b"LIST" + struct.pack(">I", list_size) + list_type + children_bytes
    if list_size % 2 == 1:
        out += b"\x00"
    return out


def aepx_xml_to_rifx_bytes(xml_text: str) -> bytes:
    """Convert an `.aepx` XML document string into a big-endian RIFX `.aep` byte buffer."""
    root = ET.fromstring(xml_text)
    return _serialize_aepx_elem_to_rifx(root)


def rifx_bytes_to_aepx_xml(rifx_bytes: bytes) -> str:
    """Convert binary RIFX `.aep` bytes into an `.aepx` XML string (useful for roundtrip & fixtures)."""
    if len(rifx_bytes) < 12 or rifx_bytes[:4] not in (b"RIFX", b"RIFF"):
        raise ValueError("Input bytes are not a valid RIFX/RIFF After Effects container")
    endian = ">" if rifx_bytes[:4] == b"RIFX" else "<"
    total_size = struct.unpack(f"{endian}I", rifx_bytes[4:8])[0]
    end_offset = min(len(rifx_bytes), 8 + total_size)

    root_el = ET.Element(
        "AfterEffectsProject",
        attrib={" xmlns": "http://www.adobe.com/products/aftereffects", "version": "1.0"},
    )
    # Remove leading space in attrib key used only to avoid ElementTree reserved checks
    root_el.attrib.clear()
    root_el.set("xmlns", "http://www.adobe.com/products/aftereffects")

    def _parse_chunks_into_xml(buf: bytes, start: int, limit: int, parent_el: ET.Element) -> None:
        pos = start
        while pos + 8 <= limit:
            hdr_bytes = buf[pos : pos + 4]
            hdr = hdr_bytes.decode("latin1", errors="replace")
            sz = struct.unpack(f"{endian}I", buf[pos + 4 : pos + 8])[0]
            data_start = pos + 8
            data_end = min(limit, data_start + sz)
            payload = buf[data_start:data_end]

            if hdr == "LIST" and len(payload) >= 4:
                ltype_raw = payload[:4].decode("latin1", errors="replace")
                if ltype_raw == "btdk":
                    el = ET.SubElement(parent_el, "btdk")
                    el.set("bdata", payload[4:].hex())
                else:
                    tag_name = "Pin" if ltype_raw == "Pin " else ltype_raw.strip() or "LIST"
                    el = ET.SubElement(parent_el, tag_name)
                    _parse_chunks_into_xml(payload, 4, len(payload), el)
            elif hdr in _NON_LIST_CONTAINERS and len(payload) >= 8 and payload[:4] == b"Utf8":
                el = ET.SubElement(parent_el, hdr)
                _parse_chunks_into_xml(payload, 0, len(payload), el)
            elif hdr == "Utf8":
                str_el = ET.SubElement(parent_el, "string")
                str_el.text = payload.decode("utf-8", errors="replace").rstrip("\x00")
            else:
                el = ET.SubElement(parent_el, hdr.strip() or "chunk")
                el.set("bdata", payload.hex())

            pos = data_end + (sz % 2)

    _parse_chunks_into_xml(rifx_bytes, 12, end_offset, root_el)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root_el, encoding="unicode")


def _parse_aepx_dom_fallback(
    project_path: Path,
    xml_text: str,
    size_bytes: int,
    sha256_hex: str,
    analysis_id: str,
    rerun_command: str,
    transcode_error: str,
) -> ProjectAnalysisResult:
    """Direct XML DOM parser fallback for simplified or partial `.aepx` files."""
    root = ET.fromstring(xml_text)

    def _strip_ns(tag: str) -> str:
        return tag.split("}")[-1]

    def _child_text(parent: ET.Element) -> str:
        for ch in parent:
            t = _strip_ns(ch.tag)
            if t == "string":
                return (ch.text or "").strip()
            if t == "Utf8":
                if ch.text and ch.text.strip():
                    return ch.text.strip()
                for sub in ch:
                    if _strip_ns(sub.tag) == "string":
                        return (sub.text or "").strip()
        return ""

    compositions: list[CompositionSchema] = []
    dependencies: list[FootageDependencySchema] = []
    missing_assets: list[FootageDependencySchema] = []
    plugin_map: dict[str, PluginInventoryItemSchema] = {}
    comp_hierarchy: list[CompositionGraphEdgeSchema] = []
    expressions_inventory: list[dict[str, Any]] = []
    unsupported_fields: list[FieldProvenance] = [
        FieldProvenance(
            field_path="Property.synthesized_defaults",
            status=DataAvailabilityStatus.UNSUPPORTED,
            source_method="offline_aepx_dom_fallback",
            reason="Simplified XML did not contain full binary RIFX header chunks for synthesis.",
        )
    ]

    # Scan global EfdG definitions if present
    for efdf in root.iter():
        if _strip_ns(efdf.tag) == "EfDf":
            mn = ""
            dn = ""
            for ch in efdf:
                ct = _strip_ns(ch.tag)
                if ct == "tdmn" and ch.get("bdata"):
                    mn = bytes.fromhex(ch.get("bdata", "")).decode("utf-8", errors="replace").rstrip("\x00")
                elif ct == "sspc":
                    for sc in ch:
                        if _strip_ns(sc.tag) == "fnam":
                            dn = _child_text(sc)
            if mn:
                c_info = classify_effect(mn, dn or mn)
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

    # Scan Items
    for item_el in root.iter():
        if _strip_ns(item_el.tag) != "Item":
            continue
        item_name = _child_text(item_el) or "Unnamed Item"
        idta_el = next((c for c in item_el if _strip_ns(c.tag) == "idta"), None)
        cdta_el = next((c for c in item_el if _strip_ns(c.tag) == "cdta"), None)
        pin_el = next((c for c in item_el if _strip_ns(c.tag) in ("Pin", "Pin ")), None)

        item_id: int | None = None
        if idta_el is not None and idta_el.get("bdata"):
            raw_idta = bytes.fromhex(idta_el.get("bdata", ""))
            if len(raw_idta) >= 20:
                item_id = struct.unpack(">I", raw_idta[16:20])[0]

        if cdta_el is not None:
            width: int | None = None
            height: int | None = None
            fps: float | None = None
            duration: float | None = None

            if cdta_el.get("bdata"):
                raw_cdta = bytes.fromhex("".join(cdta_el.get("bdata", "").split()))
                if len(raw_cdta) >= 52:
                    dur_num, dur_den = struct.unpack(">II", raw_cdta[44:52])
                    if dur_num > 0 and dur_den > 0:
                        duration = round(dur_num / dur_den, 6)
                if len(raw_cdta) >= 144:
                    w, h = struct.unpack(">HH", raw_cdta[140:144])
                    if w > 0 and h > 0:
                        width, height = w, h
                if len(raw_cdta) >= 160:
                    fps_int, fps_frac = struct.unpack(">HH", raw_cdta[156:160])
                    if fps_int > 0 or fps_frac > 0:
                        fps = round(fps_int + fps_frac / 65536.0, 4)

            comp_field_status: dict[str, DataAvailabilityStatus] = {}
            for f_name, f_val in (
                ("width", width),
                ("height", height),
                ("frame_rate", fps),
                ("duration", duration),
            ):
                if f_val is not None:
                    comp_field_status[f_name] = DataAvailabilityStatus.OBSERVED
                else:
                    comp_field_status[f_name] = DataAvailabilityStatus.UNAVAILABLE
                    unsupported_fields.append(
                        FieldProvenance(
                            field_path=f"compositions[{item_name}].{f_name}",
                            status=DataAvailabilityStatus.UNAVAILABLE,
                            source_method="offline_aepx_dom_fallback",
                            reason=f"Missing or incomplete <cdta> binary payload for '{f_name}' in simplified AEPX XML.",
                        )
                    )
            layers_list: list[LayerSchema] = []
            for layr_idx, layr_el in enumerate(
                [c for c in item_el if _strip_ns(c.tag) == "Layr"], start=1
            ):
                l_name = _child_text(layr_el) or f"Layer {layr_idx}"
                # Extract effects under Layr -> tdgp -> ADBE Effect Parade
                layer_effects: list[EffectInstanceSchema] = []
                eff_counter = 0
                for sspc_el in layr_el.iter():
                    if _strip_ns(sspc_el.tag) == "sspc":
                        eff_counter += 1
                        fnam_el = next((c for c in sspc_el if _strip_ns(c.tag) == "fnam"), None)
                        eff_inst_name = _child_text(fnam_el) if fnam_el is not None else f"Effect {eff_counter}"
                        # Find preceding or child tdmn if any
                        eff_mn = eff_inst_name
                        for tdmn_el in sspc_el.iter():
                            if _strip_ns(tdmn_el.tag) == "tdmn" and tdmn_el.get("bdata"):
                                candidate = (
                                    bytes.fromhex(tdmn_el.get("bdata", ""))
                                    .decode("utf-8", errors="replace")
                                    .rstrip("\x00")
                                )
                                if candidate and not candidate.endswith("-0000") and candidate != "ADBE Group End":
                                    eff_mn = candidate.split("-")[0]
                                    break
                        c_info = classify_effect(eff_mn, eff_inst_name)
                        layer_effects.append(
                            EffectInstanceSchema(
                                index=eff_counter,
                                name=eff_inst_name,
                                match_name=eff_mn,
                                display_name=c_info.display_name,
                                enabled=True,
                                is_third_party=c_info.is_third_party,
                                plugin_vendor=c_info.plugin_vendor,
                                plugin_package=c_info.plugin_package,
                                category=c_info.category,
                                status=DataAvailabilityStatus.OBSERVED,
                            )
                        )
                        if eff_mn not in plugin_map:
                            plugin_map[eff_mn] = PluginInventoryItemSchema(
                                match_name=eff_mn,
                                display_name=c_info.display_name,
                                plugin_vendor=c_info.plugin_vendor,
                                plugin_package=c_info.plugin_package,
                                category=c_info.category,
                                is_third_party=c_info.is_third_party,
                                is_builtin=c_info.is_builtin,
                                occurrences_count=0,
                                status=DataAvailabilityStatus.OBSERVED,
                            )
                        plugin_map[eff_mn].occurrences_count += 1
                        if item_name not in plugin_map[eff_mn].used_in_compositions:
                            plugin_map[eff_mn].used_in_compositions.append(item_name)

                layers_list.append(
                    LayerSchema(
                        index=layr_idx,
                        name=l_name,
                        layer_type="AVLayer",
                        effects=layer_effects,
                        status=DataAvailabilityStatus.OBSERVED,
                    )
                )

            compositions.append(
                CompositionSchema(
                    item_id=item_id,
                    name=item_name,
                    width=width,
                    height=height,
                    frame_rate=fps,
                    duration=duration,
                    layers_count=len(layers_list),
                    layers=layers_list,
                    field_status=comp_field_status,
                )
            )
        elif pin_el is not None:
            f_ref = next((c for c in pin_el.iter() if _strip_ns(c.tag) == "fileReference"), None)
            fpath = f_ref.get("fullpath") if f_ref is not None else None
            exists_disk = Path(fpath).exists() if fpath else None
            is_miss = exists_disk is False
            dep = FootageDependencySchema(
                item_id=item_id,
                name=item_name,
                asset_type="file" if fpath else "solid",
                file_path=fpath,
                exists_on_disk=exists_disk,
                is_missing=is_miss,
            )
            dependencies.append(dep)
            if is_miss:
                missing_assets.append(dep)

    metadata = ProjectMetadataSchema(
        file_path=str(project_path.resolve()),
        file_name=project_path.name,
        file_format="aepx",
        file_size_bytes=size_bytes,
        sha256=sha256_hex,
        total_items=len(compositions) + len(dependencies),
        total_compositions=len(compositions),
        total_footage_items=len(dependencies),
        field_status={
            "compositions": DataAvailabilityStatus.OBSERVED,
            "layers": DataAvailabilityStatus.OBSERVED,
            "effect_stack": DataAvailabilityStatus.OBSERVED,
        },
    )

    return ProjectAnalysisResult(
        analysis_id=analysis_id,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        extraction_method="offline_aepx",
        live_bridge_tested=False,
        live_bridge_status_note="Parsed via direct XML DOM fallback for .aepx",
        rerun_command=rerun_command,
        metadata=metadata,
        compositions=compositions,
        composition_hierarchy=comp_hierarchy,
        plugin_inventory=list(plugin_map.values()),
        dependencies=dependencies,
        missing_assets=missing_assets,
        missing_effects=[
            f"{p.display_name} ({p.match_name})" for p in plugin_map.values() if p.is_third_party
        ],
        expressions_inventory=expressions_inventory,
        warnings=[
            AnalysisWarning(
                code="AEPX_DOM_FALLBACK_USED",
                message=(
                    f"Full RIFX binary synthesis reported '{transcode_error}'; "
                    "extracted structure via direct XML DOM fallback."
                ),
                status=DataAvailabilityStatus.OBSERVED,
            )
        ],
        unsupported_fields=unsupported_fields,
        raw_summary={"xml_root_tag": root.tag, "fallback_mode": True},
    )


def parse_aepx_project(
    project_path: Path,
    analysis_id: str,
    rerun_command: str,
) -> ProjectAnalysisResult:
    """Parse an After Effects XML `.aepx` project file."""
    _, size_bytes, sha256_hex = validate_project_file_safety(project_path)
    with readonly_file_guard(project_path):
        xml_text = project_path.read_text(encoding="utf-8", errors="replace")

    try:
        rifx_bytes = aepx_xml_to_rifx_bytes(xml_text)
        return parse_aep_with_py_aep(
            project_path=project_path,
            analysis_id=analysis_id,
            rerun_command=rerun_command,
            rifx_bytes_override=rifx_bytes,
            file_format_override="aepx",
        )
    except ET.ParseError as exc:
        raise ValueError(f"Malformed XML in .aepx file '{project_path.name}': {exc}") from exc
    except Exception as exc:
        logger.info("AEPX-to-RIFX transcode encountered '%s'; falling back to direct XML DOM parser", exc)
        return _parse_aepx_dom_fallback(
            project_path=project_path,
            xml_text=xml_text,
            size_bytes=size_bytes,
            sha256_hex=sha256_hex,
            analysis_id=analysis_id,
            rerun_command=rerun_command,
            transcode_error=str(exc),
        )
