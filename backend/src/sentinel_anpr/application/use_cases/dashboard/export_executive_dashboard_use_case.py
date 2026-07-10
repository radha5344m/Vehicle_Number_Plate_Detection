"""Export Executive Command Center analytics."""

from datetime import datetime

from sentinel_anpr.application.dto.executive_dashboard_dto import ExecutiveDashboardFilters
from sentinel_anpr.application.ports.outbound.executive_dashboard_export_port import (
    ExecutiveDashboardExportPort,
)
from sentinel_anpr.application.ports.outbound.executive_dashboard_port import (
    ExecutiveDashboardPort,
)


class ExportExecutiveDashboardUseCase:
    def __init__(
        self,
        dashboard_port: ExecutiveDashboardPort,
        export_port: ExecutiveDashboardExportPort,
    ) -> None:
        self._dashboard_port = dashboard_port
        self._export_port = export_port

    def execute(
        self,
        *,
        export_format: str,
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
        filters = ExecutiveDashboardFilters(
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
        bundle = self._dashboard_port.export_dashboard(filters)
        if export_format == "pdf":
            return self._export_port.export_pdf(bundle)
        if export_format == "csv":
            return self._export_port.export_csv(bundle)
        if export_format == "excel":
            return self._export_port.export_excel(bundle)
        raise ValueError(f"Unsupported export format: {export_format}")
