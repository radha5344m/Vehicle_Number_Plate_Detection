"""Risk assessment aggregate."""

from dataclasses import dataclass

from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel
from sentinel_anpr.domain.risk.value_objects.risk_signal import RiskSignal


@dataclass(frozen=True)
class RiskAssessment:
    """Composite risk outcome with explainability."""

    risk_score: float
    risk_level: RiskLevel
    explanation: str
    recommendation: str
    signals: tuple[RiskSignal, ...]
    policy_version: str
