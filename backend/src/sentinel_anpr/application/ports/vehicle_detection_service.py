"""Port for scene-level vehicle detection (no OCR)."""

from __future__ import annotations

from typing import Protocol

from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto


class VehicleDetectionService(Protocol):
    """Detect visible vehicles and return bounding boxes."""

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        """Return all detected vehicles in the image."""
