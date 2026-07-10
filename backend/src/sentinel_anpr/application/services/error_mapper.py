"""Map machine error codes to user-friendly API messages."""

USER_FRIENDLY_MESSAGES: dict[str, str] = {
    "VALIDATION_ERROR": "The request contains invalid data. Please check your input and try again.",
    "UNPROCESSABLE": "We could not process the image. Please upload a clearer photo and try again.",
    "AUTH_MISSING": "Authentication is required. Please sign in and try again.",
    "AUTH_INVALID": "Your session is invalid or has expired. Please sign in again.",
    "AUTH_LOGIN_INVALID": "Invalid credentials. Check your username, employee ID, badge number, and password.",
    "AUTH_ACCOUNT_INACTIVE": "Your account is inactive. Please contact an administrator.",
    "AUTH_FORBIDDEN": "You do not have permission to perform this action.",
    "DATABASE_ERROR": "The database is temporarily unavailable. Please try again shortly.",
    "AI_TIMEOUT": "AI processing took too long. Please try again with a smaller image.",
    "SERVICE_UNAVAILABLE": "A required service is temporarily unavailable. Please try again later.",
    "INTERNAL_ERROR": "An unexpected error occurred. Please try again or contact support.",
    "NOT_FOUND": "The requested resource was not found.",
}


def to_user_message(code: str, fallback_message: str) -> str:
    """Return a user-friendly message for an error code."""
    return USER_FRIENDLY_MESSAGES.get(code, fallback_message)
