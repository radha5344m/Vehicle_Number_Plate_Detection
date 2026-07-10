"""Database connectivity port."""

from typing import Protocol


class DatabasePort(Protocol):
    """Minimal database health probe."""

    def ping(self) -> bool: ...
