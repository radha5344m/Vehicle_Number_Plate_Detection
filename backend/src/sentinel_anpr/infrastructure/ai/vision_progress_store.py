"""In-memory Vision AI retry progress for long-running workflow requests."""

from __future__ import annotations

import threading
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal

ProgressPhase = Literal["idle", "busy", "retrying", "completed", "failed"]

_correlation_id: ContextVar[str | None] = ContextVar("vision_progress_correlation_id", default=None)
_lock = threading.Lock()
_store: dict[str, VisionProgressSnapshot] = {}


@dataclass(frozen=True)
class VisionProgressSnapshot:
    """Latest Vision AI retry progress for a workflow correlation identifier."""

    message: str
    attempt: int = 0
    max_attempts: int = 5
    phase: ProgressPhase = "idle"


def bind_vision_progress(correlation_id: str | None, *, max_attempts: int = 5) -> None:
    """Associate the current request with a correlation id and initialize progress."""
    _correlation_id.set(correlation_id)
    if not correlation_id:
        return
    with _lock:
        _store[correlation_id] = VisionProgressSnapshot(
            message="Vision AI busy...",
            attempt=0,
            max_attempts=max_attempts,
            phase="busy",
        )


def update_vision_progress(
    message: str,
    *,
    attempt: int = 0,
    max_attempts: int = 5,
    phase: ProgressPhase = "retrying",
) -> None:
    """Update progress for the correlation id bound to the current execution context."""
    correlation_id = _correlation_id.get()
    if not correlation_id:
        return
    with _lock:
        _store[correlation_id] = VisionProgressSnapshot(
            message=message,
            attempt=attempt,
            max_attempts=max_attempts,
            phase=phase,
        )


def get_vision_progress(correlation_id: str) -> VisionProgressSnapshot | None:
    """Return the latest progress snapshot for a correlation id, if any."""
    with _lock:
        return _store.get(correlation_id)


def clear_vision_progress(correlation_id: str | None) -> None:
    """Remove stored progress for a correlation id and reset the context binding."""
    if correlation_id:
        with _lock:
            _store.pop(correlation_id, None)
    _correlation_id.set(None)
