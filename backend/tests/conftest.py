"""Shared image fixtures and test environment."""

import io

import pytest
from PIL import Image

from sentinel_anpr.infrastructure.config.settings import get_settings


@pytest.fixture(autouse=True)
def use_stub_ai_adapters_in_tests(monkeypatch: pytest.MonkeyPatch):
    """Use the deterministic stub vision service for tests (no API key)."""
    monkeypatch.setenv("SENTINEL_VISION_PROVIDER", "stub")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def jpeg_bytes() -> bytes:
    image = Image.new("RGB", (800, 600), color=(30, 90, 180))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()
