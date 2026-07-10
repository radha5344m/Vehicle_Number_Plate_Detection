"""Analytics aggregation port."""

from typing import Protocol

from sentinel_anpr.application.dto.analytics_dto import AnalyticsDateRange, AnalyticsOverviewDto


class AnalyticsRepositoryPort(Protocol):
    """Read-only analytics queries over stored scan history."""

    def get_overview(self, date_range: AnalyticsDateRange) -> AnalyticsOverviewDto:
        """Aggregate chart datasets from completed scans."""
        ...
