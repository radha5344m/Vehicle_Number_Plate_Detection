"""Cached scene analysis for multi-vehicle batch processing."""

from __future__ import annotations

from dataclasses import dataclass

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto


@dataclass(frozen=True)
class PlateAssignmentDto:
    """Plate-to-vehicle assignment used for masking and crop boxes."""

    plate_id: str
    vehicle_id: str | None


@dataclass(frozen=True)
class SceneAnalysisContextDto:
    """Single-pass vehicle and plate detection with assignments."""

    raw_vehicles: tuple[DetectedVehicleDto, ...]
    raw_plates: tuple[DetectedPlateDto, ...]
    assignments: tuple[PlateAssignmentDto, ...]
    image_width: int
    image_height: int
