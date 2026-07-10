"""Vision AI service port.

Abstraction for a multimodal vision model that analyzes a vehicle image and
returns registration and attribute details in a single call. This is a pure
application-layer port (Protocol) — no concrete implementation is provided
here. It is the sole analysis abstraction the verification workflow depends on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VisionAnalysisResult:
    """Structured output from a vision AI vehicle-image analysis."""

    registration_number: str | None
    vehicle_color: str | None
    vehicle_type: str | None
    brand: str | None
    model: str | None
    confidence: float | None
    explanation: str | None


class VisionAiService(Protocol):
    """Analyze a vehicle image with a multimodal vision AI model."""

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        """Return registration and attribute details for one vehicle image."""
        ...
