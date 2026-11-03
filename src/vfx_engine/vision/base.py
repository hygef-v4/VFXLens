"""AI Vision adapter interface and safe local/configured implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..core.config import VFXEngineConfig
from ..schemas.common import DataAvailabilityStatus
from ..schemas.video_schema import VideoEffectEventSchema, VisionAnalysisSummarySchema


class VisionAnalyzer(ABC):
    """Abstract interface for analyzing contact sheets and evidence frames with a multimodal model."""

    @abstractmethod
    def analyze(
        self,
        contact_sheet_path: Path,
        evidence_frame_paths: list[Path],
        detected_events: list[VideoEffectEventSchema],
    ) -> VisionAnalysisSummarySchema:
        """Analyze visual evidence and return a structured VisionAnalysisSummarySchema."""


class NoOpVisionAnalyzer(VisionAnalyzer):
    """Default local fallback when no AI Vision provider is configured. Never fabricates AI output."""

    def analyze(
        self,
        contact_sheet_path: Path,
        evidence_frame_paths: list[Path],
        detected_events: list[VideoEffectEventSchema],
    ) -> VisionAnalysisSummarySchema:
        return VisionAnalysisSummarySchema(
            provider="none",
            model=None,
            status=DataAvailabilityStatus.UNAVAILABLE,
            analyzed=False,
            semantic_observations=[],
            note=(
                "No AI Vision provider configured (VFX_VISION_PROVIDER=none). "
                f"Computer-vision signal detectors ran locally and exported {len(evidence_frame_paths)} "
                f"evidence frame(s) plus '{contact_sheet_path.name}' for inspection. "
                "Semantic-only judgements (e.g., exact text reading, 3D model identity, complex matte semantics) "
                "are marked as unavailable rather than fabricated."
            ),
        )


class ConfiguredHTTPVisionAnalyzer(VisionAnalyzer):
    """Adapter for an explicitly user-configured OpenAI-compatible vision endpoint (e.g., local Ollama/vLLM)."""

    def __init__(self, provider: str, model: str, endpoint: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.endpoint = endpoint

    def analyze(
        self,
        contact_sheet_path: Path,
        evidence_frame_paths: list[Path],
        detected_events: list[VideoEffectEventSchema],
    ) -> VisionAnalysisSummarySchema:
        if not self.endpoint:
            return VisionAnalysisSummarySchema(
                provider=self.provider,
                model=self.model,
                status=DataAvailabilityStatus.UNAVAILABLE,
                analyzed=False,
                semantic_observations=[],
                note=(
                    f"Vision provider '{self.provider}' (model '{self.model}') was specified without an active "
                    "local endpoint URL; paid external APIs are never called automatically."
                ),
            )
        return VisionAnalysisSummarySchema(
            provider=self.provider,
            model=self.model,
            status=DataAvailabilityStatus.UNAVAILABLE,
            analyzed=False,
            semantic_observations=[],
            note=(
                f"Vision adapter configured for '{self.provider}' ({self.model}), "
                "operating in strict offline/no-paid-API mode."
            ),
        )


def create_vision_analyzer(config: VFXEngineConfig) -> VisionAnalyzer:
    """Factory that returns NoOpVisionAnalyzer unless a provider is explicitly configured."""
    provider = (config.vision_provider or "none").strip().lower()
    if provider in ("", "none", "disabled", "off") or not config.vision_model:
        return NoOpVisionAnalyzer()
    return ConfiguredHTTPVisionAnalyzer(
        provider=provider,
        model=config.vision_model,
    )
