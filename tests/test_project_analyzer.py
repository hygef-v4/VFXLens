"""Unit and integration tests for After Effects Project Analyzer (.aep / .aepx / .aex refusal)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vfx_engine.core.safety import (
    FileIntegrityViolationError,
    UnsafeFileError,
    compute_sha256,
    readonly_file_guard,
)
from vfx_engine.project_analyzer.ae_bridge.bridge_client import AfterEffectsReadOnlyBridge
from vfx_engine.project_analyzer.analyzer import analyze_ae_project
from vfx_engine.project_analyzer.effect_extractor.plugin_registry import classify_effect
from vfx_engine.project_analyzer.normalizer.comparator import compare_offline_and_live
from vfx_engine.reports.project_reporter import write_project_reports


def test_plugin_registry_classifies_third_party_and_builtin_accurately() -> None:
    """Verify Sapphire, Deep Glow, BCC, Trapcode, Element 3D, Twixtor, and built-in AE matchNames."""
    s_shake = classify_effect("S_Shake", "S_Shake")
    assert s_shake.is_third_party is True
    assert "Sapphire" in s_shake.plugin_package

    s_glow = classify_effect("S_Glow", "S_Glow")
    assert s_glow.is_third_party is True
    assert "Sapphire" in s_glow.plugin_package

    s_blur = classify_effect("S_BlurMoCurves", "S_BlurMoCurves")
    assert s_blur.is_third_party is True
    assert "Sapphire" in s_blur.plugin_package

    deep_glow = classify_effect("Deep Glow", "Deep Glow")
    assert deep_glow.is_third_party is True
    assert "Deep Glow" in deep_glow.plugin_package

    bcc = classify_effect("BCC+Glow", "BCC+ Glow")
    assert bcc.is_third_party is True
    assert "Continuum" in bcc.plugin_package

    particular = classify_effect("RG Trapcode Particular", "Particular")
    assert particular.is_third_party is True
    assert "Trapcode" in particular.plugin_package

    e3d = classify_effect("VIDEOCOPILOT 3DArray", "Element")
    assert e3d.is_third_party is True
    assert "Element 3D" in e3d.plugin_package

    twixtor = classify_effect("RE:Vision Twixtor", "Twixtor")
    assert twixtor.is_third_party is True
    assert "Twixtor" in twixtor.plugin_package

    builtin_glow = classify_effect("ADBE Glo2", "Glow")
    assert builtin_glow.is_third_party is False
    assert builtin_glow.is_builtin is True


def test_refuses_aex_binary_plugin_as_project(fake_aex_plugin_path: Path) -> None:
    """Ensure `.aex` Windows binary plugins are strictly rejected with UnsafeFileError."""
    with pytest.raises(UnsafeFileError, match=r"\.aex.*binary plug-in"):
        analyze_ae_project(fake_aex_plugin_path)


def test_corrupted_aep_handled_cleanly(corrupted_aep_path: Path) -> None:
    """Ensure corrupted/non-RIFX `.aep` files raise a clean error without crashing uncontrollably."""
    with pytest.raises(Exception):
        analyze_ae_project(corrupted_aep_path)


def test_analyze_real_ae2026_complete_aep(
    real_ae2026_complete_aep: Path,
    tmp_path: Path,
) -> None:
    """Verify full offline extraction on authentic AE 2026 `complete.aep` without modifying source."""
    before_sha = compute_sha256(real_ae2026_complete_aep)
    result = analyze_ae_project(real_ae2026_complete_aep)
    after_sha = compute_sha256(real_ae2026_complete_aep)

    assert before_sha == after_sha, "Source .aep file must never be modified!"
    assert result.metadata.file_format == "aep"
    assert result.metadata.ae_version is not None
    assert "26.0" in result.metadata.ae_version
    assert result.metadata.total_compositions == 6
    assert result.metadata.total_precompositions >= 1
    assert result.live_bridge_tested is False

    # Locate Main_Comp
    main_comp = next((c for c in result.compositions if c.name == "Main_Comp"), None)
    assert main_comp is not None
    assert main_comp.layers_count == 27

    # Verify Effect_Demo layer has ordered effect stack with parameters
    eff_layer = next((lyr for lyr in main_comp.layers if lyr.name == "Effect_Demo"), None)
    assert eff_layer is not None
    assert len(eff_layer.effects) == 7
    assert [e.index for e in eff_layer.effects] == [1, 2, 3, 4, 5, 6, 7]
    assert eff_layer.effects[0].parameters_count > 0

    # Verify expressions, keyframes, masks, track mattes, cameras, lights, text, shapes
    assert len(result.expressions_inventory) >= 4
    masked_layer = next((lyr for lyr in main_comp.layers if lyr.name == "Masked_Layer"), None)
    assert masked_layer is not None and len(masked_layer.masks) >= 1

    tm_layer = next((lyr for lyr in main_comp.layers if lyr.name == "TrackMatte_Target"), None)
    assert tm_layer is not None and tm_layer.has_track_matte is True

    # Write JSON and Markdown reports
    json_path, md_path = write_project_reports(result, tmp_path / "out_ae2026")
    assert json_path.exists()
    assert md_path.exists()


def test_analyze_complex_third_party_vfx_aep_and_aepx(
    complex_vfx_aep_and_aepx: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    """Verify both `.aep` and `.aepx` extraction on a complex VFX stack (S_Shake, S_Glow, S_BlurMoCurves, Deep Glow, RGB Split, Particular, Element 3D)."""
    aep_path, aepx_path = complex_vfx_aep_and_aepx

    res_aep = analyze_ae_project(aep_path)
    res_aepx = analyze_ae_project(aepx_path)

    assert res_aep.metadata.file_format == "aep"
    assert res_aepx.metadata.file_format == "aepx"
    assert res_aep.metadata.total_compositions == res_aepx.metadata.total_compositions == 6

    expected_match_names = {
        "S_Shake",
        "S_Glow",
        "S_BlurMoCurves",
        "Deep Glow",
        "ADBE Shift Channels",
        "RG Trapcode Particular",
        "VIDEOCOPILOT 3DArray",
    }

    aep_plugins = {p.match_name: p for p in res_aep.plugin_inventory}
    aepx_plugins = {p.match_name: p for p in res_aepx.plugin_inventory}

    assert expected_match_names.issubset(set(aep_plugins.keys()))
    assert expected_match_names.issubset(set(aepx_plugins.keys()))

    # Verify third-party classification in plugin inventory
    assert aep_plugins["S_Shake"].is_third_party is True
    assert aep_plugins["S_Glow"].is_third_party is True
    assert aep_plugins["S_BlurMoCurves"].is_third_party is True
    assert aep_plugins["Deep Glow"].is_third_party is True
    assert aep_plugins["RG Trapcode Particular"].is_third_party is True
    assert aep_plugins["VIDEOCOPILOT 3DArray"].is_third_party is True

    # Verify ordered effect stack on Effect_Demo layer
    main_comp = next(c for c in res_aep.compositions if c.name == "Main_Comp")
    eff_layer = next(lyr for lyr in main_comp.layers if lyr.name == "Effect_Demo")
    stack_match_names = [e.match_name for e in eff_layer.effects]
    assert stack_match_names == [
        "S_Shake",
        "S_Glow",
        "S_BlurMoCurves",
        "Deep Glow",
        "ADBE Shift Channels",
        "RG Trapcode Particular",
        "VIDEOCOPILOT 3DArray",
    ]
    # Verify parameters are extracted inside each third-party plugin instance
    for eff in eff_layer.effects:
        assert eff.parameters_count > 0
        assert len(eff.parameters) == eff.parameters_count

    write_project_reports(res_aep, tmp_path / "complex_aep")
    write_project_reports(res_aepx, tmp_path / "complex_aepx")


def test_readonly_bridge_blocks_forbidden_mutation_scripts() -> None:
    """Verify that the AE bridge strictly blocks any ExtendScript containing write/save/modify calls."""
    bridge = AfterEffectsReadOnlyBridge()
    with pytest.raises(PermissionError, match="Forbidden write/mutation"):
        bridge.validate_script_is_readonly("app.project.save(new File('hack.aep'));")
    with pytest.raises(PermissionError, match="Forbidden write/mutation"):
        bridge.validate_script_is_readonly("layer.property('Opacity').setValue(50);")


def test_offline_and_live_comparator(real_ae2026_complete_aep: Path) -> None:
    """Verify `compare_offline_and_live` detects matches, value mismatches, and runtime expression values."""
    offline_res = analyze_ae_project(real_ae2026_complete_aep)
    mock_live_payload = {
        "compositions": [
            {
                "name": "Main_Comp",
                "width": 1920,
                "height": 1080,
                "frameRate": 30.0,
                "duration": 10.0,
                "layersCount": 27,
                "layers": [
                    {
                        "index": 2,
                        "name": "Effect_Demo",
                        "effects": [
                            {"index": 1, "name": "Gaussian Blur", "matchName": "ADBE Gaussian Blur 2"}
                        ],
                    }
                ],
            }
        ]
    }
    diffs = compare_offline_and_live(offline_res, mock_live_payload)
    assert len(diffs) > 0
    assert any(d.comparison_result in ("matched", "value_mismatch", "only_in_offline") for d in diffs)


def test_aepx_fallback_does_not_fabricate_missing_dimensions_or_timing(tmp_path: Path) -> None:
    """Regression for Task 2: missing AEPX cdta fields must be unavailable/None, never fabricated 1920x1080/30fps/10s."""
    import struct

    from vfx_engine.schemas.common import DataAvailabilityStatus

    # 1. Exact empty <cdta /> case from audit
    empty_cdta_path = tmp_path / "empty_cdta.aepx"
    empty_cdta_path.write_text(
        "<AfterEffectsProject><Item><string>UnknownComp</string><cdta /></Item></AfterEffectsProject>",
        encoding="utf-8",
    )
    res_empty = analyze_ae_project(empty_cdta_path)
    assert len(res_empty.compositions) == 1
    comp = res_empty.compositions[0]
    assert comp.name == "UnknownComp"
    assert comp.width is None
    assert comp.height is None
    assert comp.frame_rate is None
    assert comp.duration is None
    assert comp.field_status.get("width") in (
        DataAvailabilityStatus.UNAVAILABLE,
        DataAvailabilityStatus.UNSUPPORTED,
    )
    assert comp.field_status.get("height") in (
        DataAvailabilityStatus.UNAVAILABLE,
        DataAvailabilityStatus.UNSUPPORTED,
    )
    assert comp.field_status.get("frame_rate") in (
        DataAvailabilityStatus.UNAVAILABLE,
        DataAvailabilityStatus.UNSUPPORTED,
    )
    assert comp.field_status.get("duration") in (
        DataAvailabilityStatus.UNAVAILABLE,
        DataAvailabilityStatus.UNSUPPORTED,
    )
    assert any("UnknownComp" in uf.field_path for uf in res_empty.unsupported_fields)

    # Ensure markdown/json report generation handles None dimensions/timing cleanly without fabricating 1920x1080
    _, md_path = write_project_reports(res_empty, tmp_path / "empty_cdta_report")
    md_text = md_path.read_text(encoding="utf-8")
    assert "1920x1080" not in md_text
    assert "unavailable" in md_text.lower()

    # 2. Partial valid dimension case (144-byte cdta with width=1280, height=720, but no fps bytes and zero duration)
    buf = bytearray(144)
    struct.pack_into(">HH", buf, 140, 1280, 720)
    partial_cdta_path = tmp_path / "partial_cdta.aepx"
    partial_cdta_path.write_text(
        f'<AfterEffectsProject><Item><string>PartialComp</string><cdta bdata="{buf.hex()}" /></Item></AfterEffectsProject>',
        encoding="utf-8",
    )
    res_partial = analyze_ae_project(partial_cdta_path)
    pcomp = res_partial.compositions[0]
    assert pcomp.width == 1280
    assert pcomp.height == 720
    assert pcomp.frame_rate is None
    assert pcomp.duration is None
    assert pcomp.field_status.get("width") == DataAvailabilityStatus.OBSERVED
    assert pcomp.field_status.get("frame_rate") == DataAvailabilityStatus.UNAVAILABLE

    # 3. Malformed XML rejection
    bad_xml_path = tmp_path / "malformed.aepx"
    bad_xml_path.write_text("<AfterEffectsProject><Item><unclosed>", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed XML"):
        analyze_ae_project(bad_xml_path)


def test_live_bridge_requires_matching_project_identity_and_valid_payload(
    real_ae2026_complete_aep: Path,
    complex_vfx_aep_and_aepx: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for Task 3: only a valid live payload whose canonical project identity matches the input may count as hybrid_compared."""
    other_aep, _ = complex_vfx_aep_and_aepx

    monkeypatch.setattr(
        AfterEffectsReadOnlyBridge,
        "is_available",
        lambda self: (True, "Mocked live AE bridge online"),
    )

    # Case 1: Different project open in AE -> must NOT mark live_bridge_tested=True or hybrid_compared
    monkeypatch.setattr(
        AfterEffectsReadOnlyBridge,
        "fetch_live_project_state",
        lambda self: {
            "ok": True,
            "project_file": str(other_aep.resolve()),
            "compositions": [{"name": "Main_Comp", "width": 1920, "height": 1080, "layers": []}],
        },
    )
    res_mismatch = analyze_ae_project(real_ae2026_complete_aep, use_ae_bridge=True)
    assert res_mismatch.live_bridge_tested is False
    assert res_mismatch.extraction_method == "offline_py_aep"
    assert res_mismatch.comparison_with_live is None
    assert any("MISMATCH" in w.code for w in res_mismatch.warnings)

    # Case 2: Missing project identity in live payload -> must NOT mark live_bridge_tested=True
    monkeypatch.setattr(
        AfterEffectsReadOnlyBridge,
        "fetch_live_project_state",
        lambda self: {
            "ok": True,
            "compositions": [{"name": "Main_Comp", "width": 1920, "height": 1080, "layers": []}],
        },
    )
    res_missing_id = analyze_ae_project(real_ae2026_complete_aep, use_ae_bridge=True)
    assert res_missing_id.live_bridge_tested is False
    assert res_missing_id.extraction_method == "offline_py_aep"
    assert res_missing_id.comparison_with_live is None
    assert any("IDENTITY" in w.code for w in res_missing_id.warnings)

    # Case 3: Unsuccessful / malformed live payload -> must NOT mark live_bridge_tested=True
    monkeypatch.setattr(
        AfterEffectsReadOnlyBridge,
        "fetch_live_project_state",
        lambda self: {"ok": False, "error": "No project open in After Effects"},
    )
    res_bad_payload = analyze_ae_project(real_ae2026_complete_aep, use_ae_bridge=True)
    assert res_bad_payload.live_bridge_tested is False
    assert res_bad_payload.extraction_method == "offline_py_aep"
    assert res_bad_payload.comparison_with_live is None
    assert any("INVALID" in w.code or "FAILED" in w.code for w in res_bad_payload.warnings)

    # Case 4: Matching canonical project identity and valid payload -> succeeds with hybrid_compared
    monkeypatch.setattr(
        AfterEffectsReadOnlyBridge,
        "fetch_live_project_state",
        lambda self: {
            "ok": True,
            "project_file": str(real_ae2026_complete_aep.resolve()),
            "compositions": [{"name": "Main_Comp", "width": 1920, "height": 1080, "layers": []}],
        },
    )
    res_match = analyze_ae_project(real_ae2026_complete_aep, use_ae_bridge=True)
    assert res_match.live_bridge_tested is True
    assert res_match.extraction_method == "hybrid_compared"
    assert res_match.comparison_with_live is not None
    assert len(res_match.comparison_with_live) > 0


