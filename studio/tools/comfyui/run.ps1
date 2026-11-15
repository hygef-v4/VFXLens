param([Parameter(Mandatory)][string]$ToolsRoot)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:DO_NOT_TRACK = '1'
& (Join-Path $ToolsRoot 'envs/comfyui/Scripts/python.exe') (Join-Path $ToolsRoot 'sources/ComfyUI/main.py') --listen 127.0.0.1 --offline --disable-all-custom-nodes --disable-auto-launch --disable-product-tips --output-directory (Join-Path $PSScriptRoot '../../../local/productions/comfyui/exports')
exit $LASTEXITCODE
