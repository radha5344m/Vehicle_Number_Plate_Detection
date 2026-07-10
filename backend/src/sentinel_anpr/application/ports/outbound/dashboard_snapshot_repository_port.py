"""Dashboard snapshot persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.persistence_dto import SaveDashboardSnapshotCommand
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class DashboardSnapshotRepositoryPort(Protocol):
    """Store materialized dashboard KPI snapshots."""

    def save_snapshot(
        self,
        command: SaveDashboardSnapshotCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        snapshot_id: str | None = None,
    ) -> str:
        """Persist dashboard snapshot and return its identifier."""
        ...
