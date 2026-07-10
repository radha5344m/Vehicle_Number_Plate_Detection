"""Get Executive Command Center analytics."""

from datetime import datetime

from sentinel_anpr.application.dto.executive_dashboard_dto import (
    ExecutiveDashboardFilters,
)
from sentinel_anpr.application.ports.outbound.executive_dashboard_port import (
    ExecutiveDashboardPort,
)


class GetExecutiveDashboardUseCase:
    def __init__(self, dashboard_port: ExecutiveDashboardPort) -> None:
        self._dashboard_port = dashboard_port

    def execute(
        self,
        *,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        district: str | None = None,
        station: str | None = None,
        officer: str | None = None,
        vehicle_type: str | None = None,
        risk_level: str | None = None,
        brand: str | None = None,
        station_id: str | None = None,
        officer_id: str | None = None,
    ):
        if from_date and to_date and from_date > to_date:
            raise ValueError("from date must be before to date")
        return self._dashboard_port.get_dashboard(
            ExecutiveDashboardFilters(
                from_date=from_date,
                to_date=to_date,
                district=district,
                station=station,
                officer=officer,
                vehicle_type=vehicle_type,
                risk_level=risk_level,
                brand=brand,
                station_id=station_id,
                officer_id=officer_id,
            )
        )
