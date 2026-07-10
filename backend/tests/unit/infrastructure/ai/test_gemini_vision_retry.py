"""Unit tests for GeminiVisionService retry behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from google.genai import errors

from sentinel_anpr.infrastructure.ai.gemini_retry import VISION_UNAVAILABLE_MESSAGE
from sentinel_anpr.infrastructure.ai.gemini_vision_service import GeminiVisionService
from sentinel_anpr.infrastructure.ai.vision_progress_store import (
    bind_vision_progress,
    clear_vision_progress,
    get_vision_progress,
)


class _FakeLogger:
    def __init__(self) -> None:
        self.infos: list[tuple[str, dict]] = []
        self.errors: list[tuple[str, dict]] = []
        self.warnings: list[tuple[str, dict]] = []

    def info(self, message: str, **context) -> None:
        self.infos.append((message, context))

    def error(self, message: str, **context) -> None:
        self.errors.append((message, context))

    def warning(self, message: str, **context) -> None:
        self.warnings.append((message, context))

    def debug(self, message: str, **context) -> None:
        del message, context


def _server_error(code: int, message: str, status: str = "UNAVAILABLE") -> errors.ServerError:
    return errors.ServerError(
        code,
        {"error": {"code": code, "message": message, "status": status}},
        None,
    )


def _client_error(code: int, message: str, status: str) -> errors.ClientError:
    return errors.ClientError(
        code,
        {"error": {"code": code, "message": message, "status": status}},
        None,
    )


class _FakeModels:
    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = list(outcomes)
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class _FakeClient:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models


def _success_response() -> SimpleNamespace:
    return SimpleNamespace(
        text=(
            '{"registration_number":"AP09AB1234","vehicle_color":"white",'
            '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
            '"confidence":0.91,"explanation":"Clear front plate"}'
        )
    )


def test_gemini_retries_503_until_success() -> None:
    sleeps: list[float] = []
    models = _FakeModels(
        [
            _server_error(503, "high demand"),
            _server_error(503, "high demand"),
            _success_response(),
        ]
    )
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        sleep_fn=sleeps.append,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 3
    assert len(sleeps) == 2
    assert result.registration_number == "AP09AB1234"


def test_gemini_retries_429_until_success() -> None:
    models = _FakeModels([_client_error(429, "quota", "RESOURCE_EXHAUSTED"), _success_response()])
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 2
    assert result.registration_number == "AP09AB1234"


def test_gemini_retries_500_until_success() -> None:
    models = _FakeModels([_server_error(500, "internal", "INTERNAL"), _success_response()])
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 2
    assert result.registration_number == "AP09AB1234"


def test_gemini_does_not_retry_400() -> None:
    models = _FakeModels([_client_error(400, "bad request", "INVALID_ARGUMENT")])
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 1
    assert "Vision analysis request failed" in (result.explanation or "")


def test_gemini_does_not_retry_403() -> None:
    models = _FakeModels([_client_error(403, "forbidden", "PERMISSION_DENIED")])
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 1
    assert result.registration_number is None


def test_gemini_returns_unavailable_message_after_exhausted_503_retries() -> None:
    models = _FakeModels([_server_error(503, "high demand")] * 6)
    service = GeminiVisionService(
        client=_FakeClient(models),
        max_retries=5,
        fallback_models=[],
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 6
    assert result.explanation == VISION_UNAVAILABLE_MESSAGE


def test_gemini_switches_model_after_repeated_503() -> None:
    models = _FakeModels([_server_error(503, "high demand")] * 6 + [_success_response()])
    service = GeminiVisionService(
        client=_FakeClient(models),
        model="gemini-2.5-flash",
        fallback_models=["gemini-2.0-flash"],
        max_retries=5,
        sleep_fn=lambda _delay: None,
    )

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 7
    assert result.registration_number == "AP09AB1234"


def test_gemini_updates_progress_store_during_retries() -> None:
    correlation_id = "test-correlation"
    bind_vision_progress(correlation_id, max_attempts=5)
    try:
        models = _FakeModels([_server_error(503, "high demand"), _success_response()])
        service = GeminiVisionService(
            client=_FakeClient(models),
            max_retries=5,
            sleep_fn=lambda _delay: None,
        )
        service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")
        snapshot = get_vision_progress(correlation_id)
        assert snapshot is not None
        assert snapshot.phase == "completed"
    finally:
        clear_vision_progress(correlation_id)
