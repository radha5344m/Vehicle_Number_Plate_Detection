"""Revoke refresh token and end session."""

from sentinel_anpr.application.dto.auth_dto import LogoutCommand
from sentinel_anpr.application.ports.outbound.refresh_token_store_port import RefreshTokenStorePort
from sentinel_anpr.domain.authentication.errors import TokenInvalidError


class LogoutUseCase:
    """Invalidate refresh token for the current session."""

    def __init__(self, refresh_token_store: RefreshTokenStorePort) -> None:
        self._refresh_token_store = refresh_token_store

    def execute(self, command: LogoutCommand) -> None:
        if not self._refresh_token_store.is_active(command.refresh_token):
            raise TokenInvalidError("Refresh token is invalid or already revoked")
        if command.principal.session_id:
            self._refresh_token_store.revoke(command.refresh_token)
