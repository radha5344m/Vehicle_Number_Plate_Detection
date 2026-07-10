"""Persist completed workflow outcomes atomically."""

from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeCommand,
    PersistWorkflowOutcomeResult,
)
from sentinel_anpr.application.ports.outbound.workflow_persistence_port import WorkflowPersistencePort


class PersistWorkflowOutcomeUseCase:
    """Coordinate transactional persistence for workflow artifacts."""

    def __init__(self, workflow_persistence: WorkflowPersistencePort) -> None:
        self._workflow_persistence = workflow_persistence

    def execute(self, command: PersistWorkflowOutcomeCommand) -> PersistWorkflowOutcomeResult:
        return self._workflow_persistence.persist_workflow_outcome(command)
