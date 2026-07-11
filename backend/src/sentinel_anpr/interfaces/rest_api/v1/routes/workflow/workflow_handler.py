"""End-to-end vehicle verification workflow routes."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.vehicle_detection_dto import (
    DetectVehiclesCommand,
    SelectedVehicleRegionDto,
)
from sentinel_anpr.application.dto.visible_vehicle_count_dto import CountVisibleVehiclesCommand
from sentinel_anpr.application.dto.workflow_dto import RunVehicleVerificationWorkflowCommand
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.count_visible_vehicles_use_case import (
    CountVisibleVehiclesUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.detect_vehicles_use_case import (
    DetectVehiclesUseCase,
)
from sentinel_anpr.application.use_cases.orchestration.run_selected_vehicles_verification_workflow_use_case import (
    RunSelectedVehiclesVerificationWorkflowUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response
from sentinel_anpr.interfaces.rest_api.v1.routes.workflow.workflow_mapper import (
    map_detection_result_to_response,
    map_visible_vehicle_count_to_response,
    map_workflow_batch_result_to_response,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.workflow.workflow_response import (
    VehicleDetectionData,
    VisibleVehicleCountData,
    VehicleVerificationWorkflowData,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _parse_selected_regions(raw_regions: str | None) -> tuple[SelectedVehicleRegionDto, ...] | None:
    if not raw_regions:
        return None

    payload = json.loads(raw_regions)
    if not isinstance(payload, list) or not payload:
        raise ValueError("selected_regions must be a non-empty JSON array")

    regions: list[SelectedVehicleRegionDto] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each selected region must be an object")
        regions.append(
            SelectedVehicleRegionDto(
                vehicle_id=str(item["vehicle_id"]),
                x=float(item["x"]),
                y=float(item["y"]),
                width=float(item["width"]),
                height=float(item["height"]),
            )
        )
    return tuple(regions)


@router.post(
    "/detect-vehicles",
    response_model=ApiResponse[VehicleDetectionData],
)
async def detect_vehicles(
    request: Request,
    vehicle_image: UploadFile = File(...),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VehicleDetectionData] | JSONResponse:
    """Detect visible vehicles in an uploaded scene image."""
    del principal
    try:
        image_bytes = await vehicle_image.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            from sentinel_anpr.domain.ingestion.errors import InvalidImageError

            raise InvalidImageError("Vehicle image must not exceed 10 MB")

        correlation_id = getattr(request.state, "correlation_id", None) or str(uuid.uuid4())
        use_case: DetectVehiclesUseCase = request.app.state.container.detect_vehicles_use_case
        result = use_case.execute(
            DetectVehiclesCommand(
                image_bytes=image_bytes,
                content_type=vehicle_image.content_type or "application/octet-stream",
            )
        )
        return ApiResponse(
            data=map_detection_result_to_response(result),
            meta=ResponseMeta(correlation_id=correlation_id),
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Vehicle detection failed.",
            log_level="error",
            exc=exc,
        )


@router.post(
    "/count-visible-vehicles",
    response_model=ApiResponse[VisibleVehicleCountData],
)
async def count_visible_vehicles(
    request: Request,
    vehicle_image: UploadFile = File(...),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VisibleVehicleCountData] | JSONResponse:
    """Count visible vehicles with vision AI before upload investigation routing."""
    del principal
    try:
        image_bytes = await vehicle_image.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            from sentinel_anpr.domain.ingestion.errors import InvalidImageError

            raise InvalidImageError("Vehicle image must not exceed 10 MB")

        correlation_id = getattr(request.state, "correlation_id", None) or str(uuid.uuid4())
        use_case: CountVisibleVehiclesUseCase = request.app.state.container.count_visible_vehicles_use_case
        result = use_case.execute(
            CountVisibleVehiclesCommand(
                image_bytes=image_bytes,
                content_type=vehicle_image.content_type or "application/octet-stream",
            )
        )
        return ApiResponse(
            data=map_visible_vehicle_count_to_response(result),
            meta=ResponseMeta(correlation_id=correlation_id),
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Visible vehicle counting failed.",
            log_level="error",
            exc=exc,
        )


@router.post(
    "/vehicle-verification",
    response_model=ApiResponse[VehicleVerificationWorkflowData],
)
async def run_vehicle_verification_workflow(
    request: Request,
    vehicle_image: UploadFile = File(...),
    location_label: str | None = Form(default=None),
    selected_regions: str | None = Form(default=None),
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
        regions = _parse_selected_regions(selected_regions)

        use_case: RunSelectedVehiclesVerificationWorkflowUseCase = (
            request.app.state.container.run_selected_vehicles_verification_workflow_use_case
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
            selected_regions=regions,
        )

        result = use_case.execute(command)

        return ApiResponse(
            data=map_workflow_batch_result_to_response(result),
            meta=ResponseMeta(correlation_id=workflow_id),
        )
    except ValueError as exc:
        return build_error_response(
            request,
            400,
            "VALIDATION_ERROR",
            str(exc),
            log_level="warning",
            exc=exc,
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
