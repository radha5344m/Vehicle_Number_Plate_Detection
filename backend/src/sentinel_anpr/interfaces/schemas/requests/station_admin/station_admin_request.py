"""Station admin request schemas."""

from pydantic import BaseModel, Field


class CreateOfficerRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    username: str | None = Field(default=None, max_length=64)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=32)
    badge_number: str | None = Field(default=None, max_length=32)
    rank: str = Field(min_length=1, max_length=100)
    status: str = Field(default="active", min_length=1, max_length=32)


class UpdateStationDetailsRequest(BaseModel):
    address: str = Field(min_length=1, max_length=500)
    phone_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)


class UpdateOfficerRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=32)
    rank: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1, max_length=32)


class ResetOfficerPasswordRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


class ChangeOwnPasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
