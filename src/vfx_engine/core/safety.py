"""Safety and read-only integrity guards for user files (.aep, .aepx, videos)."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class UnsafeFileError(ValueError):
    """Raised when a file violates safety rules (e.g. .aex binary plugin passed as project)."""


class FileIntegrityViolationError(RuntimeError):
    """Raised if a read-only operation unexpectedly alters a source file."""


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 hex digest of a file without modifying it."""
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        while True:
            block = fp.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def validate_project_file_safety(path: Path, max_size_mb: int = 512) -> tuple[str, int, str]:
    """Validate that a path is a readable .aep or .aepx project and never an .aex plugin.

    Returns:
        Tuple of (file_format, size_bytes, sha256_hex).
    """
    if not path.exists():
        raise FileNotFoundError(f"Project file does not exist: {path}")
    if not path.is_file():
        raise UnsafeFileError(f"Path is not a regular file: {path}")

    suffix = path.suffix.lower()
    if suffix == ".aex":
        raise UnsafeFileError(
            f"Refusing to open '{path.name}': '.aex' is a compiled Windows After Effects binary "
            "plug-in (DLL), NOT an After Effects project (.aep / .aepx). VFX Learning Engine "
            "never loads or executes untrusted binary plug-ins."
        )
    if suffix not in (".aep", ".aepx", ".aet"):
        raise UnsafeFileError(
            f"Unsupported project extension '{suffix}' for '{path.name}'. "
            "Expected '.aep' (binary project) or '.aepx' (XML project)."
        )

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise UnsafeFileError(f"Project file is empty (0 bytes): {path}")
    if size_bytes > max_size_mb * 1024 * 1024:
        raise UnsafeFileError(
            f"Project file exceeds safety limit of {max_size_mb} MB ({size_bytes} bytes): {path}"
        )

    sha256_hex = compute_sha256(path)
    return suffix.lstrip("."), size_bytes, sha256_hex


SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
    ".m4v",
    ".mxf",
    ".ts",
}


def validate_video_input(path: Path, max_size_mb: int = 2048) -> Path:
    """Validate that a video path exists, is a regular file, and is not an executable/plugin."""
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Video file does not exist: {resolved}")
    if not resolved.is_file():
        raise UnsafeFileError(f"Video path is not a regular file: {resolved}")
    suffix = resolved.suffix.lower()
    if suffix in (".aex", ".exe", ".dll", ".bat", ".cmd", ".ps1"):
        raise UnsafeFileError(f"Refusing to open executable/binary file as video: {resolved.name}")
    if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise UnsafeFileError(
            f"Unsupported video extension '{suffix}' for '{resolved.name}'. "
            f"Supported extensions: {sorted(SUPPORTED_VIDEO_EXTENSIONS)}"
        )
    size_bytes = resolved.stat().st_size
    if size_bytes == 0:
        raise UnsafeFileError(f"Video file is empty (0 bytes): {resolved}")
    if size_bytes > max_size_mb * 1024 * 1024:
        raise UnsafeFileError(
            f"Video file exceeds safety size limit of {max_size_mb} MB ({size_bytes} bytes): {resolved}"
        )
    return resolved


@contextmanager
def readonly_file_guard(path: Path) -> Iterator[str]:
    """Context manager that verifies the source file's SHA-256 and size are untouched after read."""
    before_hash = compute_sha256(path)
    before_size = path.stat().st_size
    yield before_hash
    after_hash = compute_sha256(path)
    after_size = path.stat().st_size
    if before_hash != after_hash or before_size != after_size:
        raise FileIntegrityViolationError(
            f"CRITICAL: Read-only integrity check failed for {path}!"
        )


ReadOnlyFileGuard = readonly_file_guard


@contextmanager
def temporary_project_snapshot(source_path: Path) -> Iterator[Path]:
    """Create an isolated temporary copy of a project file for any external/AE bridge inspection.

    Guarantees the original user project is never opened or touched directly by After Effects.
    """
    with tempfile.TemporaryDirectory(prefix="vfx_engine_snapshot_") as tmp_dir:
        snapshot_path = Path(tmp_dir) / f"snapshot_{source_path.name}"
        shutil.copy2(source_path, snapshot_path)
        yield snapshot_path
