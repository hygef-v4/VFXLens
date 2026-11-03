"""Pytest fixtures for VFX Learning Engine — Phase 1 (Project & Video Analyzers)."""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
import pytest

from vfx_engine.project_analyzer.parsers.aepx_parser import (
    aepx_xml_to_rifx_bytes,
    rifx_bytes_to_aepx_xml,
)


def _patch_xml_with_third_party_vfx_plugins(xml_text: str) -> str:
    """Replace built-in demo effect matchNames in AE2026 complete.aep XML with third-party VFX plugins."""
    root = ET.fromstring(xml_text)

    replacements = {
        "ADBE Gaussian Blur 2": ("S_Shake", "S_Shake"),
        "ADBE Drop Shadow": ("S_Glow", "S_Glow"),
        "ADBE Fill": ("S_BlurMoCurves", "S_BlurMoCurves"),
        "ADBE Glo2": ("Deep Glow", "Deep Glow"),
        "ADBE HUE SATURATION": ("ADBE Shift Channels", "RGB Split (Shift Channels)"),
        "ADBE Tint": ("RG Trapcode Particular", "Trapcode Particular"),
        "ADBE Exposure2": ("VIDEOCOPILOT 3DArray", "Element 3D"),
    }

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        if tag == "tdmn" and elem.get("bdata"):
            raw = bytes.fromhex(elem.get("bdata", ""))
            txt = raw.decode("latin1", errors="replace").rstrip("\x00")
            for old_mn, (new_mn, _) in replacements.items():
                if txt == old_mn:
                    new_bytes = new_mn.encode("latin1") + b"\x00"
                    elem.set("bdata", new_bytes.hex())
                    break
                elif txt.startswith(old_mn + "-"):
                    suffix = txt[len(old_mn) :]
                    new_bytes = (new_mn + suffix).encode("latin1") + b"\x00"
                    elem.set("bdata", new_bytes.hex())
                    break
        elif tag == "string" and elem.text:
            val = elem.text
            for old_mn, (_, new_label) in replacements.items():
                if val in ("Gaussian Blur", "Drop Shadow", "Fill", "Glow", "Hue/Saturation", "Tint", "Exposure"):
                    label_map = {
                        "Gaussian Blur": "S_Shake",
                        "Drop Shadow": "S_Glow",
                        "Fill": "S_BlurMoCurves",
                        "Glow": "Deep Glow",
                        "Hue/Saturation": "RGB Split (Shift Channels)",
                        "Tint": "Trapcode Particular",
                        "Exposure": "Element 3D",
                    }
                    if val in label_map:
                        elem.text = label_map[val]
                        break

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a session-scoped directory containing generated .aep, .aepx, .aex, and .mp4 fixtures."""
    d = tmp_path_factory.mktemp("vfx_fixtures")
    return d


@pytest.fixture(scope="session")
def real_ae2026_complete_aep() -> Path:
    """Path to the authentic AE 2026 `complete.aep` sample from `references/py-aep`."""
    p = Path(__file__).resolve().parents[1] / "references" / "py-aep" / "samples" / "versions" / "ae2026" / "complete.aep"
    assert p.exists(), f"Missing sample file: {p}"
    return p


@pytest.fixture(scope="session")
def complex_vfx_aep_and_aepx(
    fixtures_dir: Path,
    real_ae2026_complete_aep: Path,
) -> tuple[Path, Path]:
    """Generate both binary `.aep` and XML `.aepx` files containing third-party VFX plugin stacks."""
    raw_bytes = real_ae2026_complete_aep.read_bytes()
    base_xml = rifx_bytes_to_aepx_xml(raw_bytes)
    patched_xml = _patch_xml_with_third_party_vfx_plugins(base_xml)
    patched_rifx = aepx_xml_to_rifx_bytes(patched_xml)

    aep_path = fixtures_dir / "vfx_showcase_complex.aep"
    aepx_path = fixtures_dir / "vfx_showcase_complex.aepx"

    aep_path.write_bytes(patched_rifx)
    aepx_path.write_text(patched_xml, encoding="utf-8")
    return aep_path, aepx_path


@pytest.fixture(scope="session")
def fake_aex_plugin_path(fixtures_dir: Path) -> Path:
    """Create a dummy `.aex` file to test that the engine refuses to execute or parse binary plugins."""
    p = fixtures_dir / "Sapphire_S_Shake.aex"
    p.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00UNTRUSTED_WINDOWS_AEX_BINARY_PLUGIN")
    return p


@pytest.fixture(scope="session")
def corrupted_aep_path(fixtures_dir: Path) -> Path:
    """Create a corrupted/invalid `.aep` file to test graceful error handling."""
    p = fixtures_dir / "corrupted_project.aep"
    p.write_bytes(b"NOT_A_VALID_RIFX_HEADER_1234567890")
    return p


def _draw_textured_grid(w: int, h: int, offset_x: float = 0.0, offset_y: float = 0.0, hue_shift: int = 0) -> np.ndarray:
    """Create a rich textured geometric background for accurate optical flow and edge tracking."""
    img = np.full((h, w, 3), 28, dtype=np.uint8)
    step = 48
    ox = int(round(offset_x))
    oy = int(round(offset_y))

    for x in range(-step, w + step, step):
        cx = x + (ox % step)
        cv2.line(img, (cx, 0), (cx, h), (70, 95, 130), 2)
    for y in range(-step, h + step, step):
        cy = y + (oy % step)
        cv2.line(img, (0, cy), (w, cy), (85, 70, 120), 2)

    # Central geometric rings and diagonal struts
    center = (w // 2 + ox, h // 2 + oy)
    cv2.circle(img, center, 95, (180, 140, 60), 4, cv2.LINE_AA)
    cv2.circle(img, center, 45, (90, 200, 180), -1, cv2.LINE_AA)
    cv2.rectangle(
        img,
        (center[0] - 130, center[1] - 65),
        (center[0] + 130, center[1] + 65),
        (140, 210, 240),
        3,
    )
    if hue_shift != 0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[..., 0] = (hsv[..., 0].astype(np.int32) + hue_shift) % 180
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


@pytest.fixture(scope="session")
def synthetic_fast_vfx_video(fixtures_dir: Path) -> Path:
    """Synthesize a 5.0-second 30fps (150 frames) MP4 video with real visual VFX signatures."""
    w, h, fps, total_frames = 640, 360, 30, 150
    raw_avi = fixtures_dir / "temp_raw.avi"
    final_mp4 = fixtures_dir / "fast_vfx_reel_sample.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(raw_avi), fourcc, float(fps), (w, h))
    rng = np.random.default_rng(42)

    prev_frames_buf: list[np.ndarray] = []

    for f in range(total_frames):
        # Segment 1 (0..29): Camera Shake (oscillatory sign-reversing offsets) + Particles
        if f < 30:
            if 8 <= f <= 22:
                # High-frequency alternating camera shake
                sign = 1.0 if (f % 2 == 0) else -1.0
                dx = sign * 14.0
                dy = -sign * 10.0
            else:
                dx, dy = 0.0, 0.0
            frame = _draw_textured_grid(w, h, dx, dy, hue_shift=0)
            # Add moving bright particle speckles (frames 4..26)
            if 4 <= f <= 26:
                for p_idx in range(28):
                    px = int((p_idx * 73 + f * 11) % (w - 20)) + 10
                    py = int((p_idx * 41 + f * 7) % (h - 20)) + 10
                    cv2.circle(frame, (px, py), 2, (255, 255, 255), -1)

        # Segment 2 (30..33): Hard Cut + White Exposure Flash Frame
        elif f < 34:
            frame = _draw_textured_grid(w, h, 0, 0, hue_shift=55)
            if f in (30, 31):
                frame = np.clip(frame.astype(np.float32) + 215.0, 0, 255).astype(np.uint8)
            elif f == 32:
                frame = np.clip(frame.astype(np.float32) + 120.0, 0, 255).astype(np.uint8)

        # Segment 3 (34..64): Glow / Bloom + RGB Split (Chromatic Aberration)
        elif f < 65:
            frame = np.full((h, w, 3), 18, dtype=np.uint8)
            # Draw bright core shapes
            cv2.circle(frame, (w // 2, h // 2), 42, (255, 255, 255), -1)
            cv2.rectangle(frame, (120, 80), (520, 280), (250, 250, 250), 6)
            # Add wide soft bloom halo around bright core
            halo = cv2.GaussianBlur(frame.astype(np.float32), (45, 45), 14.0)
            frame = np.clip(frame.astype(np.float32) + halo * 0.85, 0, 255).astype(np.uint8)
            # Apply strong RGB channel spatial shift on frames 45..60
            if 45 <= f <= 60:
                b, g, r = cv2.split(frame)
                r_shifted = np.roll(r, 7, axis=1)
                b_shifted = np.roll(b, -7, axis=1)
                frame = cv2.merge([b_shifted, g, r_shifted])

        # Segment 4 (65..84): Zoom Punch Transition + Directional Motion Blur
        elif f < 85:
            base = _draw_textured_grid(w, h, 0, 0, hue_shift=95)
            zoom_factor = 1.0 + max(0, (f - 65)) * 0.055
            zw = int(round(w * zoom_factor))
            zh = int(round(h * zoom_factor))
            resized = cv2.resize(base, (zw, zh), interpolation=cv2.INTER_LINEAR)
            x0 = (zw - w) // 2
            y0 = (zh - h) // 2
            frame = resized[y0 : y0 + h, x0 : x0 + w].copy()
            # Apply strong horizontal directional motion blur on frames 72..82
            if 72 <= f <= 82:
                ksize = 25
                kernel = np.zeros((ksize, ksize), dtype=np.float32)
                kernel[ksize // 2, :] = 1.0 / ksize
                frame = cv2.filter2D(frame, -1, kernel)

        # Segment 5 (85..124): Speed Ramp (slow -> fast burst -> slow) + Motion Trail Echo
        elif f < 125:
            t_local = f - 85
            if t_local < 12:
                pos_x = t_local * 1.2
            elif t_local < 22:
                pos_x = 14.4 + (t_local - 12) * 18.0
            else:
                pos_x = 194.4 + (t_local - 22) * 1.2
            frame = _draw_textured_grid(w, h, pos_x, 0.0, hue_shift=130)
            # Blend lagged frames for echo trail during fast burst
            if 97 <= f <= 107 and len(prev_frames_buf) >= 3:
                frame = cv2.addWeighted(frame, 0.65, prev_frames_buf[-2], 0.35, 0.0)

        # Segment 6 (125..149): Scanline Glitch Distortion + Sharp High-Contrast Graphic Overlay
        else:
            frame = _draw_textured_grid(w, h, (f - 125) * 2.0, 0.0, hue_shift=20)
            if 128 <= f <= 138:
                # Horizontal scanline tear bands
                for band_y in range(40, h - 40, 36):
                    shift = int(rng.choice([-28, -20, 20, 28]))
                    frame[band_y : band_y + 10, :] = np.roll(frame[band_y : band_y + 10, :], shift, axis=1)
            if 139 <= f <= 148:
                # High-contrast sharp kinetic graphic callout
                cv2.putText(
                    frame,
                    "VFX ENGINE",
                    (110, 200),
                    cv2.FONT_HERSHEY_DUPLEX,
                    2.2,
                    (255, 255, 255),
                    5,
                    cv2.LINE_AA,
                )

        prev_frames_buf.append(frame.copy())
        if len(prev_frames_buf) > 5:
            prev_frames_buf.pop(0)
        writer.write(frame)

    writer.release()

    # Encode to H.264 MP4 via FFmpeg
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "quiet",
            "-i",
            str(raw_avi),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "16",
            str(final_mp4),
        ],
        check=True,
    )
    raw_avi.unlink(missing_ok=True)
    return final_mp4


@pytest.fixture(scope="session")
def synthetic_vfr_video(fixtures_dir: Path, synthetic_fast_vfx_video: Path) -> Path:
    """Create a Variable Frame Rate (VFR) video using FFmpeg frame-drop with VFR muxing to test VFR handling."""
    vfr_mp4 = fixtures_dir / "vfr_sample.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "quiet",
            "-i",
            str(synthetic_fast_vfx_video),
            "-vf",
            "select='not(eq(mod(n,4),2))'",
            "-fps_mode",
            "vfr",
            "-t",
            "2.0",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(vfr_mp4),
        ],
        check=True,
    )
    return vfr_mp4
