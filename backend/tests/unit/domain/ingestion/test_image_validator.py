"""Image validator unit tests."""

import pytest

from sentinel_anpr.domain.ingestion.errors import InvalidImageError
from sentinel_anpr.domain.ingestion.validators.image_validator import validate_vehicle_image


def test_validate_accepts_valid_image() -> None:
    validate_vehicle_image(
        content_type="image/jpeg",
        size_bytes=1024,
        width=800,
        height=600,
    )


def test_validate_rejects_small_resolution() -> None:
    with pytest.raises(InvalidImageError):
        validate_vehicle_image(
            content_type="image/png",
            size_bytes=1024,
            width=320,
            height=240,
        )


def test_validate_rejects_invalid_type() -> None:
    with pytest.raises(InvalidImageError):
        validate_vehicle_image(
            content_type="image/gif",
            size_bytes=1024,
            width=800,
            height=600,
        )
