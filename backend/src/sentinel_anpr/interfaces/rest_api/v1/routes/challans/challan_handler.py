"""e-Challan management routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.challan_dto import ChallanFilters, CreateChallanCommand, UpdateChallanCommand
from sentinel_anpr.application.use_cases.challans.challan_use_cases import (
    CancelChallanUseCase,
    CreateChallanUseCase,
    DeleteChallanUseCase,
    GenerateChallanPdfUseCase,
    GetChallanAnalyticsUseCase,
    GetChallanUseCase,
    ListViolationMasterUseCase,
    MarkChallanPaidUseCase,
    QueryChallansUseCase,
    SearchVehicleForChallanUseCase,
    UpdateChallanUseCase,
)
from sentinel_anpr.domain.challans.errors import ChallanAccessDeniedError, ChallanNotFoundError
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal, require_permission
from sentinel_anpr.interfaces.schemas.requests.challans.challan_request import (
    CreateChallanRequest,
    UpdateChallanRequest,
)
from sentinel_anpr.interfaces.schemas.responses.challans.challan_response import (
    ChallanAnalyticsData,
    ChallanDetailData,
    ChallanItemData,
    ChallanMutationData,
    ChallanPaginationData,
    ChallanSummaryData,
    ChallansListData,
    DistributionItemData,
    MonthlyFineCollectionData,
    VehicleChallanSearchData,
    ViolationMasterData,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta

router = APIRouter(prefix="/challans", tags=["challans"])


def _map_item(item) -> ChallanItemData:  # noqa: ANN001
    return ChallanItemData(
        id=item.id,
        challan_number=item.challan_number,
        registration_number=item.registration_number,
        owner_name=item.owner_name,
        violation_type=item.violation_type,
        violation_description=item.violation_description,
        fine_amount=item.fine_amount,
        payment_status=item.payment_status,
        officer_id=item.officer_id,
        officer_name=item.officer_name,
        station_id=item.station_id,
        station_name=item.station_name,
        issued_at=item.issued_at,
    )


def _map_detail(item) -> ChallanDetailData:  # noqa: ANN001
    return ChallanDetailData(
        **_map_item(item).model_dump(),
        investigation_id=item.investigation_id,
        vehicle_id=item.vehicle_id,
        remarks=item.remarks,
        location_label=item.location_label,
        gps_coordinates=item.gps_coordinates,
        evidence_image_path=item.evidence_image_path,
        paid_at=item.paid_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/violations", response_model=ApiResponse[list[ViolationMasterData]])
def list_violations(
    request: Request,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[list[ViolationMasterData]]:
    use_case: ListViolationMasterUseCase = request.app.state.container.list_violation_master_use_case
    items = use_case.execute()
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=[
            ViolationMasterData(
                violation_code=item.violation_code,
                violation_name=item.violation_name,
                default_fine_amount=item.default_fine_amount,
                amount_editable=item.amount_editable,
            )
            for item in items
        ],
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/search", response_model=ApiResponse[VehicleChallanSearchData])
def search_vehicle(
    request: Request,
    registration_number: str = Query(min_length=1, max_length=32),
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[VehicleChallanSearchData]:
    use_case: SearchVehicleForChallanUseCase = request.app.state.container.search_vehicle_for_challan_use_case
    try:
        result = use_case.execute(registration_number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=VehicleChallanSearchData(
            registration_number=result.registration_number,
            vehicle_found=result.vehicle_found,
            owner_name=result.owner_name,
            vehicle_name=result.vehicle_name,
            brand=result.brand,
            model=result.model,
            color=result.color,
            vehicle_type=result.vehicle_type,
            rc_status=result.rc_status,
            insurance_status=result.insurance_status,
            pollution_status=result.pollution_status,
            risk_level=result.risk_level,
            outstanding_fine_inr=result.outstanding_fine_inr,
            pending_challans_count=result.pending_challans_count,
            previous_violations=list(result.previous_violations),
            existing_challans=[_map_item(item) for item in result.existing_challans],
            challan_summary=ChallanSummaryData(
                outstanding_fine_inr=result.challan_summary.outstanding_fine_inr,
                pending_challans_count=result.challan_summary.pending_challans_count,
                latest_violation=result.challan_summary.latest_violation,
            ),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("", response_model=ApiResponse[ChallansListData])
def list_challans(
    request: Request,
    search: str | None = Query(default=None),
    registration_number: str | None = Query(default=None),
    challan_number: str | None = Query(default=None),
    owner_name: str | None = Query(default=None),
    officer_id: str | None = Query(default=None),
    station_id: str | None = Query(default=None),
    violation_type: str | None = Query(default=None),
    payment_status: str | None = Query(default=None),
    pending_only: bool = Query(default=False),
    issued_from: datetime | None = Query(default=None),
    issued_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallansListData]:
    use_case: QueryChallansUseCase = request.app.state.container.query_challans_use_case
    result = use_case.execute(
        principal,
        ChallanFilters(
            search=search,
            registration_number=registration_number,
            challan_number=challan_number,
            owner_name=owner_name,
            officer_id=officer_id,
            station_id=station_id,
            violation_type=violation_type,
            payment_status=payment_status,
            pending_only=pending_only,
            issued_from=issued_from,
            issued_to=issued_to,
            page=page,
            page_size=page_size,
        ),
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallansListData(
            items=[_map_item(item) for item in result.items],
            pagination=ChallanPaginationData(**result.pagination.__dict__),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/analytics", response_model=ApiResponse[ChallanAnalyticsData])
def challan_analytics(
    request: Request,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanAnalyticsData]:
    use_case: GetChallanAnalyticsUseCase = request.app.state.container.get_challan_analytics_use_case
    result = use_case.execute(principal)
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallanAnalyticsData(
            total_challans=result.total_challans,
            todays_challans=result.todays_challans,
            pending_challans=result.pending_challans,
            paid_challans=result.paid_challans,
            collected_fine_inr=result.collected_fine_inr,
            outstanding_fine_inr=result.outstanding_fine_inr,
            most_common_violation=result.most_common_violation,
            top_issuing_officer=result.top_issuing_officer,
            top_station=result.top_station,
            violation_distribution=[
                DistributionItemData(label=item.label, value=item.value)
                for item in result.violation_distribution
            ],
            monthly_fine_collection=[
                MonthlyFineCollectionData(
                    month=item.month,
                    collected_fine_inr=item.collected_fine_inr,
                    issued_count=item.issued_count,
                )
                for item in result.monthly_fine_collection
            ],
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("", response_model=ApiResponse[ChallanMutationData], status_code=201)
def create_challan(
    request: Request,
    body: CreateChallanRequest,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanMutationData]:
    use_case: CreateChallanUseCase = request.app.state.container.create_challan_use_case
    try:
        result = use_case.execute(
            principal,
            CreateChallanCommand(
                registration_number=body.registration_number,
                owner_name=body.owner_name,
                vehicle_id=body.vehicle_id,
                investigation_id=body.investigation_id,
                violation_type=body.violation_type,
                violation_description=body.violation_description,
                fine_amount=body.fine_amount,
                remarks=body.remarks,
                location_label=body.location_label,
                gps_coordinates=body.gps_coordinates,
                evidence_image_path=None,
                officer_id="",
                officer_name="",
                station_id="",
                station_name="",
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallanMutationData(
            challan=_map_detail(result.challan),
            pdf_download_url=result.pdf_download_url,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/{challan_id}", response_model=ApiResponse[ChallanDetailData])
def get_challan(
    request: Request,
    challan_id: str,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanDetailData]:
    use_case: GetChallanUseCase = request.app.state.container.get_challan_use_case
    try:
        challan = use_case.execute(principal, challan_id)
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=_map_detail(challan), meta=ResponseMeta(correlation_id=correlation_id))


@router.patch("/{challan_id}", response_model=ApiResponse[ChallanMutationData])
def update_challan(
    request: Request,
    challan_id: str,
    body: UpdateChallanRequest,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanMutationData]:
    use_case: UpdateChallanUseCase = request.app.state.container.update_challan_use_case
    try:
        result = use_case.execute(
            principal,
            UpdateChallanCommand(
                challan_id=challan_id,
                violation_type=body.violation_type,
                violation_description=body.violation_description,
                fine_amount=body.fine_amount,
                remarks=body.remarks,
                location_label=body.location_label,
                gps_coordinates=body.gps_coordinates,
            ),
        )
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallanMutationData(challan=_map_detail(result.challan)),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/{challan_id}/cancel", response_model=ApiResponse[ChallanMutationData])
def cancel_challan(
    request: Request,
    challan_id: str,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanMutationData]:
    use_case: CancelChallanUseCase = request.app.state.container.cancel_challan_use_case
    try:
        result = use_case.execute(principal, challan_id)
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallanMutationData(challan=_map_detail(result.challan)),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/{challan_id}/mark-paid", response_model=ApiResponse[ChallanMutationData])
def mark_challan_paid(
    request: Request,
    challan_id: str,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> ApiResponse[ChallanMutationData]:
    use_case: MarkChallanPaidUseCase = request.app.state.container.mark_challan_paid_use_case
    try:
        result = use_case.execute(principal, challan_id)
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ChallanMutationData(challan=_map_detail(result.challan)),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.delete("/{challan_id}", status_code=204)
def delete_challan(
    request: Request,
    challan_id: str,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> None:
    use_case: DeleteChallanUseCase = request.app.state.container.delete_challan_use_case
    try:
        use_case.execute(principal, challan_id)
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/{challan_id}/download")
def download_challan_pdf(
    request: Request,
    challan_id: str,
    principal: AuthPrincipal = Depends(require_permission("challans")),
) -> Response:
    use_case: GenerateChallanPdfUseCase = request.app.state.container.generate_challan_pdf_use_case
    try:
        challan, pdf_bytes = use_case.execute(principal, challan_id)
    except ChallanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Challan not found") from exc
    except ChallanAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{challan.challan_number}.pdf"'},
    )
