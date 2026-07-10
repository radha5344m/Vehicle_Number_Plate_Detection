"""Tests for backend/.env loading precedence."""

import os

import pytest

from sentinel_anpr.infrastructure.config.settings import (
    get_settings,
    load_env_file,
)


def test_load_env_file_overrides_stale_process_env_outside_pytest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """backend/.env must win over a stale SENTINEL_VISION_PROVIDER in the shell."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("SENTINEL_VISION_PROVIDER", "stub")
    get_settings.cache_clear()

    load_env_file()
    settings = get_settings()

    assert settings.vision_provider.strip().lower() == "huggingface"


def test_load_env_file_preserves_pytest_stub_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """During pytest, the autouse stub fixture must remain effective."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/unit/test_example.py::test_x")
    monkeypatch.setenv("SENTINEL_VISION_PROVIDER", "stub")
    get_settings.cache_clear()

    load_env_file()
    settings = get_settings()

    assert settings.vision_provider.strip().lower() == "stub"


def test_running_under_pytest_detected() -> None:
  assert os.getenv("PYTEST_CURRENT_TEST") is not None
