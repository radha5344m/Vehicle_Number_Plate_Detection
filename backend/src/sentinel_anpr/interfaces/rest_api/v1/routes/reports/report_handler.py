"""Investigation report routes."""

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.report_dto import (
    GenerateInvestigationReportCommand,
    OcrResultDto,
    VehicleDetailsDto,
)
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.reporting.download_investigation_report_use_case import (
    DownloadInvestigationReportUseCase,
)
from sentinel_anpr.application.use_cases.reporting.generate_investigation_report_use_case import (
    GenerateInvestigationReportUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.schemas.requests.reporting.generate_report_request import (
    GenerateInvestigationReportRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.reporting.report_response import (
    InvestigationReportResponseData,
)

router = APIRouter(prefix="/reports", tags=["reports"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post(
    "/investigation",
    response_model=ApiResponse[InvestigationReportResponseData],
    status_code=201,
)
async def generate_investigation_report(
    request: Request,
    vehicle_image: UploadFile = File(...),
    payload: str = Form(...),
    principal: AuthPrincipal = Depends(require_permission("reports")),
) -> ApiResponse[InvestigationReportResponseData]:
    """Generate a professional investigation PDF from supplied scan data."""
    image_bytes = await vehicle_image.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Vehicle image must not exceed 10 MB")

    try:
        body = GenerateInvestigationReportRequest.model_validate(json.loads(payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid report payload") from exc

    get_officer: GetCurrentOfficerUseCase = request.app.state.container.get_current_officer_use_case
    officer_result = get_officer.execute(principal)
    officer = officer_result.officer

    vehicle_details = None
    if body.vehicle_details is not None:
        vehicle_details = VehicleDetailsDto(
            plate_number=body.vehicle_details.plate_number,
            make=body.vehicle_details.make,
            model=body.vehicle_details.model,
            color=body.vehicle_details.color,
            vehicle_type=body.vehicle_details.vehicle_type,
            registration_status=body.vehicle_details.registration_status,
            registered_owner=body.vehicle_details.registered_owner,
        )

    use_case: GenerateInvestigationReportUseCase = (
        request.app.state.container.generate_investigation_report_use_case
    )
    try:
        result = use_case.execute(
            GenerateInvestigationReportCommand(
                officer_id=officer.officer_id,
                officer_name=f"{officer.first_name} {officer.last_name}",
                badge_number=officer.badge_number,
                officer_rank=officer.rank,
                vehicle_image_bytes=image_bytes,
                detected_plate=body.detected_plate,
                ocr_result=OcrResultDto(
                    registration_number=body.ocr_registration_number,
                    detected_plate_text=body.ocr_detected_text,
                    ocr_confidence=body.ocr_confidence,
                ),
                vehicle_details=vehicle_details,
                risk_score=body.risk_score,
                risk_level=body.risk_level,
                recommendation=body.recommendation,
                title=body.title,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=InvestigationReportResponseData(
            report_id=result.report_id,
            title=result.title,
            file_size_bytes=result.file_size_bytes,
            checksum_sha256=result.checksum_sha256,
            generated_at=result.generated_at,
            download_url=f"/v1/reports/{result.report_id}/download",
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/{report_id}/download")
def download_investigation_report(
    request: Request,
    report_id: str,
    principal: AuthPrincipal = Depends(require_permission("reports")),
) -> Response:
    """Download a generated investigation report PDF."""
    use_case: DownloadInvestigationReportUseCase = (
        request.app.state.container.download_investigation_report_use_case
    )
    try:
        result = use_case.execute(report_id=report_id, principal=principal)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return Response(
        content=result.pdf_bytes,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
