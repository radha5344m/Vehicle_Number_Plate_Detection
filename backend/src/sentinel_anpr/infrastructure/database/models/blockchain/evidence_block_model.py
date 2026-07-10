"""Evidence blockchain ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class EvidenceBlockModel(Base):
    """Private evidence blockchain block."""

    __tablename__ = "evidence_blocks"
    __table_args__ = (
        Index("idx_evidence_blocks_investigation_id", "investigation_id"),
        Index("idx_evidence_blocks_block_number", "block_number"),
    )

    block_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    block_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    block_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    investigation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    report_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(32), nullable=False)
    officer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    report_sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