def test_readonly_file_guard_verifies_integrity_even_on_exception(tmp_path: Path) -> None:
    """Regression for Task 6: readonly_file_guard must verify source file integrity on both normal and exceptional exits."""
    # 1. Unchanged success
    f1 = tmp_path / "unchanged_ok.aep"
    f1.write_bytes(b"ORIGINAL_AEP_BYTES_1")
    with readonly_file_guard(f1) as digest:
        assert digest == compute_sha256(f1)

    # 2. Changed on normal exit -> FileIntegrityViolationError
    f2 = tmp_path / "mutated_ok.aep"
    f2.write_bytes(b"ORIGINAL_AEP_BYTES_2")
    with pytest.raises(FileIntegrityViolationError):
        with readonly_file_guard(f2):
            f2.write_bytes(b"MUTATED_AEP_BYTES_2")

    # 3. Unchanged on parser error -> original exception propagates
    f3 = tmp_path / "unchanged_err.aep"
    f3.write_bytes(b"ORIGINAL_AEP_BYTES_3")
    with pytest.raises(RuntimeError, match="Simulated parser crash"):
        with readonly_file_guard(f3):
            raise RuntimeError("Simulated parser crash")

    # 4. Mutated AND parser raises -> FileIntegrityViolationError raised with original exception as __cause__
    f4 = tmp_path / "mutated_and_err.aep"
    f4.write_bytes(b"ORIGINAL_AEP_BYTES_4")
    with pytest.raises(FileIntegrityViolationError) as exc_info:
        with readonly_file_guard(f4):
            f4.write_bytes(b"CORRUPTED_DURING_EXCEPTION")
            raise ValueError("Parser failed after mutating file")
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "Parser failed after mutating file" in str(exc_info.value.__cause__)

    # 5. Deleted AND parser raises -> FileIntegrityViolationError raised with original exception as __cause__
    f5 = tmp_path / "deleted_and_err.aep"
    f5.write_bytes(b"ORIGINAL_AEP_BYTES_5")
    with pytest.raises(FileIntegrityViolationError) as del_exc_info:
        with readonly_file_guard(f5):
            f5.unlink()
            raise RuntimeError("Parser failed after deleting file")
    assert isinstance(del_exc_info.value.__cause__, RuntimeError)


