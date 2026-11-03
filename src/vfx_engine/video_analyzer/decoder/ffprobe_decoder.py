"""Video stream prober and exact frame-timestamp decoder using FFprobe + OpenCV."""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from ...core.config import EngineConfig
from ...core.logging import get_logger
from ...core.safety import compute_sha256
from ...schemas.video_schema import VideoMetadataSchema

logger = get_logger("video_analyzer.decoder")


@dataclass
class DecodedFrame:
    """Single decoded video frame with its exact presentation timestamp."""

    frame_index: int
    timestamp: float
    delta_t: float
    image_bgr: np.ndarray

    @property
    def bgr(self) -> np.ndarray:
        """Alias for `image_bgr`."""
        return self.image_bgr


def _parse_rational(rate_str: str | None) -> float:
    if not rate_str or rate_str in ("0/0", "N/A"):
        return 0.0
    if "/" in rate_str:
        num_s, den_s = rate_str.split("/", 1)
        try:
            num, den = float(num_s), float(den_s)
            return num / den if den != 0 else 0.0
        except ValueError:
            return 0.0
    try:
        return float(rate_str)
    except ValueError:
        return 0.0


def probe_video_metadata_and_timestamps(
    video_path: Path,
    config: EngineConfig | None = None,
) -> tuple[VideoMetadataSchema, list[float]]:
    """Extract stream metadata and exact per-frame presentation timestamps via `ffprobe`.

    Handles Variable Frame Rate (VFR) videos accurately by reading packet/frame PTS times.
    """
    cfg = config or EngineConfig()
    if not video_path.exists() or not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    size_bytes = video_path.stat().st_size
    if size_bytes == 0:
        raise ValueError(f"Video file is empty (0 bytes): {video_path}")
    sha256_hex = compute_sha256(video_path)

    # 1. Probe container and streams
    cmd_streams = [
        cfg.ffprobe_bin,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    proc = subprocess.run(
        cmd_streams,
        capture_output=True,
        text=True,
        timeout=cfg.subprocess_timeout_sec,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise ValueError(f"ffprobe failed on '{video_path.name}': {proc.stderr.strip()}")

    probe_data = json.loads(proc.stdout)
    streams = probe_data.get("streams") or []
    fmt_info = probe_data.get("format") or {}

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if video_stream is None:
        raise ValueError(f"No video stream found in '{video_path.name}'")

    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)
    r_frame_rate = video_stream.get("r_frame_rate")
    avg_frame_rate = video_stream.get("avg_frame_rate")
    nominal_fps = _parse_rational(r_frame_rate) or _parse_rational(avg_frame_rate) or 30.0
    average_fps = _parse_rational(avg_frame_rate) or nominal_fps

    duration = float(
        video_stream.get("duration")
        or fmt_info.get("duration")
        or 0.0
    )

    # 2. Extract exact per-frame timestamps via ffprobe frame/packet inspection
    cmd_pts = [
        cfg.ffprobe_bin,
        "-v",
        "quiet",
        "-select_streams",
        "v:0",
        "-show_entries",
        "frame=best_effort_timestamp_time,pkt_pts_time,pts_time",
        "-of",
        "json",
        str(video_path),
    ]
    timestamps: list[float] = []
    try:
        proc_pts = subprocess.run(
            cmd_pts,
            capture_output=True,
            text=True,
            timeout=cfg.subprocess_timeout_sec,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if proc_pts.returncode == 0 and proc_pts.stdout.strip():
            pts_json = json.loads(proc_pts.stdout)
            for f_entry in pts_json.get("frames") or []:
                t_val = (
                    f_entry.get("best_effort_timestamp_time")
                    or f_entry.get("pkt_pts_time")
                    or f_entry.get("pts_time")
                )
                if t_val is not None:
                    try:
                        timestamps.append(float(t_val))
                    except ValueError:
                        pass
    except Exception as exc:
        logger.warning("Frame-level PTS probe fallback triggered: %s", exc)

    # Ensure monotonic timestamps and compute VFR metrics
    if timestamps:
        # Normalize if first frame PTS is offset
        t0 = timestamps[0]
        if t0 > 0 and t0 < 1.0:
            timestamps = [max(0.0, t - t0) for t in timestamps]
        frame_count = len(timestamps)
        if duration <= 0.0 and len(timestamps) > 1:
            duration = timestamps[-1] + (timestamps[-1] - timestamps[-2])
    else:
        nb_frames_raw = video_stream.get("nb_frames")
        frame_count = int(nb_frames_raw) if nb_frames_raw and str(nb_frames_raw).isdigit() else int(round(duration * nominal_fps))
        timestamps = [i / nominal_fps for i in range(max(1, frame_count))]

    # Detect VFR by checking inter-frame delta_t variance
    is_vfr = False
    vfr_jitter_ms = 0.0
    if len(timestamps) > 2:
        deltas = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
            if timestamps[i] >= timestamps[i - 1]
        ]
        if deltas:
            mean_dt = sum(deltas) / len(deltas)
            variance = sum((d - mean_dt) ** 2 for d in deltas) / len(deltas)
            std_ms = math.sqrt(variance) * 1000.0
            vfr_jitter_ms = round(std_ms, 4)
            # If inter-frame delta standard deviation exceeds 1.5 ms or nominal != average by >2%
            if std_ms > 1.5 or abs(nominal_fps - average_fps) / max(1.0, nominal_fps) > 0.02:
                is_vfr = True

    if len(timestamps) > 1 and duration > 0:
        average_fps = len(timestamps) / duration

    bit_rate_raw = video_stream.get("bit_rate") or fmt_info.get("bit_rate")
    bit_rate = int(bit_rate_raw) if bit_rate_raw and str(bit_rate_raw).isdigit() else None

    metadata = VideoMetadataSchema(
        file_path=str(video_path.resolve()),
        file_name=video_path.name,
        file_size_bytes=size_bytes,
        sha256=sha256_hex,
        container_format=str(fmt_info.get("format_name") or video_path.suffix.lstrip(".")),
        video_codec=str(video_stream.get("codec_name") or "unknown"),
        codec_profile=video_stream.get("profile"),
        pixel_format=video_stream.get("pix_fmt"),
        width=width,
        height=height,
        aspect_ratio=video_stream.get("display_aspect_ratio"),
        nominal_fps=round(nominal_fps, 4),
        average_fps=round(average_fps, 4),
        r_frame_rate=r_frame_rate,
        avg_frame_rate=avg_frame_rate,
        is_vfr=is_vfr,
        vfr_jitter_ms=vfr_jitter_ms,
        duration_seconds=round(duration, 6),
        frame_count=frame_count,
        bit_rate=bit_rate,
        has_audio=audio_stream is not None,
        audio_codec=audio_stream.get("codec_name") if audio_stream else None,
        audio_sample_rate=(
            int(audio_stream["sample_rate"])
            if audio_stream and str(audio_stream.get("sample_rate", "")).isdigit()
            else None
        ),
        audio_channels=audio_stream.get("channels") if audio_stream else None,
    )
    return metadata, timestamps


def iter_decoded_frames(
    video_path: Path,
    timestamps: list[float],
    nominal_fps: float,
    max_frames: int | None = None,
) -> Iterator[DecodedFrame]:
    """Yield decoded BGR frames paired with their exact native presentation timestamps."""
    if max_frames is not None and max_frames <= 0:
        raise ValueError(f"max_frames must be a positive integer, got {max_frames}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV failed to open video file: {video_path}")

    default_dt = 1.0 / max(1.0, nominal_fps)
    idx = 0
    prev_ts = 0.0
    try:
        while True:
            if max_frames is not None and idx >= max_frames:
                break
            ret, frame_bgr = cap.read()
            if not ret or frame_bgr is None:
                break
            if idx < len(timestamps):
                ts = timestamps[idx]
            else:
                pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                ts = (pos_msec / 1000.0) if pos_msec > 0 else (prev_ts + default_dt)

            dt = (ts - prev_ts) if idx > 0 and ts > prev_ts else default_dt
            yield DecodedFrame(
                frame_index=idx,
                timestamp=round(ts, 6),
                delta_t=round(dt, 6),
                image_bgr=frame_bgr,
            )
            prev_ts = ts
            idx += 1
    finally:
        cap.release()
