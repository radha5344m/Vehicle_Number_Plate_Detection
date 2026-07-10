"""Unit tests for dynamic investigation report reasoning."""

from sentinel_anpr.application.dto.report_dto import (
    AttributeComparisonItemReportDto,
    AttributeComparisonReportDto,
    GenerateInvestigationReportCommand,
    OcrResultDto,
    RiskSignalReportDto,
    VehicleDetailsDto,
    VisionAnalysisDto,
)
from sentinel_anpr.application.services.investigation_report_reasoning import (
    compose_investigation_reasoning,
)


def test_compose_reasoning_uses_investigation_outputs() -> None:
    command = GenerateInvestigationReportCommand(
        officer_id="officer-1",
        officer_name="Ravi Kumar",
        badge_number="AP001",
        officer_rank="Sub-Inspector",
        vehicle_image_bytes=b"image",
        detected_plate="AP09AB1234",
        ocr_result=OcrResultDto(
            registration_number="AP09AB1234",
            detected_plate_text="AP09AB1234",
            ocr_confidence=0.91,
        ),
        vehicle_details=VehicleDetailsDto(
            plate_number="AP09AB1234",
            make="Toyota",
            model="Innova",
            color="White",
            registered_owner="Ravi Kumar",
            registration_status="active",
        ),
        risk_score=0.22,
        risk_level="medium",
        recommendation="Conduct secondary physical verification.",
        vision_analysis=VisionAnalysisDto(
            registration_number="AP09AB1234",
            brand="Toyota",
            model="Innova",
            color="white",
            vehicle_type="car",
            confidence=0.91,
            explanation="Clear front plate",
        ),
        attribute_comparison=AttributeComparisonReportDto(
            items=(
                AttributeComparisonItemReportDto(
                    attribute="color",
                    observed="white",
                    registered="White",
                    matches=True,
                    confidence=0.9,
                ),
                AttributeComparisonItemReportDto(
                    attribute="brand",
                    observed="Honda",
                    registered="Toyota",
                    matches=False,
                    confidence=0.8,
                ),
            ),
            overall_match=False,
        ),
        risk_signals=(
            RiskSignalReportDto(
                name="attribute_mismatch",
                weight=0.4,
                detail="Brand mismatch observed",
            ),
        ),
        lookup_status="found",
        verification_message="Vehicle found",
        risk_explanation="Partial attribute mismatch",
        investigation_summary="Medium risk due to brand mismatch",
    )

    text = compose_investigation_reasoning(command)

    assert "AP09AB1234" in text
    assert "91%" in text or "0.91" in text or "91" in text
    assert "Registry verification located" in text
    assert "match rate" in text.lower()
    assert "Brand mismatch" in text or "brand" in text.lower()
    assert "MEDIUM" in text
    assert "Conduct secondary physical verification." in text
