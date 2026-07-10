"""Port for intelligent vehicle + plate scene analysis."""

from __future__ import annotations

from typing import Protocol

from sentinel_anpr.application.dto.scene_analysis_dto import SceneAnalysisContextDto
from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto, SelectedVehicleRegionDto


class IntelligentSceneDetectionService(Protocol):
    """Detect vehicles, assign plates, and return plate-aware vehicle boxes."""

    def analyze_scene(self, image_bytes: bytes) -> SceneAnalysisContextDto:
        """Run vehicle, plate, and assignment detection once for batch reuse."""

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        """Return one bounding box per vehicle, expanded to include its assigned plate."""

    def mask_regions_for_selection(
        self,
        image_bytes: bytes,
        selected_vehicle_id: str,
        scene_context: SceneAnalysisContextDto | None = None,
    ) -> tuple[SelectedVehicleRegionDto, ...]:
        """Return every non-selected vehicle and non-assigned plate region to mask."""
