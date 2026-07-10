"""ReportLab police investigation PDF generator with visual analytics."""

from __future__ import annotations

import io
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from sentinel_anpr.domain.reporting.entities.investigation_report_content import (
    InvestigationReportContent,
)

TEMPLATE_VERSION = "investigation-v2-police"

# Brand palette — police command / formal evidence
NAVY = colors.HexColor("#0B1F3A")
NAVY_MID = colors.HexColor("#1E3A5F")
SLATE = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#CBD5E1")
PANEL = colors.HexColor("#F8FAFC")
WHITE = colors.white
TEAL = colors.HexColor("#0F766E")
GREEN = colors.HexColor("#15803D")
AMBER = colors.HexColor("#B45309")
RED = colors.HexColor("#B91C1C")
BLUE = colors.HexColor("#1D4ED8")

PAGE_WIDTH, PAGE_HEIGHT = A4
CONTENT_WIDTH = PAGE_WIDTH - 1.2 * inch

STAGE_LABELS = {
    "upload": "Image Upload",
    "vision_analysis": "Vision AI Analysis",
    "registry_verification": "Registry Verification",
    "risk_assessment": "Risk Assessment",
    "save_investigation": "Save Investigation",
    "report_generation": "Report Generation",
}


class ReportLabInvestigationPdfGenerator:
    """Render a comprehensive police-style investigation report PDF."""

    def generate_investigation_report(self, content: InvestigationReportContent) -> bytes:
        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.65 * inch,
            title=content.title,
            author="SentinelANPR AI",
        )
        styles = _build_styles()
        story: list[object] = []

        story.extend(_header_block(content, styles))
        story.append(_section_banner("1. Case Information"))
        story.append(_case_information_table(content))
        story.append(Spacer(1, 8))

        story.append(_section_banner("2. Investigation Metadata"))
        story.append(_metadata_table(content))
        story.append(Spacer(1, 8))

        story.append(_section_banner("3. Vehicle Evidence"))
        story.extend(_evidence_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("4. Vision AI Observation"))
        story.extend(_vision_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("5. Registry Verification"))
        story.append(_registry_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("6. Vehicle Attribute Comparison"))
        story.extend(_comparison_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("7. Risk Analytics"))
        story.extend(_risk_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("8. AI Reasoning"))
        story.append(
            Paragraph(
                _escape(content.ai_reasoning or _fallback_reasoning(content)),
                styles["body_justify"],
            )
        )
        story.append(Spacer(1, 8))

        story.append(_section_banner("9. Investigation Timeline"))
        story.extend(_timeline_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("10. Investigation Statistics"))
        story.append(_statistics_table(content))
        story.append(Spacer(1, 8))

        story.append(_section_banner("11. Digital Evidence"))
        story.append(_digital_evidence_table(content))
        story.append(Spacer(1, 8))

        story.append(_section_banner("12. Final Investigation Conclusion"))
        story.append(_conclusion_block(content, styles))
        story.append(Spacer(1, 8))

        story.append(_section_banner("13. Officer Recommendation"))
        story.append(
            Paragraph(_escape(content.recommendation), styles["recommendation"])
        )
        story.append(Spacer(1, 14))
        story.append(
            Paragraph(
                "DISCLAIMER: This report is AI-assisted investigative support material. "
                "Enforcement action requires officer judgment and applicable law / departmental SOP. "
                f"Template {TEMPLATE_VERSION} · SentinelANPR AI · Prakasam Police Hackathon",
                styles["footer"],
            )
        )

        document.build(
            story,
            onFirstPage=_draw_page_chrome,
            onLaterPages=_draw_page_chrome,
        )
        return buffer.getvalue()


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "agency": ParagraphStyle(
            "Agency",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "doc_title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=20,
        ),
        "doc_sub": ParagraphStyle(
            "DocSub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=WHITE,
            leading=14,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=MUTED,
            leading=11,
        ),
        "value": ParagraphStyle(
            "Value",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE,
            leading=12,
        ),
        "value_strong": ParagraphStyle(
            "ValueStrong",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=NAVY,
            leading=13,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE,
            leading=13,
            alignment=TA_LEFT,
        ),
        "body_justify": ParagraphStyle(
            "BodyJustify",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        ),
        "recommendation": ParagraphStyle(
            "Recommendation",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=NAVY,
            leading=14,
            borderPadding=6,
        ),
        "status": ParagraphStyle(
            "Status",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "footer": ParagraphStyle(
            "FooterNote",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            textColor=MUTED,
            alignment=TA_CENTER,
            leading=9,
        ),
        "mono": ParagraphStyle(
            "Mono",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=8,
            textColor=SLATE,
            leading=11,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            leading=10,
        ),
    }


