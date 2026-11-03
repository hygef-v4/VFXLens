"""Unit and integration tests for After Effects Project Analyzer (.aep / .aepx / .aex refusal)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vfx_engine.core.safety import UnsafeFileError, compute_sha256
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
