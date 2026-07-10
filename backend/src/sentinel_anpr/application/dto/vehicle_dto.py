"""Vehicle lookup data transfer objects."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class LookupStatus(StrEnum):
    """Vehicle lookup outcome."""

    FOUND = "found"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class VehicleRecordDto:
    """Registered vehicle details."""

    vehicle_id: str
    plate_number: str
    jurisdiction: str
    make: str
    model: str
    color: str
    year: int
    vehicle_type: str
    registration_status: str
    registered_owner: str
    registry_external_id: str | None
    registry_synced_at: datetime | None


@dataclass(frozen=True)
class LookupVehicleCommand:
    """Lookup request by registration number."""

    plate: str
    jurisdiction: str | None = None


@dataclass(frozen=True)
class LookupVehicleResult:
    """Vehicle lookup response."""

    lookup_status: LookupStatus
    vehicle: VehicleRecordDto | None
    message: str
    registry_synced_at: datetime | None = None
    registry_external_id: str | None = None
