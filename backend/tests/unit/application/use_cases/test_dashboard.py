"""Dashboard use case unit tests."""

from sentinel_anpr.application.use_cases.dashboard.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_recent_activity_use_case import (
    GetRecentActivityUseCase,
)
from sentinel_anpr.infrastructure.dashboard.placeholder_dashboard_adapter import (
    PlaceholderDashboardDataAdapter,
)


def test_dashboard_summary_returns_placeholder_metrics() -> None:
    adapter = PlaceholderDashboardDataAdapter()
    use_case = GetDashboardSummaryUseCase(dashboard_data=adapter)
    result = use_case.execute()
    assert result.total_scans == 1247
    assert result.verified_vehicles == 1089
    assert result.suspicious_vehicles == 23
    assert result.pending_verification == 135


def test_recent_activity_returns_items() -> None:
    adapter = PlaceholderDashboardDataAdapter()
    use_case = GetRecentActivityUseCase(dashboard_data=adapter)
    result = use_case.execute(limit=5)
    assert len(result.items) == 5
    assert result.items[0].plate_text == "AP09AB1234"
