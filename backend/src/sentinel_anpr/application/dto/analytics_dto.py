"""Analytics data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AnalyticsDateRange:
    """Optional date range for analytics queries."""

    from_date: datetime | None = None
    to_date: datetime | None = None
    station_id: str | None = None
    officer_id: str | None = None


@dataclass(frozen=True)
class ChartSeriesDto:
    """Generic label/value chart series."""

    labels: tuple[str, ...]
    values: tuple[int, ...]


@dataclass(frozen=True)
class SuspiciousVehicleItemDto:
    """Suspicious vehicle summary row."""

    plate_text: str
    scan_count: int
    max_risk_score: float
    risk_level: str


@dataclass(frozen=True)
class AnalyticsOverviewDto:
    """Aggregated analytics for dashboard charts."""

    daily_scans: ChartSeriesDto
    risk_distribution: ChartSeriesDto
    vehicle_types: ChartSeriesDto
    suspicious_vehicles: tuple[SuspiciousVehicleItemDto, ...]
    officer_activity: ChartSeriesDto
    total_scans: int
    generated_at: datetime
