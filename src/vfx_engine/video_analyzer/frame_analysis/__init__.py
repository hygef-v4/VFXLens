"""Per-frame signal extraction and contact sheet exports."""

from .contact_sheet import export_evidence_frames_and_contact_sheet
from .signal_extractor import detect_high_activity_windows, extract_frame_signals

__all__ = [
    "detect_high_activity_windows",
    "export_evidence_frames_and_contact_sheet",
    "extract_frame_signals",
]
