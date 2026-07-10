"""Challan payment status values."""

from enum import StrEnum


class ChallanPaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    WAIVED = "waived"
