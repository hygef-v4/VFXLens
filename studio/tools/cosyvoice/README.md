# Local CosyVoice

`source.json` pins the official source and Matcha-TTS submodule. `requirements.in` preserves upstream requirements. Keep its Python 3.11 environment separate: upstream pins legacy PyTorch 2.3.1, NumPy 1.26.4 and Transformers 4.51.3. `setuptools<81` retains the `pkg_resources` API required by `pyworld`; `build-constraints.txt` also retains it while building the old Whisper release.

From the repository root, choose a tools directory on a drive with sufficient free space:

```powershell
$ToolsRoot = $env:VFXLENS_TOOLS_ROOT
if (-not $ToolsRoot) { throw 'Set VFXLENS_TOOLS_ROOT to your tools directory first.' }
git clone --recursive https://github.com/QwenAudio/CosyVoice.git "$ToolsRoot/sources/CosyVoice"
git -C "$ToolsRoot/sources/CosyVoice" checkout 074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc
git -C "$ToolsRoot/sources/CosyVoice" submodule update --init --recursive
uv venv --python 3.11 "$ToolsRoot/envs/cosyvoice"
uv pip sync --python "$ToolsRoot/envs/cosyvoice/Scripts/python.exe" studio/tools/cosyvoice/requirements.lock --extra-index-url https://download.pytorch.org/whl/cu121 --index-strategy unsafe-best-match --build-constraints studio/tools/cosyvoice/build-constraints.txt
$env:PYTHONUTF8 = '1'
$env:HF_HUB_OFFLINE = '1'
$env:GRADIO_ANALYTICS_ENABLED = 'False'
& "$ToolsRoot/envs/cosyvoice/Scripts/python.exe" "$ToolsRoot/sources/CosyVoice/webui.py" --help
& "$ToolsRoot/envs/cosyvoice/Scripts/python.exe" studio/tools/cosyvoice/check.py $ToolsRoot
```

Windows source builds such as pyworld need Microsoft C++ Build Tools. The checked installation uses the CPU ONNX Runtime selected by upstream for Windows; TensorRT, vLLM and DeepSpeed acceleration are Linux-specific options and are not part of this environment.

No model weights or voice samples are included. Core imports/CLI help do not establish speech synthesis quality. Choose an explicitly authorized local model and supported language before narration work. The upstream web UI hardcodes `0.0.0.0`; it was not started during setup. Use a localhost binding before enabling that UI. Actual checks and any platform limitations are recorded in ignored `local/setup/ai-apps-status.json`.

Source: [official installation and model requirements](https://github.com/QwenAudio/CosyVoice#install).
