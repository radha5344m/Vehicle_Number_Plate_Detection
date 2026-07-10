"""ReportLab e-Challan PDF generator."""

from __future__ import annotations

import io
from datetime import UTC

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sentinel_anpr.application.dto.challan_dto import ChallanDetailDto
from sentinel_anpr.application.ports.outbound.challan_pdf_generator_port import ChallanPdfGeneratorPort

_NAVY = colors.HexColor("#0B1F3A")
_SLATE = colors.HexColor("#475569")


class ReportLabChallanPdfGenerator(ChallanPdfGeneratorPort):
    def generate_challan_pdf(self, challan: ChallanDetailDto) -> bytes:
        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ChallanTitle",
            parent=styles["Heading1"],
            textColor=_NAVY,
            fontSize=18,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "ChallanBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=_SLATE,
        )
        issued = challan.issued_at.astimezone(UTC)
        rows = [
            ["Challan Number", challan.challan_number],
            ["Registration Number", challan.registration_number],
            ["Owner", challan.owner_name or "—"],
            ["Violation", challan.violation_description or challan.violation_type],
            ["Fine Amount", f"₹{challan.fine_amount:,.0f}"],
            ["Payment Status", challan.payment_status.upper()],
            ["Officer", challan.officer_name],
            ["Police Station", challan.station_name],
            ["Date", issued.strftime("%d %b %Y")],
            ["Time", issued.strftime("%H:%M")],
            ["Location", challan.location_label or "—"],
            ["Remarks", challan.remarks or "—"],
        ]
        table = Table(rows, colWidths=[55 * mm, 110 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F8FAFC")),
                ]
            )
        )
        story = [
            Paragraph("Andhra Pradesh Traffic Police", title_style),
            Paragraph("Electronic Challan (e-Challan)", body_style),
            Spacer(1, 8),
            table,
            Spacer(1, 12),
            Paragraph(
                "This is a system-generated enforcement notice. Verify details before payment.",
                body_style,
            ),
        ]
        document.build(story)
        return buffer.getvalue()
