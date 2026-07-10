"""Password hashing port."""

from typing import Protocol


class PasswordHasherPort(Protocol):
    """Hash and verify officer passwords."""

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...
