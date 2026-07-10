"""Login request schema."""

import re

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Officer login credentials."""

    identifier: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    station_code: str | None = Field(default=None, max_length=16)

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        normalized = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]+", normalized):
            raise ValueError("identifier must contain only letters, numbers, dot, underscore, or hyphen")
        return normalized
