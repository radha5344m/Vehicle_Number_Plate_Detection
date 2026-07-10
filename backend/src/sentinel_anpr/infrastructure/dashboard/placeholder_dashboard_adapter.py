"""Placeholder dashboard data — no database or AI."""

from datetime import UTC, datetime, timedelta

from sentinel_anpr.application.dto.dashboard_dto import (
    DashboardSummaryResult,
    RecentActivityItem,
    RecentActivityResult,
)
from sentinel_anpr.application.ports.outbound.dashboard_data_port import DashboardDataPort


class PlaceholderDashboardDataAdapter(DashboardDataPort):
    """Static placeholder metrics for dashboard development."""

    def get_summary(self) -> DashboardSummaryResult:
        return DashboardSummaryResult(
            total_scans=1247,
            verified_vehicles=1089,
            suspicious_vehicles=23,
            pending_verification=135,
            last_updated_at=datetime.now(UTC),
        )

    def get_recent_activity(self, limit: int = 10) -> RecentActivityResult:
        now = datetime.now(UTC)
        samples = [
            ("AP09AB1234", "scan", "Plate scanned at Ongole checkpoint", "completed"),
            ("AP10CD5678", "verification", "Registry match confirmed", "verified"),
            ("AP11EF9012", "alert", "Clone risk flagged — investigate", "suspicious"),
            ("AP12GH3456", "scan", "Plate scanned at Chirala gate", "completed"),
            ("AP13JK7890", "verification", "Awaiting registry lookup", "pending"),
            ("AP14LM2345", "alert", "Stolen vehicle report match", "suspicious"),
            ("AP15NO6789", "scan", "Low OCR confidence — retry", "failed"),
            ("AP16PQ1234", "verification", "Plate verified against RTO", "verified"),
        ]
        items = tuple(
            RecentActivityItem(
                id=f"act-{index:03d}",
                plate_text=plate,
                activity_type=activity_type,
                description=description,
                status=status,
                occurred_at=now - timedelta(minutes=index * 12),
            )
            for index, (plate, activity_type, description, status) in enumerate(samples[:limit])
        )
        return RecentActivityResult(items=items)
