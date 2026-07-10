"""User management DTOs."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserFilters:
    search: str | None = None
    role: str | None = None
    station: str | None = None
    status: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_desc: bool = True


@dataclass(frozen=True)
class UserListItemDto:
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


@dataclass(frozen=True)
class UserDetailDto:
    officer_id: str
    user_id: str
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    username: str
    email: str
    phone_number: str | None
    badge_number: str
    rank: str
    role: str
    police_station: str
    station_code: str
    station_id: str
    district: str | None
    status: str
    created_at: datetime
    last_login_at: datetime | None


@dataclass(frozen=True)
class UsersPaginationDto:
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class QueryUsersResult:
    items: tuple[UserListItemDto, ...]
    pagination: UsersPaginationDto
    summary: "UsersSummaryDto"


@dataclass(frozen=True)
class UsersSummaryDto:
    total_users: int
    super_admins: int
    station_admins: int
    police_officers: int


@dataclass(frozen=True)
class CreateUserCommand:
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    badge_number: str | None
    rank: str | None
    role: str
    police_station: str | None
    district: str | None
    status: str
    user_id: str | None = None
    employee_id: str | None = None
    username: str | None = None


@dataclass(frozen=True)
class UpdateUserCommand:
    officer_id: str
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    rank: str
    role: str | None
    police_station: str | None
    district: str | None
    status: str


@dataclass(frozen=True)
class ResetUserPasswordCommand:
    officer_id: str
    new_password: str | None = None


@dataclass(frozen=True)
class UserMutationResult:
    user: UserDetailDto
    temporary_password: str | None = None
    password_change_required: bool = False


@dataclass(frozen=True)
class UserStatusChangeCommand:
    officer_id: str
    status: str
