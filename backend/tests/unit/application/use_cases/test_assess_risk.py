"""Assess risk use case unit tests."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.attribute_dto import VehicleAttributesResult
from sentinel_anpr.application.dto.recognition_dto import RecognizePlateResult
from sentinel_anpr.application.dto.risk_dto import AssessRiskCommand
from sentinel_anpr.application.dto.vehicle_dto import VehicleRecordDto
from sentinel_anpr.application.use_cases.risk.assess_risk_use_case import AssessRiskUseCase
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel
from sentinel_anpr.domain.risk.services.risk_engine_policy import RiskEnginePolicy


def _vehicle_record(**overrides: object) -> VehicleRecordDto:
    defaults = {
        "vehicle_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "plate_number": "AP09AB1234",
        "jurisdiction": "AP",
        "make": "Toyota",
        "model": "Innova Crysta",
        "color": "White",
        "year": 2020,
        "vehicle_type": "car",
        "registration_status": "active",
        "registered_owner": "Ravi Kumar",
        "registry_external_id": "RTO-ONG-1001",
        "registry_synced_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return VehicleRecordDto(**defaults)  # type: ignore[arg-type]


def _attributes(**overrides: object) -> VehicleAttributesResult:
    defaults = {
        "color": "white",
        "vehicle_type": "car",
        "brand": "Toyota",
        "color_confidence": 0.85,
        "vehicle_type_confidence": 0.80,
        "brand_confidence": 0.40,
        "model_version": "test",
    }
    defaults.update(overrides)
    return VehicleAttributesResult(**defaults)  # type: ignore[arg-type]


def _ocr_result(**overrides: object) -> RecognizePlateResult:
    defaults = {
        "registration_number": "AP09AB1234",
        "detected_plate_text": "AP09AB1234",
        "ocr_confidence": 0.92,
        "char_confidences": (0.9, 0.9, 0.9),
        "model_version": "test",
    }
    defaults.update(overrides)
    return RecognizePlateResult(**defaults)  # type: ignore[arg-type]


def test_assess_risk_use_case_returns_structured_result() -> None:
    use_case = AssessRiskUseCase(risk_engine_policy=RiskEnginePolicy())
    result = use_case.execute(
        AssessRiskCommand(
            ocr_result=_ocr_result(),
            vehicle_record=_vehicle_record(),
            detected_attributes=_attributes(),
        )
    )
    assert result.risk_score == 0.0
    assert result.risk_level == RiskLevel.LOW
    assert result.explanation
    assert result.recommendation
    assert result.policy_version == "risk-engine-v1"


def test_assess_risk_use_case_without_vehicle_record() -> None:
    use_case = AssessRiskUseCase(risk_engine_policy=RiskEnginePolicy())
    result = use_case.execute(
        AssessRiskCommand(
            ocr_result=_ocr_result(),
            vehicle_record=None,
            detected_attributes=_attributes(),
        )
    )
    assert result.risk_level == RiskLevel.HIGH
    assert any(signal.name == "PLATE_NOT_IN_REGISTRY" for signal in result.signals)
