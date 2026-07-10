"""End-to-end vehicle verification workflow routes."""

from __future__ import annotations

import uuid

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
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response
from sentinel_anpr.interfaces.rest_api.v1.routes.workflow.workflow_mapper import (
    map_workflow_result_to_response,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.workflow.workflow_response import (
    VehicleVerificationWorkflowData,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post(
    "/vehicle-verification",
    response_model=ApiResponse[VehicleVerificationWorkflowData],
)
async def run_vehicle_verification_workflow(
    request: Request,
    vehicle_image: UploadFile = File(...),
    location_label: str | None = Form(default=None),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VehicleVerificationWorkflowData] | JSONResponse:
    """Run vehicle verification synchronously and return the complete investigation result."""
    try:
        image_bytes = await vehicle_image.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            from sentinel_anpr.domain.ingestion.errors import InvalidImageError

            raise InvalidImageError("Vehicle image must not exceed 10 MB")

        get_officer: GetCurrentOfficerUseCase = request.app.state.container.get_current_officer_use_case
        officer_result = get_officer.execute(principal)
        officer = officer_result.officer
        workflow_id = getattr(request.state, "correlation_id", None) or str(uuid.uuid4())

        use_case: RunVisionVerificationWorkflowUseCase = (
            request.app.state.container.run_vehicle_verification_workflow_use_case
        )
        command = RunVehicleVerificationWorkflowCommand(
            officer_id=officer.officer_id,
            officer_name=f"{officer.first_name} {officer.last_name}",
            badge_number=officer.badge_number,
            officer_rank=officer.rank,
            image_bytes=image_bytes,
            content_type=vehicle_image.content_type or "application/octet-stream",
            original_filename=vehicle_image.filename or "vehicle.jpg",
            location_label=location_label,
            correlation_id=workflow_id,
        )

        result = use_case.execute(command)

        return ApiResponse(
            data=map_workflow_result_to_response(result),
            meta=ResponseMeta(correlation_id=workflow_id),
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