def _header_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    case_id = _case_reference(content)
    return [
        Paragraph("PRAKASAM POLICE · SENTINELANPR AI", styles["agency"]),
        Paragraph("OFFICIAL VEHICLE INVESTIGATION REPORT", styles["doc_title"]),
        Paragraph(
            f"{_escape(content.title)} · Generated {_fmt_dt(content.generated_at)}",
            styles["doc_sub"],
        ),
        _status_strip(content),
        Spacer(1, 6),
        Paragraph(f"<b>Case Reference:</b> {_escape(case_id)}", styles["value"]),
        HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceBefore=4, spaceAfter=8),
    ]


def _status_strip(content: InvestigationReportContent) -> Table:
    risk_color = _risk_color(content.risk_level)
    lookup = (content.metadata.lookup_status if content.metadata else None) or "—"
    match_pct = _match_percentage(content)
    vision_conf = _vision_confidence(content)
    data = [
        [
            Paragraph(f"<b>RISK</b><br/>{content.risk_level.upper()}", _center_white()),
            Paragraph(
                f"<b>REGISTRY</b><br/>{_escape(str(lookup).upper())}",
                _center_white(),
            ),
            Paragraph(f"<b>VISION</b><br/>{vision_conf:.0%}", _center_white()),
            Paragraph(f"<b>ATTR MATCH</b><br/>{match_pct}%", _center_white()),
        ]
    ]
    table = Table(data, colWidths=[CONTENT_WIDTH / 4.0] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), risk_color),
                ("BACKGROUND", (1, 0), (1, 0), NAVY_MID),
                ("BACKGROUND", (2, 0), (2, 0), TEAL),
                ("BACKGROUND", (3, 0), (3, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, WHITE),
            ]
        )
    )
    return table


def _center_white() -> ParagraphStyle:
    return ParagraphStyle(
        "StripCell",
        fontName="Helvetica",
        fontSize=8,
        textColor=WHITE,
        alignment=TA_CENTER,
        leading=11,
    )


def _section_banner(title: str) -> Table:
    styles = _build_styles()
    table = Table(
        [[Paragraph(_escape(title), styles["section"])]],
        colWidths=[CONTENT_WIDTH],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
            ]
        )
    )
    return KeepTogether([Spacer(1, 2), table, Spacer(1, 6)])


def _case_information_table(content: InvestigationReportContent) -> Table:
    meta = content.metadata
    rows = [
        ("Investigating Officer", content.officer.officer_name),
        ("Badge Number", content.officer.badge_number),
        ("Rank", content.officer.rank),
        ("Officer ID", content.officer.officer_id),
        ("Subject Registration", content.detected_plate),
        ("Location", (meta.location_label if meta and meta.location_label else "—")),
        ("Report Generated (UTC)", _fmt_dt(content.generated_at)),
        ("Report Classification", "RESTRICTED — LAW ENFORCEMENT USE"),
    ]
    return _kv_table(rows)


def _metadata_table(content: InvestigationReportContent) -> Table:
    meta = content.metadata
    rows = [
        ("Workflow ID", (meta.workflow_id if meta else None) or "—"),
        ("Scan ID", (meta.scan_id if meta else None) or "—"),
        ("Case Reference", _case_reference(content)),
        ("Lookup Status", (meta.lookup_status if meta else None) or "—"),
        ("Verification Message", (meta.verification_message if meta else None) or "—"),
        (
            "Total Duration",
            _fmt_duration(meta.total_duration_ms if meta else None),
        ),
        ("AI Template", TEMPLATE_VERSION),
        ("Generating System", "SentinelANPR AI Vision Investigation Platform"),
    ]
    return _kv_table(rows)


