"""Tests for user identity formatting helpers."""

from sentinel_anpr.application.services.user_identity_service import (
    build_temporary_password,
    default_username_for_employee_id,
    format_employee_id,
    format_user_id,
)


def test_format_user_id_uses_zero_padded_sequence() -> None:
    assert format_user_id(1, year_suffix=26) == "AP-26-01"
    assert format_user_id(2, year_suffix=26) == "AP-26-02"
    assert format_user_id(99, year_suffix=26) == "AP-26-99"
    assert format_user_id(100, year_suffix=26) == "AP-26-100"


def test_format_employee_id_by_role() -> None:
    assert format_employee_id("SUPER_ADMIN", 1) == "ADMIN001"
    assert format_employee_id("STATION_ADMIN", 2) == "STA002"
    assert format_employee_id("POLICE_OFFICER", 3) == "OFF003"


def test_build_temporary_password_uses_employee_id_and_year() -> None:
    assert build_temporary_password("ADMIN001") == "ADMIN001@2026"
    assert build_temporary_password("STA001") == "STA001@2026"
    assert build_temporary_password("OFF001") == "OFF001@2026"


def test_default_username_is_lowercase_employee_id() -> None:
    assert default_username_for_employee_id("ADMIN001") == "admin001"
