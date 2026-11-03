"""Core configuration and environment discovery for VFX Learning Engine."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EngineConfig(BaseModel):
    """Runtime configuration for VFX Learning Engine."""

    workspace_root: Path = Field(default_factory=lambda: Path.cwd())
    outputs_dir: Path = Field(default_factory=lambda: Path.cwd() / "outputs")
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data")
    ae_scripts_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3] / "ae-scripts")
    ffmpeg_bin: str = Field(default_factory=lambda: shutil.which("ffmpeg") or "ffmpeg")
    ffprobe_bin: str = Field(default_factory=lambda: shutil.which("ffprobe") or "ffprobe")
    max_project_size_mb: int = 512
    max_video_duration_sec: float = 600.0
    full_frame_max_duration_sec: float = 20.0
    subprocess_timeout_sec: int = 120
    prefer_gpu: bool = True
    gpu_vram_limit_mb: int = 6144  # Safe ceiling for 8GB RTX 4060
    vision_provider: str = Field(
        default_factory=lambda: os.environ.get("VFX_VISION_PROVIDER", "none").strip().lower()
    )
    vision_model: str = Field(
        default_factory=lambda: os.environ.get("VFX_VISION_MODEL", "").strip()
    )
    vision_base_url: str = Field(
        default_factory=lambda: os.environ.get("VFX_VISION_BASE_URL", "").strip()
    )
    ae_mcp_junkdoge_url: str = Field(
        default_factory=lambda: os.environ.get("AE_MCP_HTTP_URL", "http://127.0.0.1:11488/mcp")
    )
    ae_mcp_solomon_port: int = Field(
        default_factory=lambda: int(os.environ.get("AE_BRIDGE_PORT", "7788"))
    )

    @classmethod
    def from_env(cls) -> EngineConfig:
        """Instantiate configuration populated from environment variables."""
        return cls()


VFXEngineConfig = EngineConfig


def discover_after_effects_installations() -> list[dict[str, Any]]:
    """Discover installed Adobe After Effects versions on Windows (read-only check)."""
    installs: list[dict[str, Any]] = []
    program_files = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    ]
    seen: set[str] = set()
    for base in program_files:
        adobe_dir = Path(base) / "Adobe"
        if not adobe_dir.exists():
            continue
        try:
            for child in sorted(adobe_dir.iterdir(), reverse=True):
                if child.is_dir() and "After Effects" in child.name:
                    support_files = child / "Support Files"
                    afterfx_exe = support_files / "AfterFX.exe"
                    aerender_exe = support_files / "aerender.exe"
                    key = str(child.resolve())
                    if key in seen:
                        continue
                    seen.add(key)
                    installs.append(
                        {
                            "name": child.name,
                            "root_path": str(child),
                            "afterfx_exe": str(afterfx_exe) if afterfx_exe.exists() else None,
                            "aerender_exe": str(aerender_exe) if aerender_exe.exists() else None,
                            "valid": afterfx_exe.exists() or aerender_exe.exists(),
                        }
                    )
        except OSError:
            continue
    return installs
