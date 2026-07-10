"""Save completed scan request schema."""

from pydantic import BaseModel, Field


class SaveCompletedScanRequest(BaseModel):
    """Request body for storing a completed scan."""

    plate: str = Field(..., min_length=1, max_length=16)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., min_length=1, max_length=16)
    vehicle_id: str | None = Field(default=None, max_length=36)
    location_label: str | None = Field(default=None, max_length=200)
