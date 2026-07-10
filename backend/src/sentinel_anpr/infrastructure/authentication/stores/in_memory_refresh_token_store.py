"""In-memory refresh token session store."""

from sentinel_anpr.application.ports.outbound.refresh_token_store_port import RefreshTokenStorePort


class InMemoryRefreshTokenStore(RefreshTokenStorePort):
    """Track active refresh tokens in memory."""

    def __init__(self) -> None:
        self._active_tokens: set[str] = set()

    def register(self, session_id: str, refresh_token: str) -> None:
        del session_id  # session tracked inside JWT; store token only
        self._active_tokens.add(refresh_token)

    def revoke(self, refresh_token: str) -> None:
        self._active_tokens.discard(refresh_token)

    def is_active(self, refresh_token: str) -> bool:
        return refresh_token in self._active_tokens
