"""Police station management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.station_management_dto import (
    CreateStationCommand,
    StationFilters,
    StationStatusCommand,
    UpdateStationCommand,
)
from sentinel_anpr.application.use_cases.authentication.station_management_use_cases import (
    ChangeStationStatusUseCase,
    CreateStationUseCase,
    DeleteStationUseCase,
    GetStationUseCase,
    QueryStationsUseCase,
    UpdateStationUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.schemas.requests.stations.station_management_request import (
    CreateStationRequest,
    UpdateStationRequest,
    UpdateStationStatusRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.stations.station_management_response import (
    ActionMessageData,
    StationItemData,
    StationMutationData,
    StationPaginationData,
    StationsListData,
)

router = APIRouter(prefix="/stations", tags=["stations"])


def _map_station(item) -> StationItemData:  # noqa: ANN001
    return StationItemData(
        station_id=item.station_id,
        station_name=item.station_name,
        station_code=item.station_code,
        district=item.district,
        state=item.state,
        address=item.address,
        pincode=item.pincode,
        phone_number=item.phone_number,
        email=item.email,
        station_type=item.station_type,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=ApiResponse[StationsListData])
def list_stations(
    request: Request,
    search: str | None = Query(default=None),
    district: str | None = Query(default=None),
    state: str | None = Query(default=None),
    status: str | None = Query(default=None),
    station_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_desc: bool = Query(default=True),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationsListData]:
    use_case: QueryStationsUseCase = request.app.state.container.query_stations_use_case
    result = use_case.execute(
        principal,
        StationFilters(
            search=search,
            district=district,
            state=state,
            status=status,
            station_type=station_type,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        ),
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=StationsListData(
            items=[_map_station(item) for item in result.items],
            pagination=StationPaginationData(
                page=result.pagination.page,
                page_size=result.pagination.page_size,
                total_items=result.pagination.total_items,
                total_pages=result.pagination.total_pages,
            ),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/{station_id}", response_model=ApiResponse[StationMutationData])
def get_station(
    request: Request,
    station_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationMutationData]:
    use_case: GetStationUseCase = request.app.state.container.get_station_use_case
    try:
        station = use_case.execute(principal, station_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Station not found") from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=StationMutationData(station=_map_station(station)), meta=ResponseMeta(correlation_id=correlation_id))


@router.post("", response_model=ApiResponse[StationMutationData], status_code=201)
def create_station(
    request: Request,
    body: CreateStationRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationMutationData]:
    use_case: CreateStationUseCase = request.app.state.container.create_station_use_case
    try:
        result = use_case.execute(
            principal,
            CreateStationCommand(
                station_name=body.station_name,
                station_code=body.station_code,
                district=body.district,
                state=body.state,
                address=body.address,
                pincode=body.pincode,
                phone_number=body.phone_number,
                email=body.email,
                station_type=body.station_type,
                status=body.status,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=StationMutationData(station=_map_station(result.station)), meta=ResponseMeta(correlation_id=correlation_id))


@router.put("/{station_id}", response_model=ApiResponse[StationMutationData])
def update_station(
    request: Request,
    station_id: str,
    body: UpdateStationRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationMutationData]:
    use_case: UpdateStationUseCase = request.app.state.container.update_station_use_case
    try:
        result = use_case.execute(
            principal,
            UpdateStationCommand(
                station_id=station_id,
                station_name=body.station_name,
                district=body.district,
                state=body.state,
                address=body.address,
                pincode=body.pincode,
                phone_number=body.phone_number,
                email=body.email,
                station_type=body.station_type,
                status=body.status,
            ),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Station not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=StationMutationData(station=_map_station(result.station)), meta=ResponseMeta(correlation_id=correlation_id))


@router.patch("/{station_id}/status", response_model=ApiResponse[StationMutationData])
def update_station_status(
    request: Request,
    station_id: str,
    body: UpdateStationStatusRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationMutationData]:
    use_case: ChangeStationStatusUseCase = request.app.state.container.change_station_status_use_case
    try:
        result = use_case.execute(principal, StationStatusCommand(station_id=station_id, status=body.status))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Station not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=StationMutationData(station=_map_station(result.station)), meta=ResponseMeta(correlation_id=correlation_id))


@router.delete("/{station_id}", response_model=ApiResponse[ActionMessageData])
def delete_station(
    request: Request,
    station_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    use_case: DeleteStationUseCase = request.app.state.container.delete_station_use_case
    try:
        use_case.execute(principal, station_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Station not found") from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=ActionMessageData(message="Station deleted successfully"), meta=ResponseMeta(correlation_id=correlation_id))
