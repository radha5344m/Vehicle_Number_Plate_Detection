"""Internal license plate detection DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedPlateDto:
    """License plate detected in a scene image."""

    plate_id: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    text: str | None = None
