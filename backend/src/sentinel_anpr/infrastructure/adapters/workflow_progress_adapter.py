"""No-op workflow progress adapter for synchronous workflow execution."""

from __future__ import annotations

from sentinel_anpr.application.ports.outbound.workflow_progress_port import WorkflowProgressPort


class NoOpWorkflowProgressAdapter(WorkflowProgressPort):
    """Discard workflow progress updates when no async polling is required."""

    def bind(self, workflow_id: str, *, max_attempts: int = 5) -> None:
        del workflow_id, max_attempts

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
        del workflow_id, current_step, message, progress, phase, attempt, max_attempts

    def clear(self, workflow_id: str | None) -> None:
        del workflow_id
