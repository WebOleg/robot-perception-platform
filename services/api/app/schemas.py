"""Data contracts (principle #7).

These models define exactly what a detection looks like as it crosses the seam
from World A (robot) into World B (web). The bridge must send this shape;
anything else is rejected at the door before it can reach the database.
"""
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DetectionIn(BaseModel):
    """A detection as sent by the bridge (input contract)."""

    label: str = Field(..., min_length=1, description="Detected class, e.g. 'person'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence 0..1")
    x: float = Field(..., description="Bounding box top-left x")
    y: float = Field(..., description="Bounding box top-left y")
    width: float = Field(..., gt=0, description="Bounding box width")
    height: float = Field(..., gt=0, description="Bounding box height")
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the detection happened (defaults to now, UTC)",
    )


class DetectionOut(DetectionIn):
    """A detection as returned by the API (adds the DB-assigned id)."""

    id: int
