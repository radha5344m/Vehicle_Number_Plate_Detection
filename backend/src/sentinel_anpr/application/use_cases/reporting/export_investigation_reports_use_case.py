"""Export filtered investigation reports in department-level formats."""

from sentinel_anpr.application.dto.investigation_reports_dto import (
    ExportFormat,
    InvestigationReportExportResult,
    InvestigationReportsFilters,
)
from sentinel_anpr.application.ports.outbound.investigation_reports_query_port import (
    InvestigationReportsQueryPort,
)
from sentinel_anpr.application.ports.outbound.tabular_export_port import TabularExportPort
from sentinel_anpr.application.use_cases.reporting.query_investigation_reports_use_case import (
    QueryInvestigationReportsUseCase,
)


class ExportInvestigationReportsUseCase:
    """Export filtered investigation reports to PDF, CSV, or Excel."""

    def __init__(
        self,
        query_port: InvestigationReportsQueryPort,
        export_port: TabularExportPort,
    ) -> None:
        self._query_port = query_port
        self._export_port = export_port
        self._validator = QueryInvestigationReportsUseCase(query_port)

    def execute(
        self,
        *,
        filters: InvestigationReportsFilters,
        export_format: ExportFormat,
    ) -> InvestigationReportExportResult:
        self._validator._validate(filters)
        bundle = self._query_port.export_investigation_reports(filters)
        if export_format == ExportFormat.PDF:
            return self._export_port.export_pdf(bundle)
        if export_format == ExportFormat.CSV:
            return self._export_port.export_csv(bundle)
        if export_format == ExportFormat.EXCEL:
            return self._export_port.export_excel(bundle)
        raise ValueError(f"Unsupported export format: {export_format}")
