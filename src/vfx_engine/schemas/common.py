"""Common schemas and provenance status enums for VFX Learning Engine."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DataAvailabilityStatus(str, Enum):
    """Explicit distinction between data observation, inference, and unavailability."""

    OBSERVED = "observed"
    INFERRED = "inferred"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    ERROR = "error"


class AnalysisWarning(BaseModel):
    """Structured warning or non-fatal issue encountered during analysis."""

    code: str = Field(..., description="Short machine-readable warning code")
    message: str = Field(..., description="Human-readable explanation of the warning")
    location: str | None = Field(default=None, description="Composition, layer, property, or frame path")
    status: DataAvailabilityStatus = Field(
        default=DataAvailabilityStatus.UNSUPPORTED,
        description="Availability status associated with this warning",
    )


class FieldProvenance(BaseModel):
    """Metadata describing why a field is unavailable, unsupported, or inferred."""

    field_path: str = Field(..., description="Dot or slash path of the field")
    status: DataAvailabilityStatus = Field(..., description="Availability classification")
    source_method: str = Field(..., description="Parser or analyzer method that reported this status")
    reason: str = Field(..., description="Detailed explanation")
    raw_hint: dict[str, Any] | None = Field(default=None, description="Optional raw diagnostic context")
