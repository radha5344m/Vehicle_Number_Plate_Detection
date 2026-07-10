"""Query scan history with filters."""

from sentinel_anpr.application.dto.history_dto import (
    QueryScanHistoryResult,
    ScanHistoryFilters,
)
from sentinel_anpr.application.ports.outbound.scan_repository_port import ScanRepositoryPort
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel


class QueryScanHistoryUseCase:
    """List completed scans with optional filters."""

    def __init__(self, scan_repository: ScanRepositoryPort) -> None:
        self._scan_repository = scan_repository

    def execute(self, filters: ScanHistoryFilters) -> QueryScanHistoryResult:
        if filters.risk_level:
            risk_level = filters.risk_level.lower()
            if risk_level not in {level.value for level in RiskLevel}:
                raise ValueError(f"Invalid risk level: {filters.risk_level}")

        if filters.from_date and filters.to_date and filters.from_date > filters.to_date:
            raise ValueError("from date must be before to date")

        return self._scan_repository.list_scans(filters)
