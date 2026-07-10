"""Fetch analytics overview from stored scan history."""

from datetime import datetime

from sentinel_anpr.application.dto.analytics_dto import AnalyticsDateRange
from sentinel_anpr.application.ports.outbound.analytics_repository_port import AnalyticsRepositoryPort


class GetAnalyticsOverviewUseCase:
    """Aggregate chart data from completed scans — no AI."""

    def __init__(self, analytics_repository: AnalyticsRepositoryPort) -> None:
        self._analytics_repository = analytics_repository

    def execute(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        station_id: str | None = None,
        officer_id: str | None = None,
    ):
        if from_date and to_date and from_date > to_date:
            raise ValueError("from date must be before to date")

        return self._analytics_repository.get_overview(
            AnalyticsDateRange(
                from_date=from_date,
                to_date=to_date,
                station_id=station_id,
                officer_id=officer_id,
            )
        )
