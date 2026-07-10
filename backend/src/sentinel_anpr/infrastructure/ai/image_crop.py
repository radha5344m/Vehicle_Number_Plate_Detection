"""Crop and isolate single-vehicle regions from scene images."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw

from sentinel_anpr.application.dto.vehicle_detection_dto import SelectedVehicleRegionDto
from sentinel_anpr.domain.ingestion.validators.image_validator import MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH
from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox

_DEFAULT_PADDING_PX = 15


def _ensure_minimum_resolution(image: Image.Image) -> Image.Image:
    width, height = image.size
    scale = max(MIN_IMAGE_WIDTH / width, MIN_IMAGE_HEIGHT / height, 1.0)
    if scale <= 1.0:
        return image
    return image.resize(
        (max(MIN_IMAGE_WIDTH, int(width * scale)), max(MIN_IMAGE_HEIGHT, int(height * scale))),
        Image.Resampling.LANCZOS,
    )


def _region_pixels(
    region: SelectedVehicleRegionDto,
    image_width: int,
    image_height: int,
    *,
    padding_px: int = 0,
) -> tuple[int, int, int, int]:
    box = NormalizedBoundingBox(
        x=region.x,
        y=region.y,
        width=region.width,
        height=region.height,
    ).clamp()
    left = int(box.x * image_width) - padding_px
    top = int(box.y * image_height) - padding_px
    right = int((box.x + box.width) * image_width) + padding_px
    bottom = int((box.y + box.height) * image_height) + padding_px
    left = max(0, left)
    top = max(0, top)
    right = min(image_width, max(left + 1, right))
    bottom = min(image_height, max(top + 1, bottom))
    return left, top, right, bottom


def _intersection_over_union(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
) -> float:
    left_a, top_a, right_a, bottom_a = first
    left_b, top_b, right_b, bottom_b = second
    inter_left = max(left_a, left_b)
    inter_top = max(top_a, top_b)
    inter_right = min(right_a, right_b)
    inter_bottom = min(bottom_a, bottom_b)
    if inter_right <= inter_left or inter_bottom <= inter_top:
        return 0.0
    inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
    area_a = max(1, (right_a - left_a) * (bottom_a - top_a))
    area_b = max(1, (right_b - left_b) * (bottom_b - top_b))
    return inter_area / (area_a + area_b - inter_area)


def prepare_isolated_vehicle_image(
    image_bytes: bytes,
    selected_region: SelectedVehicleRegionDto,
    mask_regions: tuple[SelectedVehicleRegionDto, ...],
    *,
    padding_px: int = _DEFAULT_PADDING_PX,
) -> bytes:
    """Mask every other vehicle, then crop tightly around the selected vehicle only."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        rgb_image = image.convert("RGB")
        image_width, image_height = rgb_image.size

        draw = ImageDraw.Draw(rgb_image)
        for region in mask_regions:
            if region.vehicle_id == selected_region.vehicle_id:
                continue
            other_pixels = _region_pixels(region, image_width, image_height, padding_px=2)
            draw.rectangle(other_pixels, fill=(0, 0, 0))

        crop_box = _region_pixels(
            selected_region,
            image_width,
            image_height,
            padding_px=padding_px,
        )
        cropped = rgb_image.crop(crop_box)
        cropped = _ensure_minimum_resolution(cropped)
        buffer = io.BytesIO()
        cropped.save(buffer, format="JPEG", quality=90, optimize=True)
        return buffer.getvalue()


def crop_vehicle_region(image_bytes: bytes, region: SelectedVehicleRegionDto) -> bytes:
    """Crop a normalized bounding box from ``image_bytes`` and return JPEG bytes."""
    return prepare_isolated_vehicle_image(image_bytes, region, ())
