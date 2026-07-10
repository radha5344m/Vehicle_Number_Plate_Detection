"""Deterministic stub vehicle detection for tests and local development."""

from __future__ import annotations

import uuid

from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto
from sentinel_anpr.application.ports.vehicle_detection_service import VehicleDetectionService


class StubVehicleDetectionService(VehicleDetectionService):
    """Return predictable vehicle boxes without OpenCV model files."""

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        del image_bytes
        return (
            DetectedVehicleDto(
                vehicle_id=str(uuid.uuid4()),
                x=0.08,
                y=0.12,
                width=0.38,
                height=0.62,
                confidence=0.91,
                vehicle_type="car",
            ),
            DetectedVehicleDto(
                vehicle_id=str(uuid.uuid4()),
                x=0.52,
                y=0.18,
                width=0.36,
                height=0.58,
                confidence=0.87,
                vehicle_type="suv",
            ),
        )
