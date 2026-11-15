"""Tests for frame-bounded scene detection."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import scenedetect

from vfx_engine.schemas.video_schema import FrameSignalEntry
from vfx_engine.video_analyzer.scene_detection.scene_detector import detect_scenes


def test_scene_detection_decodes_only_analyzed_frame_range(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """The PySceneDetect pass must not decode beyond the supplied analyzed signals."""
    video_path = tmp_path / "scene_limit.avi"
    writer = cv2.VideoWriter(
        str(video_path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (32, 32)
    )
    assert writer.isOpened()
    for index in range(30):
        writer.write(np.full((32, 32, 3), index * 7, dtype=np.uint8))
    writer.release()

    decoded_frames = 0
    open_video = scenedetect.open_video

    class CountingVideo:
        def __init__(self, video):
            self.video = video

        def __getattr__(self, name):
            return getattr(self.video, name)

        def read(self, *args, **kwargs):
            nonlocal decoded_frames
            frame = self.video.read(*args, **kwargs)
            if isinstance(frame, np.ndarray):
                decoded_frames += 1
            return frame

    monkeypatch.setattr(
        scenedetect, "open_video", lambda *args, **kwargs: CountingVideo(open_video(*args, **kwargs))
    )
    signals = [
        FrameSignalEntry(
            frame_index=index,
            timestamp=index / 10,
            delta_t=0.1,
            mean_luma=0,
            highlight_ratio=0,
            luma_std=0,
        )
        for index in range(7)
    ]

    detect_scenes(video_path, signals)

    assert decoded_frames > 0
    assert decoded_frames <= len(signals)
