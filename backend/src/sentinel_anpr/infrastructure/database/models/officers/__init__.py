"""Officer ORM models."""

from sentinel_anpr.infrastructure.database.models.officers.identity_sequence_model import (
    IdentitySequenceModel,
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel

__all__ = ["IdentitySequenceModel", "OfficerAuthModel"]
