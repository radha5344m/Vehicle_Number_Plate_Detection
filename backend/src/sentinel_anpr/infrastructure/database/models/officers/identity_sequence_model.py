"""Identity sequence ORM model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_anpr.infrastructure.database.models.base import Base


class IdentitySequenceModel(Base):
    """Monotonic counters for user and employee identifiers."""

    __tablename__ = "identity_sequences"

    sequence_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
