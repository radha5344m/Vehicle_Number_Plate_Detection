"""Unit tests for GeminiVisionService infrastructure adapter."""

from __future__ import annotations

from types import SimpleNamespace

from sentinel_anpr.infrastructure.ai.gemini_vision_service import GeminiVisionService


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


class _FakeModels:
    def __init__(self, response_text: str | None = None, error: Exception | None = None) -> None:
        self.response_text = response_text
        self.error = error
        self.calls = 0

    def generate_content(self, **kwargs):
        del kwargs
        self.calls += 1
        if self.error is not None:
            raise self.error
        return SimpleNamespace(text=self.response_text)


class _FakeClient:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models


def test_gemini_parses_valid_json_into_vision_result() -> None:
    logger = _FakeLogger()
    models = _FakeModels(
        response_text=(
            '{"registration_number":"KL02AR4411","vehicle_color":"white",'
            '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
            '"confidence":0.91,"explanation":"Clear front plate"}'
        )
    )
    service = GeminiVisionService(client=_FakeClient(models), logger=logger, model="gemini-2.5-flash")

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert models.calls == 1
    assert result.registration_number == "KL02AR4411"
    assert result.vehicle_color == "white"
    assert result.vehicle_type == "car"
    assert result.brand == "Toyota"
    assert result.model == "Innova"
    assert result.confidence == 0.91
    assert result.explanation == "Clear front plate"
    assert any(msg == "gemini_vision_request_start" for msg, _ in logger.infos)
    assert any(msg == "gemini_vision_request_completed" for msg, _ in logger.infos)


def test_gemini_handles_trailing_json_noise() -> None:
    models = _FakeModels(
        response_text=(
            '{"registration_number":"AP09AB1234","vehicle_color":"white",'
            '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
            '"confidence":0.91,"explanation":"Clear front plate"}\n}'
        )
    )
    service = GeminiVisionService(client=_FakeClient(models))

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert result.registration_number == "AP09AB1234"
    assert result.brand == "Toyota"


def test_gemini_handles_malformed_json_gracefully() -> None:
    models = _FakeModels(response_text="not-json at all")
    service = GeminiVisionService(client=_FakeClient(models))

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert result.registration_number is None
    assert result.explanation == "Unable to parse vision model response."


def test_gemini_strips_markdown_fences() -> None:
    models = _FakeModels(
        response_text=(
            "```json\n"
            '{"registration_number":"AP09AB1234","vehicle_color":"black",'
            '"vehicle_type":"car","brand":"Honda","model":"City",'
            '"confidence":0.8,"explanation":"ok"}\n'
            "```"
        )
    )
    service = GeminiVisionService(client=_FakeClient(models))

    result = service.analyze_vehicle_image(b"\xff\xd8\xfffake-jpeg")

    assert result.registration_number == "AP09AB1234"
    assert result.brand == "Honda"


def test_gemini_empty_image() -> None:
    service = GeminiVisionService(client=_FakeClient(_FakeModels()))
    result = service.analyze_vehicle_image(b"")
    assert result.registration_number is None
    assert result.explanation == "Image file is empty."
