"""Gemini Vision adapter implementing the VisionAiService port.

Uses the official Google GenAI SDK to analyze a vehicle image and return a
strongly typed :class:`VisionAnalysisResult`. This adapter is infrastructure-
only: it does not touch business logic, use cases, or controllers.
"""

from __future__ import annotations

import io
import json
import time
from collections.abc import Callable
from typing import Any

from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import (
    VisionAnalysisResult,
    VisionAiService,
)
from sentinel_anpr.infrastructure.ai.gemini_retry import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_REQUEST_TIMEOUT_MS,
    build_model_chain,
    format_retry_progress_message,
    is_model_fallback_candidate,
    is_retryable_gemini_error,
    parse_gemini_error,
    retry_delay_seconds,
    transient_failure_message,
)
from sentinel_anpr.infrastructure.ai.vision_progress_store import update_vision_progress
from sentinel_anpr.infrastructure.config.settings import resolve_gemini_api_key

_DEFAULT_MODEL = "gemini-2.5-flash"
_API_KEY_ENV_VAR = "GEMINI_API_KEY"

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
    "No markdown.\n"
    "No extra text."
)


class GeminiVisionService(VisionAiService):
    """Analyze vehicle images using Google Gemini multimodal vision."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        fallback_models: list[str] | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_MS / 1000,
        client: Any | None = None,
        logger: LoggingPort | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self._model = model or _DEFAULT_MODEL
        self._model_chain = build_model_chain(self._model, fallback_models)
        self._max_retries = max(0, int(max_retries))
        self._request_timeout_ms = max(1, int(request_timeout_seconds * 1000))
        self._sleep = sleep_fn or time.sleep
        self._logger = logger
        if api_key and str(api_key).strip():
            resolved_key = str(api_key).strip().strip('"').strip("'")
        else:
            resolved_key = resolve_gemini_api_key()
        self._api_key = resolved_key or None
        self._client: Any | None = None
        self._init_failure_reason: str | None = None

        if client is not None:
            self._client = client
            return

        if not self._api_key:
            self._init_failure_reason = (
                f"{_API_KEY_ENV_VAR} is not set. "
                "Create backend/.env from .env.example and set GEMINI_API_KEY, "
                "or set SENTINEL_VISION_PROVIDER=stub for local development."
            )
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_init_failed",
                    reason=self._init_failure_reason,
                )
            return

        try:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
            if self._logger is not None:
                self._logger.info(
                    "gemini_vision_client_initialized",
                    model=self._model,
                    fallback_models=self._model_chain[1:],
                )
        except ImportError as exc:
            self._init_failure_reason = (
                f"google-genai package is not installed ({exc}). "
                "Install with: pip install google-genai"
            )
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_init_failed",
                    reason=self._init_failure_reason,
                    error=str(exc),
                )
        except Exception as exc:
            self._init_failure_reason = f"Gemini client initialization failed: {exc}"
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_init_failed",
                    reason=self._init_failure_reason,
                    error=str(exc),
                )

    @property
    def is_ready(self) -> bool:
        return self._client is not None

    @property
    def init_failure_reason(self) -> str | None:
        return self._init_failure_reason

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        if not image_bytes:
            return self._empty("Image file is empty.")

        if self._client is None:
            reason = self._init_failure_reason or "Gemini client was not initialized."
            if self._logger is not None:
                self._logger.error("gemini_vision_not_ready", reason=reason)
            return self._empty(reason)

        image_size = self._image_dimensions(image_bytes)
        if self._logger is not None:
            self._logger.info(
                "gemini_vision_request_start",
                vision_provider="gemini",
                model=self._model,
                model_chain=self._model_chain,
                image_size=image_size,
                image_bytes=len(image_bytes),
                detail="Vision request started",
            )

        started = time.perf_counter()
        try:
            from google.genai import types

            mime_type = self._detect_mime_type(image_bytes)
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=_ANALYSIS_PROMPT),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ],
                )
            ]
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                http_options=types.HttpOptions(timeout=self._request_timeout_ms),
            )
            response = self._generate_with_resilience(
                contents=contents,
                config=config,
            )
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            details = parse_gemini_error(exc)
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_request_failed",
                    status_code=details.status_code,
                    status=details.status,
                    error_message=details.message,
                    latency_ms=latency_ms,
                    detail="Vision request failed",
                    final_failure_reason=details.message,
                )
            if is_retryable_gemini_error(exc):
                return self._empty(transient_failure_message(exc))
            return self._empty(f"Vision analysis request failed: {details.message}")

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        raw_text = self._extract_output_text(response)
        if not raw_text:
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_empty_response",
                    latency_ms=latency_ms,
                    detail="Vision request completed with empty response",
                )
            return self._empty("Vision model returned no output.")

        result = self._parse(raw_text)
        update_vision_progress("Vision analysis complete.", phase="completed")
        if self._logger is not None:
            self._logger.info(
                "gemini_vision_request_completed",
                detail="Vision request completed",
                latency_ms=latency_ms,
                confidence=result.confidence,
                registration_number=result.registration_number,
            )
        return result

    def _generate_with_resilience(self, *, contents: Any, config: Any) -> Any:
        last_exc: BaseException | None = None

        for model_index, model_name in enumerate(self._model_chain):
            for attempt_number in range(1, self._max_retries + 2):
                try:
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )
                    return response
                except Exception as exc:
                    last_exc = exc
                    details = parse_gemini_error(exc)
                    retry_number = attempt_number - 1
                    is_last_attempt_for_model = attempt_number > self._max_retries
                    can_retry = is_retryable_gemini_error(exc) and not is_last_attempt_for_model

                    if self._logger is not None:
                        self._logger.warning(
                            "gemini_vision_request_attempt_failed",
                            attempt_number=attempt_number,
                            retry_number=retry_number,
                            model=model_name,
                            status_code=details.status_code,
                            status=details.status,
                            error_message=details.message,
                            retry_delay_seconds=None
                            if not can_retry
                            else retry_delay_seconds(retry_number + 1),
                            will_retry=can_retry,
                        )

                    if not is_retryable_gemini_error(exc):
                        update_vision_progress(
                            details.message,
                            attempt=retry_number,
                            max_attempts=self._max_retries,
                            phase="failed",
                        )
                        if self._logger is not None:
                            self._logger.error(
                                "gemini_vision_request_final_failure",
                                model=model_name,
                                status_code=details.status_code,
                                status=details.status,
                                error_message=details.message,
                                final_failure_reason=details.message,
                            )
                        raise

                    if can_retry:
                        if retry_number == 0:
                            update_vision_progress(
                                "Vision AI busy...",
                                attempt=0,
                                max_attempts=self._max_retries,
                                phase="busy",
                            )
                        delay = retry_delay_seconds(retry_number + 1)
                        progress_message = format_retry_progress_message(
                            retry_number + 1,
                            self._max_retries,
                        )
                        update_vision_progress(
                            progress_message,
                            attempt=retry_number + 1,
                            max_attempts=self._max_retries,
                            phase="retrying",
                        )
                        if self._logger is not None:
                            self._logger.info(
                                "gemini_vision_request_retry_scheduled",
                                attempt_number=attempt_number,
                                retry_number=retry_number + 1,
                                model=model_name,
                                status_code=details.status_code,
                                status=details.status,
                                error_message=details.message,
                                retry_delay_seconds=delay,
                            )
                        self._sleep(delay)
                        continue

                    has_fallback_model = (
                        is_model_fallback_candidate(exc)
                        and model_index < len(self._model_chain) - 1
                    )
                    if has_fallback_model:
                        next_model = self._model_chain[model_index + 1]
                        if self._logger is not None:
                            self._logger.warning(
                                "gemini_vision_model_fallback",
                                previous_model=model_name,
                                next_model=next_model,
                                status_code=details.status_code,
                                error_message=details.message,
                            )
                        update_vision_progress(
                            "Vision AI busy...",
                            attempt=0,
                            max_attempts=self._max_retries,
                            phase="busy",
                        )
                        break

                    final_reason = transient_failure_message(exc)
                    update_vision_progress(
                        final_reason,
                        attempt=self._max_retries,
                        max_attempts=self._max_retries,
                        phase="failed",
                    )
                    if self._logger is not None:
                        self._logger.error(
                            "gemini_vision_request_final_failure",
                            model=model_name,
                            status_code=details.status_code,
                            status=details.status,
                            error_message=details.message,
                            final_failure_reason=final_reason,
                        )
                    raise

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Gemini vision request failed without an exception.")

    @staticmethod
    def _image_dimensions(image_bytes: bytes) -> str | None:
        try:
            from PIL import Image

            with Image.open(io.BytesIO(image_bytes)) as image:
                return f"{image.width}x{image.height}"
        except Exception:
            return None

    @staticmethod
    def _detect_mime_type(image_bytes: bytes) -> str:
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:16]:
            return "image/webp"
        if image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
            return "image/gif"
        return "image/jpeg"

    @staticmethod
    def _extract_output_text(response: Any) -> str | None:
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

        candidates = getattr(response, "candidates", None) or []
        collected: list[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str):
                    collected.append(part_text)
        joined = "".join(collected).strip()
        return joined or None

    def _parse(self, raw_text: str) -> VisionAnalysisResult:
        payload = self._load_json(raw_text)
        if payload is None:
            if self._logger is not None:
                self._logger.warning(
                    "gemini_vision_parse_failed",
                    raw=raw_text[:200],
                    detail="Malformed JSON from Gemini Vision",
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

    @staticmethod
    def _load_json(raw_text: str) -> dict[str, Any] | None:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        decoder = json.JSONDecoder()
        for start in (0, cleaned.find("{")):
            if start < 0:
                continue
            snippet = cleaned[start:]
            if not snippet:
                continue
            try:
                parsed, _end = decoder.raw_decode(snippet)
            except (ValueError, TypeError, json.JSONDecodeError):
                continue
            if isinstance(parsed, dict):
                return parsed
        return None

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
