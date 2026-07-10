"""Dashboard summary response schema."""

from datetime import datetime

from pydantic import BaseModel


class DashboardSummaryData(BaseModel):
    """Dashboard KPI payload."""

    total_scans: int
    verified_vehicles: int
    suspicious_vehicles: int
    pending_verification: int
    last_updated_at: datetime
