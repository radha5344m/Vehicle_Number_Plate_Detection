"""Executive dashboard response schemas."""

from datetime import datetime

from pydantic import BaseModel


class MetricCardData(BaseModel):
    label: str
    value: float
    display_value: str


class ChartPointData(BaseModel):
    label: str
    value: float


class ActivityFeedItemData(BaseModel):
    id: str
    title: str
    detail: str
    category: str
    occurred_at: datetime


class LeaderboardItemData(BaseModel):
    name: str
    metric: str
    value: float
    secondary_value: str | None = None


class ExecutiveInsightData(BaseModel):
    title: str
    detail: str


class ExecutiveConnectionStatusData(BaseModel):
    status: str
    last_updated_at: datetime
    auto_refresh_seconds: int


class ExecutiveDashboardData(BaseModel):
    scope_label: str
    kpis: list[MetricCardData]
    daily_trend: list[ChartPointData]
    weekly_trend: list[ChartPointData]
    monthly_trend: list[ChartPointData]
    hourly_activity: list[ChartPointData]
    investigation_status_distribution: list[ChartPointData]
    risk_distribution: list[ChartPointData]
    risk_trend: list[ChartPointData]
    top_high_risk_registrations: list[ChartPointData]
    frequent_suspicious_vehicles: list[ChartPointData]
    vehicle_type_distribution: list[ChartPointData]
    vehicle_brand_distribution: list[ChartPointData]
    vehicle_color_distribution: list[ChartPointData]
    registration_state_distribution: list[ChartPointData]
    common_vehicle_models: list[ChartPointData]
    top_performing_officers: list[LeaderboardItemData]
    most_active_officers: list[LeaderboardItemData]
    officer_leaderboard: list[LeaderboardItemData]
    top_performing_stations: list[LeaderboardItemData]
    recent_investigations: list[ActivityFeedItemData]
    recent_high_risk_alerts: list[ActivityFeedItemData]
    recent_officer_activity: list[ActivityFeedItemData]
    recent_reports_generated: list[ActivityFeedItemData]
    ai_metrics: list[MetricCardData]
    insights: list[ExecutiveInsightData]
    connection_status: ExecutiveConnectionStatusData
