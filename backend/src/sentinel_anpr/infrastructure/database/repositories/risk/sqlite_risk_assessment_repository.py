"""SQLite risk assessment repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.persistence_dto import SaveRiskAssessmentCommand
from sentinel_anpr.application.ports.outbound.risk_assessment_repository_port import (
    RiskAssessmentRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.infrastructure.database.models.risk.risk_assessment_model import (
    RiskAssessmentModel,
)


class SqliteRiskAssessmentRepository(RiskAssessmentRepositoryPort):
    """Persist risk assessments in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_risk_assessment(
        self,
        command: SaveRiskAssessmentCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        assessment_id: str | None = None,
    ) -> str:
        resolved_id = assessment_id or str(uuid.uuid4())
        model = RiskAssessmentModel(
            assessment_id=resolved_id,
            scan_id=command.scan_id,
            risk_score=command.risk_score,
            risk_level=command.risk_level.lower(),
            explanation=command.explanation,
            recommendation=command.recommendation,
            policy_version=command.policy_version,
            assessed_at=command.assessed_at,
            created_at=datetime.now(UTC),
        )

        if transaction is not None:
            session = transaction  # type: ignore[assignment]
            session.add(model)
            return resolved_id

        with self._session_factory() as session:
            session.add(model)
            session.commit()
        return resolved_id
