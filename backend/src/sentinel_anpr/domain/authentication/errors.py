"""Authentication domain errors."""


class AuthenticationError(Exception):
    """Base authentication failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(AuthenticationError):
    """Wrong login identifier or password."""

    def __init__(self) -> None:
        super().__init__("AUTH_LOGIN_INVALID", "Invalid username, employee ID, badge number, or password")


class ForbiddenOfficerError(AuthenticationError):
    """Officer account is suspended or inactive."""

    def __init__(self) -> None:
        super().__init__("AUTH_ACCOUNT_INACTIVE", "Your account is inactive. Please contact an administrator.")


class TokenMissingError(AuthenticationError):
    """No bearer token supplied."""

    def __init__(self) -> None:
        super().__init__("AUTH_MISSING", "Authentication required")


class TokenInvalidError(AuthenticationError):
    """Malformed, expired, or revoked token."""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__("AUTH_INVALID", message)
