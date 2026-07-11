"""Unit tests for HuggingFaceVisionService infrastructure adapter."""

from __future__ import annotations

from io import BytesIO

import httpx
from PIL import Image

from sentinel_anpr.infrastructure.ai.huggingface_vision_service import HuggingFaceVisionService


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


class _FakeTransport(httpx.BaseTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self._responses = list(responses)
        self.calls = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        del request
        self.calls += 1
        if not self._responses:
            raise RuntimeError("No fake responses left")
        return self._responses.pop(0)


def _jpeg_bytes(width: int = 800, height: int = 600) -> bytes:
    image = Image.new("RGB", (width, height), color=(30, 90, 180))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _chat_response(text: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": text,
                    }
                }
            ]
        },
    )


def test_huggingface_sends_original_bytes_without_preprocessing() -> None:
    logger = _FakeLogger()
    original_bytes = _jpeg_bytes(width=1800, height=1200)
    captured_payload: dict[str, object] = {}

    class _CapturingTransport(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            captured_payload["body"] = request.content
            return _chat_response(
                '{"registration_number":"KL02AR4411","vehicle_color":"white",'
                '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
                '"confidence":0.91,"explanation":"Clear front plate"}'
            )

    client = httpx.Client(transport=_CapturingTransport())
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        logger=logger,
        api_url="https://router.huggingface.co/v1/chat/completions",
    )

    result = service.analyze_vehicle_image(original_bytes)

    assert result.registration_number == "KL02AR4411"
    start_logs = [context for message, context in logger.infos if message == "huggingface_vision_request_start"]
    assert start_logs
    assert start_logs[0]["image_width"] == 1800
    assert start_logs[0]["image_height"] == 1200
    assert start_logs[0]["sha256_before_hf"] == start_logs[0]["sha256_sent_to_hf"]
    assert start_logs[0]["image_bytes"] == len(original_bytes)


def test_huggingface_parses_valid_json_into_vision_result() -> None:
    logger = _FakeLogger()
    transport = _FakeTransport(
        [
            _chat_response(
                '{"registration_number":"KL02AR4411","vehicle_color":"white",'
                '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
                '"confidence":0.91,"explanation":"Clear front plate"}'
            )
        ]
    )
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        logger=logger,
        api_url="https://router.huggingface.co/v1/chat/completions",
    )

    result = service.analyze_vehicle_image(_jpeg_bytes())

    assert transport.calls == 1
    assert result.registration_number == "KL02AR4411"
    assert result.vehicle_color == "white"
    assert result.brand == "Toyota"
    assert result.confidence == 0.91
    assert any(msg == "huggingface_vision_request_completed" for msg, _ in logger.infos)


def test_huggingface_fails_immediately_on_401_without_retry() -> None:
    transport = _FakeTransport(
        [httpx.Response(401, json={"error": {"message": "Invalid credentials"}})]
    )
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        api_url="https://router.huggingface.co/v1/chat/completions",
    )

    result = service.analyze_vehicle_image(_jpeg_bytes())

    assert transport.calls == 1
    assert "Authentication Error" in (result.explanation or "")


def test_huggingface_fails_immediately_on_429_without_retry() -> None:
    transport = _FakeTransport(
        [httpx.Response(429, json={"error": {"message": "Rate limited"}})]
    )
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        api_url="https://router.huggingface.co/v1/chat/completions",
    )

    result = service.analyze_vehicle_image(_jpeg_bytes())

    assert transport.calls == 1
    assert "Rate Limit Exceeded" in (result.explanation or "")


def test_huggingface_retries_503_only_once() -> None:
    sleeps: list[float] = []
    transport = _FakeTransport(
        [
            httpx.Response(503, json={"error": {"message": "Model is loading"}}),
            _chat_response(
                '{"registration_number":"AP09AB1234","vehicle_color":"white",'
                '"vehicle_type":"car","brand":"Toyota","model":"Innova",'
                '"confidence":0.91,"explanation":"Clear front plate"}'
            ),
        ]
    )
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        api_url="https://router.huggingface.co/v1/chat/completions",
        sleep_fn=sleeps.append,
    )

    result = service.analyze_vehicle_image(_jpeg_bytes())

    assert transport.calls == 2
    assert len(sleeps) == 1
    assert result.registration_number == "AP09AB1234"


def test_huggingface_empty_image() -> None:
    transport = _FakeTransport([])
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(token="hf-test-token", client=client)

    result = service.analyze_vehicle_image(b"")

    assert transport.calls == 0
    assert result.explanation == "Image file is empty."


def test_huggingface_counts_visible_vehicles_from_original_image() -> None:
    transport = _FakeTransport(
        [
            _chat_response(
                '{"vehicle_count":3,"vehicles":[{"type":"motorcycle"},{"type":"motorcycle"},{"type":"motorcycle"}]}'
            )
        ]
    )
    client = httpx.Client(transport=transport)
    service = HuggingFaceVisionService(
        token="hf-test-token",
        client=client,
        api_url="https://router.huggingface.co/v1/chat/completions",
    )

    result = service.count_visible_vehicles(_jpeg_bytes())

    assert transport.calls == 1
    assert result.vehicle_count == 3
    assert list(result.vehicles) == ["motorcycle", "motorcycle", "motorcycle"]
