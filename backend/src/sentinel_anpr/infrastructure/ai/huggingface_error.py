"""Error helpers for Hugging Face Inference API responses."""

from __future__ import annotations

import json
from dataclasses import dataclass

DEFAULT_REQUEST_TIMEOUT_SECONDS = 60
SERVICE_BUSY_RETRY_DELAY_SECONDS = 1.5


@dataclass(frozen=True)
class HuggingFaceErrorDetails:
    """Normalized Hugging Face HTTP error fields."""

    status_code: int | None
    message: str


def parse_response_error(status_code: int, body_text: str) -> HuggingFaceErrorDetails:
    """Extract a human-readable message from an HTTP error response body."""
    message = body_text.strip() or f"HTTP {status_code}"
    if not body_text:
        return HuggingFaceErrorDetails(status_code=status_code, message=message)

    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError:
        return HuggingFaceErrorDetails(status_code=status_code, message=message)

    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            nested_message = error.get("message")
            if isinstance(nested_message, str) and nested_message.strip():
                return HuggingFaceErrorDetails(
                    status_code=status_code,
                    message=nested_message.strip(),
                )
        if isinstance(error, str) and error.strip():
            return HuggingFaceErrorDetails(status_code=status_code, message=error.strip())

        for key in ("message", "detail", "error_message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return HuggingFaceErrorDetails(status_code=status_code, message=value.strip())

    return HuggingFaceErrorDetails(status_code=status_code, message=message)


def format_vision_error_message(details: HuggingFaceErrorDetails) -> str:
    """Map HTTP status codes to stable vision failure messages."""
    message = details.message or "Unknown Hugging Face API error."
    status_code = details.status_code

    if status_code == 401:
        return f"Authentication Error: {message}"
    if status_code == 429:
        return f"Rate Limit Exceeded: {message}"
    if status_code == 503:
        return f"Service Busy: {message}"

    if status_code is not None:
        return f"{status_code}: {_with_provider_guidance(message)}"
    return _with_provider_guidance(message)


def _with_provider_guidance(message: str) -> str:
    lowered = message.lower()
    if (
        "does not exist" in lowered
        or "not supported by any provider" in lowered
        or "not supported by provider" in lowered
    ):
        return (
            f"{message} Check HF_MODEL is a valid vision model deployed on Inference Providers. "
            "Enable providers at https://huggingface.co/settings/inference-providers and "
            "use a fine-grained HF token with 'Make calls to Inference Providers' permission."
        )
    return message
