"""Evidence frame extraction and annotated contact sheet generation."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from ...schemas.video_schema import VideoEffectEventSchema
from ..decoder.ffprobe_decoder import DecodedFrame


def export_evidence_frames_and_contact_sheet(
    decoded_frames: list[DecodedFrame],
    events: list[VideoEffectEventSchema],
    output_dir: Path,
    cols: int = 5,
    max_sheet_tiles: int = 25,
) -> tuple[str, str, list[str]]:
    """Save evidence frames for detected VFX events and generate `contact-sheet.jpg`.

    Returns:
        Tuple of (`contact_sheet_rel_path`, `evidence_dir_rel_path`, `evidence_frame_rel_paths`).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence-frames"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    frame_map: dict[int, DecodedFrame] = {f.frame_index: f for f in decoded_frames}
    saved_frames: dict[int, str] = {}

    # 1. Export evidence frames for each detected event
    for ev in events:
        candidate_indices = sorted({ev.start_frame, ev.peak_frame, ev.end_frame})
        ev_paths: list[str] = []
        for f_idx in candidate_indices:
            if f_idx not in frame_map:
                continue
            if f_idx not in saved_frames:
                df = frame_map[f_idx]
                fname = f"frame_{f_idx:05d}_{df.timestamp:.3f}s.jpg"
                fpath = evidence_dir / fname
                cv2.imwrite(str(fpath), df.bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                saved_frames[f_idx] = f"evidence-frames/{fname}"
            ev_paths.append(saved_frames[f_idx])
        ev.evidence_frames = ev_paths

    # Guarantee at least key timeline frames are exported if events are sparse
    if not saved_frames and decoded_frames:
        step = max(1, len(decoded_frames) // 6)
        for df in decoded_frames[::step][:8]:
            fname = f"frame_{df.frame_index:05d}_{df.timestamp:.3f}s.jpg"
            fpath = evidence_dir / fname
            cv2.imwrite(str(fpath), df.bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            saved_frames[df.frame_index] = f"evidence-frames/{fname}"

    # 2. Select frames for the contact sheet (prioritizing event peak frames + uniform timeline anchors)
    sheet_indices: set[int] = {ev.peak_frame for ev in events if ev.peak_frame in frame_map}
    if decoded_frames:
        target_count = min(max_sheet_tiles, len(decoded_frames))
        uniform_positions = np.linspace(0, len(decoded_frames) - 1, num=target_count, dtype=int)
        for pos in uniform_positions:
            if len(sheet_indices) >= max_sheet_tiles:
                break
            sheet_indices.add(decoded_frames[int(pos)].frame_index)

    ordered_indices = sorted(sheet_indices)[:max_sheet_tiles]

    # Map frame index -> event labels for badge annotation
    frame_badges: dict[int, list[str]] = {}
    for ev in events:
        frame_badges.setdefault(ev.peak_frame, []).append(ev.effect_type)

    tile_w = 320
    tile_h = 180
    if decoded_frames:
        src_h, src_w = decoded_frames[0].bgr.shape[:2]
        tile_h = max(120, int(round(tile_w * (src_h / max(1, src_w)))))

    num_tiles = max(1, len(ordered_indices))
    actual_cols = min(cols, num_tiles)
    rows = (num_tiles + actual_cols - 1) // actual_cols
    header_h = 34
    cell_h = tile_h + header_h
    canvas = np.full((rows * cell_h, actual_cols * tile_w, 3), 24, dtype=np.uint8)

    for idx, f_idx in enumerate(ordered_indices):
        r = idx // actual_cols
        c = idx % actual_cols
        x0 = c * tile_w
        y0 = r * cell_h

        df = frame_map[f_idx]
        thumb = cv2.resize(df.bgr, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        canvas[y0 + header_h : y0 + cell_h, x0 : x0 + tile_w] = thumb

        # Draw header bar
        cv2.rectangle(canvas, (x0, y0), (x0 + tile_w - 1, y0 + header_h - 1), (38, 38, 44), -1)
        label = f"#{f_idx} | {df.timestamp:.3f}s"
        badges = frame_badges.get(f_idx, [])
        if badges:
            label += f" [{badges[0][:14]}]"
            # Highlight border for event peak frames
            cv2.rectangle(canvas, (x0, y0), (x0 + tile_w - 1, y0 + cell_h - 1), (0, 190, 255), 2)
        else:
            cv2.rectangle(canvas, (x0, y0), (x0 + tile_w - 1, y0 + cell_h - 1), (65, 65, 72), 1)

        cv2.putText(
            canvas,
            label,
            (x0 + 6, y0 + 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.44,
            (235, 235, 240),
            1,
            cv2.LINE_AA,
        )

    contact_sheet_path = output_dir / "contact-sheet.jpg"
    cv2.imwrite(str(contact_sheet_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

    return (
        "contact-sheet.jpg",
        "evidence-frames",
        [saved_frames[k] for k in sorted(saved_frames.keys())],
    )
