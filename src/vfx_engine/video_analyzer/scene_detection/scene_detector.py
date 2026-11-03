"""Hybrid scene boundary detection combining PySceneDetect with frame-exact VFX cut signals."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ...schemas.video_schema import FrameSignalEntry, SceneBoundarySchema


def _run_pyscenedetect_cut_frames(video_path: Path) -> set[int]:
    """Run PySceneDetect ContentDetector + AdaptiveDetector with short min_scene_len for fast VFX edits."""
    cut_frames: set[int] = set()
    try:
        from scenedetect import AdaptiveDetector, ContentDetector, SceneManager, open_video

        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=24.0, min_scene_len=3))
        scene_manager.add_detector(AdaptiveDetector(adaptive_threshold=2.8, min_scene_len=3))
        scene_manager.detect_scenes(video=video, show_progress=False)
        scene_list = scene_manager.get_scene_list(start_in_scene=True)
        for idx, (start_tc, _) in enumerate(scene_list):
            if idx > 0:
                cut_frames.add(int(start_tc.frame_num))
    except Exception:
        # Fallback cleanly to frame-exact signal cut detection if PySceneDetect encounters container quirks
        pass
    return cut_frames


def detect_scenes(
    video_path: Path,
    signals: list[FrameSignalEntry],
) -> list[SceneBoundarySchema]:
    """Segment the video into scenes using PySceneDetect + frame-level color/motion discontinuity."""
    if not signals:
        return []

    pyscene_cuts = _run_pyscenedetect_cut_frames(video_path)

    diffs = np.array([s.max_channel_diff for s in signals], dtype=np.float32)

    med_diff = float(np.median(diffs))
    mad_diff = float(np.median(np.abs(diffs - med_diff))) + 1e-3
    adaptive_cut_thresh = max(24.0, med_diff + 4.5 * mad_diff)

    cut_indices: list[int] = [0]
    cut_types: dict[int, str] = {0: "initial_scene"}
    cut_scores: dict[int, float] = {0: 0.0}

    for i in range(1, len(signals)):
        sig = signals[i]
        prev_sig = signals[i - 1]
        is_pyscene = sig.frame_index in pyscene_cuts
        is_signal_cut = (
            sig.max_channel_diff >= adaptive_cut_thresh
            and sig.changed_cell_area >= 0.65
        )

        if not (is_pyscene or is_signal_cut):
            continue

        # Suppress immediate recovery frame of a 1-2 frame white/black flash so flash isn't split into 2 scenes
        if (i - cut_indices[-1]) < 3:
            continue

        # Classify transition type from measured signals
        if abs(sig.luma_delta) > 55.0 or sig.highlight_ratio > 0.72:
            t_type = "flash_cut"
        elif abs(sig.flow_scale_rate) > 0.035 or abs(prev_sig.flow_scale_rate) > 0.035 or sig.flow_magnitude_mean > 14.0:
            t_type = "whip_zoom_cut"
        else:
            t_type = "hard_cut"

        score = float(
            min(
                100.0,
                sig.max_channel_diff * 1.2 + sig.changed_cell_area * 30.0 + (15.0 if is_pyscene else 0.0),
            )
        )
        cut_indices.append(i)
        cut_types[i] = t_type
        cut_scores[i] = round(score, 2)

    scenes: list[SceneBoundarySchema] = []
    for s_idx, start_pos in enumerate(cut_indices):
        end_pos = (cut_indices[s_idx + 1] - 1) if (s_idx + 1 < len(cut_indices)) else (len(signals) - 1)
        start_sig = signals[start_pos]
        end_sig = signals[end_pos]
        duration = max(0.0, end_sig.timestamp - start_sig.timestamp + end_sig.delta_t)
        scenes.append(
            SceneBoundarySchema(
                scene_index=s_idx,
                start_frame=start_sig.frame_index,
                end_frame=end_sig.frame_index,
                start_time=round(start_sig.timestamp, 4),
                end_time=round(end_sig.timestamp, 4),
                duration=round(duration, 4),
                cut_score=cut_scores.get(start_pos, 0.0),
                transition_type=cut_types.get(start_pos, "hard_cut"),
            )
        )

    return scenes
