"""Police station management DTOs."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StationFilters:
    search: str | None = None
    district: str | None = None
    state: str | None = None
    status: str | None = None
    station_type: str | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_desc: bool = True


@dataclass(frozen=True)
class StationItemDto:
    station_id: str
    station_name: str
    station_code: str
    district: str
    state: str
    address: str
    pincode: str
    phone_number: str | None
    email: str | None
    station_type: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class StationsPaginationDto:
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class QueryStationsResult:
    items: tuple[StationItemDto, ...]
    pagination: StationsPaginationDto


@dataclass(frozen=True)
class CreateStationCommand:
    station_name: str
    station_code: str
    district: str
    state: str
    address: str
    pincode: str
    phone_number: str | None
    email: str | None
    station_type: str
    status: str


@dataclass(frozen=True)
class UpdateStationCommand:
    station_id: str
    station_name: str
    district: str
    state: str
    address: str
    pincode: str
    phone_number: str | None
    email: str | None
    station_type: str
    status: str


@dataclass(frozen=True)
class StationStatusCommand:
    station_id: str
    status: str


@dataclass(frozen=True)
class StationMutationResult:
    station: StationItemDto
