"""Plate text normalizer unit tests."""

from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)


def test_normalize_registration_number() -> None:
    assert normalize_registration_number("ap 09 ab 1234") == "AP09AB1234"
