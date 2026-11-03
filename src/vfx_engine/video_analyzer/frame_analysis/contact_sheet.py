"""Evidence frame extraction and annotated contact sheet generation with bounded O(1) full-frame memory."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

import cv2
import numpy as np

from ...schemas.video_schema import VideoEffectEventSchema
from ..decoder.ffprobe_decoder import DecodedFrame


def export_evidence_frames_and_contact_sheet(
    decoded_frames: Iterable[DecodedFrame],
    events: list[VideoEffectEventSchema],
    output_dir: Path,
    cols: int = 5,
    max_sheet_tiles: int = 25,
    frame_indices: Sequence[int] | None = None,
) -> tuple[str, str, list[str]]:
    """Save evidence frames for detected VFX events and generate `contact-sheet.jpg`.

    Streams `decoded_frames` without retaining full-resolution BGR buffers in memory.

    Returns:
        Tuple of (`contact_sheet_rel_path`, `evidence_dir_rel_path`, `evidence_frame_rel_paths`).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence-frames"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    if frame_indices is None and isinstance(decoded_frames, Sequence):
        frame_indices = [f.frame_index for f in decoded_frames]

    valid_frame_set: set[int] | None = set(frame_indices) if frame_indices is not None else None

    # 1. Determine which frame indices are needed for event evidence JPEGs
    needed_evidence_indices: set[int] = set()
    for ev in events:
        for f_idx in (ev.start_frame, ev.peak_frame, ev.end_frame):
            if valid_frame_set is None or f_idx in valid_frame_set:
                needed_evidence_indices.add(f_idx)

    # Fallback timeline evidence indices if no events fired
    if not needed_evidence_indices and frame_indices:
        step = max(1, len(frame_indices) // 6)
        for f_idx in list(frame_indices)[::step][:8]:
            needed_evidence_indices.add(int(f_idx))

    # 2. Determine which frame indices are needed for the contact sheet (bounded to max_sheet_tiles)
    candidate_peaks = sorted(
        {ev.peak_frame for ev in events if valid_frame_set is None or ev.peak_frame in valid_frame_set}
    )
    sheet_indices: set[int] = set(candidate_peaks[:max_sheet_tiles])
    if frame_indices and len(sheet_indices) < max_sheet_tiles:
        target_count = min(max_sheet_tiles, len(frame_indices))
        uniform_positions = np.linspace(0, len(frame_indices) - 1, num=target_count, dtype=int)
        for pos in uniform_positions:
            if len(sheet_indices) >= max_sheet_tiles:
                break
            sheet_indices.add(int(frame_indices[int(pos)]))

    tile_w = 320
    tile_h: int | None = None
    saved_frames: dict[int, str] = {}
    sheet_thumbs: dict[int, tuple[np.ndarray, float]] = {}

    # 3. Single streaming pass: write evidence JPEGs on the fly and keep only tiny 320px thumbnails
    for stream_pos, df in enumerate(decoded_frames):
        f_idx = df.frame_index
        bgr = df.bgr
        if tile_h is None:
            src_h, src_w = bgr.shape[:2]
            tile_h = max(120, int(round(tile_w * (src_h / max(1, src_w)))))

        want_evidence = f_idx in needed_evidence_indices or (
            frame_indices is None and not needed_evidence_indices and len(saved_frames) < 8 and stream_pos % 6 == 0
        )
        if want_evidence and f_idx not in saved_frames:
            fname = f"frame_{f_idx:05d}_{df.timestamp:.3f}s.jpg"
            fpath = evidence_dir / fname
            if not cv2.imwrite(str(fpath), bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92]):
                raise OSError(f"Failed to write evidence frame JPEG to '{fpath}'")
            saved_frames[f_idx] = f"evidence-frames/{fname}"

        want_sheet = len(sheet_thumbs) < max_sheet_tiles and (
            f_idx in sheet_indices or frame_indices is None
        )
        if want_sheet and f_idx not in sheet_thumbs:
            thumb = cv2.resize(bgr, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
            sheet_thumbs[f_idx] = (thumb, df.timestamp)
            sheet_indices.add(f_idx)

        del bgr

    # Populate each event's evidence_frames list
    for ev in events:
        candidate_indices = sorted({ev.start_frame, ev.peak_frame, ev.end_frame})
        ev.evidence_frames = [saved_frames[f_idx] for f_idx in candidate_indices if f_idx in saved_frames]

    if tile_h is None:
        tile_h = 180

    ordered_indices = [idx for idx in sorted(sheet_indices) if idx in sheet_thumbs][:max_sheet_tiles]

    frame_badges: dict[int, list[str]] = {}
    for ev in events:
        frame_badges.setdefault(ev.peak_frame, []).append(ev.effect_type)

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

        thumb, ts = sheet_thumbs[f_idx]
        canvas[y0 + header_h : y0 + cell_h, x0 : x0 + tile_w] = thumb

        cv2.rectangle(canvas, (x0, y0), (x0 + tile_w - 1, y0 + header_h - 1), (38, 38, 44), -1)
        label = f"#{f_idx} | {ts:.3f}s"
        badges = frame_badges.get(f_idx, [])
        if badges:
            label += f" [{badges[0][:14]}]"
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
    if not cv2.imwrite(str(contact_sheet_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 90]):
        raise OSError(f"Failed to write contact sheet image to '{contact_sheet_path}'")

    return (
        "contact-sheet.jpg",
        "evidence-frames",
        [saved_frames[k] for k in sorted(saved_frames.keys())],
    )
