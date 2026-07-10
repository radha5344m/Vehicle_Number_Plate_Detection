"""Blockchain evidence integrity routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.use_cases.blockchain.verify_investigation_integrity_use_case import (
    VerifyInvestigationIntegrityUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response
from sentinel_anpr.interfaces.schemas.responses.blockchain.blockchain_response import (
    BlockchainIntegrityVerificationData,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.post(
    "/investigations/{investigation_id}/verify-integrity",
    response_model=ApiResponse[BlockchainIntegrityVerificationData],
)
async def verify_investigation_integrity(
    request: Request,
    investigation_id: str,
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[BlockchainIntegrityVerificationData] | JSONResponse:
    """Verify investigation report integrity against the private evidence blockchain."""
    del principal
    try:
        correlation_id = getattr(request.state, "correlation_id", None) or str(uuid.uuid4())
        use_case: VerifyInvestigationIntegrityUseCase = (
            request.app.state.container.verify_investigation_integrity_use_case
        )
        result = use_case.execute_by_scan_id(investigation_id)
        block = result.block
        return ApiResponse(
            data=BlockchainIntegrityVerificationData(
                investigation_id=result.investigation_id,
                integrity_verified=result.integrity_verified,
                report_sha256_hash=result.report_sha256_hash,
                stored_report_sha256_hash=result.stored_report_sha256_hash,
                block_number=block.block_number if block is not None else None,
                current_hash=block.current_hash if block is not None else None,
                block_timestamp=block.block_timestamp if block is not None else None,
                message=result.message,
            ),
            meta=ResponseMeta(correlation_id=correlation_id),
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Blockchain integrity verification failed.",
            log_level="error",
            exc=exc,
        )
