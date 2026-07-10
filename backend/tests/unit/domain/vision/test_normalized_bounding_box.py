"""Tests for normalized bounding box clamping."""

from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox


def test_clamp_keeps_box_inside_unit_square() -> None:
    box = NormalizedBoundingBox(x=0.95, y=0.9, width=0.2, height=0.2).clamp()
    assert box.x <= 0.8
    assert box.y <= 0.8
    assert box.width >= 0.02
    assert box.height >= 0.02
