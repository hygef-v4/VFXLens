"""Main orchestrator for Video VFX Analyzer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from ..core.config import VFXEngineConfig
from ..core.logging import get_logger
from ..core.safety import ReadOnlyFileGuard, validate_video_input
from ..schemas.common import AnalysisWarning
from ..schemas.video_schema import (
    SamplingSummarySchema,
    VideoAnalysisResult,
    VideoTimelineSchema,
)
from ..vision.base import VisionAnalyzer, create_vision_analyzer
from .decoder.ffprobe_decoder import (
    iter_decoded_frames,
    probe_video_metadata_and_timestamps,
)
from .effect_detection.candidate_detectors import detect_video_effect_candidates
from .frame_analysis.contact_sheet import export_evidence_frames_and_contact_sheet
from .frame_analysis.signal_extractor import (
    detect_high_activity_windows,
    extract_frame_signals,
)
from .scene_detection.scene_detector import detect_scenes

logger = get_logger("vfx_engine.video_analyzer")


UNDETERMINED_VIDEO_ASPECTS_DEFAULT = [
    "Exact After Effects layer hierarchy, precomp nesting depth, and Adjustment Layer boundaries cannot be recovered from rendered MP4/MOV pixels.",
    "Exact third-party plugin matchNames (e.g., Sapphire S_Glow vs. Deep Glow vs. stacked built-in Glow) are candidate hypotheses, never certainties from video alone.",
    "Exact numeric keyframe values, Graph Editor Bezier tangents, and JavaScript/ExtendScript expressions (e.g., wiggle seed/frequency) cannot be uniquely inverted from pixels.",
    "Track matte modes (Alpha/Luma Matte), blending modes (Add vs. Screen vs. Linear Dodge), and internal 16/32-bpc color pipeline settings are indistinguishable after 8-bit H.264/HEVC compression.",
]


class VideoVFXAnalyzer:
    """Orchestrates decoding, adaptive frame analysis, scene detection, and VFX candidate extraction."""

    def __init__(
        self,
        config: VFXEngineConfig | None = None,
        vision_analyzer: VisionAnalyzer | None = None,
    ) -> None:
        self.config = config or VFXEngineConfig.from_env()
        self.vision_analyzer = vision_analyzer or create_vision_analyzer(self.config)

    def analyze(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        max_frames: int | None = None,
    ) -> tuple[VideoAnalysisResult, VideoTimelineSchema]:
        """Analyze a video file and return `(VideoAnalysisResult, VideoTimelineSchema)`."""
        vpath = validate_video_input(Path(video_path))
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        warnings: list[AnalysisWarning] = []
        analysis_id = f"vid_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        with ReadOnlyFileGuard(vpath):
            metadata, pts_list = probe_video_metadata_and_timestamps(vpath, config=self.config)
            expected_frames = metadata.frame_count
            if max_frames is not None:
                expected_frames = min(expected_frames, max_frames) if expected_frames > 0 else max_frames

            # Determine full-frame vs two-pass adaptive optical flow strategy
            full_frame_eligible = (
                metadata.duration_seconds <= self.config.full_frame_max_duration_sec
                or expected_frames <= 1800
            )

            if full_frame_eligible:
                strategy = "full_frame_with_adaptive_windows"
                signals = extract_frame_signals(
                    iter_decoded_frames(vpath, pts_list, metadata.nominal_fps, max_frames=max_frames),
                    dense_frame_indices=None,
                )
                high_activity_windows = detect_high_activity_windows(signals)
            else:
                strategy = "adaptive_two_pass"
                # Pass 1: streaming color/grid change pass with stride-4 optical flow
                coarse_signals = extract_frame_signals(
                    iter_decoded_frames(vpath, pts_list, metadata.nominal_fps, max_frames=max_frames),
                    dense_frame_indices=None,
                    dense_frame_stride=4,
                )
                high_activity_windows = detect_high_activity_windows(coarse_signals, padding_frames=6)
                dense_set = {s.frame_index for s in coarse_signals if s.is_dense_sampled}
                for win in high_activity_windows:
                    for f_idx in range(int(win["start_frame"]), int(win["end_frame"]) + 1):
                        dense_set.add(f_idx)
                signals = extract_frame_signals(
                    iter_decoded_frames(vpath, pts_list, metadata.nominal_fps, max_frames=max_frames),
                    dense_frame_indices=dense_set,
                )

            total_frames = len(signals)
            if total_frames == 0:
                raise ValueError(f"No decodable video frames found in '{vpath.name}'")

            if metadata.frame_count <= 0:
                metadata.frame_count = total_frames
            if metadata.duration_seconds <= 0:
                metadata.duration_seconds = round(signals[-1].timestamp, 4)

            scenes = detect_scenes(vpath, signals)
            events = detect_video_effect_candidates(signals, scenes)

            contact_sheet_rel, evidence_dir_rel, evidence_files = (
                export_evidence_frames_and_contact_sheet(
                    decoded_frames=iter_decoded_frames(
                        vpath, pts_list, metadata.nominal_fps, max_frames=max_frames
                    ),
                    events=events,
                    output_dir=out_dir,
                    frame_indices=[s.frame_index for s in signals],
                )
            )

            vision_summary = self.vision_analyzer.analyze(
                contact_sheet_path=out_dir / contact_sheet_rel,
                evidence_frame_paths=[out_dir / rel for rel in evidence_files],
                detected_events=events,
            )

        dense_count = sum(1 for s in signals if s.is_dense_sampled)
        coverage = round(dense_count / max(1, total_frames), 4)

        sampling_summary = SamplingSummarySchema(
            strategy=strategy,
            total_video_frames=total_frames,
            analyzed_frames_count=dense_count,
            coverage_ratio=coverage,
            high_activity_windows=high_activity_windows,
            contact_sheet_path=contact_sheet_rel,
            evidence_frames_dir=evidence_dir_rel,
            evidence_frame_files=evidence_files,
        )

        rerun_cmd = f'vfx analyze-video "{vpath}" --output "{out_dir}"'
        now_iso = datetime.now(timezone.utc).isoformat()

        result = VideoAnalysisResult(
            analysis_id=analysis_id,
            analyzed_at=now_iso,
            rerun_command=rerun_cmd,
            metadata=metadata,
            sampling=sampling_summary,
            scenes=scenes,
            effect_events=events,
            vision_analysis=vision_summary,
            undetermined_video_aspects=list(UNDETERMINED_VIDEO_ASPECTS_DEFAULT),
            warnings=warnings,
        )

        timeline = VideoTimelineSchema(
            analysis_id=analysis_id,
            video_file=str(vpath),
            nominal_fps=metadata.nominal_fps,
            is_vfr=metadata.is_vfr,
            frame_count=total_frames,
            duration_seconds=metadata.duration_seconds,
            high_activity_windows=high_activity_windows,
            scenes=scenes,
            events_summary=[
                {
                    "event_id": ev.event_id,
                    "effect_type": ev.effect_type,
                    "start_time": ev.start_time,
                    "end_time": ev.end_time,
                    "start_frame": ev.start_frame,
                    "end_frame": ev.end_frame,
                    "peak_frame": ev.peak_frame,
                    "confidence": ev.confidence,
                }
                for ev in events
            ],
            frames=signals,
        )

        return result, timeline
