"""Dashboard data source port."""

from typing import Protocol

from sentinel_anpr.application.dto.dashboard_dto import (
    DashboardSummaryResult,
    RecentActivityResult,
)


class DashboardDataPort(Protocol):
    """Provides dashboard metrics and activity (placeholder or live)."""

    def get_summary(
        self,
        *,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> DashboardSummaryResult: ...

    def get_recent_activity(
        self,
        *,
        limit: int = 10,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> RecentActivityResult: ...
