"""Analytics response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ChartSeriesData(BaseModel):
    """Label/value chart series."""

    labels: list[str]
    values: list[int]


class SuspiciousVehicleItemData(BaseModel):
    """Suspicious vehicle row."""

    plate_text: str
    scan_count: int
    max_risk_score: float
    risk_level: str


class AnalyticsOverviewData(BaseModel):
    """Analytics dashboard payload."""

    daily_scans: ChartSeriesData
    risk_distribution: ChartSeriesData
    vehicle_types: ChartSeriesData
    suspicious_vehicles: list[SuspiciousVehicleItemData]
    officer_activity: ChartSeriesData
    total_scans: int
    generated_at: datetime
