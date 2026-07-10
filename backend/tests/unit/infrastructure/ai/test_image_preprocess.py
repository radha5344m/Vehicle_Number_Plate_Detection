"""Unit tests for image preprocessing before vision inference."""

from io import BytesIO

from PIL import Image

from sentinel_anpr.infrastructure.ai.image_preprocess import preprocess_vehicle_image


def test_preprocess_resizes_wide_images_to_max_width() -> None:
    image = Image.new("RGB", (2000, 1000), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    processed, mime_type = preprocess_vehicle_image(buffer.getvalue(), max_width=1024)

    with Image.open(BytesIO(processed)) as resized:
        assert resized.width == 1024
        assert resized.height == 512
    assert mime_type == "image/jpeg"


def test_preprocess_keeps_small_images_under_limit() -> None:
    image = Image.new("RGB", (640, 480), color=(255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    processed, mime_type = preprocess_vehicle_image(buffer.getvalue(), max_width=1024)

    with Image.open(BytesIO(processed)) as resized:
        assert resized.width == 640
        assert resized.height == 480
    assert mime_type == "image/jpeg"
