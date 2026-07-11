"""Hugging Face Inference API adapter implementing the VisionAiService port."""

from __future__ import annotations

import base64
import hashlib
import io
import time
from collections.abc import Callable
from typing import Any

import httpx

from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import (
    VisionAnalysisResult,
    VisionAiService,
    VisibleVehicleCountResult,
)
from sentinel_anpr.infrastructure.ai.huggingface_error import (
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    SERVICE_BUSY_RETRY_DELAY_SECONDS,
    format_vision_error_message,
    parse_response_error,
)
from sentinel_anpr.infrastructure.ai.vision_response_parser import parse_vehicle_count_json, parse_vision_json
from sentinel_anpr.infrastructure.config.settings import resolve_hf_api_url, resolve_hf_token

_DEFAULT_MODEL = "google/gemma-3-4b-it:deepinfra"
_TOKEN_ENV_VAR = "HF_TOKEN"

_ANALYSIS_PROMPT = (
    "Analyze this vehicle image.\n"
    "Return ONLY valid JSON.\n"
    "Schema:\n"
    "{\n"
    '  "registration_number": "",\n'
    '  "vehicle_color": "",\n'
    '  "vehicle_type": "",\n'
    '  "brand": "",\n'
    '  "model": "",\n'
    '  "confidence": 0.95,\n'
    '  "explanation": ""\n'
    "}\n"
    "In explanation, note scene context, any visible damage or modifications, and any "
    "uncertainties. Use empty strings for attributes that are not visible.\n"
    "Keep explanation to one short sentence (under 120 characters).\n"
    "No markdown.\n"
    "No extra text."
)

_VEHICLE_COUNT_PROMPT = (
    "Count every fully or partially visible vehicle in this image.\n"
    "Return ONLY valid JSON.\n"
    "Schema:\n"
    "{\n"
    '  "vehicle_count": 1,\n'
    '  "vehicles": [\n'
    '    { "type": "motorcycle" }\n'
    "  ]\n"
    "}\n"
    "Rules:\n"
    "- vehicle_count must equal the number of items in vehicles.\n"
    "- type must be a short vehicle category such as car, motorcycle, truck, bus, auto, or suv.\n"
    "- Do not include registration numbers, colors, brands, or investigation details.\n"
    "- Do not guess hidden vehicles.\n"
    "No markdown.\n"
    "No extra text."
)


