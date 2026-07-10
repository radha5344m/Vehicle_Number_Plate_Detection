"""Vehicle attribute extraction response schema."""

from pydantic import BaseModel, Field


class VehicleAttributesResponseData(BaseModel):
    """Structured vehicle attribute analysis payload."""

    color: str
    vehicle_type: str
    brand: str | None = None
    color_confidence: float = Field(ge=0.0, le=1.0)
    vehicle_type_confidence: float = Field(ge=0.0, le=1.0)
    brand_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    model_version: str
