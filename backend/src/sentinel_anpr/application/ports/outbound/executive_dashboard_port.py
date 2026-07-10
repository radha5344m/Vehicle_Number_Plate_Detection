"""Executive dashboard analytics port."""

from typing import Protocol

from sentinel_anpr.application.dto.executive_dashboard_dto import (
    ExecutiveDashboardExportBundleDto,
    ExecutiveDashboardFilters,
    ExecutiveDashboardResult,
)


class ExecutiveDashboardPort(Protocol):
    def get_dashboard(self, filters: ExecutiveDashboardFilters) -> ExecutiveDashboardResult: ...

    def export_dashboard(
        self,
        filters: ExecutiveDashboardFilters,
    ) -> ExecutiveDashboardExportBundleDto: ...
