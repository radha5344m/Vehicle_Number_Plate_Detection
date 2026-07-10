"""Query filtered investigation reports for department-level reporting."""

from __future__ import annotations

from sentinel_anpr.application.dto.investigation_reports_dto import (
    InvestigationReportsFilters,
    InvestigationReportsQueryResult,
)
from sentinel_anpr.application.ports.outbound.investigation_reports_query_port import (
    InvestigationReportsQueryPort,
)
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel

_ALLOWED_VERIFICATION_STATUSES = {"found", "not_found", "pending", "unknown"}


class QueryInvestigationReportsUseCase:
    """Validate filters and query persisted investigations for reporting."""

    def __init__(self, query_port: InvestigationReportsQueryPort) -> None:
        self._query_port = query_port

    def execute(
        self, filters: InvestigationReportsFilters
    ) -> InvestigationReportsQueryResult:
        self._validate(filters)
        return self._query_port.query_investigation_reports(filters)

    @staticmethod
    def _validate(filters: InvestigationReportsFilters) -> None:
        if filters.from_date and filters.to_date and filters.from_date > filters.to_date:
            raise ValueError("from date must be before to date")

        if filters.risk_level:
            risk_level = filters.risk_level.lower()
            if risk_level not in {level.value for level in RiskLevel}:
                raise ValueError(f"Invalid risk level: {filters.risk_level}")

        if filters.verification_status:
            status = filters.verification_status.lower()
            if status not in _ALLOWED_VERIFICATION_STATUSES:
                raise ValueError(
                    f"Invalid verification status: {filters.verification_status}"
                )

        if (
            filters.ai_confidence_min is not None
            and not 0.0 <= filters.ai_confidence_min <= 1.0
        ):
            raise ValueError("ai confidence minimum must be between 0.0 and 1.0")

        if (
            filters.ai_confidence_max is not None
            and not 0.0 <= filters.ai_confidence_max <= 1.0
        ):
            raise ValueError("ai confidence maximum must be between 0.0 and 1.0")

        if (
            filters.ai_confidence_min is not None
            and filters.ai_confidence_max is not None
            and filters.ai_confidence_min > filters.ai_confidence_max
        ):
            raise ValueError(
                "ai confidence minimum must be less than or equal to maximum"
            )
