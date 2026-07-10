"""User management request schemas."""

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    username: str | None = Field(default=None, max_length=64)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=32)
    badge_number: str | None = Field(default=None, max_length=32)
    rank: str | None = Field(default=None, max_length=100)
    role: str = Field(min_length=1, max_length=32)
    police_station: str | None = Field(default=None, max_length=200)
    district: str | None = Field(default=None, max_length=200)
    status: str = Field(min_length=1, max_length=32)


class UpdateUserRequest(BaseModel):
    employee_id: str = Field(min_length=1, max_length=32)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=32)
    rank: str = Field(min_length=1, max_length=100)
    role: str | None = Field(default=None, max_length=32)
    police_station: str | None = Field(default=None, max_length=200)
    district: str | None = Field(default=None, max_length=200)
    status: str = Field(min_length=1, max_length=32)


class ResetPasswordRequest(BaseModel):
    new_password: str | None = Field(default=None, min_length=8, max_length=128)
