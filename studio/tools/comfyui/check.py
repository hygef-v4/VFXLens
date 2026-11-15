"""Check CUDA and a temporary localhost ComfyUI server without loading models."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import torch

tools_root = Path(sys.argv[1]).resolve()
source = tools_root / "sources/ComfyUI"
assert (source / "main.py").is_file(), source
assert torch.cuda.is_available(), "CUDA unavailable"
assert (torch.ones(2, device="cuda") + 1).sum().item() == 4
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
log_path = Path(__file__).resolve().parents[3] / "local/setup/comfyui-startup.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
with log_path.open("w", encoding="utf-8") as log:
    process = subprocess.Popen(
        [sys.executable, str(source / "main.py"), "--listen", "127.0.0.1",
         "--port", str(port), "--offline", "--disable-all-custom-nodes",
         "--disable-auto-launch", "--disable-product-tips"],
        cwd=source, stdout=log, stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + 180
        while True:
            assert process.poll() is None, f"ComfyUI exited; inspect {log_path}"
            try:
                with urlopen(f"http://127.0.0.1:{port}/system_stats", timeout=2) as response:
                    stats = json.load(response)
                break
            except (URLError, TimeoutError):
                assert time.monotonic() < deadline, f"Startup timeout; inspect {log_path}"
                time.sleep(1)
        with urlopen(f"http://127.0.0.1:{port}/object_info", timeout=30) as response:
            nodes = json.load(response)
        assert "KSampler" in nodes and "CheckpointLoaderSimple" in nodes
        print(json.dumps({"torch": torch.__version__, "cuda": torch.version.cuda,
                          "gpu": torch.cuda.get_device_name(), "nodes": len(nodes),
                          "system_stats": stats}, indent=2))
    finally:
        process.terminate()
        process.wait(timeout=30)
