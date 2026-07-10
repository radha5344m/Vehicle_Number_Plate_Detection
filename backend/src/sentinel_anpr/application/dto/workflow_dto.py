"""End-to-end vehicle verification workflow DTOs."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sentinel_anpr.application.dto.attribute_dto import VehicleAttributesResult
from sentinel_anpr.application.dto.risk_dto import RiskSignalDto
from sentinel_anpr.application.dto.vehicle_dto import LookupStatus, VehicleRecordDto


class WorkflowStatus(StrEnum):
    """Overall workflow outcome."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorkflowStepLog:
    """Structured log entry for a workflow stage."""

    stage: str
    status: str
    message: str
    duration_ms: int | None = None


@dataclass(frozen=True)
class AttributeComparisonItemDto:
    """Observed vs registered attribute comparison."""

    attribute: str
    observed: str
    registered: str | None
    matches: bool | None
    confidence: float | None


@dataclass(frozen=True)
class AttributeComparisonDto:
    """Attribute comparison summary."""

    items: tuple[AttributeComparisonItemDto, ...]
    overall_match: bool | None


@dataclass(frozen=True)
class VerificationResultDto:
    """Registry lookup outcome."""

    lookup_status: LookupStatus
    message: str


@dataclass(frozen=True)
class RunVehicleVerificationWorkflowCommand:
    """Start a full vehicle verification workflow."""

    officer_id: str
    officer_name: str
    badge_number: str
    officer_rank: str
    image_bytes: bytes
    content_type: str
    original_filename: str
    location_label: str | None = None
    correlation_id: str | None = None


@dataclass(frozen=True)
class RunVehicleVerificationWorkflowResult:
    """Complete verification workflow response."""

    status: WorkflowStatus
    workflow_id: str
    steps: tuple[WorkflowStepLog, ...]
    registration_number: str | None
    vision_confidence: float | None
    vehicle_information: VehicleRecordDto | None
    vehicle_attributes: VehicleAttributesResult | None
    attribute_comparison: AttributeComparisonDto | None
    verification_result: VerificationResultDto | None
    risk_score: float | None
    risk_level: str | None
    risk_explanation: str | None
    recommendation: str | None
    investigation_summary: str | None
    risk_signals: tuple[RiskSignalDto, ...]
    scan_id: str | None
    report_id: str | None
    failed_stage: str | None
    failure_message: str | None
    total_duration_ms: int | None
    completed_at: datetime
    vehicle_model: str | None = None
    vision_explanation: str | None = None
    outstanding_fine_inr: float | None = None
    pending_challans_count: int | None = None
    latest_violation: str | None = None
