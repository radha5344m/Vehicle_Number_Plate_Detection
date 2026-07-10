"""Return current authenticated officer profile."""

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal, MeResult
from sentinel_anpr.application.ports.outbound.credential_store_port import CredentialStorePort
from sentinel_anpr.application.services.auth_permissions import permissions_for_roles
from sentinel_anpr.domain.authentication.errors import TokenInvalidError


class GetCurrentOfficerUseCase:
    """Resolve officer profile and permissions from principal."""

    def __init__(self, credential_store: CredentialStorePort) -> None:
        self._credential_store = credential_store

    def execute(self, principal: AuthPrincipal) -> MeResult:
        stored = self._credential_store.find_by_id(principal.officer_id)
        if stored is None:
            raise TokenInvalidError("Officer not found")

        return MeResult(
            officer=stored.officer,
            permissions=principal.permissions or permissions_for_roles(principal.roles),
            session_id=principal.session_id,
        )
