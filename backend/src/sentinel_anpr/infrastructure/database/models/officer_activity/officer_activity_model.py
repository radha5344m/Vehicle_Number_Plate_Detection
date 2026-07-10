"""Officer activity ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class OfficerActivityModel(Base):
    """Officer activity and notification feed events."""

    __tablename__ = "officer_activity_events"
    __table_args__ = (
        Index("idx_officer_activity_officer_id", "officer_id"),
        Index("idx_officer_activity_scan_id", "scan_id"),
        Index("idx_officer_activity_correlation_id", "correlation_id"),
        Index("idx_officer_activity_occurred_at", "occurred_at"),
    )

    activity_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    officer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    officer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scan_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
