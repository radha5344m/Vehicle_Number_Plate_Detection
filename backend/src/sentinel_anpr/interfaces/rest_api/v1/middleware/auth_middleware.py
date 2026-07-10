"""JWT authentication middleware."""

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from sentinel_anpr.domain.authentication.errors import AuthenticationError, TokenMissingError
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response

PUBLIC_ROUTES: set[tuple[str, str]] = {
    ("GET", "/v1/health"),
    ("POST", "/v1/auth/login"),
}

PROTECTED_ROUTES: set[tuple[str, str]] = {
    ("GET", "/v1/auth/me"),
    ("POST", "/v1/auth/logout"),
    ("POST", "/v1/uploads/vehicle-image"),
    ("GET", "/v1/vehicles/lookup"),
    ("GET", "/v1/history/scans"),
    ("POST", "/v1/history/scans"),
    ("POST", "/v1/reports/investigation"),
    ("GET", "/v1/investigation-reports"),
    ("GET", "/v1/analytics/overview"),
    ("GET", "/v1/dashboard/summary"),
    ("GET", "/v1/dashboard/recent-activity"),
    ("GET", "/v1/dashboard/executive"),
    ("GET", "/v1/users"),
    ("POST", "/v1/users"),
    ("GET", "/v1/stations"),
    ("POST", "/v1/stations"),
    ("GET", "/v1/station-admin/dashboard"),
    ("GET", "/v1/station-admin/officers"),
    ("POST", "/v1/station-admin/officers"),
    ("GET", "/v1/station-admin/investigations"),
    ("GET", "/v1/station-admin/reports"),
    ("GET", "/v1/station-admin/analytics"),
    ("GET", "/v1/station-admin/notifications"),
    ("GET", "/v1/station-admin/profile"),
    ("PATCH", "/v1/station-admin/profile"),
    ("POST", "/v1/station-admin/profile/change-password"),
    ("PATCH", "/v1/police-officer/profile"),
    ("GET", "/v1/police-officer/dashboard"),
    ("GET", "/v1/police-officer/investigations"),
    ("GET", "/v1/police-officer/reports"),
    ("GET", "/v1/police-officer/notifications"),
    ("GET", "/v1/police-officer/profile"),
    ("POST", "/v1/police-officer/profile/change-password"),
    ("POST", "/v1/workflow/vehicle-verification"),
    ("GET", "/v1/challans/violations"),
    ("GET", "/v1/challans/search"),
    ("GET", "/v1/challans"),
    ("POST", "/v1/challans"),
    ("GET", "/v1/challans/analytics"),
}

PROTECTED_PREFIXES: tuple[str, ...] = (
    "/v1/dashboard/executive/export/",
    "/v1/reports/",
    "/v1/investigation-reports/",
    "/v1/users/",
    "/v1/stations/",
    "/v1/station-admin/",
    "/v1/police-officer/",
    "/v1/challans/",
    "/v1/workflow/",
)


def _is_protected_route(method: str, path: str) -> bool:
    normalized_path = path.rstrip("/") or "/"
    route_key = (method.upper(), normalized_path)
    if route_key in PROTECTED_ROUTES:
        return True
    return any(
        normalized_path.startswith(prefix.rstrip("/"))
        for prefix in PROTECTED_PREFIXES
        if normalized_path != prefix.rstrip("/")
    )


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT for protected authentication routes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        route_key = (request.method.upper(), request.url.path.rstrip("/") or "/")
        if not _is_protected_route(route_key[0], route_key[1]):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _error_response(TokenMissingError(), request)

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return _error_response(TokenMissingError(), request)

        token_provider = request.app.state.container.token_provider
        try:
            principal = token_provider.decode_access_token(token)
            request.state.principal = principal
        except AuthenticationError as exc:
            return _error_response(exc, request)

        return await call_next(request)


def _error_response(exc: AuthenticationError, request: Request) -> JSONResponse:
    status_code = 403 if exc.code in {"AUTH_FORBIDDEN", "AUTH_ACCOUNT_INACTIVE"} else 401
    return build_error_response(request, status_code, exc.code, exc.message)
