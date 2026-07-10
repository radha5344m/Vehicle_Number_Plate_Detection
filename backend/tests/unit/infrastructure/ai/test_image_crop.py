"""Tests for server-side vehicle region cropping and isolation."""

import io

from PIL import Image, ImageDraw

from sentinel_anpr.application.dto.vehicle_detection_dto import SelectedVehicleRegionDto
from sentinel_anpr.infrastructure.ai.image_crop import crop_vehicle_region, prepare_isolated_vehicle_image


def _image_bytes() -> bytes:
    image = Image.new("RGB", (800, 600), color=(20, 30, 40))
    draw = ImageDraw.Draw(image)
    draw.rectangle((80, 120, 280, 360), fill=(180, 40, 40))
    draw.rectangle((460, 140, 700, 380), fill=(40, 120, 180))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_crop_vehicle_region_returns_jpeg_bytes() -> None:
    image = Image.new("RGB", (400, 300), color=(20, 30, 40))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    region = SelectedVehicleRegionDto(
        vehicle_id="vehicle-1",
        x=0.25,
        y=0.1,
        width=0.5,
        height=0.7,
    )

    cropped = crop_vehicle_region(buffer.getvalue(), region)

    with Image.open(io.BytesIO(cropped)) as result:
        assert result.format == "JPEG"
        assert result.size[0] > 0
        assert result.size[1] > 0


def test_prepare_isolated_vehicle_image_masks_other_vehicle_regions() -> None:
    image_bytes = _image_bytes()
    selected = SelectedVehicleRegionDto("vehicle-1", 0.1, 0.2, 0.45, 0.45)
    other = SelectedVehicleRegionDto("vehicle-2", 0.42, 0.24, 0.28, 0.38)

    isolated = prepare_isolated_vehicle_image(image_bytes, selected, (other,))

    with Image.open(io.BytesIO(isolated)) as result:
        pixels = list(result.convert("RGB").getdata())
        black_pixels = sum(1 for pixel in pixels if pixel == (0, 0, 0))
        assert black_pixels > 0
        assert result.size[0] >= 640
