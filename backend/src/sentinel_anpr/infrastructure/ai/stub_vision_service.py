"""Deterministic stub VisionAiService for local development and tests.

Returns a fixed :class:`VisionAnalysisResult` so the vehicle-verification
pipeline runs end-to-end without a Hugging Face token or network access. Selected
via ``SENTINEL_VISION_PROVIDER=stub``.
"""

from __future__ import annotations

from sentinel_anpr.application.ports.vision_ai_service import (
    VisionAiService,
    VisionAnalysisResult,
    VisibleVehicleCountResult,
)

_STUB_REGISTRATION_NUMBER = "AP09AB1234"


class StubVisionService(VisionAiService):
    """Return a plausible, deterministic vehicle analysis for development."""

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        del image_bytes
        return VisionAnalysisResult(
            registration_number=_STUB_REGISTRATION_NUMBER,
            vehicle_color="white",
            vehicle_type="car",
            brand="Toyota",
            model="Innova",
            confidence=0.9,
            explanation="Stub vision analysis for development and tests.",
        )

    def count_visible_vehicles(self, image_bytes: bytes) -> VisibleVehicleCountResult:
        del image_bytes
        return VisibleVehicleCountResult(
            vehicle_count=1,
            vehicles=("car",),
        )
