"""Executive Command Center DTOs."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ExecutiveDashboardFilters:
    from_date: datetime | None = None
    to_date: datetime | None = None
    district: str | None = None
    station: str | None = None
    officer: str | None = None
    vehicle_type: str | None = None
    risk_level: str | None = None
    brand: str | None = None
    station_id: str | None = None
    officer_id: str | None = None


@dataclass(frozen=True)
class MetricCardDto:
    label: str
    value: float
    display_value: str


@dataclass(frozen=True)
class ChartPointDto:
    label: str
    value: float


@dataclass(frozen=True)
class ActivityFeedItemDto:
    id: str
    title: str
    detail: str
    category: str
    occurred_at: datetime


@dataclass(frozen=True)
class LeaderboardItemDto:
    name: str
    metric: str
    value: float
    secondary_value: str | None = None


@dataclass(frozen=True)
class ExecutiveInsightDto:
    title: str
    detail: str


@dataclass(frozen=True)
class ExecutiveConnectionStatusDto:
    status: str
    last_updated_at: datetime
    auto_refresh_seconds: int


@dataclass(frozen=True)
class ExecutiveDashboardResult:
    scope_label: str
    kpis: tuple[MetricCardDto, ...]
    daily_trend: tuple[ChartPointDto, ...]
    weekly_trend: tuple[ChartPointDto, ...]
    monthly_trend: tuple[ChartPointDto, ...]
    hourly_activity: tuple[ChartPointDto, ...]
    investigation_status_distribution: tuple[ChartPointDto, ...]
    risk_distribution: tuple[ChartPointDto, ...]
    risk_trend: tuple[ChartPointDto, ...]
    top_high_risk_registrations: tuple[ChartPointDto, ...]
    frequent_suspicious_vehicles: tuple[ChartPointDto, ...]
    vehicle_type_distribution: tuple[ChartPointDto, ...]
    vehicle_brand_distribution: tuple[ChartPointDto, ...]
    vehicle_color_distribution: tuple[ChartPointDto, ...]
    registration_state_distribution: tuple[ChartPointDto, ...]
    common_vehicle_models: tuple[ChartPointDto, ...]
    top_performing_officers: tuple[LeaderboardItemDto, ...]
    most_active_officers: tuple[LeaderboardItemDto, ...]
    officer_leaderboard: tuple[LeaderboardItemDto, ...]
    top_performing_stations: tuple[LeaderboardItemDto, ...]
    recent_investigations: tuple[ActivityFeedItemDto, ...]
    recent_high_risk_alerts: tuple[ActivityFeedItemDto, ...]
    recent_officer_activity: tuple[ActivityFeedItemDto, ...]
    recent_reports_generated: tuple[ActivityFeedItemDto, ...]
    ai_metrics: tuple[MetricCardDto, ...]
    insights: tuple[ExecutiveInsightDto, ...]
    connection_status: ExecutiveConnectionStatusDto


@dataclass(frozen=True)
class ExecutiveDashboardExportRowDto:
    section: str
    label: str
    value: str


@dataclass(frozen=True)
class ExecutiveDashboardExportBundleDto:
    scope_label: str
    filters: ExecutiveDashboardFilters
    generated_at: datetime
    rows: tuple[ExecutiveDashboardExportRowDto, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutiveDashboardExportResult:
    filename: str
    content_type: str
    content: bytes
