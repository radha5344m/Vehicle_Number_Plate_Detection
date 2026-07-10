"""Investigation report validation rules."""

from sentinel_anpr.domain.reporting.entities.investigation_report_content import (
    InvestigationReportContent,
)
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel


class InvestigationReportPolicy:
    """Validate mandatory investigation report fields before PDF generation."""

    def validate(self, content: InvestigationReportContent) -> None:
        if not content.detected_plate.strip():
            raise ValueError("Detected plate is required")

        if not content.ocr_result.registration_number.strip():
            raise ValueError("OCR registration number is required")

        if not 0.0 <= content.ocr_result.ocr_confidence <= 1.0:
            raise ValueError("OCR confidence must be between 0.0 and 1.0")

        if not 0.0 <= content.risk_score <= 1.0:
            raise ValueError("Risk score must be between 0.0 and 1.0")

        if content.risk_level.lower() not in {level.value for level in RiskLevel}:
            raise ValueError(f"Invalid risk level: {content.risk_level}")

        if not content.recommendation.strip():
            raise ValueError("Recommendation is required")

        if not content.vehicle_image_bytes:
            raise ValueError("Vehicle image is required")

        if len(content.vehicle_image_bytes) > 10 * 1024 * 1024:
            raise ValueError("Vehicle image must not exceed 10 MB")
