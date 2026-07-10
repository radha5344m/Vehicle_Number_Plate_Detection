"""Normalized image bounding box (0.0–1.0 coordinates)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Normalized point in image coordinates."""

    x: float
    y: float


@dataclass(frozen=True)
class NormalizedBoundingBox:
    """Axis-aligned box relative to image width and height."""

    x: float
    y: float
    width: float
    height: float

    def clamp(self) -> NormalizedBoundingBox:
        """Clamp coordinates into the unit square with a minimum size."""
        min_size = 0.02
        width = max(min_size, min(1.0, self.width))
        height = max(min_size, min(1.0, self.height))
        x = max(0.0, min(1.0 - width, self.x))
        y = max(0.0, min(1.0 - height, self.y))
        return NormalizedBoundingBox(x=x, y=y, width=width, height=height)

    def center(self) -> Point:
        return Point(x=self.x + (self.width / 2), y=self.y + (self.height / 2))

    def contains_point(self, x: float, y: float) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def distance_to_point(self, x: float, y: float) -> float:
        dx = max(self.x - x, 0.0, x - (self.x + self.width))
        dy = max(self.y - y, 0.0, y - (self.y + self.height))
        return (dx**2 + dy**2) ** 0.5

    def union(self, other: NormalizedBoundingBox) -> NormalizedBoundingBox:
        left = min(self.x, other.x)
        top = min(self.y, other.y)
        right = max(self.x + self.width, other.x + other.width)
        bottom = max(self.y + self.height, other.y + other.height)
        return NormalizedBoundingBox(x=left, y=top, width=right - left, height=bottom - top).clamp()

    def distance_to_point_pixels(
        self,
        x_px: float,
        y_px: float,
        *,
        image_width: int,
        image_height: int,
    ) -> float:
        x_norm = x_px / image_width
        y_norm = y_px / image_height
        dx = max(self.x - x_norm, 0.0, x_norm - (self.x + self.width)) * image_width
        dy = max(self.y - y_norm, 0.0, y_norm - (self.y + self.height)) * image_height
        return (dx**2 + dy**2) ** 0.5

    def with_pixel_padding(
        self,
        *,
        image_width: int,
        image_height: int,
        padding_px: int,
    ) -> NormalizedBoundingBox:
        pad_x = padding_px / image_width
        pad_y = padding_px / image_height
        return NormalizedBoundingBox(
            x=self.x - pad_x,
            y=self.y - pad_y,
            width=self.width + (2 * pad_x),
            height=self.height + (2 * pad_y),
        ).clamp()