"""PDF generation port."""

from typing import Protocol

from sentinel_anpr.domain.reporting.entities.investigation_report_content import (
    InvestigationReportContent,
)


class PdfGeneratorPort(Protocol):
    """Render investigation report content to PDF bytes."""

    def generate_investigation_report(self, content: InvestigationReportContent) -> bytes:
        """Build a professional investigation PDF."""
        ...