def _evidence_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    blocks: list[object] = []
    image = _build_image(content.vehicle_image_bytes)
    if image is not None:
        blocks.append(image)
        blocks.append(Spacer(1, 4))
        blocks.append(
            Paragraph(
                "Exhibit A — Uploaded vehicle image retained as digital evidence.",
                styles["small"],
            )
        )
    else:
        blocks.append(Paragraph("Vehicle image could not be embedded.", styles["body"]))
    checksum = (
        content.metadata.evidence_checksum_sha256
        if content.metadata and content.metadata.evidence_checksum_sha256
        else "—"
    )
    blocks.append(Spacer(1, 4))
    blocks.append(_kv_table([("Evidence Image SHA-256", checksum[:32] + "…" if len(checksum) > 32 else checksum)]))
    return blocks


def _vision_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    vision = content.vision_analysis
    blocks: list[object] = []
    if vision is None:
        # Fall back to registration readout section (legacy path)
        blocks.append(
            _kv_table(
                [
                    ("Registration Number", content.ocr_result.registration_number),
                    ("Detected Text", content.ocr_result.detected_plate_text),
                    ("Confidence", f"{content.ocr_result.ocr_confidence:.0%}"),
                ]
            )
        )
        blocks.append(Spacer(1, 6))
        blocks.append(_progress_bar("Vision Confidence", content.ocr_result.ocr_confidence, TEAL))
        return blocks

    blocks.append(
        _kv_table(
            [
                ("Registration Number", vision.registration_number or content.detected_plate),
                ("Brand", vision.brand or "—"),
                ("Model", vision.model or "—"),
                ("Color", vision.color or "—"),
                ("Vehicle Type", vision.vehicle_type or "—"),
                ("Model Version", vision.model_version or "vision-ai"),
                ("Vision Explanation", vision.explanation or "—"),
            ]
        )
    )
    blocks.append(Spacer(1, 6))
    overall = vision.confidence if vision.confidence is not None else content.ocr_result.ocr_confidence
    blocks.append(_progress_bar("Overall Vision Confidence", overall, TEAL))
    if vision.color_confidence is not None:
        blocks.append(Spacer(1, 3))
        blocks.append(_progress_bar("Color Confidence", vision.color_confidence, BLUE))
    if vision.vehicle_type_confidence is not None:
        blocks.append(Spacer(1, 3))
        blocks.append(_progress_bar("Type Confidence", vision.vehicle_type_confidence, BLUE))
    if vision.brand_confidence is not None:
        blocks.append(Spacer(1, 3))
        blocks.append(_progress_bar("Brand Confidence", vision.brand_confidence, BLUE))
    return blocks


def _registry_block(content: InvestigationReportContent, styles: dict) -> object:
    details = content.vehicle_details
    meta = content.metadata
    lookup = (meta.lookup_status if meta else None) or (
        "found" if details and (details.plate_number or details.make) else "not_found"
    )
    if details is None and str(lookup).lower() in {"not_found", "missing"}:
        return Paragraph(
            _escape(
                (meta.verification_message if meta and meta.verification_message else None)
                or "No matching vehicle record was found in the registry."
            ),
            styles["body"],
        )
    if details is None:
        return Paragraph("No registry vehicle details were provided.", styles["body"])

    return _kv_table(
        [
            ("Lookup Status", str(lookup).upper()),
            ("Plate Number", details.plate_number or "—"),
            ("Registered Owner", details.registered_owner or "—"),
            ("Make", details.make or "—"),
            ("Model", details.model or "—"),
            ("Year", str(details.year) if details.year is not None else "—"),
            ("Color", details.color or "—"),
            ("Vehicle Type", details.vehicle_type or "—"),
            ("Registration Status", details.registration_status or "—"),
            ("Jurisdiction", details.jurisdiction or "—"),
            (
                "Verification Message",
                (meta.verification_message if meta and meta.verification_message else "—"),
            ),
        ]
    )


