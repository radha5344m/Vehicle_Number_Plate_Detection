"""Scan history routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.history_dto import SaveCompletedScanCommand, ScanHistoryFilters
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.history.query_scan_history_use_case import (
    QueryScanHistoryUseCase,
)
from sentinel_anpr.application.use_cases.history.save_completed_scan_use_case import (
    SaveCompletedScanUseCase,
)
from sentinel_anpr.domain.vehicle.errors import InvalidPlateError
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.schemas.requests.history.save_scan_request import (
    SaveCompletedScanRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.history.scan_history_response import (
    PaginationData,
    SaveCompletedScanData,
    ScanHistoryItemData,
    ScanHistoryListData,
)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/scans", response_model=ApiResponse[ScanHistoryListData])
def list_scan_history(
    request: Request,
    plate: str | None = Query(default=None, max_length=16),
    officer_id: str | None = Query(default=None, max_length=36),
    risk_level: str | None = Query(default=None, max_length=16),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    principal: AuthPrincipal = Depends(require_permission("investigation_history")),
) -> ApiResponse[ScanHistoryListData]:
    """List completed scans with optional filters."""
    use_case: QueryScanHistoryUseCase = request.app.state.container.query_scan_history_use_case
    scoped_officer_id = officer_id
    scoped_station_id = None
    if principal.role == "STATION_ADMIN":
        scoped_station_id = principal.station_id
    if principal.role == "POLICE_OFFICER":
        scoped_officer_id = principal.officer_id
    try:
        result = use_case.execute(
            ScanHistoryFilters(
                plate=plate,
                officer_id=scoped_officer_id,
                station_id=scoped_station_id,
                risk_level=risk_level,
                from_date=from_date,
                to_date=to_date,
                page=page,
                page_size=page_size,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ScanHistoryListData(
            items=[
                ScanHistoryItemData(
                    scan_id=item.scan_id,
                    plate_text=item.plate_text,
                    vehicle_id=item.vehicle_id,
                    officer_id=item.officer_id,
                    officer_name=item.officer_name,
                    risk_score=item.risk_score,
                    risk_level=item.risk_level,
                    location_label=item.location_label,
                    scanned_at=item.scanned_at,
                    completed_at=item.completed_at,
                )
                for item in result.items
            ],
            pagination=PaginationData(
                page=result.pagination.page,
                page_size=result.pagination.page_size,
                total_items=result.pagination.total_items,
                total_pages=result.pagination.total_pages,
            ),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/scans", response_model=ApiResponse[SaveCompletedScanData])
def save_completed_scan(
    request: Request,
    body: SaveCompletedScanRequest,
    principal: AuthPrincipal = Depends(require_permission("investigation_history")),
) -> ApiResponse[SaveCompletedScanData]:
    """Store a completed scan in history."""
    get_officer: GetCurrentOfficerUseCase = request.app.state.container.get_current_officer_use_case
    officer_result = get_officer.execute(principal)
    officer = officer_result.officer

    use_case: SaveCompletedScanUseCase = request.app.state.container.save_completed_scan_use_case
    try:
        result = use_case.execute(
            SaveCompletedScanCommand(
                officer_id=officer.officer_id,
                officer_name=f"{officer.first_name} {officer.last_name}",
                plate_text=body.plate,
                risk_score=body.risk_score,
                risk_level=body.risk_level,
                vehicle_id=body.vehicle_id,
                location_label=body.location_label,
            )
        )
    except InvalidPlateError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=SaveCompletedScanData(
            scan_id=result.scan_id,
            plate_text=result.plate_text,
            scanned_at=result.scanned_at,
            completed_at=result.completed_at,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
