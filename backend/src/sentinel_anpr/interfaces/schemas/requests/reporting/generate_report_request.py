"""Investigation report request schema."""

from pydantic import BaseModel, Field


class VehicleDetailsRequest(BaseModel):
    """Optional vehicle registry details."""

    plate_number: str | None = None
    make: str | None = None
    model: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    registration_status: str | None = None
    registered_owner: str | None = None


class GenerateInvestigationReportRequest(BaseModel):
    """Investigation report generation payload."""

    detected_plate: str = Field(..., min_length=1, max_length=16)
    ocr_registration_number: str = Field(..., min_length=1, max_length=16)
    ocr_detected_text: str = Field(..., min_length=1, max_length=32)
    ocr_confidence: float = Field(..., ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., min_length=1, max_length=16)
    recommendation: str = Field(..., min_length=1, max_length=2000)
    title: str | None = Field(default=None, max_length=255)
    vehicle_details: VehicleDetailsRequest | None = None
