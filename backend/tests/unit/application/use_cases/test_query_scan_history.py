"""Query scan history use case unit tests."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.history_dto import (
    PaginationDto,
    QueryScanHistoryResult,
    ScanHistoryFilters,
    ScanHistoryItemDto,
)
from sentinel_anpr.application.use_cases.history.query_scan_history_use_case import (
    QueryScanHistoryUseCase,
)


class _FakeRepository:
    def __init__(self) -> None:
        self.last_filters: ScanHistoryFilters | None = None

    def save_completed(self, command):
        del command
        raise NotImplementedError

    def list_scans(self, filters: ScanHistoryFilters) -> QueryScanHistoryResult:
        self.last_filters = filters
        now = datetime.now(UTC)
        return QueryScanHistoryResult(
            items=(
                ScanHistoryItemDto(
                    scan_id="scan-1",
                    plate_text="AP09AB1234",
                    vehicle_id=None,
                    officer_id="officer-1",
                    officer_name="Ravi Kumar",
                    risk_score=0.0,
                    risk_level="low",
                    location_label="Ongole",
                    scanned_at=now,
                    completed_at=now,
                ),
            ),
            pagination=PaginationDto(page=1, page_size=20, total_items=1, total_pages=1),
        )


def test_query_scan_history_passes_filters() -> None:
    repository = _FakeRepository()
    use_case = QueryScanHistoryUseCase(scan_repository=repository)
    result = use_case.execute(
        ScanHistoryFilters(
            plate="AP09AB1234",
            officer_id="officer-1",
            risk_level="low",
        )
    )
    assert len(result.items) == 1
    assert repository.last_filters is not None
    assert repository.last_filters.plate == "AP09AB1234"
    assert repository.last_filters.risk_level == "low"
