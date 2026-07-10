"""User management authentication errors."""

from sentinel_anpr.domain.authentication.errors import AuthenticationError


class SuperAdminRequiredError(AuthenticationError):
    """Raised when a non-super-admin accesses user management."""

    def __init__(self) -> None:
        super().__init__("AUTH_FORBIDDEN", "SUPER_ADMIN access is required")
