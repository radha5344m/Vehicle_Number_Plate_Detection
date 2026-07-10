"""Authentication route dependencies."""

from collections.abc import Callable

from fastapi import HTTPException
from fastapi import Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.services.auth_permissions import has_permission
from sentinel_anpr.domain.authentication.errors import TokenMissingError


def get_current_principal(request: Request) -> AuthPrincipal:
    """Return principal set by auth middleware."""
    principal = getattr(request.state, "principal", None)
    if principal is None:
        raise TokenMissingError()
    return principal


def require_permission(permission: str) -> Callable[[Request], AuthPrincipal]:
    """Return a dependency that enforces a permission."""

    def dependency(request: Request) -> AuthPrincipal:
        principal = get_current_principal(request)
        if not has_permission(principal.roles, permission):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return principal

    return dependency
