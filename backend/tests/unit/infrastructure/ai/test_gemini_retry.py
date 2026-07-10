"""Unit tests for Gemini retry policy helpers."""

from __future__ import annotations

import pytest
from google.genai import errors

from sentinel_anpr.infrastructure.ai.gemini_retry import (
    VISION_UNAVAILABLE_MESSAGE,
    build_model_chain,
    is_retryable_gemini_error,
    parse_fallback_models,
    parse_gemini_error,
    retry_delay_seconds,
)


def _api_error(status_code: int, *, status: str, message: str) -> errors.APIError:
    if 400 <= status_code < 500:
        error_cls = errors.ClientError
    elif 500 <= status_code < 600:
        error_cls = errors.ServerError
    else:
        error_cls = errors.APIError
    return error_cls(
        status_code,
        {"error": {"code": status_code, "message": message, "status": status}},
        None,
    )


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (503, True),
        (429, True),
        (500, True),
        (502, True),
        (504, True),
        (400, False),
        (401, False),
        (403, False),
        (404, False),
    ],
)
def test_is_retryable_gemini_error(status_code: int, expected: bool) -> None:
    exc = _api_error(status_code, status="ERROR", message="failure")
    assert is_retryable_gemini_error(exc) is expected


def test_parse_gemini_error_extracts_fields() -> None:
    exc = _api_error(503, status="UNAVAILABLE", message="high demand")
    details = parse_gemini_error(exc)
    assert details.status_code == 503
    assert details.status == "UNAVAILABLE"
    assert details.message == "high demand"


def test_retry_delay_seconds_uses_exponential_backoff() -> None:
    assert retry_delay_seconds(1) >= 1.0
    assert retry_delay_seconds(2) >= 2.0
    assert retry_delay_seconds(5) >= 16.0


def test_build_model_chain_deduplicates_models() -> None:
    chain = build_model_chain(
        "gemini-2.5-flash",
        ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"],
    )
    assert chain == ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def test_parse_fallback_models() -> None:
    assert parse_fallback_models("a, b,,c") == ["a", "b", "c"]


def test_transient_failure_message_constant() -> None:
    assert "temporarily unavailable" in VISION_UNAVAILABLE_MESSAGE.lower()
