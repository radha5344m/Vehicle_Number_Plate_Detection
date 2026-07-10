"""SQLite verification result repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.persistence_dto import SaveVerificationResultCommand
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.application.ports.outbound.verification_result_repository_port import (
    VerificationResultRepositoryPort,
)
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,
)


class SqliteVerificationResultRepository(VerificationResultRepositoryPort):
    """Persist vehicle verification outcomes in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_verification_result(
        self,
        command: SaveVerificationResultCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        verification_id: str | None = None,
    ) -> str:
        resolved_id = verification_id or str(uuid.uuid4())
        model = VerificationResultModel(
            verification_id=resolved_id,
            scan_id=command.scan_id,
            lookup_status=command.lookup_status,
            message=command.message,
            vehicle_id=command.vehicle_id,
            verified_at=command.verified_at,
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
