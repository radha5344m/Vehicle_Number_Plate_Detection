"""DTOs for Hugging Face visible-vehicle counting (upload workflow only)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisibleVehicleTypeDto:
    """One visible vehicle type returned by vision counting."""

    type: str


@dataclass(frozen=True)
class CountVisibleVehiclesCommand:
    """Count visible vehicles in an uploaded image."""

    image_bytes: bytes
    content_type: str


@dataclass(frozen=True)
class CountVisibleVehiclesResult:
    """Visible vehicle count outcome from vision AI."""

    vehicle_count: int
    vehicles: tuple[VisibleVehicleTypeDto, ...]
