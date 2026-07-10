"""Officer authentication ORM model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class OfficerAuthModel(Base):
    """Officer account credentials and profile."""

    __tablename__ = "officer_auth"
    __table_args__ = (
        Index("idx_officer_auth_user_id", "user_id", unique=True),
        Index("idx_officer_auth_employee_id", "employee_id", unique=True),
        Index("idx_officer_auth_badge_number", "badge_number", unique=True),
        Index("idx_officer_auth_username", "username", unique=True),
        Index("idx_officer_auth_email", "email", unique=True),
        Index("idx_officer_auth_station_id", "station_id"),
        Index("idx_officer_auth_station_code", "station_code"),
        Index("idx_officer_auth_status", "status"),
    )

    officer_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    employee_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    badge_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rank: Mapped[str] = mapped_column(String(100), nullable=False)
    station_id: Mapped[str] = mapped_column(String(36), nullable=False)
    station_code: Mapped[str] = mapped_column(String(32), nullable=False)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    district: Mapped[str | None] = mapped_column(String(200), nullable=True)
    roles_csv: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_change_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
