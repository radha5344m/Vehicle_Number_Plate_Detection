"""SQLite dashboard snapshot repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.persistence_dto import SaveDashboardSnapshotCommand
from sentinel_anpr.application.ports.outbound.dashboard_snapshot_repository_port import (
    DashboardSnapshotRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.infrastructure.database.models.dashboard.dashboard_snapshot_model import (
    DashboardSnapshotModel,
)


class SqliteDashboardSnapshotRepository(DashboardSnapshotRepositoryPort):
    """Persist dashboard KPI snapshots in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_snapshot(
        self,
        command: SaveDashboardSnapshotCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        snapshot_id: str | None = None,
    ) -> str:
        resolved_id = snapshot_id or str(uuid.uuid4())
        model = DashboardSnapshotModel(
            snapshot_id=resolved_id,
            total_scans=command.total_scans,
            verified_vehicles=command.verified_vehicles,
            suspicious_vehicles=command.suspicious_vehicles,
            pending_verification=command.pending_verification,
            snapshot_at=command.snapshot_at,
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
