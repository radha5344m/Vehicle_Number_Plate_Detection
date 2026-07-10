"""End-to-end vehicle verification workflow routes."""

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.workflow_dto import RunVehicleVerificationWorkflowCommand
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_vision_verification_workflow_use_case import (
    RunVisionVerificationWorkflowUseCase,
)
from sentinel_anpr.infrastructure.ai.vision_progress_store import (
    bind_vision_progress,
    clear_vision_progress,
    get_vision_progress,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response
from sentinel_anpr.interfaces.rest_api.v1.routes.vehicles.vehicle_handler import _vehicle_data
from sentinel_anpr.interfaces.schemas.responses.attributes.attribute_extraction_response import (
    VehicleAttributesResponseData,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.workflow.workflow_response import (
    AttributeComparisonData,
    AttributeComparisonItemData,
    RiskSignalData,
    VehicleVerificationWorkflowData,
    VerificationResultData,
    VisionProgressData,
    WorkflowStepData,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.get("/vision-progress", response_model=ApiResponse[VisionProgressData])
async def get_vision_progress(
    request: Request,
    correlation_id: str | None = None,
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VisionProgressData]:
    """Return live Vision AI retry progress for a workflow correlation identifier."""
    del principal
    resolved_id = correlation_id or getattr(request.state, "correlation_id", None)
    if not resolved_id:
        return ApiResponse(
            data=VisionProgressData(
                message="Waiting for Vision AI...",
                attempt=0,
                max_attempts=5,
                phase="idle",
            ),
            meta=ResponseMeta(correlation_id=None),
        )

    snapshot = get_vision_progress(resolved_id)
    if snapshot is None:
        return ApiResponse(
            data=VisionProgressData(
                message="Waiting for Vision AI...",
                attempt=0,
                max_attempts=5,
                phase="idle",
            ),
            meta=ResponseMeta(correlation_id=resolved_id),
        )

    return ApiResponse(
        data=VisionProgressData(
            message=snapshot.message,
            attempt=snapshot.attempt,
            max_attempts=snapshot.max_attempts,
            phase=snapshot.phase,
        ),
        meta=ResponseMeta(correlation_id=resolved_id),
    )


@router.post("/vehicle-verification", response_model=ApiResponse[VehicleVerificationWorkflowData])
async def run_vehicle_verification_workflow(
    request: Request,
    vehicle_image: UploadFile = File(...),
    location_label: str | None = Form(default=None),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VehicleVerificationWorkflowData] | JSONResponse:
    """Run the full vehicle verification pipeline in one request."""
    try:
        image_bytes = await vehicle_image.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            from sentinel_anpr.domain.ingestion.errors import InvalidImageError

            raise InvalidImageError("Vehicle image must not exceed 10 MB")

        get_officer: GetCurrentOfficerUseCase = request.app.state.container.get_current_officer_use_case
        officer_result = get_officer.execute(principal)
        officer = officer_result.officer
        correlation_id = getattr(request.state, "correlation_id", None)
        bind_vision_progress(correlation_id)

        use_case: RunVisionVerificationWorkflowUseCase = (
            request.app.state.container.run_vehicle_verification_workflow_use_case
        )
        try:
            result = use_case.execute(
                RunVehicleVerificationWorkflowCommand(
                    officer_id=officer.officer_id,
                    officer_name=f"{officer.first_name} {officer.last_name}",
                    badge_number=officer.badge_number,
                    officer_rank=officer.rank,
                    image_bytes=image_bytes,
                    content_type=vehicle_image.content_type or "application/octet-stream",
                    original_filename=vehicle_image.filename or "vehicle.jpg",
                    location_label=location_label,
                    correlation_id=correlation_id,
                )
            )
        finally:
            clear_vision_progress(correlation_id)

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

        return ApiResponse(
            data=VehicleVerificationWorkflowData(
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
                    _vehicle_data(result.vehicle_information)
                    if result.vehicle_information
                    else None
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
            ),
            meta=ResponseMeta(correlation_id=correlation_id),
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Vehicle verification workflow failed.",
            log_level="error",
            exc=exc,
        )
