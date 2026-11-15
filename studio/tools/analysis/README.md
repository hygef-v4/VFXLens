# Analysis and animation extras

This Python 3.12 environment isolates Manim Community, librosa, WhisperX and
[Leonxlnx/earshot](https://github.com/Leonxlnx/earshot) from the root analyzer and
`studio/voice`. Earshot is pinned to its official Git revision: the PyPI package
named `earshot` belongs to a different project. PyTorch, torchaudio and torchvision
use the explicit official CPU wheel index.

From the repository root:

```powershell
$env:PYTHONUTF8 = '1'
$env:VFXLENS_FFMPEG_SHARED_BIN = 'C:\path\to\ffmpeg-shared\bin'
uv sync --locked --directory studio/tools/analysis
uv run --locked --directory studio/tools/analysis python verify.py
uv run --locked --directory studio/tools/analysis manim --help
uv run --locked --directory studio/tools/analysis earshot sfx list
```

On Windows, set `VFXLENS_FFMPEG_SHARED_BIN` to the `bin` folder of a shared FFmpeg
build. `verify.py` adds that directory to this Python process's DLL search path
and decodes a generated WAV with TorchCodec; it does not change the system PATH.
FFmpeg's [download page](https://ffmpeg.org/download.html) links Windows builds,
including [Gyan's shared builds](https://www.gyan.dev/ffmpeg/builds/). The tested
build is [Gyan FFmpeg 7.1.1 full shared](https://github.com/GyanD/codexffmpeg/releases/download/7.1.1/ffmpeg-7.1.1-full_build-shared.zip)
(SHA-256 `9F28727E8B472A04C1D2E520AAA425DCA82721B995139B35710091130EA6E699`).
TorchCodec 0.7 with PyTorch 2.8 supports FFmpeg 4 through 7, so use a matching
shared build.

For WhisperX CLI runs on Windows, register the shared DLL directory before the
module imports TorchCodec. This PowerShell launcher forwards the normal WhisperX
arguments and leaves PATH unchanged:

```powershell
$whisperx = @'
import os, runpy, sys
_ffmpeg_dlls = os.add_dll_directory(os.environ['VFXLENS_FFMPEG_SHARED_BIN'])
sys.argv[0] = 'whisperx'
runpy.run_module('whisperx', run_name='__main__')
'@
uv run --locked --directory studio/tools/analysis python -c $whisperx --help
# Replace --help with the usual WhisperX media and model arguments to transcribe.
```

`verify.py` checks real imports, CPU tensor computation, a known-frequency librosa
signal, TorchCodec WAV decoding, a model-free earshot sound-bank render, an earshot
MCP stdio connection and tool call, WhisperX CLI help, and a Cairo video render
containing Pango text. It asserts decoded animation frames and writes generated
artifacts under `local/setup/analysis-extras-smoke/`. It explicitly disables model
downloads.

For another local MCP client, use this environment's Python executable with
arguments `-m earshot mcp`. Models load lazily. `EARSHOT_OFFLINE=1` prevents
downloads; `earshot sfx` and `earshot kit` work without models. Keep caches and
machine-specific client configuration under ignored `local/` or another local
tools directory. Existing clients need a refresh after server registration.

WhisperX transcription/alignment requires selected model weights. Diarization
also requires agreement to the relevant Hugging Face model terms and a token.
Package installation and CLI help do not verify transcription quality.
Earshot's learned audio descriptions require its model weights; the shipped
sound bank needs none. Optional Gemini audio upload is excluded from this install.
Manim geometry and `Text` work without TeX; `Tex`/`MathTex` require a separate TeX
installation. The setup smoke does not exercise OpenGL or a complete production.

References: [Manim installation](https://docs.manim.community/en/stable/installation/uv.html),
[librosa](https://librosa.org/doc/latest/install.html),
[WhisperX setup](https://github.com/m-bain/whisperX#setup-),
[earshot installation](https://github.com/Leonxlnx/earshot#install),
[TorchCodec installation and compatibility](https://github.com/meta-pytorch/torchcodec#installing-torchcodec).
