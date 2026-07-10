"""Shared infrastructure and system errors."""


class InfrastructureError(Exception):
    """Base infrastructure failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class DatabaseError(InfrastructureError):
    """Database operation failed."""

    def __init__(
        self,
        message: str = "Database service is temporarily unavailable. Please try again later.",
    ) -> None:
        super().__init__("DATABASE_ERROR", message)


class AiTimeoutError(InfrastructureError):
    """AI inference exceeded the configured timeout."""

    def __init__(self, service: str) -> None:
        super().__init__(
            "AI_TIMEOUT",
            f"{service} timed out. Please try again with a smaller image or later.",
        )


class InternalError(InfrastructureError):
    """Unexpected application failure."""

    def __init__(
        self,
        message: str = "An unexpected error occurred. Please try again or contact support.",
    ) -> None:
        super().__init__("INTERNAL_ERROR", message)
