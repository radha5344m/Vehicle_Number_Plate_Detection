"""Station admin portal DTOs."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class StationAdminOfficerFilters:
    search: str | None = None
    status: str | None = None
    rank: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class StationAdminOfficerItemDto:
    officer_id: str
    user_id: str
    employee_id: str
    badge_number: str
    officer_name: str
    rank: str
    phone_number: str | None
    status: str
    investigations: int
    last_login_at: datetime | None
    username: str
    email: str
    created_at: datetime


@dataclass(frozen=True)
class StationAdminOfficerPaginationDto:
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class StationAdminOfficerQueryResult:
    items: tuple[StationAdminOfficerItemDto, ...]
    pagination: StationAdminOfficerPaginationDto


@dataclass(frozen=True)
class CreatePoliceOfficerCommand:
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    rank: str
    status: str = "active"
    user_id: str | None = None
    employee_id: str | None = None
    username: str | None = None
    badge_number: str | None = None


@dataclass(frozen=True)
class UpdatePoliceOfficerCommand:
    officer_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    rank: str
    status: str


@dataclass(frozen=True)
class StationAdminOfficerMutationResult:
    officer: StationAdminOfficerItemDto
    temporary_password: str | None = None
    password_change_required: bool = False


@dataclass(frozen=True)
class UpdateStationDetailsCommand:
    address: str
    phone_number: str | None
    email: str | None


@dataclass(frozen=True)
class StationAdminDashboardSummaryDto:
    todays_investigations: int
    weekly_investigations: int
    monthly_investigations: int
    high_risk_vehicles: int
    verified_vehicles: int
    pending_investigations: int
    average_ai_confidence: float | None
    average_risk_score: float | None


@dataclass(frozen=True)
class StationAdminRecentInvestigationDto:
    investigation_id: str
    registration_number: str
    officer_name: str
    risk_level: str
    verification_status: str | None
    scanned_at: datetime


@dataclass(frozen=True)
class StationAdminRecentOfficerActivityDto:
    activity_id: str
    officer_name: str
    description: str
    status: str
    occurred_at: datetime


@dataclass(frozen=True)
class StationAdminHighRiskVehicleDto:
    registration_number: str
    risk_score: float
    reason: str
    officer_name: str
    occurred_at: datetime


@dataclass(frozen=True)
class StationAdminDashboardResult:
    summary: StationAdminDashboardSummaryDto
    recent_investigations: tuple[StationAdminRecentInvestigationDto, ...]
    recent_officer_activity: tuple[StationAdminRecentOfficerActivityDto, ...]
    high_risk_vehicles: tuple[StationAdminHighRiskVehicleDto, ...]


@dataclass(frozen=True)
class StationAdminInvestigationFilters:
    from_date: datetime | None = None
    to_date: datetime | None = None
    officer: str | None = None
    risk_level: str | None = None
    vehicle_type: str | None = None
    registration_number: str | None = None
    verification_status: str | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "scanned_at"
    sort_desc: bool = True


@dataclass(frozen=True)
class StationAdminInvestigationItemDto:
    investigation_id: str
    registration_number: str
    officer_id: str
    officer_name: str
    vehicle_type: str | None
    risk_score: float
    risk_level: str
    verification_status: str | None
    ai_confidence: float | None
    scanned_at: datetime
    report_download_url: str | None


@dataclass(frozen=True)
class StationAdminInvestigationPaginationDto:
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class StationAdminInvestigationQueryResult:
    items: tuple[StationAdminInvestigationItemDto, ...]
    pagination: StationAdminInvestigationPaginationDto


@dataclass(frozen=True)
class StationAdminAnalyticsResult:
    daily_investigations: tuple[int, ...]
    daily_labels: tuple[str, ...]
    weekly_trend: tuple[int, ...]
    weekly_labels: tuple[str, ...]
    monthly_trend: tuple[int, ...]
    monthly_labels: tuple[str, ...]
    risk_distribution_labels: tuple[str, ...]
    risk_distribution_values: tuple[int, ...]
    vehicle_type_labels: tuple[str, ...]
    vehicle_type_values: tuple[int, ...]
    vehicle_brand_labels: tuple[str, ...]
    vehicle_brand_values: tuple[int, ...]
    officer_performance_labels: tuple[str, ...]
    officer_performance_values: tuple[int, ...]
    average_investigation_time_minutes: float | None
    average_ai_confidence: float | None
    average_risk_score: float | None


@dataclass(frozen=True)
class StationAdminNotificationDto:
    notification_id: str
    title: str
    message: str
    category: str
    occurred_at: datetime


@dataclass(frozen=True)
class StationAdminProfileDto:
    station_id: str
    station_name: str
    station_code: str
    address: str
    phone_number: str | None
    email: str | None
    district: str
    state: str
    station_type: str
    admin_name: str
    admin_rank: str
    officer_id: str
    employee_id: str
    role: str
    account_email: str
    account_phone: str | None
    created_at: datetime
    last_login_at: datetime | None


@dataclass(frozen=True)
class ChangeOwnPasswordCommand:
    current_password: str
    new_password: str


@dataclass(frozen=True)
class StationAdminReportsResult:
    summary_text: str
    total_investigations: int
    verified_vehicles: int
    high_risk_vehicles: int
    average_ai_confidence: float | None
    average_risk_score: float | None
    risk_distribution: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    vehicle_type_distribution: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    brand_distribution: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    officer_performance: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    items: tuple[StationAdminInvestigationItemDto, ...] = field(default_factory=tuple)
    pagination: StationAdminInvestigationPaginationDto | None = None