def _comparison_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    comparison = content.attribute_comparison
    blocks: list[object] = []
    if comparison is None or not comparison.items:
        blocks.append(
            Paragraph(
                "Attribute comparison data was not supplied for this investigation.",
                styles["body"],
            )
        )
        return blocks

    match_pct = _match_percentage(content)
    overall = (
        "MATCH"
        if comparison.overall_match is True
        else "MISMATCH"
        if comparison.overall_match is False
        else "INCONCLUSIVE"
    )
    blocks.append(
        Paragraph(
            f"Overall attribute match: <b>{overall}</b> · Match rate: <b>{match_pct}%</b>",
            styles["value_strong"],
        )
    )
    blocks.append(Spacer(1, 4))
    blocks.append(_progress_bar("Attribute Match Rate", match_pct / 100.0, BLUE))
    blocks.append(Spacer(1, 6))

    header = [
        Paragraph("<b>Attribute</b>", styles["label"]),
        Paragraph("<b>Vision AI</b>", styles["label"]),
        Paragraph("<b>Registry</b>", styles["label"]),
        Paragraph("<b>Result</b>", styles["label"]),
        Paragraph("<b>Conf.</b>", styles["label"]),
    ]
    rows: list[list[object]] = [header]
    for item in comparison.items:
        result = (
            "MATCH"
            if item.matches is True
            else "MISMATCH"
            if item.matches is False
            else "—"
        )
        conf = f"{item.confidence:.0%}" if item.confidence is not None else "—"
        rows.append(
            [
                Paragraph(_escape(item.attribute), styles["value"]),
                Paragraph(_escape(item.observed or "—"), styles["value"]),
                Paragraph(_escape(item.registered or "—"), styles["value"]),
                Paragraph(result, styles["value_strong"]),
                Paragraph(conf, styles["value"]),
            ]
        )
    table = Table(
        rows,
        colWidths=[
            CONTENT_WIDTH * 0.18,
            CONTENT_WIDTH * 0.26,
            CONTENT_WIDTH * 0.26,
            CONTENT_WIDTH * 0.18,
            CONTENT_WIDTH * 0.12,
        ],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    blocks.append(table)
    return blocks


def _risk_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    blocks: list[object] = [
        _risk_gauge(content.risk_score, content.risk_level),
        Spacer(1, 6),
        _kv_table(
            [
                ("Risk Score", f"{int(round(content.risk_score * 100))}/100"),
                ("Risk Level", content.risk_level.upper()),
                (
                    "Risk Explanation",
                    (
                        content.metadata.risk_explanation
                        if content.metadata and content.metadata.risk_explanation
                        else "—"
                    ),
                ),
            ]
        ),
    ]
    if content.risk_signals:
        blocks.append(Spacer(1, 6))
        blocks.append(Paragraph("<b>Risk Signals</b>", styles["value_strong"]))
        blocks.append(Spacer(1, 3))
        signal_rows = [
            [
                Paragraph("<b>Signal</b>", styles["label"]),
                Paragraph("<b>Weight</b>", styles["label"]),
                Paragraph("<b>Detail</b>", styles["label"]),
            ]
        ]
        for signal in content.risk_signals:
            signal_rows.append(
                [
                    Paragraph(_escape(signal.name), styles["value"]),
                    Paragraph(f"{signal.weight:.2f}", styles["value"]),
                    Paragraph(_escape(signal.detail), styles["value"]),
                ]
            )
        table = Table(
            signal_rows,
            colWidths=[CONTENT_WIDTH * 0.28, CONTENT_WIDTH * 0.12, CONTENT_WIDTH * 0.60],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        blocks.append(table)
    return blocks


def _timeline_block(content: InvestigationReportContent, styles: dict) -> list[object]:
    if not content.timeline:
        return [Paragraph("Investigation timeline steps were not recorded.", styles["body"])]

    rows = [
        [
            Paragraph("<b>#</b>", styles["label"]),
            Paragraph("<b>Stage</b>", styles["label"]),
            Paragraph("<b>Status</b>", styles["label"]),
            Paragraph("<b>Message</b>", styles["label"]),
            Paragraph("<b>Duration</b>", styles["label"]),
        ]
    ]
    for index, step in enumerate(content.timeline, start=1):
        label = STAGE_LABELS.get(step.stage, step.stage.replace("_", " ").title())
        rows.append(
            [
                Paragraph(str(index), styles["value"]),
                Paragraph(_escape(label), styles["value"]),
                Paragraph(_escape(step.status.upper()), styles["value_strong"]),
                Paragraph(_escape(step.message), styles["value"]),
                Paragraph(_fmt_duration(step.duration_ms), styles["value"]),
            ]
        )
    table = Table(
        rows,
        colWidths=[
            CONTENT_WIDTH * 0.06,
            CONTENT_WIDTH * 0.24,
            CONTENT_WIDTH * 0.12,
            CONTENT_WIDTH * 0.42,
            CONTENT_WIDTH * 0.16,
        ],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return [table]


def _statistics_table(content: InvestigationReportContent) -> Table:
    steps = content.timeline
    success_steps = sum(1 for s in steps if s.status.lower() == "success")
    failed_steps = sum(1 for s in steps if s.status.lower() != "success")
    timed = [s.duration_ms for s in steps if s.duration_ms is not None]
    avg_ms = int(sum(timed) / len(timed)) if timed else None
    match_pct = _match_percentage(content)
    vision_conf = _vision_confidence(content)
    rows = [
        ("Stages Executed", str(len(steps)) if steps else "—"),
        ("Successful Stages", str(success_steps) if steps else "—"),
        ("Failed / Incomplete Stages", str(failed_steps) if steps else "—"),
        ("Average Stage Duration", _fmt_duration(avg_ms)),
        ("Total Investigation Duration", _fmt_duration(
            content.metadata.total_duration_ms if content.metadata else None
        )),
        ("Vision Confidence", f"{vision_conf:.0%}"),
        ("Attribute Match Rate", f"{match_pct}%"),
        ("Risk Score", f"{int(round(content.risk_score * 100))}/100"),
        ("Risk Signals Count", str(len(content.risk_signals))),
    ]
    return _kv_table(rows)


def _digital_evidence_table(content: InvestigationReportContent) -> Table:
    meta = content.metadata
    checksum = (meta.evidence_checksum_sha256 if meta else None) or "—"
    rows = [
        ("Evidence Type", "Vehicle photograph (binary image)"),
        ("Evidence Size", f"{len(content.vehicle_image_bytes):,} bytes"),
        ("Evidence SHA-256", checksum),
        ("Custody", "Captured via authenticated officer session"),
        ("Retention", "Stored with investigation scan / report artifact"),
        ("Integrity Note", "Hash computed at report generation time from image bytes"),
    ]
    return _kv_table(rows)


def _conclusion_block(content: InvestigationReportContent, styles: dict) -> object:
    meta = content.metadata
    summary = meta.investigation_summary if meta and meta.investigation_summary else None
    if summary:
        text = summary
    else:
        text = (
            f"Subject registration {content.detected_plate} was investigated with risk level "
            f"{content.risk_level.upper()} "
            f"({int(round(content.risk_score * 100))}/100). "
            f"Registry status: {(meta.lookup_status if meta and meta.lookup_status else 'unavailable')}. "
            f"Attribute match rate: {_match_percentage(content)}%."
        )
    return Paragraph(_escape(text), styles["body_justify"])


def _fallback_reasoning(content: InvestigationReportContent) -> str:
    return (
        f"Investigation of registration {content.detected_plate} produced risk level "
        f"{content.risk_level.upper()} with score {int(round(content.risk_score * 100))}/100. "
        f"Officer recommendation: {content.recommendation}"
    )


def _progress_bar(label: str, value: float, fill_color: colors.Color) -> Table:
    ratio = max(0.0, min(1.0, float(value)))
    pct = int(round(ratio * 100))
    bar_width = CONTENT_WIDTH
    filled = max(bar_width * ratio, 0.5 * mm if ratio > 0 else 0)
    empty = bar_width - filled
    label_para = Paragraph(
        f"<b>{_escape(label)}</b> &nbsp; {pct}%",
        ParagraphStyle("BarLabel", fontName="Helvetica", fontSize=8, textColor=SLATE),
    )
    # Two-segment bar
    if empty <= 0:
        bar = Table([[""]], colWidths=[bar_width], rowHeights=[8])
        bar.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), fill_color),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ]
            )
        )
    elif filled <= 0:
        bar = Table([[""]], colWidths=[bar_width], rowHeights=[8])
        bar.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E2E8F0")),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ]
            )
        )
    else:
        bar = Table([["", ""]], colWidths=[filled, empty], rowHeights=[8])
        bar.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), fill_color),
                    ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#E2E8F0")),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ]
            )
        )
    wrapper = Table([[label_para], [bar]], colWidths=[bar_width])
    wrapper.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return wrapper


