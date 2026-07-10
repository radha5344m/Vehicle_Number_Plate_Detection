"""Officer account status values used during authentication."""

from enum import StrEnum


class OfficerStatus(StrEnum):
    """Whether an officer may authenticate."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
