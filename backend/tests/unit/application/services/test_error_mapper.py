"""Error mapper unit tests."""

from sentinel_anpr.application.services.error_mapper import to_user_message


def test_to_user_message_returns_friendly_text_for_known_codes() -> None:
    message = to_user_message("AUTH_INVALID", "raw message")
    assert "sign in again" in message.lower()


def test_to_user_message_falls_back_to_original_message() -> None:
    message = to_user_message("UNKNOWN_CODE", "Specific failure detail")
    assert message == "Specific failure detail"
