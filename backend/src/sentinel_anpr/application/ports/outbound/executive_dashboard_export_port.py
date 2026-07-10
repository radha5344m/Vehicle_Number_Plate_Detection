"""Executive dashboard export port."""

from typing import Protocol

from sentinel_anpr.application.dto.executive_dashboard_dto import (
    ExecutiveDashboardExportBundleDto,
    ExecutiveDashboardExportResult,
)


class ExecutiveDashboardExportPort(Protocol):
    def export_pdf(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult: ...

    def export_csv(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult: ...

    def export_excel(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult: ...
