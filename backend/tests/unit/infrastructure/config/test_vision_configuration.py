"""Configuration management tests for Gemini vision settings."""

import pytest

from sentinel_anpr.infrastructure.config.settings import (
    MissingGeminiApiKeyError,
    Settings,
    validate_vision_configuration,
)


def test_validate_vision_configuration_requires_gemini_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sentinel_anpr.infrastructure.config.settings.resolve_gemini_api_key",
        lambda _settings=None: None,
    )
    settings = Settings(vision_provider="gemini", gemini_api_key=None)
    with pytest.raises(MissingGeminiApiKeyError, match="GEMINI_API_KEY is not set"):
        validate_vision_configuration(settings)


def test_validate_vision_configuration_passes_with_key() -> None:
    settings = Settings(
        vision_provider="gemini",
        gemini_api_key="test-key",
        gemini_model="gemini-2.5-flash",
    )
    validate_vision_configuration(settings)


def test_validate_vision_configuration_skipped_for_stub() -> None:
    settings = Settings(vision_provider="stub", gemini_api_key=None)
    validate_vision_configuration(settings)


def test_default_gemini_model() -> None:
    settings = Settings(vision_provider="stub")
    assert settings.gemini_model == "gemini-2.5-flash"


def test_settings_have_no_openai_fields() -> None:
    """OPENAI_API_KEY must not be a Settings field or validation dependency."""
    field_names = set(Settings.model_fields)
    assert "openai_api_key" not in field_names
    assert not any("openai" in name.lower() for name in field_names)
