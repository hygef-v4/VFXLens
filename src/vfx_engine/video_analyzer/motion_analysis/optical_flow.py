"""Dense Optical Flow and global/local motion decomposition for Video VFX Analyzer."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class OpticalFlowMetrics:
    """Decomposed motion metrics between frame t-1 and frame t."""

    magnitude_mean: float = 0.0
    magnitude_p95: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    scale_rate: float = 0.0
    rotation_deg: float = 0.0
    residual_mean: float = 0.0
    depth_layers_score: float = 0.0


def compute_optical_flow_metrics(
    prev_gray: np.ndarray,
    curr_gray: np.ndarray,
) -> OpticalFlowMetrics:
    """Compute dense Farneback optical flow and decompose into translation, zoom, rotation, and residual."""
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray,
        curr_gray,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0,
    )
    ux = flow[..., 0]
    uy = flow[..., 1]
    mag = np.hypot(ux, uy)

    mag_mean = float(np.mean(mag))
    mag_p95 = float(np.percentile(mag, 95))

    if mag_mean < 1e-4:
        return OpticalFlowMetrics()

    h, w = curr_gray.shape[:2]
    cx = (w - 1) * 0.5
    cy = (h - 1) * 0.5

    # Coordinate grid centered at (cx, cy), normalized by half-diagonal
    half_diag = max(1.0, float(np.hypot(cx, cy)))
    xs = (np.arange(w, dtype=np.float32) - cx)[None, :] / half_diag
    ys = (np.arange(h, dtype=np.float32) - cy)[:, None] / half_diag

    dx = float(np.mean(ux))
    dy = float(np.mean(uy))

    dux = ux - dx
    duy = uy - dy
    r2 = xs * xs + ys * ys
    denom = float(np.sum(r2)) + 1e-6

    # Radial expansion (zoom punch) and rotational velocity
    scale_rate = float(np.sum(xs * dux + ys * duy) / denom) / half_diag
    rot_rad = float(np.sum(xs * duy - ys * dux) / denom) / half_diag
    rot_deg = float(np.degrees(rot_rad))

    # Reconstruct global similarity velocity field to measure non-rigid distortion residual
    pred_ux = dx + (scale_rate * half_diag) * xs - (rot_rad * half_diag) * ys
    pred_uy = dy + (scale_rate * half_diag) * ys + (rot_rad * half_diag) * xs
    res_mag = np.hypot(ux - pred_ux, uy - pred_uy)
    residual_mean = float(np.mean(res_mag))

    # Parallax / depth layers cue: when global translation is significant, check if flow magnitudes
    # split into distinct foreground/background velocity bands
    trans_speed = float(np.hypot(dx, dy))
    depth_score = 0.0
    if trans_speed > 0.8 and mag_p95 > 1.5:
        p25 = float(np.percentile(mag, 25))
        p75 = float(np.percentile(mag, 75))
        iqr_ratio = (p75 - p25) / (mag_mean + 0.5)
        # Distinguish smooth depth parallax from pure radial zoom
        if abs(scale_rate) < 0.03:
            depth_score = float(np.clip(iqr_ratio / 2.0, 0.0, 1.0))

    return OpticalFlowMetrics(
        magnitude_mean=round(mag_mean, 4),
        magnitude_p95=round(mag_p95, 4),
        dx=round(dx, 4),
        dy=round(dy, 4),
        scale_rate=round(scale_rate, 5),
        rotation_deg=round(rot_deg, 4),
        residual_mean=round(residual_mean, 4),
        depth_layers_score=round(depth_score, 4),
    )
