"""Police officer portal response schemas."""

from datetime import datetime

from pydantic import BaseModel


class PoliceOfficerSummaryData(BaseModel):
    todays_verifications: int
    weekly_verifications: int
    monthly_verifications: int
    high_risk_vehicles_found: int
    average_ai_confidence: float | None
    average_risk_score: float | None


class PoliceOfficerRecentInvestigationData(BaseModel):
    investigation_id: str
    registration_number: str
    vehicle_type: str | None
    risk_level: str
    verification_status: str | None
    scanned_at: datetime
    report_download_url: str | None


class PoliceOfficerRecentActivityData(BaseModel):
    activity_id: str
    description: str
    status: str
    occurred_at: datetime


class PoliceOfficerDashboardData(BaseModel):
    summary: PoliceOfficerSummaryData
    recent_investigations: list[PoliceOfficerRecentInvestigationData]
    recent_activity: list[PoliceOfficerRecentActivityData]


class PoliceOfficerNotificationData(BaseModel):
    notification_id: str
    title: str
    message: str
    category: str
    occurred_at: datetime


class PoliceOfficerNotificationsData(BaseModel):
    items: list[PoliceOfficerNotificationData]


class PoliceOfficerProfileData(BaseModel):
    officer_id: str
    employee_id: str
    officer_name: str
    badge_number: str
    rank: str
    station_name: str
    station_code: str
    phone_number: str | None
    email: str
    username: str
    role: str
    created_at: datetime
    last_login_at: datetime | None


class ActionMessageData(BaseModel):
    message: str
