"""Vehicle image upload routes."""

from fastapi import APIRouter, Depends, File, Request, UploadFile

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.upload_dto import UploadImageCommand
from sentinel_anpr.application.use_cases.ingestion.upload_vehicle_image_use_case import (
    UploadVehicleImageUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.upload.upload_response import (
    UploadImageResponseData,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/vehicle-image", response_model=ApiResponse[UploadImageResponseData], status_code=201)
async def upload_vehicle_image(
    request: Request,
    image: UploadFile = File(...),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[UploadImageResponseData]:
    """Store a vehicle image without AI or OCR processing."""
    content = await image.read()
    if len(content) > MAX_UPLOAD_BYTES:
        from sentinel_anpr.domain.ingestion.errors import InvalidImageError

        raise InvalidImageError("Image must not exceed 10 MB")

    use_case: UploadVehicleImageUseCase = request.app.state.container.upload_vehicle_image_use_case
    result = use_case.execute(
        UploadImageCommand(
            officer_id=principal.officer_id,
            content=content,
            content_type=image.content_type or "application/octet-stream",
            original_filename=image.filename or "upload.jpg",
        )
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UploadImageResponseData(
            upload_id=result.upload_id,
            storage_key=result.storage_key,
            original_filename=result.original_filename,
            content_type=result.content_type,
            size_bytes=result.size_bytes,
            width=result.width,
            height=result.height,
            uploaded_at=result.uploaded_at,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
