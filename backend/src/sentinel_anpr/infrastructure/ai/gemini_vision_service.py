"""Gemini Vision adapter implementing the VisionAiService port.

Uses the official Google GenAI SDK to analyze a vehicle image and return a
strongly typed :class:`VisionAnalysisResult`. This adapter is infrastructure-
only: it does not touch business logic, use cases, or controllers.
"""

from __future__ import annotations

import io
import json
import time
from typing import Any

from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import (
    VisionAnalysisResult,
    VisionAiService,
)
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
        client: Any | None = None,
        logger: LoggingPort | None = None,
    ) -> None:
        self._model = model or _DEFAULT_MODEL
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
                image_size=image_size,
                image_bytes=len(image_bytes),
                detail="Vision request started",
            )

        started = time.perf_counter()
        try:
            from google.genai import types

            mime_type = self._detect_mime_type(image_bytes)
            response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=_ANALYSIS_PROMPT),
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            if self._logger is not None:
                self._logger.error(
                    "gemini_vision_request_failed",
                    error=str(exc),
                    latency_ms=latency_ms,
                    detail="Vision request failed",
                )
            return self._empty(f"Vision analysis request failed: {exc}")

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
        if self._logger is not None:
            self._logger.info(
                "gemini_vision_request_completed",
                detail="Vision request completed",
                latency_ms=latency_ms,
                confidence=result.confidence,
                registration_number=result.registration_number,
            )
        return result

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

        try:
            parsed = json.loads(cleaned)
        except (ValueError, TypeError):
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            try:
                parsed = json.loads(cleaned[start : end + 1])
            except (ValueError, TypeError):
                return None
        return parsed if isinstance(parsed, dict) else None

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
