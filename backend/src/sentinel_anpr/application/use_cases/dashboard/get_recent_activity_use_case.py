"""Return recent dashboard activity."""

from sentinel_anpr.application.dto.dashboard_dto import RecentActivityResult
from sentinel_anpr.application.ports.outbound.dashboard_data_port import DashboardDataPort


class GetRecentActivityUseCase:
    """Fetch recent activity from data port."""

    def __init__(self, dashboard_data: DashboardDataPort) -> None:
        self._dashboard_data = dashboard_data

    def execute(
        self,
        *,
        limit: int = 10,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> RecentActivityResult:
        return self._dashboard_data.get_recent_activity(
            limit=limit,
            station_id=station_id,
            officer_id=officer_id,
        )
