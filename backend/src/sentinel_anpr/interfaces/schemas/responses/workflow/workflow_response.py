"""Vehicle verification workflow response schemas."""

from datetime import datetime

from pydantic import BaseModel

from sentinel_anpr.interfaces.schemas.responses.attributes.attribute_extraction_response import (
    VehicleAttributesResponseData,
)
from sentinel_anpr.interfaces.schemas.responses.vehicle.vehicle_response import VehicleRecordData


class WorkflowStepData(BaseModel):
    """Workflow stage log entry."""

    stage: str
    status: str
    message: str
    duration_ms: int | None = None


class VerificationResultData(BaseModel):
    """Registry lookup outcome."""

    lookup_status: str
    message: str


class AttributeComparisonItemData(BaseModel):
    """Observed vs registered attribute comparison."""

    attribute: str
    observed: str
    registered: str | None
    matches: bool | None
    confidence: float | None


class AttributeComparisonData(BaseModel):
    """Attribute comparison summary."""

    items: list[AttributeComparisonItemData]
    overall_match: bool | None


class RiskSignalData(BaseModel):
    """Explainable risk signal."""

    name: str
    weight: float
    detail: str


class VehicleVerificationWorkflowData(BaseModel):
    """Complete end-to-end verification result."""

    status: str
    workflow_id: str
    steps: list[WorkflowStepData]
    registration_number: str | None
    vision_confidence: float | None
    vehicle_information: VehicleRecordData | None
    vision_attributes: VehicleAttributesResponseData | None
    vehicle_model: str | None = None
    vision_explanation: str | None = None
    attribute_comparison: AttributeComparisonData | None
    verification_result: VerificationResultData | None
    risk_score: float | None
    risk_level: str | None
    risk_explanation: str | None
    recommendation: str | None
    investigation_summary: str | None
    risk_signals: list[RiskSignalData]
    scan_id: str | None
    report_id: str | None
    report_download_url: str | None
    failed_stage: str | None
    failure_message: str | None
    total_duration_ms: int | None
    completed_at: datetime
    outstanding_fine_inr: float | None = None
    pending_challans_count: int | None = None
    latest_violation: str | None = None
