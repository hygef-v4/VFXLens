"""Environment diagnostics (`vfx doctor`) for VFX Learning Engine."""

from __future__ import annotations

import importlib.metadata
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import EngineConfig, discover_after_effects_installations


def _run_cmd_probe(args: list[str], timeout: int = 8) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        out = (proc.stdout or proc.stderr or "").strip()
        first_line = out.splitlines()[0] if out else ""
        return proc.returncode == 0, first_line
    except Exception as exc:
        return False, str(exc)


def run_environment_doctor(config: EngineConfig | None = None) -> dict[str, Any]:
    """Inspect Python, FFmpeg/FFprobe, GPU/CUDA, After Effects, MCP bridges, and dependencies."""
    cfg = config or EngineConfig()

    # 1. Python & OS
    python_info = {
        "version": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
        "architecture": platform.machine(),
    }

    # 2. FFmpeg & FFprobe
    ffmpeg_ok, ffmpeg_ver = _run_cmd_probe([cfg.ffmpeg_bin, "-version"])
    ffprobe_ok, ffprobe_ver = _run_cmd_probe([cfg.ffprobe_bin, "-version"])

    # 3. GPU (NVIDIA RTX 4060 8GB check via nvidia-smi)
    gpu_ok, gpu_raw = _run_cmd_probe(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.free,driver_version",
            "--format=csv,noheader",
        ]
    )
    gpu_info: dict[str, Any] = {
        "available": gpu_ok,
        "details": gpu_raw if gpu_ok else "No NVIDIA GPU detected via nvidia-smi (CPU-only mode active)",
        "vram_budget_mb": cfg.gpu_vram_limit_mb,
        "cpu_fallback_ready": True,
    }

    # 4. Python packages
    required_pkgs = [
        "pydantic",
        "typer",
        "rich",
        "numpy",
        "opencv-python-headless",
        "scenedetect",
        "Pillow",
        "py-aep",
        "PyYAML",
        "httpx",
    ]
    packages_status: dict[str, str] = {}
    for pkg in required_pkgs:
        try:
            packages_status[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            # Handle opencv-python vs opencv-python-headless
            if pkg == "opencv-python-headless":
                try:
                    packages_status[pkg] = importlib.metadata.version("opencv-python")
                    continue
                except importlib.metadata.PackageNotFoundError:
                    pass
            packages_status[pkg] = "MISSING"

    # 5. After Effects Installations & CEP Bridges
    ae_installs = discover_after_effects_installations()
    solomon_token_file = Path.home() / ".ae-mcp-bridge.json"

    # Check if MCP servers are currently listening (non-intrusive TCP/HTTP check)
    from ..project_analyzer.ae_bridge.bridge_client import probe_live_ae_bridges

    bridge_status = probe_live_ae_bridges(cfg)

    # 6. Vision Provider Config
    vision_status = {
        "provider": cfg.vision_provider,
        "model": cfg.vision_model or "none",
        "configured": cfg.vision_provider not in ("none", "", "noop"),
        "note": (
            "Vision provider configured"
            if cfg.vision_provider not in ("none", "", "noop")
            else "Defaulting to local Computer Vision only (NoOpVisionAnalyzer)"
        ),
    }

    all_core_ready = (
        ffmpeg_ok
        and ffprobe_ok
        and all(v != "MISSING" for v in packages_status.values())
    )

    return {
        "ready": all_core_ready,
        "python": python_info,
        "ffmpeg": {"available": ffmpeg_ok, "binary": cfg.ffmpeg_bin, "version": ffmpeg_ver},
        "ffprobe": {"available": ffprobe_ok, "binary": cfg.ffprobe_bin, "version": ffprobe_ver},
        "gpu": gpu_info,
        "packages": packages_status,
        "after_effects": {
            "installed_versions": ae_installs,
            "solomon_bridge_token_present": solomon_token_file.exists(),
            "live_bridges": bridge_status,
        },
        "vision": vision_status,
        "paths": {
            "workspace_root": str(cfg.workspace_root),
            "outputs_dir": str(cfg.outputs_dir),
            "ae_scripts_dir": str(cfg.ae_scripts_dir),
        },
    }
