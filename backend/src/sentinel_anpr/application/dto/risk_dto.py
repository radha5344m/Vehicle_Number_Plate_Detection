"""Risk assessment data transfer objects."""

from dataclasses import dataclass

from sentinel_anpr.application.dto.attribute_dto import VehicleAttributesResult
from sentinel_anpr.application.dto.recognition_dto import RecognizePlateResult
from sentinel_anpr.application.dto.vehicle_dto import VehicleRecordDto
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel


@dataclass(frozen=True)
class AssessRiskCommand:
    """Inputs for composite risk scoring."""

    ocr_result: RecognizePlateResult
    vehicle_record: VehicleRecordDto | None
    detected_attributes: VehicleAttributesResult


@dataclass(frozen=True)
class RiskSignalDto:
    """Explainable risk signal for API and reporting layers."""

    name: str
    weight: float
    detail: str


@dataclass(frozen=True)
class AssessRiskResult:
    """Structured risk engine output."""

    risk_score: float
    risk_level: RiskLevel
    explanation: str
    recommendation: str
    signals: tuple[RiskSignalDto, ...]
    policy_version: str
