"""Risk assessment persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.persistence_dto import SaveRiskAssessmentCommand
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class RiskAssessmentRepositoryPort(Protocol):
    """Store risk engine assessments."""

    def save_risk_assessment(
        self,
        command: SaveRiskAssessmentCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        assessment_id: str | None = None,
    ) -> str:
        """Persist risk assessment and return its identifier."""
        ...
