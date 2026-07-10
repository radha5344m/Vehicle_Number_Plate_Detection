"""Verification result ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class VerificationResultModel(Base):
    """Registry verification outcome for a scan."""

    __tablename__ = "verification_results"

    verification_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    lookup_status: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    vehicle_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
