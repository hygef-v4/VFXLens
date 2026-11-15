"""Offline smoke checks; writes only generated setup artifacts under local/setup."""

import asyncio
import importlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

import av
import librosa
import numpy as np
import soundfile as sf
import torch
from earshot.forge import bank
from manim import BLUE, UP, Circle, Create, Scene, Text, tempconfig
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


class AnalysisSmoke(Scene):
    def construct(self):
        self.add(Text("VFXLens", font_size=48).shift(UP))
        self.play(Create(Circle(radius=0.6, color=BLUE)), run_time=0.5)
        self.wait(0.5)


async def check_mcp():
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "earshot", "mcp"],
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    async with asyncio.timeout(60):
        async with Client(server) as client:
            tools = (await client.list_tools()).tools
            assert "sfx_list" in {tool.name for tool in tools}
            result = await client.call_tool("sfx_list", {"kind": "whoosh"})
            assert not result.is_error, result
            assert "whoosh" in str(result.content)
            return {"transport": "stdio", "tools": len(tools), "sfx_list": "passed"}


def main():
    os.environ.update(EARSHOT_OFFLINE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    ffmpeg_dll_dir = os.getenv("VFXLENS_FFMPEG_SHARED_BIN")
    if os.name == "nt":
        if not ffmpeg_dll_dir or not Path(ffmpeg_dll_dir).is_dir():
            raise RuntimeError("Set VFXLENS_FFMPEG_SHARED_BIN to a shared FFmpeg bin directory")
        _ffmpeg_dlls = os.add_dll_directory(ffmpeg_dll_dir)
    root = Path(__file__).resolve().parents[3]
    output = root / "local/setup/analysis-extras-smoke"
    output.mkdir(parents=True, exist_ok=True)
    packages = (
        "manim",
        "librosa",
        "whisperx",
        "earshot",
        "mcp",
        "torch",
        "torchaudio",
        "torchvision",
        "torchcodec",
    )
    versions = {name: importlib.metadata.version(name) for name in packages}
    for name in (
        "whisperx",
        "whisperx.asr",
        "whisperx.alignment",
        "whisperx.diarize",
        "torchaudio",
        "torchvision",
    ):
        importlib.import_module(name)
    assert torch.version.cuda is None, "Expected the locked CPU PyTorch build"
    assert torch.isfinite(torch.ones(2) @ torch.ones(2))

    sr = 22050
    tone = 0.2 * np.sin(2 * np.pi * 440 * np.arange(sr) / sr)
    spectrum = np.abs(librosa.stft(tone))
    peak_hz = float(librosa.fft_frequencies(sr=sr)[np.argmax(spectrum.mean(axis=1))])
    assert abs(peak_hz - 440) < 12, peak_hz
    assert librosa.feature.melspectrogram(y=tone, sr=sr).shape[0] == 128

    from torchcodec.decoders import AudioDecoder

    codec_sr = 16_000
    codec_tone = 0.25 * np.sin(2 * np.pi * 440 * np.arange(codec_sr) / codec_sr)
    codec_wav = output / "torchcodec-tone.wav"
    sf.write(codec_wav, codec_tone, codec_sr, subtype="PCM_16")
    decoded = AudioDecoder(codec_wav).get_all_samples()
    assert decoded.data.shape[-1] == codec_sr, decoded.data.shape
    assert abs(decoded.data.abs().max().item() - 0.25) < 0.02
    whisperx_entry = """
import os, runpy, sys
if os.name == "nt":
    _ffmpeg_dlls = os.add_dll_directory(os.environ["VFXLENS_FFMPEG_SHARED_BIN"])
sys.argv[0] = "whisperx"
runpy.run_module("whisperx", run_name="__main__")
"""

    sound, meta = bank.render("ui_pop/soft")
    assert np.isfinite(sound).all() and np.max(np.abs(sound)) > 0.01
    sf.write(output / "earshot-pop.wav", sound, meta["sr"], subtype="PCM_24")
    mcp = asyncio.run(check_mcp())
    subprocess.run(
        [sys.executable, "-c", whisperx_entry, "--help"],
        check=True,
        capture_output=True,
    )

    with tempconfig(
        {
            "media_dir": str(output / "manim"),
            "pixel_width": 640,
            "pixel_height": 360,
            "frame_rate": 15,
            "disable_caching": True,
            "output_file": "analysis-smoke",
            "verbosity": "WARNING",
        }
    ):
        scene = AnalysisSmoke()
        scene.render()
        video = Path(scene.renderer.file_writer.movie_file_path)
    with av.open(str(video)) as container:
        frames = [frame.to_ndarray(format="rgb24") for frame in container.decode(video=0)]
    assert len(frames) >= 14 and frames[-1].std() > 10
    assert np.abs(frames[0].astype(float) - frames[-1]).mean() > 0.1
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-ss",
            "0.8",
            "-frames:v",
            "1",
            str(output / "manim-frame.png"),
        ],
        check=True,
        capture_output=True,
    )
    report = {
        "versions": versions,
        "cpu_torch": True,
        "imports": "passed",
        "librosa_tone_peak_hz": peak_hz,
        "torchcodec_wav_frames": decoded.data.shape[-1],
        "torchcodec_wav_sample_rate": decoded.sample_rate,
        "earshot_bank_samples": len(sound),
        "earshot_mcp": mcp,
        "whisperx_cli_help": "passed",
        "manim_video": str(video),
        "manim_decoded_frames": len(frames),
        "models_downloaded": False,
        "paid_calls": False,
    }
    (output / "checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
