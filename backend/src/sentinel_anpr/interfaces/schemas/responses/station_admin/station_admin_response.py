"""Station admin response schemas."""

from datetime import datetime

from pydantic import BaseModel


class StationAdminOfficerItemData(BaseModel):
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


class StationAdminOfficerPaginationData(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class StationAdminOfficersData(BaseModel):
    items: list[StationAdminOfficerItemData]
    pagination: StationAdminOfficerPaginationData


class StationAdminOfficerMutationData(BaseModel):
    officer: StationAdminOfficerItemData
    temporary_password: str | None = None
    password_change_required: bool = False


class StationAdminSummaryData(BaseModel):
    todays_investigations: int
    weekly_investigations: int
    monthly_investigations: int
    high_risk_vehicles: int
    verified_vehicles: int
    pending_investigations: int
    average_ai_confidence: float | None
    average_risk_score: float | None


class StationAdminRecentInvestigationData(BaseModel):
    investigation_id: str
    registration_number: str
    officer_name: str
    risk_level: str
    verification_status: str | None
    scanned_at: datetime


class StationAdminRecentOfficerActivityData(BaseModel):
    activity_id: str
    officer_name: str
    description: str
    status: str
    occurred_at: datetime


class StationAdminHighRiskVehicleData(BaseModel):
    registration_number: str
    risk_score: float
    reason: str
    officer_name: str
    occurred_at: datetime


class StationAdminDashboardData(BaseModel):
    summary: StationAdminSummaryData
    recent_investigations: list[StationAdminRecentInvestigationData]
    recent_officer_activity: list[StationAdminRecentOfficerActivityData]
    high_risk_vehicles: list[StationAdminHighRiskVehicleData]


class StationAdminAnalyticsData(BaseModel):
    daily_labels: list[str]
    daily_investigations: list[int]
    weekly_labels: list[str]
    weekly_trend: list[int]
    monthly_labels: list[str]
    monthly_trend: list[int]
    risk_distribution_labels: list[str]
    risk_distribution_values: list[int]
    vehicle_type_labels: list[str]
    vehicle_type_values: list[int]
    vehicle_brand_labels: list[str]
    vehicle_brand_values: list[int]
    officer_performance_labels: list[str]
    officer_performance_values: list[int]
    average_investigation_time_minutes: float | None
    average_ai_confidence: float | None
    average_risk_score: float | None


class StationAdminNotificationData(BaseModel):
    notification_id: str
    title: str
    message: str
    category: str
    occurred_at: datetime


class StationAdminNotificationsData(BaseModel):
    items: list[StationAdminNotificationData]


class StationAdminProfileData(BaseModel):
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


class ActionMessageData(BaseModel):
    message: str
