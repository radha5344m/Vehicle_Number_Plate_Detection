"""Investigation report ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class ReportModel(Base):
    """Generated investigation PDF metadata."""

    __tablename__ = "investigation_reports"
    __table_args__ = (
        Index("idx_investigation_reports_scan_id", "scan_id"),
        Index("idx_investigation_reports_officer_id", "officer_id"),
        Index("idx_investigation_reports_plate_text", "plate_text"),
    )

    report_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    officer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    officer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    plate_text: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
