"""Resize and compress vehicle images before vision inference."""

from __future__ import annotations

import io

_DEFAULT_MAX_WIDTH = 1024
_DEFAULT_JPEG_QUALITY = 85


def preprocess_vehicle_image(
    image_bytes: bytes,
    *,
    max_width: int = _DEFAULT_MAX_WIDTH,
    jpeg_quality: int = _DEFAULT_JPEG_QUALITY,
) -> tuple[bytes, str]:
    """Return JPEG bytes and mime type, resizing to at most ``max_width`` pixels wide."""
    from PIL import Image

    with Image.open(io.BytesIO(image_bytes)) as image:
        rgb_image = image.convert("RGB")
        width, height = rgb_image.size
        if width > max_width:
            new_height = max(1, int(height * (max_width / width)))
            rgb_image = rgb_image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        rgb_image.save(
            buffer,
            format="JPEG",
            quality=jpeg_quality,
            optimize=True,
        )
        return buffer.getvalue(), "image/jpeg"
