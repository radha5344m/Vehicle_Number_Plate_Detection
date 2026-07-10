"""Dashboard snapshot ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class DashboardSnapshotModel(Base):
    """Cached dashboard KPI counters."""

    __tablename__ = "dashboard_snapshots"
    __table_args__ = (Index("idx_dashboard_snapshot_at", "snapshot_at"),)

    snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    total_scans: Mapped[int] = mapped_column(Integer, nullable=False)
    verified_vehicles: Mapped[int] = mapped_column(Integer, nullable=False)
    suspicious_vehicles: Mapped[int] = mapped_column(Integer, nullable=False)
    pending_verification: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
