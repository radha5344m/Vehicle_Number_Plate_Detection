"""Police officer portal DTOs."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PoliceOfficerDashboardSummaryDto:
    todays_verifications: int
    weekly_verifications: int
    monthly_verifications: int
    high_risk_vehicles_found: int
    average_ai_confidence: float | None
    average_risk_score: float | None


@dataclass(frozen=True)
class PoliceOfficerRecentInvestigationDto:
    investigation_id: str
    registration_number: str
    vehicle_type: str | None
    risk_level: str
    verification_status: str | None
    scanned_at: datetime
    report_download_url: str | None


@dataclass(frozen=True)
class PoliceOfficerRecentActivityDto:
    activity_id: str
    description: str
    status: str
    occurred_at: datetime


@dataclass(frozen=True)
class PoliceOfficerDashboardResult:
    summary: PoliceOfficerDashboardSummaryDto
    recent_investigations: tuple[PoliceOfficerRecentInvestigationDto, ...]
    recent_activity: tuple[PoliceOfficerRecentActivityDto, ...]


@dataclass(frozen=True)
class PoliceOfficerNotificationDto:
    notification_id: str
    title: str
    message: str
    category: str
    occurred_at: datetime


@dataclass(frozen=True)
class PoliceOfficerProfileDto:
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


@dataclass(frozen=True)
class ChangeOwnPasswordCommand:
    current_password: str
    new_password: str
