"""Unit tests for Hugging Face vision error helpers."""

from sentinel_anpr.infrastructure.ai.huggingface_error import (
    format_vision_error_message,
    parse_response_error,
)


def test_parse_response_error_from_json_body() -> None:
    details = parse_response_error(
        401,
        '{"error":{"message":"Invalid credentials"}}',
    )
    assert details.status_code == 401
    assert details.message == "Invalid credentials"


def test_format_vision_error_message_for_401() -> None:
    message = format_vision_error_message(
        parse_response_error(401, '{"error":"Unauthorized"}'),
    )
    assert message.startswith("Authentication Error:")


def test_format_vision_error_message_for_429() -> None:
    message = format_vision_error_message(
        parse_response_error(429, '{"error":"Too Many Requests"}'),
    )
    assert message.startswith("Rate Limit Exceeded:")


def test_format_vision_error_message_for_503() -> None:
    message = format_vision_error_message(
        parse_response_error(503, '{"error":"Model is loading"}'),
    )
    assert message.startswith("Service Busy:")
