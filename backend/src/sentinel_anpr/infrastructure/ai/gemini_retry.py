"""Retry policy helpers for transient Gemini Vision API failures."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

TRANSIENT_HTTP_CODES = frozenset({429, 500, 502, 503, 504})
NON_RETRY_HTTP_CODES = frozenset({400, 401, 403, 404})
DEFAULT_MAX_RETRIES = 5
DEFAULT_REQUEST_TIMEOUT_MS = 60_000
VISION_UNAVAILABLE_MESSAGE = (
    "Vision AI service is temporarily unavailable due to high demand. "
    "Please try again in a few moments."
)


@dataclass(frozen=True)
class GeminiErrorDetails:
    """Normalized Gemini API error fields for logging and retry decisions."""

    status_code: int | None
    status: str | None
    message: str


def parse_gemini_error(exc: BaseException) -> GeminiErrorDetails:
    """Extract HTTP status and message from a Gemini SDK or compatible error."""
    status_code = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    message = getattr(exc, "message", None)

    if status_code is not None:
        try:
            status_code = int(status_code)
        except (TypeError, ValueError):
            status_code = None

    if not message:
        message = str(exc)

    try:
        from google.genai import errors as genai_errors

        if isinstance(exc, genai_errors.APIError):
            status_code = int(exc.code) if exc.code is not None else status_code
            status = exc.status or status
            message = exc.message or message
    except ImportError:
        pass

    return GeminiErrorDetails(
        status_code=status_code,
        status=str(status) if status is not None else None,
        message=str(message),
    )


def is_retryable_gemini_error(exc: BaseException) -> bool:
    """Return True only for transient Gemini HTTP errors that should be retried."""
    details = parse_gemini_error(exc)
    if details.status_code in NON_RETRY_HTTP_CODES:
        return False
    return details.status_code in TRANSIENT_HTTP_CODES


def is_model_fallback_candidate(exc: BaseException) -> bool:
    """Return True when repeated 503 errors should trigger the next configured model."""
    return parse_gemini_error(exc).status_code == 503


def retry_delay_seconds(attempt_number: int) -> float:
    """Exponential backoff delay before retry attempt (1 -> 1s, 5 -> 16s) with jitter."""
    if attempt_number < 1:
        return 0.0
    base_delay = float(2 ** (attempt_number - 1))
    jitter = random.uniform(0.0, base_delay * 0.1)
    return base_delay + jitter


def build_model_chain(primary_model: str, fallback_models: list[str] | None = None) -> list[str]:
    """Deduplicate primary and fallback Gemini model identifiers."""
    chain: list[str] = []
    seen: set[str] = set()
    for candidate in [primary_model, *(fallback_models or [])]:
        normalized = str(candidate).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        chain.append(normalized)
    return chain


def parse_fallback_models(raw: str | None) -> list[str]:
    """Parse a comma-separated fallback model list from settings."""
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def transient_failure_message(exc: BaseException) -> str:
    """User-facing message after all retries are exhausted for transient errors."""
    del exc
    return VISION_UNAVAILABLE_MESSAGE


def format_retry_progress_message(attempt: int, max_retries: int) -> str:
    """Build a progress message shown while a retry is scheduled."""
    return f"Retrying ({attempt}/{max_retries})..."
