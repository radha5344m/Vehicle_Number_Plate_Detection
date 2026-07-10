"""SQLite officer activity repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.persistence_dto import SaveOfficerActivityCommand
from sentinel_anpr.application.ports.outbound.officer_activity_repository_port import (
    OfficerActivityRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import (
    OfficerActivityModel,
)


class SqliteOfficerActivityRepository(OfficerActivityRepositoryPort):
    """Persist officer activity events in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_activities(
        self,
        commands: tuple[SaveOfficerActivityCommand, ...],
        *,
        transaction: TransactionHandlePort | None = None,
    ) -> tuple[str, ...]:
        activity_ids: list[str] = []
        models: list[OfficerActivityModel] = []
        now = datetime.now(UTC)

        for command in commands:
            activity_id = str(uuid.uuid4())
            activity_ids.append(activity_id)
            models.append(
                OfficerActivityModel(
                    activity_id=activity_id,
                    officer_id=command.officer_id,
                    officer_name=command.officer_name,
                    scan_id=command.scan_id,
                    activity_type=command.activity_type,
                    description=command.description,
                    status=command.status,
                    correlation_id=command.correlation_id,
                    occurred_at=command.occurred_at,
                    created_at=now,
                )
            )

        if transaction is not None:
            session = transaction  # type: ignore[assignment]
            session.add_all(models)
            return tuple(activity_ids)

        with self._session_factory() as session:
            session.add_all(models)
            session.commit()
        return tuple(activity_ids)
