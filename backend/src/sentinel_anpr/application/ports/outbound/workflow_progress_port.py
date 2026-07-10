"""Outbound port for reporting long-running workflow progress."""

from __future__ import annotations

from typing import Protocol


class WorkflowProgressPort(Protocol):
    """Report workflow stage progress (optional; no-op in synchronous mode)."""

    def bind(self, workflow_id: str, *, max_attempts: int = 5) -> None:
        """Associate subsequent updates with a workflow identifier."""

    def update(
        self,
        workflow_id: str,
        *,
        current_step: str,
        message: str,
        progress: int,
        phase: str = "processing",
        attempt: int = 0,
        max_attempts: int = 5,
    ) -> None:
        """Publish an in-progress workflow update."""

    def clear(self, workflow_id: str | None) -> None:
        """Remove progress tracking for a workflow identifier."""
