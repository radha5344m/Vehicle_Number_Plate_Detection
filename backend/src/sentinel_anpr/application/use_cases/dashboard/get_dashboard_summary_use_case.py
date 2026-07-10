"""Return dashboard summary KPIs."""

from sentinel_anpr.application.dto.dashboard_dto import DashboardSummaryResult
from sentinel_anpr.application.ports.outbound.dashboard_data_port import DashboardDataPort


class GetDashboardSummaryUseCase:
    """Fetch dashboard summary from data port."""

    def __init__(self, dashboard_data: DashboardDataPort) -> None:
        self._dashboard_data = dashboard_data

    def execute(
        self,
        *,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> DashboardSummaryResult:
        return self._dashboard_data.get_summary(
            station_id=station_id,
            officer_id=officer_id,
        )
