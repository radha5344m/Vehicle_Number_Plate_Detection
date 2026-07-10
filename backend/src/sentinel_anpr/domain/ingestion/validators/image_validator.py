"""Vehicle image validation rules."""

from sentinel_anpr.domain.ingestion.errors import InvalidImageError

ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset({"image/jpeg", "image/png"})
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MIN_IMAGE_WIDTH = 640
MIN_IMAGE_HEIGHT = 480


def validate_vehicle_image(
    *,
    content_type: str,
    size_bytes: int,
    width: int,
    height: int,
) -> None:
    """Raise InvalidImageError when image constraints are not met."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidImageError("Image must be JPEG or PNG")

    if size_bytes <= 0:
        raise InvalidImageError("Image file is empty")

    if size_bytes > MAX_IMAGE_BYTES:
        raise InvalidImageError("Image must not exceed 10 MB")

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        raise InvalidImageError(
            f"Image resolution must be at least {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT} pixels"
        )
