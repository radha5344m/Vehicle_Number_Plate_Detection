"""Shared account profile DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateOwnProfileCommand:
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    employee_id: str
