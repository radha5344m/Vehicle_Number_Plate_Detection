"""Download a generated investigation report PDF."""

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.report_dto import DownloadInvestigationReportResult
from sentinel_anpr.application.ports.outbound.credential_store_port import CredentialStorePort
from sentinel_anpr.application.ports.outbound.report_repository_port import ReportRepositoryPort
from sentinel_anpr.application.services.auth_permissions import has_permission


class DownloadInvestigationReportUseCase:
    """Load stored investigation report PDF bytes."""

    def __init__(
        self,
        report_repository: ReportRepositoryPort,
        credential_store: CredentialStorePort,
    ) -> None:
        self._report_repository = report_repository
        self._credential_store = credential_store

    def execute(
        self,
        *,
        report_id: str,
        principal: AuthPrincipal,
    ) -> DownloadInvestigationReportResult:
        if not has_permission(principal.roles, "reports"):
            raise PermissionError("Missing permission: reports")
        report = self._report_repository.get_report(report_id)
        if report is None:
            raise LookupError("Report not found")
        if principal.role == "POLICE_OFFICER" and report.officer_id != principal.officer_id:
            raise PermissionError("Report access denied")
        if principal.role == "STATION_ADMIN":
            stored = self._credential_store.find_by_id(report.officer_id)
            if stored is None or stored.officer.station_id != principal.station_id:
                raise PermissionError("Report access denied")

        pdf_bytes = self._report_repository.load_pdf_bytes(report)
        return DownloadInvestigationReportResult(
            report_id=report.report_id,
            filename=f"investigation-report-{report.plate_text}.pdf",
            content_type="application/pdf",
            pdf_bytes=pdf_bytes,
        )
