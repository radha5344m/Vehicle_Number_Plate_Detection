"""Supported vehicle body types."""

from enum import StrEnum


class VehicleType(StrEnum):
    """Vehicle body style categories."""

    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    OTHER = "other"
