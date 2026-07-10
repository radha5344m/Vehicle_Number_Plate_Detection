"""Police station response schemas."""

from datetime import datetime

from pydantic import BaseModel


class StationItemData(BaseModel):
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


class StationPaginationData(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class StationsListData(BaseModel):
    items: list[StationItemData]
    pagination: StationPaginationData


class StationMutationData(BaseModel):
    station: StationItemData


class ActionMessageData(BaseModel):
    message: str
