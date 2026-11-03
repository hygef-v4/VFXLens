"""Structured logging setup for VFX Learning Engine."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()
log_console = Console(stderr=True)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured Rich logging for the engine."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=log_console,
                rich_tracebacks=True,
                show_path=False,
                markup=True,
            )
        ],
        force=True,
    )
    return logging.getLogger("vfx_engine")


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under `vfx_engine`."""
    return logging.getLogger(f"vfx_engine.{name}")