class HuggingFaceVisionService(VisionAiService):
    """Analyze vehicle images using the Hugging Face Inference API."""

    def __init__(
        self,
        *,
        token: str | None = None,
        model: str = _DEFAULT_MODEL,
        api_url: str | None = None,
        request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        client: httpx.Client | None = None,
        logger: LoggingPort | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self._model = model or _DEFAULT_MODEL
        self._api_url = (api_url or "").strip() or resolve_hf_api_url(
            model=self._model,
            api_url=None,
        )
        self._request_timeout_seconds = max(1.0, float(request_timeout_seconds))
        self._token = (token or resolve_hf_token() or "").strip() or None
        self._logger = logger
        self._sleep = sleep_fn or time.sleep
        self._client = client or httpx.Client(timeout=self._request_timeout_seconds)
        self._init_failure_reason: str | None = None

        if not self._token:
            self._init_failure_reason = (
                f"{_TOKEN_ENV_VAR} is not set. "
                "Create backend/.env from .env.example and set HF_TOKEN, "
                "or set SENTINEL_VISION_PROVIDER=stub for local development."
            )
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vision_init_failed",
                    reason=self._init_failure_reason,
                )

    @property
    def is_ready(self) -> bool:
        return self._token is not None

    @property
    def init_failure_reason(self) -> str | None:
        return self._init_failure_reason

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        if not image_bytes:
            return self._empty("Image file is empty.")

        if self._token is None:
            reason = self._init_failure_reason or "Hugging Face client was not initialized."
            if self._logger is not None:
                self._logger.error("huggingface_vision_not_ready", reason=reason)
            return self._empty(reason)

        original_size = self._image_dimensions(image_bytes)
        mime_type = self._detect_mime_type(image_bytes)
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        width, height = self._image_width_height(image_bytes)
        if self._logger is not None:
            self._logger.info(
                "huggingface_vision_request_start",
                vision_provider="huggingface",
                model=self._model,
                api_url=self._api_url,
                image_size=original_size,
                image_width=width,
                image_height=height,
                image_bytes=len(image_bytes),
                mime_type=mime_type,
                sha256_before_hf=sha256_hash,
                sha256_sent_to_hf=sha256_hash,
                detail="Upload image bytes sent to Hugging Face without preprocessing",
            )

        started = time.perf_counter()
        payload = self._build_request_payload(image_bytes, mime_type)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        response, failure_message = self._post_with_optional_service_busy_retry(
            payload=payload,
            headers=headers,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        if failure_message is not None:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vision_request_failed",
                    model=self._model,
                    latency_ms=latency_ms,
                    error_message=failure_message,
                    detail="Vision request failed",
                )
            return self._empty(f"Vision analysis request failed: {failure_message}")

        raw_text = self._extract_output_text(response)
        if not raw_text:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vision_empty_response",
                    latency_ms=latency_ms,
                    detail="Vision request completed with empty response",
                )
            return self._empty("Vision model returned no output.")

        result = self._parse(raw_text)
        if self._logger is not None:
            self._logger.info(
                "huggingface_vision_request_completed",
                detail="Vision request completed",
                latency_ms=latency_ms,
                model=self._model,
                confidence=result.confidence,
                registration_number=result.registration_number,
            )
        return result

    def count_visible_vehicles(self, image_bytes: bytes) -> VisibleVehicleCountResult:
        if not image_bytes:
            return self._empty_vehicle_count("Image file is empty.")

        if self._token is None:
            reason = self._init_failure_reason or "Hugging Face client was not initialized."
            if self._logger is not None:
                self._logger.error("huggingface_vehicle_count_not_ready", reason=reason)
            return self._empty_vehicle_count(reason)

        mime_type = self._detect_mime_type(image_bytes)
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        width, height = self._image_width_height(image_bytes)
        if self._logger is not None:
            self._logger.info(
                "huggingface_vehicle_count_request_start",
                vision_provider="huggingface",
                model=self._model,
                api_url=self._api_url,
                image_width=width,
                image_height=height,
                image_bytes=len(image_bytes),
                mime_type=mime_type,
                sha256_before_hf=sha256_hash,
                detail="Original upload image sent to Hugging Face for visible vehicle counting only",
            )

        started = time.perf_counter()
        payload = self._build_request_payload(image_bytes, mime_type, prompt=_VEHICLE_COUNT_PROMPT)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        response, failure_message = self._post_with_optional_service_busy_retry(
            payload=payload,
            headers=headers,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        if failure_message is not None:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vehicle_count_request_failed",
                    model=self._model,
                    latency_ms=latency_ms,
                    error_message=failure_message,
                )
            return self._empty_vehicle_count(f"Vehicle count request failed: {failure_message}")

        raw_text = self._extract_output_text(response)
        if not raw_text:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vehicle_count_empty_response",
                    latency_ms=latency_ms,
                )
            return self._empty_vehicle_count("Vision model returned no vehicle count output.")

        result = self._parse_vehicle_count(raw_text)
        if self._logger is not None:
            self._logger.info(
                "huggingface_vehicle_count_request_completed",
                latency_ms=latency_ms,
                model=self._model,
                vehicle_count=result.vehicle_count,
                vehicle_types=list(result.vehicles),
            )
        return result

    def _post_with_optional_service_busy_retry(
        self,
        *,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> tuple[dict[str, Any] | None, str | None]:
        response, transport_error = self._post_once(payload=payload, headers=headers)
        if transport_error is not None:
            return None, transport_error
        if response is None:
            return None, "No response received from Hugging Face API."

        if response.status_code == 503:
            if self._logger is not None:
                self._logger.warning(
                    "huggingface_vision_service_busy_retry",
                    model=self._model,
                    retry_delay_seconds=SERVICE_BUSY_RETRY_DELAY_SECONDS,
                )
            self._sleep(SERVICE_BUSY_RETRY_DELAY_SECONDS)
            response, transport_error = self._post_once(payload=payload, headers=headers)
            if transport_error is not None:
                return None, transport_error
            if response is None:
                return None, "Service Busy: No response received from Hugging Face API."

        if response.is_success:
            try:
                body = response.json()
            except ValueError as exc:
                return None, f"Invalid JSON response from Hugging Face API: {exc}"
            if isinstance(body, dict):
                return body, None
            return {"data": body}, None

        details = parse_response_error(response.status_code, response.text)
        return None, format_vision_error_message(details)

    def _post_once(
        self,
        *,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> tuple[httpx.Response | None, str | None]:
        if self._logger is not None:
            self._logger.info(
                "huggingface_vision_single_request",
                model=self._model,
                api_url=self._api_url,
            )
        try:
            return self._client.post(self._api_url, headers=headers, json=payload), None
        except httpx.TimeoutException as exc:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vision_request_timeout",
                    model=self._model,
                    error=str(exc),
                )
            return None, "Request timed out waiting for Hugging Face API."
        except httpx.HTTPError as exc:
            if self._logger is not None:
                self._logger.error(
                    "huggingface_vision_transport_error",
                    model=self._model,
                    error=str(exc),
                )
            return None, str(exc)

    def _build_request_payload(
        self,
        image_bytes: bytes,
        mime_type: str,
        *,
        prompt: str = _ANALYSIS_PROMPT,
    ) -> dict[str, Any]:
        image_data_url = self._to_data_url(image_bytes, mime_type)
        if self._uses_chat_completions_api():
            return {
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_data_url}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": 1024,
                "temperature": 0.1,
            }

        return {
            "inputs": {
                "text": prompt,
                "image": image_data_url,
            },
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.1,
                "return_full_text": False,
            },
        }

    def _uses_chat_completions_api(self) -> bool:
        lowered = self._api_url.lower()
        return "chat/completions" in lowered or lowered.endswith("/v1/chat/completions")

    @staticmethod
    def _to_data_url(image_bytes: bytes, mime_type: str) -> str:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _extract_output_text(response_body: dict[str, Any]) -> str | None:
        choices = response_body.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str) and content.strip():
                        return content.strip()

        data = response_body.get("data")
        if isinstance(data, list) and data:
            return HuggingFaceVisionService._extract_output_text_from_item(data[0])
        if isinstance(data, dict):
            return HuggingFaceVisionService._extract_output_text_from_item(data)

        return HuggingFaceVisionService._extract_output_text_from_item(response_body)

    @staticmethod
    def _extract_output_text_from_item(item: Any) -> str | None:
        if isinstance(item, str) and item.strip():
            return item.strip()
        if not isinstance(item, dict):
            return None

        for key in ("generated_text", "summary_text", "answer", "text"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    def _image_dimensions(image_bytes: bytes) -> str | None:
        width, height = HuggingFaceVisionService._image_width_height(image_bytes)
        if width is None or height is None:
            return None
        return f"{width}x{height}"

    @staticmethod
    def _image_width_height(image_bytes: bytes) -> tuple[int | None, int | None]:
        try:
            from PIL import Image

            with Image.open(io.BytesIO(image_bytes)) as image:
                return image.width, image.height
        except Exception:
            return None, None

    @staticmethod
    def _detect_mime_type(image_bytes: bytes) -> str:
        try:
            from PIL import Image

            with Image.open(io.BytesIO(image_bytes)) as image:
                format_name = (image.format or "").upper()
                if format_name == "PNG":
                    return "image/png"
                if format_name == "WEBP":
                    return "image/webp"
                if format_name in {"JPEG", "JPG"}:
                    return "image/jpeg"
        except Exception:
            pass
        return "application/octet-stream"

    def _parse(self, raw_text: str) -> VisionAnalysisResult:
        payload = parse_vision_json(raw_text)
        if payload is None:
            if self._logger is not None:
                self._logger.warning(
                    "huggingface_vision_parse_failed",
                    raw=raw_text[:500],
                    detail="Malformed JSON from Hugging Face Vision",
                )
            return self._empty("Unable to parse vision model response.")

        return VisionAnalysisResult(
            registration_number=self._as_str(payload.get("registration_number")),
            vehicle_color=self._as_str(payload.get("vehicle_color")),
            vehicle_type=self._as_str(payload.get("vehicle_type")),
            brand=self._as_str(payload.get("brand")),
            model=self._as_str(payload.get("model")),
            confidence=self._as_float(payload.get("confidence")),
            explanation=self._as_str(payload.get("explanation")),
        )

    def _parse_vehicle_count(self, raw_text: str) -> VisibleVehicleCountResult:
        payload = parse_vehicle_count_json(raw_text)
        if payload is None:
            if self._logger is not None:
                self._logger.warning(
                    "huggingface_vehicle_count_parse_failed",
                    raw=raw_text[:500],
                )
            return self._empty_vehicle_count("Unable to parse vehicle count response.")

        vehicles_payload = payload.get("vehicles")
        vehicle_types: list[str] = []
        if isinstance(vehicles_payload, list):
            for item in vehicles_payload:
                if isinstance(item, dict):
                    vehicle_type = self._as_str(item.get("type"))
                    if vehicle_type is not None:
                        vehicle_types.append(vehicle_type)

        vehicle_count = self._as_int(payload.get("vehicle_count"))
        if vehicle_count is None:
            vehicle_count = len(vehicle_types)

        if vehicle_count < 0:
            vehicle_count = 0
        if vehicle_types and vehicle_count < len(vehicle_types):
            vehicle_count = len(vehicle_types)
        if vehicle_count > 0 and not vehicle_types:
            vehicle_types = ["vehicle"] * vehicle_count

        return VisibleVehicleCountResult(
            vehicle_count=vehicle_count,
            vehicles=tuple(vehicle_types),
        )

    @staticmethod
    def _as_str(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _as_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _as_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _empty(explanation: str) -> VisionAnalysisResult:
        return VisionAnalysisResult(
            registration_number=None,
            vehicle_color=None,
            vehicle_type=None,
            brand=None,
            model=None,
            confidence=None,
            explanation=explanation,
        )

    @staticmethod
    def _empty_vehicle_count(explanation: str) -> VisibleVehicleCountResult:
        return VisibleVehicleCountResult(
            vehicle_count=0,
            vehicles=(),
            explanation=explanation,
        )
