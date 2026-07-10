"""Transactional workflow persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeCommand,
    PersistWorkflowOutcomeResult,
)


class WorkflowPersistencePort(Protocol):
    """Persist all workflow outcomes in a single database transaction."""

    def persist_workflow_outcome(
        self,
        command: PersistWorkflowOutcomeCommand,
    ) -> PersistWorkflowOutcomeResult:
        """Save scan, verification, risk, activity, dashboard, and report atomically."""
        ...
