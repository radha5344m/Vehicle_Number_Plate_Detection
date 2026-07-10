"""Assess vehicle risk from OCR, registry, and visual attributes."""

from sentinel_anpr.application.dto.risk_dto import AssessRiskCommand, AssessRiskResult, RiskSignalDto
from sentinel_anpr.domain.risk.services.risk_engine_policy import RiskEnginePolicy
from sentinel_anpr.domain.risk.value_objects.risk_assessment_input import (
    RegistryVehicleSnapshot,
    RiskAssessmentInput,
)


class AssessRiskUseCase:
    """Pure business-logic risk scoring — no OCR, database, or UI."""

    def __init__(self, risk_engine_policy: RiskEnginePolicy) -> None:
        self._risk_engine_policy = risk_engine_policy

    def execute(self, command: AssessRiskCommand) -> AssessRiskResult:
        assessment = self._risk_engine_policy.assess(self._to_domain_input(command))
        return AssessRiskResult(
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            explanation=assessment.explanation,
            recommendation=assessment.recommendation,
            signals=tuple(
                RiskSignalDto(name=signal.name, weight=signal.weight, detail=signal.detail)
                for signal in assessment.signals
            ),
            policy_version=assessment.policy_version,
        )

    def _to_domain_input(self, command: AssessRiskCommand) -> RiskAssessmentInput:
        registry_vehicle = None
        if command.vehicle_record is not None:
            vehicle = command.vehicle_record
            registry_vehicle = RegistryVehicleSnapshot(
                plate_number=vehicle.plate_number,
                make=vehicle.make,
                color=vehicle.color,
                vehicle_type=vehicle.vehicle_type,
                registration_status=vehicle.registration_status,
            )

        attributes = command.detected_attributes
        ocr = command.ocr_result
        return RiskAssessmentInput(
            plate_number=ocr.registration_number,
            ocr_confidence=ocr.ocr_confidence,
            registry_vehicle=registry_vehicle,
            observed_color=attributes.color,
            observed_vehicle_type=attributes.vehicle_type,
            observed_brand=attributes.brand,
            color_confidence=attributes.color_confidence,
            vehicle_type_confidence=attributes.vehicle_type_confidence,
            brand_confidence=attributes.brand_confidence,
        )
