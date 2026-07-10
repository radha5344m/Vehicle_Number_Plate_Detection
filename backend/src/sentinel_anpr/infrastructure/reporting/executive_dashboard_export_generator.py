"""Executive dashboard export generator."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sentinel_anpr.application.dto.executive_dashboard_dto import (
    ExecutiveDashboardExportBundleDto,
    ExecutiveDashboardExportResult,
)
from sentinel_anpr.application.ports.outbound.executive_dashboard_export_port import (
    ExecutiveDashboardExportPort,
)


class ExecutiveDashboardExportGenerator(ExecutiveDashboardExportPort):
    def export_pdf(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=32, bottomMargin=32)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("SentinelANPR AI Executive Command Center", styles["Title"]),
            Spacer(1, 8),
            Paragraph(f"Scope: {bundle.scope_label}", styles["Heading3"]),
            Paragraph(f"Generated: {bundle.generated_at.isoformat()}", styles["Normal"]),
            Spacer(1, 12),
        ]
        table = Table(
            [["Section", "Label", "Value"]]
            + [[row.section, row.label, row.value] for row in bundle.rows],
            colWidths=[100, 160, 240],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        doc.build(story)
        return ExecutiveDashboardExportResult(
            filename="executive-command-center.pdf",
            content_type="application/pdf",
            content=buffer.getvalue(),
        )

    def export_csv(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Section", "Label", "Value"])
        for row in bundle.rows:
            writer.writerow([row.section, row.label, row.value])
        return ExecutiveDashboardExportResult(
            filename="executive-command-center.csv",
            content_type="text/csv",
            content=output.getvalue().encode("utf-8"),
        )

    def export_excel(
        self,
        bundle: ExecutiveDashboardExportBundleDto,
    ) -> ExecutiveDashboardExportResult:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Executive Command Center"
        sheet.append(["Section", "Label", "Value"])
        for row in bundle.rows:
            sheet.append([row.section, row.label, row.value])
        for cell in sheet[1]:
            cell.font = cell.font.copy(bold=True)
        buffer = BytesIO()
        workbook.save(buffer)
        return ExecutiveDashboardExportResult(
            filename="executive-command-center.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            content=buffer.getvalue(),
        )