def test_missing_reference_sample_skips_with_actionable_setup_instructions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for Task 7: missing optional external reference sample must skip cleanly with setup instructions instead of raw AssertionError."""
    import conftest

    missing_sample = tmp_path / "nonexistent_refs" / "py-aep" / "samples" / "versions" / "ae2026" / "complete.aep"
    monkeypatch.setenv("VFX_AE2026_SAMPLE_PATH", str(missing_sample))

    with pytest.raises(pytest.skip.Exception) as skip_info:
        conftest.resolve_ae2026_reference_sample()
    assert "git clone https://github.com/forticheprod/py-aep.git" in str(skip_info.value)


def test_aepx_integrity_failure_never_falls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for Follow-up Task 1: FileIntegrityViolationError during .aepx parsing must propagate and never trigger DOM fallback."""
    from vfx_engine.project_analyzer.parsers import aepx_parser

    disposable_aepx = tmp_path / "integrity_violation.aepx"
    disposable_aepx.write_text(
        '<AfterEffectsProject><Item><string>CompA</string><cdta bdata="00" /></Item></AfterEffectsProject>',
        encoding="utf-8",
    )

    fallback_called = False
    orig_fallback = aepx_parser._parse_aepx_dom_fallback

    def spy_fallback(*args: object, **kwargs: object) -> object:
        nonlocal fallback_called
        fallback_called = True
        return orig_fallback(*args, **kwargs)  # type: ignore[arg-type]

    def mutating_binary_parser(*args: object, **kwargs: object) -> object:
        disposable_aepx.write_text("<AfterEffectsProject>MUTATED</AfterEffectsProject>", encoding="utf-8")
        raise FileIntegrityViolationError(f"CRITICAL: Read-only integrity check failed for {disposable_aepx}!")

    monkeypatch.setattr(aepx_parser, "_parse_aepx_dom_fallback", spy_fallback)
    monkeypatch.setattr(aepx_parser, "parse_aep_with_py_aep", mutating_binary_parser)

    with pytest.raises(FileIntegrityViolationError, match="Read-only integrity check failed"):
        analyze_ae_project(disposable_aepx)

    assert fallback_called is False





