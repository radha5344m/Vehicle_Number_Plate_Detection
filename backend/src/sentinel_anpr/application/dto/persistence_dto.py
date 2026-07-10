"""Database persistence data transfer objects."""

from dataclasses import dataclass
from datetime import datetime

from sentinel_anpr.application.dto.history_dto import SaveCompletedScanCommand
from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand


@dataclass(frozen=True)
class SaveVerificationResultCommand:
    """Persist vehicle registry verification outcome."""

    scan_id: str
    lookup_status: str
    message: str
    vehicle_id: str | None
    verified_at: datetime


@dataclass(frozen=True)
class SaveRiskAssessmentCommand:
    """Persist risk engine output for a scan."""

    scan_id: str
    risk_score: float
    risk_level: str
    explanation: str
    recommendation: str
    policy_version: str
    assessed_at: datetime


@dataclass(frozen=True)
class SaveOfficerActivityCommand:
    """Persist a single officer workflow activity event."""

    officer_id: str
    officer_name: str
    scan_id: str | None
    activity_type: str
    description: str
    status: str
    occurred_at: datetime
    correlation_id: str | None = None


@dataclass(frozen=True)
class SaveDashboardSnapshotCommand:
    """Persist dashboard KPI snapshot."""

    total_scans: int
    verified_vehicles: int
    suspicious_vehicles: int
    pending_verification: int
    snapshot_at: datetime


@dataclass(frozen=True)
class RenderedReportDto:
    """Generated PDF ready for persistence."""

    pdf_bytes: bytes
    title: str
    checksum_sha256: str
    generated_at: datetime
    plate_text: str
    risk_score: float
    risk_level: str


@dataclass(frozen=True)
class PersistWorkflowOutcomeCommand:
    """Atomic persistence payload for a completed workflow."""

    scan: SaveCompletedScanCommand
    verification: SaveVerificationResultCommand
    risk: SaveRiskAssessmentCommand
    officer_activities: tuple[SaveOfficerActivityCommand, ...]
    dashboard_snapshot: SaveDashboardSnapshotCommand
    report: RenderedReportDto | None
    report_command: GenerateInvestigationReportCommand | None
    scan_id: str | None = None


@dataclass(frozen=True)
class PersistWorkflowOutcomeResult:
    """References to persisted workflow artifacts."""

    scan_id: str
    report_id: str | None
    verification_id: str
    risk_assessment_id: str
    snapshot_id: str
