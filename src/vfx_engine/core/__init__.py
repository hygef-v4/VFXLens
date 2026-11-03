"""Core utilities for VFX Learning Engine."""

from .config import EngineConfig, discover_after_effects_installations
from .doctor import run_environment_doctor
from .logging import console, get_logger, setup_logging
from .safety import (
    FileIntegrityViolationError,
    UnsafeFileError,
    compute_sha256,
    readonly_file_guard,
    temporary_project_snapshot,
    validate_project_file_safety,
)

__all__ = [
    "EngineConfig",
    "discover_after_effects_installations",
    "run_environment_doctor",
    "console",
    "get_logger",
    "setup_logging",
    "FileIntegrityViolationError",
    "UnsafeFileError",
    "compute_sha256",
    "readonly_file_guard",
    "temporary_project_snapshot",
    "validate_project_file_safety",
]
