"""Vehicle registry ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class VehicleModel(Base):
    """Registered vehicle master record."""

    __tablename__ = "vehicles"
    __table_args__ = (
        Index("idx_vehicles_plate_number", "plate_number"),
        Index("idx_vehicles_jurisdiction", "jurisdiction"),
    )

    vehicle_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(32), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(8), nullable=False)
    make: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicle_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    registration_status: Mapped[str] = mapped_column(String(32), nullable=False)
    registered_owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    registry_external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    registry_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
