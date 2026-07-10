"""Atomic allocation of user and employee identifier sequences."""

from typing import Protocol


class UserIdentitySequencePort(Protocol):
    def next_user_id(self) -> str:
        """Allocate the next global user ID (for example AP-26-01)."""
        ...

    def next_employee_id(self, role: str) -> str:
        """Allocate the next employee ID for the given role."""
        ...
