"""Refresh token session store port."""

from typing import Protocol


class RefreshTokenStorePort(Protocol):
    """Track active refresh tokens for logout revocation."""

    def register(self, session_id: str, refresh_token: str) -> None: ...

    def revoke(self, refresh_token: str) -> None: ...

    def is_active(self, refresh_token: str) -> bool: ...