def _risk_gauge(score: float, level: str) -> Table:
    ratio = max(0.0, min(1.0, float(score)))
    pct = int(round(ratio * 100))
    fill = _risk_color(level)
    styles = _build_styles()
    left = Paragraph(
        f"<b>RISK GAUGE</b><br/>Level: {level.upper()}<br/>Score: {pct}/100",
        ParagraphStyle(
            "GaugeText",
            fontName="Helvetica",
            fontSize=9,
            textColor=NAVY,
            leading=12,
        ),
    )
    bar = _progress_bar("Risk Intensity", ratio, fill)
    table = Table([[left, bar]], colWidths=[CONTENT_WIDTH * 0.32, CONTENT_WIDTH * 0.68])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.75, _risk_color(level)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    del styles
    return table


def _kv_table(rows: Sequence[tuple[str, str]]) -> Table:
    styles = _build_styles()
    data = [
        [
            Paragraph(_escape(label), styles["label"]),
            Paragraph(_escape(value if value is not None else "—"), styles["value"]),
        ]
        for label, value in rows
    ]
    table = Table(data, colWidths=[CONTENT_WIDTH * 0.32, CONTENT_WIDTH * 0.68])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _build_image(image_bytes: bytes) -> Image | None:
    try:
        image = Image(io.BytesIO(image_bytes))
        max_width = CONTENT_WIDTH
        max_height = 2.6 * inch
        width_scale = max_width / image.drawWidth
        height_scale = max_height / image.drawHeight
        scale = min(width_scale, height_scale, 1.0)
        image.drawWidth *= scale
        image.drawHeight *= scale
        image.hAlign = "CENTER"
        return image
    except Exception:
        return None


