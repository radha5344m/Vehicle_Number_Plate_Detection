"""Investigation report policy unit tests."""

from datetime import UTC, datetime

import pytest

from sentinel_anpr.domain.reporting.entities.investigation_report_content import (
    InvestigationReportContent,
    OcrReportSection,
    OfficerReportSection,
)
from sentinel_anpr.domain.reporting.services.investigation_report_policy import (
    InvestigationReportPolicy,
)


def _content(**overrides: object) -> InvestigationReportContent:
    defaults = {
        "title": "Investigation Report",
        "generated_at": datetime.now(UTC),
        "officer": OfficerReportSection(
            officer_id="officer-1",
            officer_name="Ravi Kumar",
            badge_number="AP001",
            rank="Sub-Inspector",
        ),
        "detected_plate": "AP09AB1234",
        "ocr_result": OcrReportSection(
            registration_number="AP09AB1234",
            detected_plate_text="AP09AB1234",
            ocr_confidence=0.92,
        ),
        "vehicle_details": None,
        "risk_score": 0.1,
        "risk_level": "low",
        "recommendation": "Proceed with routine checks.",
        "vehicle_image_bytes": b"fake-image",
        "vision_analysis": None,
        "attribute_comparison": None,
        "risk_signals": (),
        "timeline": (),
        "metadata": None,
        "ai_reasoning": None,
    }
    defaults.update(overrides)
    return InvestigationReportContent(**defaults)  # type: ignore[arg-type]


def test_validate_accepts_valid_content() -> None:
    InvestigationReportPolicy().validate(_content())


def test_validate_rejects_missing_image() -> None:
    with pytest.raises(ValueError, match="Vehicle image is required"):
        InvestigationReportPolicy().validate(_content(vehicle_image_bytes=b""))
