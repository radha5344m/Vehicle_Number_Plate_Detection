"""Vehicle detection and region-selection DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectedVehicleRegionDto:
    """Officer-selected vehicle region in normalized image coordinates."""

    vehicle_id: str
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class DetectedVehicleDto:
    """Vehicle detected in an uploaded scene image."""

    vehicle_id: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    vehicle_type: str


@dataclass(frozen=True)
class DetectedPlateDto:
    """License plate detected in an uploaded scene image."""

    plate_id: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    text: str | None = None


@dataclass(frozen=True)
class VehicleSceneAnalysisResult:
    """Intelligent scene analysis with plate-aware vehicle regions."""

    vehicles: tuple[DetectedVehicleDto, ...]
    plates: tuple[DetectedPlateDto, ...]
    unassigned_plate_count: int


@dataclass(frozen=True)
class DetectVehiclesCommand:
    """Detect vehicles in an uploaded image."""

    image_bytes: bytes
    content_type: str


@dataclass(frozen=True)
class DetectVehiclesResult:
    """Vehicle detection outcome."""

    vehicles: tuple[DetectedVehicleDto, ...]
    visible_plate_count: int
