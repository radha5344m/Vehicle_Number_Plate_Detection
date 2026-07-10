"""Map workflow use-case results to REST response schemas."""

from __future__ import annotations

from sentinel_anpr.application.dto.workflow_dto import RunVehicleVerificationWorkflowResult
from sentinel_anpr.interfaces.rest_api.v1.routes.vehicles.vehicle_handler import _vehicle_data
from sentinel_anpr.interfaces.schemas.responses.attributes.attribute_extraction_response import (
    VehicleAttributesResponseData,
)
from sentinel_anpr.interfaces.schemas.responses.workflow.workflow_response import (
    AttributeComparisonData,
    AttributeComparisonItemData,
    RiskSignalData,
    VehicleVerificationWorkflowData,
    VerificationResultData,
    WorkflowStepData,
)


def map_workflow_result_to_response(
    result: RunVehicleVerificationWorkflowResult,
) -> VehicleVerificationWorkflowData:
    """Convert an application workflow result into an API response payload."""
    attributes = None
    if result.vehicle_attributes is not None:
        attr = result.vehicle_attributes
        attributes = VehicleAttributesResponseData(
            color=attr.color,
            vehicle_type=attr.vehicle_type,
            brand=attr.brand,
            color_confidence=attr.color_confidence,
            vehicle_type_confidence=attr.vehicle_type_confidence,
            brand_confidence=attr.brand_confidence,
            model_version=attr.model_version,
        )

    verification = None
    if result.verification_result is not None:
        verification = VerificationResultData(
            lookup_status=result.verification_result.lookup_status.value,
            message=result.verification_result.message,
        )

    attribute_comparison = None
    if result.attribute_comparison is not None:
        attribute_comparison = AttributeComparisonData(
            items=[
                AttributeComparisonItemData(
                    attribute=item.attribute,
                    observed=item.observed,
                    registered=item.registered,
                    matches=item.matches,
                    confidence=item.confidence,
                )
                for item in result.attribute_comparison.items
            ],
            overall_match=result.attribute_comparison.overall_match,
        )

    return VehicleVerificationWorkflowData(
        status=result.status.value,
        workflow_id=result.workflow_id,
        steps=[
            WorkflowStepData(
                stage=step.stage,
                status=step.status,
                message=step.message,
                duration_ms=step.duration_ms,
            )
            for step in result.steps
        ],
        registration_number=result.registration_number,
        vision_confidence=result.vision_confidence,
        vehicle_information=(
            _vehicle_data(result.vehicle_information) if result.vehicle_information else None
        ),
        vision_attributes=attributes,
        vehicle_model=result.vehicle_model,
        vision_explanation=result.vision_explanation,
        attribute_comparison=attribute_comparison,
        verification_result=verification,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        risk_explanation=result.risk_explanation,
        recommendation=result.recommendation,
        investigation_summary=result.investigation_summary,
        risk_signals=[
            RiskSignalData(name=signal.name, weight=signal.weight, detail=signal.detail)
            for signal in result.risk_signals
        ],
        scan_id=result.scan_id,
        report_id=result.report_id,
        report_download_url=(
            f"/v1/reports/{result.report_id}/download" if result.report_id else None
        ),
        failed_stage=result.failed_stage,
        failure_message=result.failure_message,
        total_duration_ms=result.total_duration_ms,
        completed_at=result.completed_at,
        outstanding_fine_inr=result.outstanding_fine_inr,
        pending_challans_count=result.pending_challans_count,
        latest_violation=result.latest_violation,
    )
