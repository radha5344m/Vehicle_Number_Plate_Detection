"""Scan history persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.history_dto import (
    QueryScanHistoryResult,
    SaveCompletedScanCommand,
    SaveCompletedScanResult,
    ScanHistoryFilters,
)
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class ScanRepositoryPort(Protocol):
    """Store and query completed scans."""

    def save_completed(
        self,
        command: SaveCompletedScanCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        scan_id: str | None = None,
    ) -> SaveCompletedScanResult:
        """Persist a completed scan."""
        ...

    def list_scans(self, filters: ScanHistoryFilters) -> QueryScanHistoryResult:
        """List scans matching filters."""
        ...
