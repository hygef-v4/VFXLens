"""Check CosyVoice's core imports and CUDA without downloading models."""
import json
import os
from pathlib import Path
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
source = Path(sys.argv[1]).resolve() / "sources/CosyVoice"
assert (source / "webui.py").is_file(), source
sys.path[:0] = [str(source), str(source / "third_party/Matcha-TTS")]

import torch
import torchaudio
import onnxruntime
import pyworld
import wetext
from cosyvoice.cli.cosyvoice import AutoModel, CosyVoice, CosyVoice2, CosyVoice3

assert torch.cuda.is_available(), "CUDA unavailable"
assert (torch.ones(2, device="cuda") + 1).sum().item() == 4
print(json.dumps({"torch": torch.__version__, "torchaudio": torchaudio.__version__,
                  "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(),
                  "onnx_providers": onnxruntime.get_available_providers(),
                  "core_imports": [AutoModel.__name__, CosyVoice.__name__,
                                   CosyVoice2.__name__, CosyVoice3.__name__],
                  "models": "not downloaded"}, indent=2))
