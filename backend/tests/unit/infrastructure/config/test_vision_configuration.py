"""Configuration management tests for Hugging Face vision settings."""

import pytest

from sentinel_anpr.infrastructure.config.settings import (
    MissingHuggingFaceTokenError,
    Settings,
    resolve_hf_api_url,
    validate_vision_configuration,
)


def test_validate_vision_configuration_requires_hf_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sentinel_anpr.infrastructure.config.settings.resolve_hf_token",
        lambda _settings=None: None,
    )
    settings = Settings(vision_provider="huggingface", hf_token=None)
    with pytest.raises(MissingHuggingFaceTokenError, match="HF_TOKEN is not set"):
        validate_vision_configuration(settings)


def test_validate_vision_configuration_passes_with_token() -> None:
    settings = Settings(
        vision_provider="huggingface",
        hf_token="hf_test_token",
        hf_model="Qwen/Qwen2.5-VL-7B-Instruct",
    )
    validate_vision_configuration(settings)


def test_validate_vision_configuration_skipped_for_stub() -> None:
    settings = Settings(vision_provider="stub", hf_token=None)
    validate_vision_configuration(settings)


def test_default_hf_model() -> None:
    settings = Settings(vision_provider="stub")
    assert settings.hf_model == "google/gemma-3-4b-it:deepinfra"


def test_resolve_hf_api_url_replaces_model_placeholder() -> None:
    settings = Settings(
        hf_model="org/custom-model",
        hf_api_url="https://api-inference.huggingface.co/models/{model}",
    )
    assert (
        resolve_hf_api_url(settings=settings)
        == "https://api-inference.huggingface.co/models/org/custom-model"
    )


def test_settings_have_no_openai_fields() -> None:
    """OPENAI_API_KEY must not be a Settings field or validation dependency."""
    field_names = set(Settings.model_fields)
    assert "openai_api_key" not in field_names
    assert not any("openai" in name.lower() for name in field_names)
