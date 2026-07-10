"""Authenticate an officer and issue tokens."""

import uuid

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal, LoginCommand, LoginResult
from sentinel_anpr.application.services.auth_permissions import (
    permissions_for_roles,
    primary_role_for_roles,
)
from sentinel_anpr.application.ports.outbound.credential_store_port import CredentialStorePort
from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.application.ports.outbound.refresh_token_store_port import RefreshTokenStorePort
from sentinel_anpr.application.ports.outbound.token_provider_port import TokenProviderPort
from sentinel_anpr.domain.authentication.errors import (
    ForbiddenOfficerError,
    InvalidCredentialsError,
)
from sentinel_anpr.domain.authentication.officer_status import OfficerStatus


class LoginUseCase:
    """Validate credentials and return JWT tokens."""

    def __init__(
        self,
        credential_store: CredentialStorePort,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
        refresh_token_store: RefreshTokenStorePort,
    ) -> None:
        self._credential_store = credential_store
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._refresh_token_store = refresh_token_store

    def execute(self, command: LoginCommand) -> LoginResult:
        stored = self._credential_store.find_by_identifier(command.identifier.strip())
        if stored is None:
            raise InvalidCredentialsError()

        if stored.officer.status != OfficerStatus.ACTIVE:
            raise ForbiddenOfficerError()

        if command.station_code and command.station_code != stored.officer.station_code:
            raise InvalidCredentialsError()

        if not self._password_hasher.verify(command.password.strip(), stored.password_hash):
            raise InvalidCredentialsError()

        self._credential_store.record_successful_login(stored.officer.officer_id)
        session_id = str(uuid.uuid4())
        principal = AuthPrincipal(
            officer_id=stored.officer.officer_id,
            badge_number=stored.officer.badge_number,
            station_id=stored.officer.station_id,
            roles=stored.officer.roles,
            role=primary_role_for_roles(stored.officer.roles),
            permissions=permissions_for_roles(stored.officer.roles),
            session_id=session_id,
        )
        access_token = self._token_provider.create_access_token(principal)
        refresh_token = self._token_provider.create_refresh_token(principal)
        self._refresh_token_store.register(session_id, refresh_token)
        primary_role = primary_role_for_roles(stored.officer.roles)

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._token_provider.access_token_ttl_seconds,
            officer=stored.officer,
            role=primary_role,
            permissions=principal.permissions,
            session_id=session_id,
        )
