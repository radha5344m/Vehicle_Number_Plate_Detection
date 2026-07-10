"""Investigation reports query port."""

from typing import Protocol

from sentinel_anpr.application.dto.investigation_reports_dto import (
    InvestigationReportExportBundleDto,
    InvestigationReportsFilters,
    InvestigationReportsQueryResult,
)


class InvestigationReportsQueryPort(Protocol):
    """Read-only reporting queries over persisted investigations."""

    def query_investigation_reports(
        self, filters: InvestigationReportsFilters
    ) -> InvestigationReportsQueryResult:
        """Return paginated investigations plus aggregate analytics."""
        ...

    def export_investigation_reports(
        self, filters: InvestigationReportsFilters
    ) -> InvestigationReportExportBundleDto:
        """Return all rows and analytics for department-level exports."""
        ...
