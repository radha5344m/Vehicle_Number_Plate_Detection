"""Risk severity levels."""

from enum import StrEnum


class RiskLevel(StrEnum):
    """Composite risk band derived from the risk score."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
