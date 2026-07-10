"""Pillow-based image inspection adapter."""

import io

from PIL import Image, UnidentifiedImageError

from sentinel_anpr.application.ports.outbound.image_inspector_port import ImageInspectorPort
from sentinel_anpr.domain.ingestion.errors import InvalidImageError


class PillowImageInspector(ImageInspectorPort):
    """Inspect JPEG/PNG bytes for dimensions and content type."""

    def get_dimensions(self, content: bytes) -> tuple[int, int]:
        try:
            with Image.open(io.BytesIO(content)) as image:
                return image.size
        except UnidentifiedImageError as exc:
            raise InvalidImageError("Unable to read image file") from exc

    def detect_content_type(self, content: bytes, declared_content_type: str) -> str:
        try:
            with Image.open(io.BytesIO(content)) as image:
                detected = image.format
        except UnidentifiedImageError as exc:
            raise InvalidImageError("Unable to read image file") from exc

        if detected == "JPEG":
            return "image/jpeg"
        if detected == "PNG":
            return "image/png"

        if declared_content_type in {"image/jpeg", "image/png"}:
            return declared_content_type

        raise InvalidImageError("Image must be JPEG or PNG")
