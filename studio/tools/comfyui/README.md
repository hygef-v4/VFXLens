# Local ComfyUI

`source.json` pins the reviewed official source. `requirements.in` is its upstream requirement list; `requirements.lock` freezes the installed Windows environment, including GPU PyTorch from the official CUDA 13.0 index. Keep this environment separate from the analyzer and speech tools.

From the repository root, choose a tools directory on a drive with sufficient free space:

```powershell
$ToolsRoot = $env:VFXLENS_TOOLS_ROOT
if (-not $ToolsRoot) { throw 'Set VFXLENS_TOOLS_ROOT to your tools directory first.' }
git clone https://github.com/Comfy-Org/ComfyUI.git "$ToolsRoot/sources/ComfyUI"
git -C "$ToolsRoot/sources/ComfyUI" checkout c844cb672186f187bf9455e2808821417a10d296
uv venv --python 3.12 "$ToolsRoot/envs/comfyui"
uv pip sync --python "$ToolsRoot/envs/comfyui/Scripts/python.exe" studio/tools/comfyui/requirements.lock --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match
./studio/tools/comfyui/run.ps1 -ToolsRoot $ToolsRoot
& "$ToolsRoot/envs/comfyui/Scripts/python.exe" studio/tools/comfyui/check.py $ToolsRoot
```

The launcher binds to `127.0.0.1:8188`, blocks frontend internet access and paid partner nodes, disables custom nodes and browser auto-launch, and leaves the optional manager disabled. Stop with Ctrl+C before running the check. Outputs default to `local/productions/comfyui/exports/`; use an episode workspace for actual production. The source clone is disposable application code.

No generation checkpoints are included. Startup/API and CUDA tensor checks establish application readiness, not model compatibility, generation quality or fit within 8 GB VRAM. Actual machine paths and observed checks are recorded in ignored `local/setup/ai-apps-status.json`.

Sources: [official installation](https://github.com/Comfy-Org/ComfyUI#manual-install-windows-linux), [PyTorch wheels](https://download.pytorch.org/whl/cu130).
