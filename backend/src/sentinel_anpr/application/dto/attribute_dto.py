"""Vehicle attribute extraction data transfer objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractVehicleAttributesCommand:
    """Vehicle image to analyze."""

    image_bytes: bytes


@dataclass(frozen=True)
class VehicleAttributesOutput:
    """Raw extractor output."""

    color: str
    vehicle_type: str
    brand: str | None
    color_confidence: float
    vehicle_type_confidence: float
    brand_confidence: float | None
    model_version: str


@dataclass(frozen=True)
class VehicleAttributesResult:
    """Structured vehicle attribute analysis result."""

    color: str
    vehicle_type: str
    brand: str | None
    color_confidence: float
    vehicle_type_confidence: float
    brand_confidence: float | None
    model_version: str
