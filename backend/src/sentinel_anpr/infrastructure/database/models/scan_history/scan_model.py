"""Scan history ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class ScanModel(Base):
    """Persisted vehicle verification / scan record."""

    __tablename__ = "scan_history"
    __table_args__ = (
        Index("idx_scan_officer_id", "officer_id"),
        Index("idx_scan_vehicle_id", "vehicle_id"),
        Index("idx_scan_plate_text", "plate_text"),
        Index("idx_scan_risk_level", "risk_level"),
        Index("idx_scan_correlation_id", "correlation_id"),
        Index("idx_scan_scanned_at", "scanned_at"),
    )

    scan_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    officer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    officer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    vehicle_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    plate_text: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False)
    location_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
