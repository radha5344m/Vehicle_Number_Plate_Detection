"""Inputs for pure risk scoring."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryVehicleSnapshot:
    """Registry vehicle fields used for risk comparison."""

    plate_number: str
    make: str
    color: str
    vehicle_type: str
    registration_status: str


@dataclass(frozen=True)
class RiskAssessmentInput:
    """Normalized inputs for the risk engine."""

    plate_number: str
    ocr_confidence: float
    registry_vehicle: RegistryVehicleSnapshot | None
    observed_color: str
    observed_vehicle_type: str
    observed_brand: str | None
    color_confidence: float
    vehicle_type_confidence: float
    brand_confidence: float | None
