"""Dashboard data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DashboardSummaryResult:
    """Operational KPI summary."""

    total_scans: int
    verified_vehicles: int
    suspicious_vehicles: int
    pending_verification: int
    last_updated_at: datetime


@dataclass(frozen=True)
class RecentActivityItem:
    """Single dashboard activity row."""

    id: str
    plate_text: str
    activity_type: str
    description: str
    status: str
    occurred_at: datetime


@dataclass(frozen=True)
class RecentActivityResult:
    """Recent activity list."""

    items: tuple[RecentActivityItem, ...]
