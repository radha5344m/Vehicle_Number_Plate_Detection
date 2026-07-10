"""Investigation summary policy unit tests."""

from sentinel_anpr.domain.verification.services.attribute_comparison_policy import (
    AttributeComparisonItem,
    AttributeComparisonResult,
)
from sentinel_anpr.domain.verification.services.investigation_summary_policy import (
    InvestigationSummaryInput,
    InvestigationSummaryPolicy,
)


def test_summary_for_found_vehicle() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=True,
            detection_confidence=0.9,
            registration_number="AP09AB1234",
            ocr_confidence=0.92,
            vehicle_found=True,
            registration_status="active",
            attribute_comparison=AttributeComparisonResult(
                items=(
                    AttributeComparisonItem(
                        attribute="color",
                        observed="white",
                        registered="white",
                        matches=True,
                        confidence=0.9,
                    ),
                ),
                overall_match=True,
            ),
            risk_level="low",
        )
    )
    assert "Plate detected successfully" in summary
    assert "AP09AB1234" in summary
    assert "matches registry" in summary
    assert "LOW" in summary


def test_summary_for_not_found_vehicle() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=True,
            detection_confidence=0.8,
            registration_number="AP99ZZ9999",
            ocr_confidence=0.75,
            vehicle_found=False,
            registration_status=None,
            attribute_comparison=None,
            risk_level="high",
        )
    )
    assert "not found in the registry" in summary
    assert "fake plate" in summary.lower()
