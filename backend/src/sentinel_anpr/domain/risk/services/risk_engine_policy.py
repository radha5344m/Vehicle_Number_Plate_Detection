"""Pure risk scoring policy."""

from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.domain.risk.entities.risk_assessment import RiskAssessment
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel
from sentinel_anpr.domain.risk.value_objects.risk_assessment_input import RiskAssessmentInput
from sentinel_anpr.domain.risk.value_objects.risk_signal import RiskSignal

POLICY_VERSION = "risk-engine-v1"

_LOW_OCR_THRESHOLD = 0.60
_COLOR_MISMATCH_WEIGHT = 0.25
_TYPE_MISMATCH_WEIGHT = 0.30
_BRAND_MISMATCH_WEIGHT = 0.20
_PLATE_MISMATCH_WEIGHT = 0.45
_NOT_IN_REGISTRY_WEIGHT = 0.50
_STOLEN_WEIGHT = 0.55
_SUSPENDED_WEIGHT = 0.35
_INACTIVE_WEIGHT = 0.15


class RiskEnginePolicy:
    """Score fraud and clone risk from OCR, registry, and visual attributes."""

    def assess(self, inputs: RiskAssessmentInput) -> RiskAssessment:
        signals = self._collect_signals(inputs)
        risk_score = min(1.0, round(sum(signal.weight for signal in signals), 4))
        risk_level = self._resolve_level(risk_score, signals)
        explanation = self._build_explanation(signals, risk_level)
        recommendation = self._build_recommendation(risk_level, signals)
        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation,
            recommendation=recommendation,
            signals=tuple(signals),
            policy_version=POLICY_VERSION,
        )

    def _collect_signals(self, inputs: RiskAssessmentInput) -> list[RiskSignal]:
        signals: list[RiskSignal] = []

        ocr_signal = self._low_ocr_signal(inputs.ocr_confidence)
        if ocr_signal is not None:
            signals.append(ocr_signal)

        registry = inputs.registry_vehicle
        if registry is None:
            signals.append(
                RiskSignal(
                    name="PLATE_NOT_IN_REGISTRY",
                    weight=_NOT_IN_REGISTRY_WEIGHT,
                    detail="Registration number was not found in the vehicle registry.",
                )
            )
            return signals

        normalized_plate = normalize_registration_number(inputs.plate_number)
        normalized_registry_plate = normalize_registration_number(registry.plate_number)
        if normalized_plate != normalized_registry_plate:
            signals.append(
                RiskSignal(
                    name="PLATE_MISMATCH",
                    weight=_PLATE_MISMATCH_WEIGHT,
                    detail=(
                        f"OCR plate '{inputs.plate_number}' does not match registry plate "
                        f"'{registry.plate_number}'."
                    ),
                )
            )

        status_signal = self._registration_status_signal(registry.registration_status)
        if status_signal is not None:
            signals.append(status_signal)

        if not _colors_match(inputs.observed_color, registry.color):
            signals.append(
                RiskSignal(
                    name="COLOR_MISMATCH",
                    weight=_COLOR_MISMATCH_WEIGHT,
                    detail=(
                        f"Observed color '{inputs.observed_color}' does not match registered "
                        f"color '{registry.color}'."
                    ),
                )
            )

        if not _types_match(inputs.observed_vehicle_type, registry.vehicle_type):
            signals.append(
                RiskSignal(
                    name="TYPE_MISMATCH",
                    weight=_TYPE_MISMATCH_WEIGHT,
                    detail=(
                        f"Observed vehicle type '{inputs.observed_vehicle_type}' does not match "
                        f"registered type '{registry.vehicle_type}'."
                    ),
                )
            )

        brand_signal = self._brand_mismatch_signal(inputs.observed_brand, registry.make)
        if brand_signal is not None:
            signals.append(brand_signal)

        return signals

    def _low_ocr_signal(self, ocr_confidence: float) -> RiskSignal | None:
        if ocr_confidence >= _LOW_OCR_THRESHOLD:
            return None
        weight = round(0.20 * (1.0 - max(ocr_confidence, 0.0) / _LOW_OCR_THRESHOLD), 4)
        return RiskSignal(
            name="LOW_OCR_CONFIDENCE",
            weight=weight,
            detail=f"OCR confidence {ocr_confidence:.2f} is below {_LOW_OCR_THRESHOLD:.2f}.",
        )

    def _registration_status_signal(self, registration_status: str) -> RiskSignal | None:
        status = registration_status.strip().lower()
        if status == "stolen":
            return RiskSignal(
                name="REGISTRATION_STOLEN",
                weight=_STOLEN_WEIGHT,
                detail="Vehicle is flagged as stolen in the registry.",
            )
        if status == "suspended":
            return RiskSignal(
                name="REGISTRATION_SUSPENDED",
                weight=_SUSPENDED_WEIGHT,
                detail="Vehicle registration is suspended.",
            )
        if status != "active":
            return RiskSignal(
                name="REGISTRATION_INACTIVE",
                weight=_INACTIVE_WEIGHT,
                detail=f"Vehicle registration status is '{registration_status}'.",
            )
        return None

    def _brand_mismatch_signal(
        self,
        observed_brand: str | None,
        registered_make: str,
    ) -> RiskSignal | None:
        if observed_brand is None:
            return None
        if _brands_match(observed_brand, registered_make):
            return None
        return RiskSignal(
            name="BRAND_MISMATCH",
            weight=_BRAND_MISMATCH_WEIGHT,
            detail=(
                f"Observed brand '{observed_brand}' does not match registered make "
                f"'{registered_make}'."
            ),
        )

    def _resolve_level(self, risk_score: float, signals: list[RiskSignal]) -> RiskLevel:
        critical_signals = {"REGISTRATION_STOLEN", "PLATE_MISMATCH"}
        if any(signal.name in critical_signals for signal in signals) and risk_score >= 0.45:
            return RiskLevel.CRITICAL
        if risk_score >= 0.75:
            return RiskLevel.CRITICAL
        if risk_score >= 0.50:
            return RiskLevel.HIGH
        if risk_score >= 0.25:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _build_explanation(self, signals: list[RiskSignal], risk_level: RiskLevel) -> str:
        if not signals:
            return (
                "No significant risk signals detected. OCR result, registry record, and "
                "detected attributes are consistent."
            )
        details = "; ".join(signal.detail for signal in signals)
        return f"Risk level {risk_level.value}: {details}"

    def _build_recommendation(self, risk_level: RiskLevel, signals: list[RiskSignal]) -> str:
        if any(signal.name == "PLATE_NOT_IN_REGISTRY" for signal in signals):
            return (
                "Vehicle not found in registry. Possible fake plate or unregistered vehicle. "
                "Conduct detailed verification and detain the vehicle if inconsistencies persist."
            )
        if any(signal.name == "REGISTRATION_STOLEN" for signal in signals):
            return "Immediate intervention required. Detain the vehicle and contact control room."
        if risk_level == RiskLevel.CRITICAL:
            return "Escalate immediately. Detain the vehicle for full investigation."
        if risk_level == RiskLevel.HIGH:
            return "Conduct detailed verification and detain the vehicle if inconsistencies persist."
        if risk_level == RiskLevel.MEDIUM:
            return "Verify documents, inspect the vehicle visually, and confirm owner identity."
        return "Proceed with routine checks."


def _normalize_token(value: str) -> str:
    return value.strip().lower()


def _colors_match(observed: str, registered: str) -> bool:
    return _normalize_token(observed) == _normalize_token(registered)


def _types_match(observed: str, registered: str) -> bool:
    observed_type = _normalize_token(observed)
    registered_type = _normalize_token(registered)
    if observed_type == registered_type:
        return True
    compatible_groups = (
        {"car", "suv"},
        {"truck", "bus"},
    )
    return any(
        observed_type in group and registered_type in group for group in compatible_groups
    )


def _brands_match(observed_brand: str, registered_make: str) -> bool:
    observed = _normalize_token(observed_brand)
    registered = _normalize_token(registered_make)
    return observed in registered or registered in observed
