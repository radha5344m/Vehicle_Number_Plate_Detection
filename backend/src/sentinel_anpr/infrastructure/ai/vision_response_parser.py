"""Parse vision AI JSON responses, including partially truncated output."""

from __future__ import annotations

import json
import re
from typing import Any

_VISION_STRING_FIELDS = (
    "registration_number",
    "vehicle_color",
    "vehicle_type",
    "brand",
    "model",
    "explanation",
)


def _strip_markdown_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _decode_json_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value


def _parse_with_json_decoder(cleaned: str) -> dict[str, Any] | None:
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


def _extract_fields_from_fragment(cleaned: str) -> dict[str, Any] | None:
    """Best-effort extraction when the model returns truncated or slightly invalid JSON."""
    payload: dict[str, Any] = {}

    for field in _VISION_STRING_FIELDS:
        pattern = re.compile(
            rf'"{re.escape(field)}"\s*:\s*"(?P<value>(?:\\.|[^"\\])*)"',
            re.DOTALL,
        )
        match = pattern.search(cleaned)
        if match is not None:
            payload[field] = _decode_json_string(match.group("value"))

    confidence_match = re.search(
        r'"confidence"\s*:\s*(?P<value>-?\d+(?:\.\d+)?)',
        cleaned,
    )
    if confidence_match is not None:
        payload["confidence"] = float(confidence_match.group("value"))

    if not payload.get("registration_number") and len(payload) < 2:
        return None
    return payload


def parse_vehicle_count_json(raw_text: str) -> dict[str, Any] | None:
    """Return a vehicle-count payload dict from model output text."""
    cleaned = _strip_markdown_fences(raw_text)
    if not cleaned:
        return None

    payload = _parse_with_json_decoder(cleaned)
    if payload is not None:
        return payload

    vehicle_count_match = re.search(
        r'"vehicle_count"\s*:\s*(?P<value>\d+)',
        cleaned,
    )
    if vehicle_count_match is None:
        return None

    return {"vehicle_count": int(vehicle_count_match.group("value")), "vehicles": []}


def parse_vision_json(raw_text: str) -> dict[str, Any] | None:
    """Return a vision payload dict from model output text."""
    cleaned = _strip_markdown_fences(raw_text)
    if not cleaned:
        return None

    payload = _parse_with_json_decoder(cleaned)
    if payload is not None:
        return payload

    return _extract_fields_from_fragment(cleaned)
