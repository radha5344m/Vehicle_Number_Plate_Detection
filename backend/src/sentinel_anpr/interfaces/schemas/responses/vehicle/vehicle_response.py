"""Vehicle lookup response schemas."""

from datetime import datetime

from pydantic import BaseModel


class VehicleRecordData(BaseModel):
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


class VehicleLookupResponseData(BaseModel):
    """Vehicle verification lookup payload."""

    lookup_status: str
    message: str
    vehicle: VehicleRecordData | None = None
    registry_synced_at: datetime | None = None
    registry_external_id: str | None = None
