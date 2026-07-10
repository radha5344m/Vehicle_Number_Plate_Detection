"""Format human-readable user and employee identifiers."""

from __future__ import annotations

from datetime import UTC, datetime

_EMPLOYEE_ID_PREFIXES = {
    "SUPER_ADMIN": "ADMIN",
    "STATION_ADMIN": "STA",
    "POLICE_OFFICER": "OFF",
}

_TEMPORARY_PASSWORD_YEAR = 2026


def current_user_id_year_suffix() -> int:
    """Return the two-digit year suffix used in user IDs."""
    return datetime.now(UTC).year % 100


def format_user_id(sequence: int, *, year_suffix: int | None = None) -> str:
    """Format a global user ID such as AP-26-01."""
    suffix = current_user_id_year_suffix() if year_suffix is None else year_suffix
    if sequence < 100:
        return f"AP-{suffix:02d}-{sequence:02d}"
    return f"AP-{suffix:02d}-{sequence}"


def format_employee_id(role: str, sequence: int) -> str:
    """Format a role-scoped employee ID such as ADMIN001."""
    normalized_role = role.upper()
    prefix = _EMPLOYEE_ID_PREFIXES.get(normalized_role)
    if prefix is None:
        raise ValueError("Invalid role")
    return f"{prefix}{sequence:03d}"


def build_temporary_password(employee_id: str, *, year: int = _TEMPORARY_PASSWORD_YEAR) -> str:
    """Build the one-time password shown after account creation."""
    return f"{employee_id}@{year}"


def default_username_for_employee_id(employee_id: str) -> str:
    """Derive the default login username from an employee ID."""
    return employee_id.lower()
