"""User management response schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserItemData(BaseModel):
    officer_id: str
    user_id: str
    employee_id: str
    full_name: str
    username: str
    email: str
    phone_number: str | None
    badge_number: str
    rank: str
    role: str
    police_station: str
    district: str | None
    status: str
    created_at: datetime
    last_login_at: datetime | None


class UserPaginationData(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class UsersListData(BaseModel):
    items: list[UserItemData]
    pagination: UserPaginationData
    summary: "UsersSummaryData"


class UsersSummaryData(BaseModel):
    total_users: int
    super_admins: int
    station_admins: int
    police_officers: int


class UserMutationData(BaseModel):
    user: UserItemData
    temporary_password: str | None = None
    password_change_required: bool = False


class ActionMessageData(BaseModel):
    message: str
