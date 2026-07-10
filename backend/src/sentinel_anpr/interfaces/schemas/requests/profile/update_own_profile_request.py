"""Shared profile update request schema."""

from pydantic import BaseModel, Field


class UpdateOwnProfileRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=32)
    employee_id: str = Field(min_length=1, max_length=32)
