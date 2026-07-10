"""Challan request schemas."""

from pydantic import BaseModel, Field


class CreateChallanRequest(BaseModel):
    registration_number: str = Field(min_length=1, max_length=32)
    owner_name: str | None = Field(default=None, max_length=200)
    vehicle_id: str | None = Field(default=None, max_length=36)
    investigation_id: str | None = Field(default=None, max_length=36)
    violation_type: str = Field(min_length=1, max_length=64)
    violation_description: str | None = Field(default=None, max_length=500)
    fine_amount: float = Field(ge=0)
    remarks: str | None = Field(default=None, max_length=1000)
    location_label: str | None = Field(default=None, max_length=255)
    gps_coordinates: str | None = Field(default=None, max_length=64)


class UpdateChallanRequest(BaseModel):
    violation_type: str | None = Field(default=None, max_length=64)
    violation_description: str | None = Field(default=None, max_length=500)
    fine_amount: float | None = Field(default=None, ge=0)
    remarks: str | None = Field(default=None, max_length=1000)
    location_label: str | None = Field(default=None, max_length=255)
    gps_coordinates: str | None = Field(default=None, max_length=64)
