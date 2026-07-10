"""Port for license plate detection (no OCR workflow)."""

from __future__ import annotations

from typing import Protocol

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto


class LicensePlateDetectionService(Protocol):
    """Detect visible license plates and return bounding boxes."""

    def detect_plates(self, image_bytes: bytes) -> tuple[DetectedPlateDto, ...]:
        """Return all detected plates in the image."""
