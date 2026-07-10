"""JWT token provider implementation."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.ports.outbound.token_provider_port import TokenProviderPort
from sentinel_anpr.domain.authentication.errors import TokenInvalidError


class JwtTokenProvider(TokenProviderPort):
    """Issue and validate HS256 JWT tokens."""

    def __init__(
        self,
        secret: str,
        issuer: str,
        access_token_ttl_seconds: int,
        refresh_token_ttl_seconds: int,
    ) -> None:
        self._secret = secret
        self._issuer = issuer
        self._access_ttl = access_token_ttl_seconds
        self._refresh_ttl = refresh_token_ttl_seconds

    @property
    def access_token_ttl_seconds(self) -> int:
        return self._access_ttl

    def create_access_token(self, principal: AuthPrincipal) -> str:
        return self._encode(
            principal,
            token_type="access",
            ttl_seconds=self._access_ttl,
        )

    def create_refresh_token(self, principal: AuthPrincipal) -> str:
        return self._encode(
            principal,
            token_type="refresh",
            ttl_seconds=self._refresh_ttl,
        )

    def decode_access_token(self, token: str) -> AuthPrincipal:
        return self._decode(token, expected_type="access")

    def decode_refresh_token(self, token: str) -> AuthPrincipal:
        return self._decode(token, expected_type="refresh")

    def _encode(self, principal: AuthPrincipal, token_type: str, ttl_seconds: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": principal.officer_id,
            "badge": principal.badge_number,
            "station_id": principal.station_id,
            "roles": list(principal.roles),
            "role": principal.role,
            "permissions": list(principal.permissions),
            "session_id": principal.session_id,
            "type": token_type,
            "iss": self._issuer,
            "iat": now,
            "exp": now + timedelta(seconds=ttl_seconds),
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def _decode(self, token: str, expected_type: str) -> AuthPrincipal:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer=self._issuer,
            )
        except jwt.PyJWTError as exc:
            raise TokenInvalidError() from exc

        if payload.get("type") != expected_type:
            raise TokenInvalidError("Unexpected token type")

        return AuthPrincipal(
            officer_id=str(payload["sub"]),
            badge_number=str(payload["badge"]),
            station_id=str(payload.get("station_id", "")),
            roles=tuple(payload.get("roles", [])),
            role=str(payload.get("role", "")),
            permissions=tuple(payload.get("permissions", [])),
            session_id=str(payload["session_id"]),
        )