def _draw_page_chrome(canvas, doc) -> None:  # noqa: ANN001
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(2)
    canvas.rect(0.4 * inch, 0.4 * inch, PAGE_WIDTH - 0.8 * inch, PAGE_HEIGHT - 0.8 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.6 * inch, 0.28 * inch, "SentinelANPR AI · Confidential Law Enforcement Record")
    canvas.drawRightString(PAGE_WIDTH - 0.6 * inch, 0.28 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _case_reference(content: InvestigationReportContent) -> str:
    meta = content.metadata
    if meta and meta.scan_id:
        return f"INV-{meta.scan_id[:8].upper()}-{content.detected_plate}"
    if meta and meta.workflow_id:
        return f"INV-{meta.workflow_id[:8].upper()}-{content.detected_plate}"
    stamp = content.generated_at.strftime("%Y%m%d%H%M")
    return f"INV-{stamp}-{content.detected_plate}"


def _vision_confidence(content: InvestigationReportContent) -> float:
    if content.vision_analysis and content.vision_analysis.confidence is not None:
        return float(content.vision_analysis.confidence)
    return float(content.ocr_result.ocr_confidence)


def _match_percentage(content: InvestigationReportContent) -> int:
    comparison = content.attribute_comparison
    if comparison is None or not comparison.items:
        return 0
    matched = sum(1 for item in comparison.items if item.matches is True)
    return int(round((matched / len(comparison.items)) * 100))


def _risk_color(level: str) -> colors.Color:
    normalized = (level or "").lower()
    if normalized == "critical":
        return colors.HexColor("#7F1D1D")
    if normalized == "high":
        return RED
    if normalized == "medium":
        return AMBER
    return GREEN


def _fmt_dt(value) -> str:  # noqa: ANN001
    return value.strftime("%d %b %Y, %H:%M:%S UTC")


def _fmt_duration(ms: int | None) -> str:
    if ms is None:
        return "—"
    if ms < 1000:
        return f"{ms} ms"
    return f"{ms / 1000:.2f} s"


def _escape(text: str | None) -> str:
    if text is None:
        return "—"
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
