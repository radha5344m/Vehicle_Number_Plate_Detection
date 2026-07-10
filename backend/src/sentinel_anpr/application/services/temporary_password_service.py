"""Generate compliant temporary passwords for new and reset accounts."""

from __future__ import annotations

from sentinel_anpr.application.services.user_identity_service import build_temporary_password


def generate_temporary_password(employee_id: str) -> str:
    """Return a deterministic temporary password for the given employee ID."""
    return build_temporary_password(employee_id.strip().upper())