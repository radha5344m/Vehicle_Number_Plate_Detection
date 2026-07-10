"""JWT token provider port."""

from typing import Protocol

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal


class TokenProviderPort(Protocol):
    """Issue and validate JWT access and refresh tokens."""

    def create_access_token(self, principal: AuthPrincipal) -> str: ...

    def create_refresh_token(self, principal: AuthPrincipal) -> str: ...

    def decode_access_token(self, token: str) -> AuthPrincipal: ...

    def decode_refresh_token(self, token: str) -> AuthPrincipal: ...

    @property
    def access_token_ttl_seconds(self) -> int: ...
