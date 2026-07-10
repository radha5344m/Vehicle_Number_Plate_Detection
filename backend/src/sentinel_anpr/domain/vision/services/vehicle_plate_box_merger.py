"""Merge vehicle and plate boxes for intelligent cropping."""

from __future__ import annotations

from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox

_DEFAULT_PADDING_PX = 15


def build_vehicle_crop_box(
    vehicle_box: NormalizedBoundingBox,
    plate_box: NormalizedBoundingBox | None,
    *,
    image_width: int,
    image_height: int,
    padding_px: int = _DEFAULT_PADDING_PX,
) -> NormalizedBoundingBox:
    """Return a crop box that contains the vehicle and its assigned plate."""
    merged = vehicle_box.union(plate_box) if plate_box is not None else vehicle_box
    return merged.with_pixel_padding(
        image_width=image_width,
        image_height=image_height,
        padding_px=padding_px,
    )
