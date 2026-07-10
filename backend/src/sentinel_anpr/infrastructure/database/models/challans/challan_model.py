"""e-Challan ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class ViolationMasterModel(Base):
    """Traffic violation catalog with default fines."""

    __tablename__ = "violation_master"

    violation_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    violation_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    default_fine_amount: Mapped[float] = mapped_column(Float, nullable=False)
    amount_editable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ChallanModel(Base):
    """Issued traffic violation challan."""

    __tablename__ = "challans"
    __table_args__ = (
        Index("idx_challans_challan_number", "challan_number", unique=True),
        Index("idx_challans_registration", "registration_number"),
        Index("idx_challans_vehicle_id", "vehicle_id"),
        Index("idx_challans_officer_id", "officer_id"),
        Index("idx_challans_station_id", "station_id"),
        Index("idx_challans_violation_type", "violation_type"),
        Index("idx_challans_status", "status"),
        Index("idx_challans_payment_status", "payment_status"),
        Index("idx_challans_issued_at", "issued_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    challan_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    investigation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(32), nullable=False)
    vehicle_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    owner_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    officer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    officer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    station_id: Mapped[str] = mapped_column(String(36), nullable=False)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    violation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    violation_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(32), nullable=False)
    location_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gps_coordinates: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
