"""SHA-256 hashing for investigation report JSON payloads."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any

from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        return _normalize(asdict(value))
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return hashlib.sha256(value).hexdigest()
    if isinstance(value, dict):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value


def hash_investigation_report_json(command: GenerateInvestigationReportCommand) -> str:
    """Generate a deterministic SHA-256 hash from the complete report JSON."""
    payload = _normalize(command)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
