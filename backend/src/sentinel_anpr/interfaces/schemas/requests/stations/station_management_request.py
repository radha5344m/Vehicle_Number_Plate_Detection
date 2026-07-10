"""Police station request schemas."""

from pydantic import BaseModel, Field


class CreateStationRequest(BaseModel):
    station_name: str = Field(min_length=1, max_length=200)
    station_code: str = Field(min_length=1, max_length=32)
    district: str = Field(min_length=1, max_length=200)
    state: str = Field(min_length=1, max_length=200)
    address: str = Field(min_length=1, max_length=1000)
    pincode: str = Field(min_length=1, max_length=16)
    phone_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    station_type: str = Field(min_length=1, max_length=64)
    status: str = Field(default="active", min_length=1, max_length=32)


class UpdateStationRequest(BaseModel):
    station_name: str = Field(min_length=1, max_length=200)
    district: str = Field(min_length=1, max_length=200)
    state: str = Field(min_length=1, max_length=200)
    address: str = Field(min_length=1, max_length=1000)
    pincode: str = Field(min_length=1, max_length=16)
    phone_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    station_type: str = Field(min_length=1, max_length=64)
    status: str = Field(min_length=1, max_length=32)


class UpdateStationStatusRequest(BaseModel):
    status: str = Field(min_length=1, max_length=32)
