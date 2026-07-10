"""Investigation report persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.report_dto import (
    GenerateInvestigationReportResult,
    ReportReferenceDto,
)
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class ReportRepositoryPort(Protocol):
    """Persist report metadata and PDF files."""

    def save_report(
        self,
        *,
        officer_id: str,
        officer_name: str,
        plate_text: str,
        risk_score: float,
        risk_level: str,
        title: str,
        pdf_bytes: bytes,
        checksum_sha256: str,
        generated_at,
        scan_id: str | None = None,
        transaction: TransactionHandlePort | None = None,
        report_id: str | None = None,
    ) -> GenerateInvestigationReportResult:
        """Store PDF and metadata."""
        ...

    def get_report(self, report_id: str) -> ReportReferenceDto | None:
        """Load report metadata."""
        ...

    def load_pdf_bytes(self, report: ReportReferenceDto) -> bytes:
        """Read stored PDF bytes."""
        ...
