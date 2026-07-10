"""Tabular export port for department investigation reports."""

from typing import Protocol

from sentinel_anpr.application.dto.investigation_reports_dto import (
    InvestigationReportExportBundleDto,
    InvestigationReportExportResult,
)


class TabularExportPort(Protocol):
    """Render department-level investigation report exports."""

    def export_pdf(
        self, bundle: InvestigationReportExportBundleDto
    ) -> InvestigationReportExportResult:
        """Render a department summary PDF."""
        ...

    def export_csv(
        self, bundle: InvestigationReportExportBundleDto
    ) -> InvestigationReportExportResult:
        """Render a CSV export."""
        ...

    def export_excel(
        self, bundle: InvestigationReportExportBundleDto
    ) -> InvestigationReportExportResult:
        """Render an Excel export."""
        ...
