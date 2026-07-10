"""Police station ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class PoliceStationModel(Base):
    """Police station master record."""

    __tablename__ = "police_stations"
    __table_args__ = (
        Index("idx_police_stations_station_name", "station_name", unique=True),
        Index("idx_police_stations_station_code", "station_code", unique=True),
        Index("idx_police_stations_district", "district"),
        Index("idx_police_stations_state", "state"),
        Index("idx_police_stations_status", "status"),
        Index("idx_police_stations_type", "station_type"),
    )

    station_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    station_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    district: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    pincode: Mapped[str] = mapped_column(String(16), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    station_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
