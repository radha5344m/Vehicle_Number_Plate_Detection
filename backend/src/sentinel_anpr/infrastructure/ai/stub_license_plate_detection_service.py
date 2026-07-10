"""Deterministic stub license plate detection for tests."""

from __future__ import annotations

import uuid

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.ports.license_plate_detection_service import LicensePlateDetectionService


class StubLicensePlateDetectionService(LicensePlateDetectionService):
    """Return plate boxes aligned with stub vehicle positions."""

    def detect_plates(self, image_bytes: bytes) -> tuple[DetectedPlateDto, ...]:
        del image_bytes
        return (
            DetectedPlateDto(
                plate_id=str(uuid.uuid4()),
                x=0.16,
                y=0.58,
                width=0.18,
                height=0.06,
                confidence=0.9,
                text=None,
            ),
            DetectedPlateDto(
                plate_id=str(uuid.uuid4()),
                x=0.6,
                y=0.6,
                width=0.17,
                height=0.06,
                confidence=0.88,
                text=None,
            ),
        )
