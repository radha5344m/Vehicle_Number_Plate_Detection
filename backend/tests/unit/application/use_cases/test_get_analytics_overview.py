"""Analytics overview use case unit tests."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.analytics_dto import (
    AnalyticsOverviewDto,
    ChartSeriesDto,
    SuspiciousVehicleItemDto,
)
from sentinel_anpr.application.use_cases.analytics.get_analytics_overview_use_case import (
    GetAnalyticsOverviewUseCase,
)


class _FakeAnalyticsRepository:
    def get_overview(self, date_range):
        del date_range
        return AnalyticsOverviewDto(
            daily_scans=ChartSeriesDto(labels=("2026-07-01",), values=(3,)),
            risk_distribution=ChartSeriesDto(labels=("low", "high"), values=(2, 1)),
            vehicle_types=ChartSeriesDto(labels=("car",), values=(3,)),
            suspicious_vehicles=(
                SuspiciousVehicleItemDto(
                    plate_text="AP11EF9012",
                    scan_count=1,
                    max_risk_score=0.55,
                    risk_level="critical",
                ),
            ),
            officer_activity=ChartSeriesDto(labels=("Ravi Kumar",), values=(2,)),
            total_scans=3,
            generated_at=datetime.now(UTC),
        )


def test_get_analytics_overview() -> None:
    use_case = GetAnalyticsOverviewUseCase(analytics_repository=_FakeAnalyticsRepository())
    result = use_case.execute()
    assert result.total_scans == 3
    assert result.daily_scans.values[0] == 3
    assert len(result.suspicious_vehicles) == 1
