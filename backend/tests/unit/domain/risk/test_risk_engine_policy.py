"""Risk engine policy unit tests."""

from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel
from sentinel_anpr.domain.risk.services.risk_engine_policy import RiskEnginePolicy
from sentinel_anpr.domain.risk.value_objects.risk_assessment_input import (
    RegistryVehicleSnapshot,
    RiskAssessmentInput,
)


def _registry_vehicle(**overrides: object) -> RegistryVehicleSnapshot:
    defaults = {
        "plate_number": "AP09AB1234",
        "make": "Toyota",
        "color": "white",
        "vehicle_type": "car",
        "registration_status": "active",
    }
    defaults.update(overrides)
    return RegistryVehicleSnapshot(**defaults)  # type: ignore[arg-type]


def _inputs(**overrides: object) -> RiskAssessmentInput:
    defaults = {
        "plate_number": "AP09AB1234",
        "ocr_confidence": 0.92,
        "registry_vehicle": _registry_vehicle(),
        "observed_color": "white",
        "observed_vehicle_type": "car",
        "observed_brand": "Toyota",
        "color_confidence": 0.85,
        "vehicle_type_confidence": 0.80,
        "brand_confidence": 0.40,
    }
    defaults.update(overrides)
    return RiskAssessmentInput(**defaults)  # type: ignore[arg-type]


def test_clean_match_low_risk() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(_inputs())
    assert result.risk_score == 0.0
    assert result.risk_level == RiskLevel.LOW
    assert "routine checks" in result.recommendation.lower()


def test_not_in_registry_high_risk() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(_inputs(registry_vehicle=None))
    assert result.risk_score == 0.50
    assert result.risk_level == RiskLevel.HIGH
    assert any(signal.name == "PLATE_NOT_IN_REGISTRY" for signal in result.signals)
    assert "not found in registry" in result.recommendation.lower()


def test_stolen_vehicle_critical_risk() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(
        _inputs(
            registry_vehicle=_registry_vehicle(registration_status="stolen"),
        )
    )
    assert result.risk_score >= 0.55
    assert result.risk_level == RiskLevel.CRITICAL
    assert "control room" in result.recommendation.lower()


def test_color_and_type_mismatch_high_risk() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(
        _inputs(
            observed_color="black",
            observed_vehicle_type="motorcycle",
        )
    )
    assert result.risk_score >= 0.50
    assert result.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    signal_names = {signal.name for signal in result.signals}
    assert "COLOR_MISMATCH" in signal_names
    assert "TYPE_MISMATCH" in signal_names


def test_low_ocr_confidence_adds_signal() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(_inputs(ocr_confidence=0.40))
    assert any(signal.name == "LOW_OCR_CONFIDENCE" for signal in result.signals)
    assert result.risk_score > 0.0


def test_plate_mismatch_critical_risk() -> None:
    policy = RiskEnginePolicy()
    result = policy.assess(_inputs(plate_number="AP99ZZ9999"))
    assert any(signal.name == "PLATE_MISMATCH" for signal in result.signals)
    assert result.risk_level == RiskLevel.CRITICAL
