"""VFX Learning Engine — Phase 1 (After Effects Project Analyzer & Video VFX Analyzer)."""

from __future__ import annotations

import os

# Bound default OpenBLAS/OMP/OpenCV thread pools on Windows so multi-process CLI/test invocations
# do not exhaust VirtualAlloc commit limits on high-core-count CPUs.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENCV_FFMPEG_THREADS", "2")

try:
    import cv2

    cv2.setNumThreads(2)
except Exception:
    pass

__version__ = "0.1.0"
