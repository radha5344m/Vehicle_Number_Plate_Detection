"""Opaque transaction handle for repository participation."""

from typing import Protocol


class TransactionHandlePort(Protocol):
    """Marker protocol for an open database transaction scope."""
