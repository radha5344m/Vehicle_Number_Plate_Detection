"""Station admin portal routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.investigation_reports_dto import ExportFormat, InvestigationReportsFilters, InvestigationSortBy
from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.station_admin_portal_dto import (
    ChangeOwnPasswordCommand,
    CreatePoliceOfficerCommand,
    StationAdminInvestigationFilters,
    StationAdminOfficerFilters,
    UpdatePoliceOfficerCommand,
)
from sentinel_anpr.application.use_cases.authentication.station_admin_portal_use_cases import (
    ChangeStationAdminPasswordUseCase,
    ChangeStationOfficerStatusUseCase,
    CreateStationOfficerUseCase,
    ensure_station_admin,
    GetStationAdminDashboardUseCase,
    GetStationAdminProfileUseCase,
    GetStationAnalyticsUseCase,
    GetStationNotificationsUseCase,
    QueryStationInvestigationsUseCase,
    QueryStationOfficersUseCase,
    QueryStationReportsUseCase,
    ResetStationOfficerPasswordUseCase,
    SoftDeleteStationOfficerUseCase,
    UpdateStationAdminProfileUseCase,
    UpdateStationDetailsUseCase,
    UpdateStationOfficerUseCase,
)
from sentinel_anpr.application.dto.station_admin_portal_dto import UpdateStationDetailsCommand
from sentinel_anpr.application.use_cases.reporting.export_investigation_reports_use_case import ExportInvestigationReportsUseCase
from sentinel_anpr.application.use_cases.reporting.query_investigation_reports_use_case import QueryInvestigationReportsUseCase
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.schemas.requests.profile.update_own_profile_request import (
    UpdateOwnProfileRequest,
)
from sentinel_anpr.interfaces.schemas.requests.station_admin.station_admin_request import (
    ChangeOwnPasswordRequest,
    CreateOfficerRequest,
    ResetOfficerPasswordRequest,
    UpdateOfficerRequest,
    UpdateStationDetailsRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.reporting.investigation_reports_response import (
    DailyInvestigationTrendPointData,
    DistributionItemData,
    InvestigationReportListItemData,
    InvestigationReportsData,
    InvestigationReportsPaginationData,
    InvestigationSummaryData,
    OfficerPerformanceItemData,
    PeriodInvestigationTrendPointData,
    StationPerformanceItemData,
)
from sentinel_anpr.interfaces.schemas.responses.station_admin.station_admin_response import (
    ActionMessageData,
    StationAdminAnalyticsData,
    StationAdminDashboardData,
    StationAdminHighRiskVehicleData,
    StationAdminNotificationData,
    StationAdminNotificationsData,
    StationAdminOfficerItemData,
    StationAdminOfficerMutationData,
    StationAdminOfficerPaginationData,
    StationAdminOfficersData,
    StationAdminProfileData,
    StationAdminRecentInvestigationData,
    StationAdminRecentOfficerActivityData,
    StationAdminSummaryData,
)

router = APIRouter(prefix="/station-admin", tags=["station-admin"])


def _meta(request: Request) -> ResponseMeta:
    return ResponseMeta(correlation_id=getattr(request.state, "correlation_id", None))


def _require_station_admin(principal: AuthPrincipal) -> None:
    try:
        ensure_station_admin(principal)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


def _map_officer(item) -> StationAdminOfficerItemData:  # noqa: ANN001
    return StationAdminOfficerItemData(
        officer_id=item.officer_id,
        user_id=item.user_id,
        employee_id=item.employee_id,
        badge_number=item.badge_number,
        officer_name=item.officer_name,
        rank=item.rank,
        phone_number=item.phone_number,
        status=item.status,
        investigations=item.investigations,
        last_login_at=item.last_login_at,
        username=item.username,
        email=item.email,
        created_at=item.created_at,
    )


def _map_officer_mutation(result) -> StationAdminOfficerMutationData:  # noqa: ANN001
    return StationAdminOfficerMutationData(
        officer=_map_officer(result.officer),
        temporary_password=result.temporary_password,
        password_change_required=result.password_change_required,
    )


def _investigation_response(result) -> InvestigationReportsData:  # noqa: ANN001
    return InvestigationReportsData(
        summary=InvestigationSummaryData(
            investigation_summary=result.analytics.investigation_summary,
            total_investigations=result.analytics.totals.total_investigations,
            verified_vehicles=result.analytics.totals.verified_vehicles,
            suspicious_vehicles=result.analytics.totals.suspicious_vehicles,
            high_risk_vehicles=result.analytics.totals.high_risk_vehicles,
            average_risk_score=result.analytics.totals.average_risk_score,
            average_ai_confidence=result.analytics.totals.average_ai_confidence,
            average_investigation_time_minutes=result.analytics.totals.average_investigation_time_minutes,
            top_vehicle_type=result.analytics.totals.top_vehicle_type,
            top_vehicle_brand=result.analytics.totals.top_vehicle_brand,
            most_active_officer=result.analytics.totals.most_active_officer,
            most_active_station=result.analytics.totals.most_active_station,
        ),
        risk_distribution=[DistributionItemData(label=item.label, value=item.value) for item in result.analytics.risk_distribution],
        vehicle_type_distribution=[DistributionItemData(label=item.label, value=item.value) for item in result.analytics.vehicle_type_distribution],
        brand_distribution=[DistributionItemData(label=item.label, value=item.value) for item in result.analytics.brand_distribution],
        officer_performance=[
            OfficerPerformanceItemData(
                officer_id=item.officer_id,
                officer_name=item.officer_name,
                investigations=item.investigations,
                verified_vehicles=item.verified_vehicles,
                high_risk_vehicles=item.high_risk_vehicles,
                average_risk_score=item.average_risk_score,
                average_ai_confidence=item.average_ai_confidence,
            )
            for item in result.analytics.officer_performance
        ],
        station_performance=[
            StationPerformanceItemData(
                station_name=item.station_name,
                investigations=item.investigations,
                verified_vehicles=item.verified_vehicles,
                high_risk_vehicles=item.high_risk_vehicles,
                average_risk_score=item.average_risk_score,
                average_ai_confidence=item.average_ai_confidence,
            )
            for item in result.analytics.station_performance
        ],
        verification_status_distribution=[DistributionItemData(label=item.label, value=item.value) for item in result.analytics.verification_status_distribution],
        daily_investigation_trend=[DailyInvestigationTrendPointData(date=item.date, investigations=item.investigations) for item in result.analytics.daily_investigation_trend],
        weekly_investigation_trend=[PeriodInvestigationTrendPointData(period=item.period, investigations=item.investigations) for item in result.analytics.weekly_investigation_trend],
        monthly_investigation_trend=[PeriodInvestigationTrendPointData(period=item.period, investigations=item.investigations) for item in result.analytics.monthly_investigation_trend],
        items=[
            InvestigationReportListItemData(
                scanned_at=item.scanned_at,
                completed_at=item.completed_at,
                investigation_id=item.investigation_id,
                registration_number=item.registration_number,
                owner=item.owner,
                vehicle=item.vehicle,
                brand=item.brand,
                model=item.model,
                officer_id=item.officer_id,
                officer_name=item.officer_name,
                station_name=item.station_name,
                district=item.district,
                police_station=item.police_station,
                risk_score=item.risk_score,
                risk_level=item.risk_level,
                investigation_status=item.investigation_status,
                verification_status=item.verification_status,
                ai_confidence=item.ai_confidence,
                report_id=item.report_id,
                report_download_url=item.report_download_url,
                vehicle_type=item.vehicle_type,
                verification_message=item.verification_message,
            )
            for item in result.items
        ],
        pagination=InvestigationReportsPaginationData(
            page=result.pagination.page,
            page_size=result.pagination.page_size,
            total_items=result.pagination.total_items,
            total_pages=result.pagination.total_pages,
        ),
        generated_at=result.generated_at,
    )


@router.get("/dashboard", response_model=ApiResponse[StationAdminDashboardData])
def dashboard(
    request: Request,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminDashboardData]:
    _require_station_admin(principal)
    use_case: GetStationAdminDashboardUseCase = request.app.state.container.get_station_admin_dashboard_use_case
    result = use_case.execute(principal)
    return ApiResponse(
        data=StationAdminDashboardData(
            summary=StationAdminSummaryData(**result.summary.__dict__),
            recent_investigations=[StationAdminRecentInvestigationData(**item.__dict__) for item in result.recent_investigations],
            recent_officer_activity=[StationAdminRecentOfficerActivityData(**item.__dict__) for item in result.recent_officer_activity],
            high_risk_vehicles=[StationAdminHighRiskVehicleData(**item.__dict__) for item in result.high_risk_vehicles],
        ),
        meta=_meta(request),
    )


@router.get("/officers", response_model=ApiResponse[StationAdminOfficersData])
def list_officers(
    request: Request,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    rank: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminOfficersData]:
    _require_station_admin(principal)
    use_case: QueryStationOfficersUseCase = request.app.state.container.query_station_officers_use_case
    result = use_case.execute(principal, StationAdminOfficerFilters(search=search, status=status, rank=rank, page=page, page_size=page_size))
    return ApiResponse(
        data=StationAdminOfficersData(
            items=[_map_officer(item) for item in result.items],
            pagination=StationAdminOfficerPaginationData(**result.pagination.__dict__),
        ),
        meta=_meta(request),
    )


@router.post("/officers", response_model=ApiResponse[StationAdminOfficerMutationData], status_code=201)
def create_officer(
    request: Request,
    body: CreateOfficerRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminOfficerMutationData]:
    _require_station_admin(principal)
    use_case: CreateStationOfficerUseCase = request.app.state.container.create_station_officer_use_case
    try:
        result = use_case.execute(principal, CreatePoliceOfficerCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return ApiResponse(data=_map_officer_mutation(result), meta=_meta(request))


@router.put("/officers/{officer_id}", response_model=ApiResponse[StationAdminOfficerMutationData])
def update_officer(
    request: Request,
    officer_id: str,
    body: UpdateOfficerRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminOfficerMutationData]:
    _require_station_admin(principal)
    use_case: UpdateStationOfficerUseCase = request.app.state.container.update_station_officer_use_case
    try:
        result = use_case.execute(principal, UpdatePoliceOfficerCommand(officer_id=officer_id, **body.model_dump()))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Officer not found") from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 403, detail=str(exc)) from exc
    return ApiResponse(data=_map_officer_mutation(result), meta=_meta(request))


@router.delete("/officers/{officer_id}", response_model=ApiResponse[ActionMessageData])
def delete_officer(
    request: Request,
    officer_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    _require_station_admin(principal)
    use_case: SoftDeleteStationOfficerUseCase = request.app.state.container.soft_delete_station_officer_use_case
    try:
        use_case.execute(principal, officer_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Officer not found") from exc
    return ApiResponse(data=ActionMessageData(message="Officer deleted successfully"), meta=_meta(request))


@router.patch("/station", response_model=ApiResponse[StationAdminProfileData])
def update_station_details(
    request: Request,
    body: UpdateStationDetailsRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminProfileData]:
    _require_station_admin(principal)
    use_case: UpdateStationDetailsUseCase = request.app.state.container.update_station_details_use_case
    profile_data = use_case.execute(principal, UpdateStationDetailsCommand(**body.model_dump()))
    return ApiResponse(data=StationAdminProfileData(**profile_data.__dict__), meta=_meta(request))


@router.post("/officers/{officer_id}/activate", response_model=ApiResponse[StationAdminOfficerMutationData])
def activate_officer(request: Request, officer_id: str, principal: AuthPrincipal = Depends(get_current_principal)) -> ApiResponse[StationAdminOfficerMutationData]:
    _require_station_admin(principal)
    use_case: ChangeStationOfficerStatusUseCase = request.app.state.container.change_station_officer_status_use_case
    try:
        result = use_case.execute(principal, officer_id, "active")
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Officer not found") from exc
    return ApiResponse(data=_map_officer_mutation(result), meta=_meta(request))


@router.post("/officers/{officer_id}/deactivate", response_model=ApiResponse[StationAdminOfficerMutationData])
def deactivate_officer(request: Request, officer_id: str, principal: AuthPrincipal = Depends(get_current_principal)) -> ApiResponse[StationAdminOfficerMutationData]:
    _require_station_admin(principal)
    use_case: ChangeStationOfficerStatusUseCase = request.app.state.container.change_station_officer_status_use_case
    try:
        result = use_case.execute(principal, officer_id, "inactive")
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Officer not found") from exc
    return ApiResponse(data=_map_officer_mutation(result), meta=_meta(request))


@router.post("/officers/{officer_id}/reset-password", response_model=ApiResponse[ActionMessageData])
def reset_officer_password(
    request: Request,
    officer_id: str,
    body: ResetOfficerPasswordRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    _require_station_admin(principal)
    use_case: ResetStationOfficerPasswordUseCase = request.app.state.container.reset_station_officer_password_use_case
    try:
        use_case.execute(principal, officer_id, body.new_password)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Officer not found") from exc
    return ApiResponse(data=ActionMessageData(message="Password reset successfully"), meta=_meta(request))


@router.get("/investigations", response_model=ApiResponse[InvestigationReportsData])
def list_station_investigations(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
    officer: str | None = Query(default=None),
    district: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    registration_number: str | None = Query(default=None),
    owner_name: str | None = Query(default=None),
    verification_status: str | None = Query(default=None),
    investigation_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: InvestigationSortBy = Query(default=InvestigationSortBy.SCANNED_AT),
    sort_desc: bool = Query(default=True),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[InvestigationReportsData]:
    _require_station_admin(principal)
    context = request.app.state.container.station_admin_context
    station_id, _ = context.station_and_officer(principal)
    use_case: QueryInvestigationReportsUseCase = request.app.state.container.query_investigation_reports_use_case
    result = use_case.execute(InvestigationReportsFilters(from_date=from_date, to_date=to_date, search=search, station_id=station_id, officer=officer, district=district, risk_level=risk_level, vehicle_type=vehicle_type, registration_number=registration_number, owner_name=owner_name, verification_status=verification_status, investigation_status=investigation_status, page=page, page_size=page_size, sort_by=sort_by, sort_desc=sort_desc))
    return ApiResponse(data=_investigation_response(result), meta=_meta(request))


@router.get("/reports", response_model=ApiResponse[InvestigationReportsData])
def list_station_reports(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
    officer: str | None = Query(default=None),
    district: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    vehicle_brand: str | None = Query(default=None),
    registration_number: str | None = Query(default=None),
    owner_name: str | None = Query(default=None),
    verification_status: str | None = Query(default=None),
    investigation_status: str | None = Query(default=None),
    ai_confidence_min: float | None = Query(default=None, ge=0.0, le=1.0),
    ai_confidence_max: float | None = Query(default=None, ge=0.0, le=1.0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: InvestigationSortBy = Query(default=InvestigationSortBy.SCANNED_AT),
    sort_desc: bool = Query(default=True),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[InvestigationReportsData]:
    _require_station_admin(principal)
    context = request.app.state.container.station_admin_context
    station_id, _ = context.station_and_officer(principal)
    use_case: QueryInvestigationReportsUseCase = request.app.state.container.query_investigation_reports_use_case
    result = use_case.execute(InvestigationReportsFilters(from_date=from_date, to_date=to_date, search=search, station_id=station_id, officer=officer, district=district, risk_level=risk_level, vehicle_type=vehicle_type, vehicle_brand=vehicle_brand, registration_number=registration_number, owner_name=owner_name, verification_status=verification_status, investigation_status=investigation_status, ai_confidence_min=ai_confidence_min, ai_confidence_max=ai_confidence_max, page=page, page_size=page_size, sort_by=sort_by, sort_desc=sort_desc))
    return ApiResponse(data=_investigation_response(result), meta=_meta(request))


@router.get("/reports/export/{export_format}")
def export_station_reports(
    request: Request,
    export_format: ExportFormat,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
    officer: str | None = Query(default=None),
    district: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    vehicle_brand: str | None = Query(default=None),
    registration_number: str | None = Query(default=None),
    owner_name: str | None = Query(default=None),
    verification_status: str | None = Query(default=None),
    investigation_status: str | None = Query(default=None),
    ai_confidence_min: float | None = Query(default=None, ge=0.0, le=1.0),
    ai_confidence_max: float | None = Query(default=None, ge=0.0, le=1.0),
    sort_by: InvestigationSortBy = Query(default=InvestigationSortBy.SCANNED_AT),
    sort_desc: bool = Query(default=True),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> Response:
    _require_station_admin(principal)
    context = request.app.state.container.station_admin_context
    station_id, officer_profile = context.station_and_officer(principal)
    use_case: ExportInvestigationReportsUseCase = request.app.state.container.export_investigation_reports_use_case
    result = use_case.execute(
        filters=InvestigationReportsFilters(from_date=from_date, to_date=to_date, search=search, station_id=station_id, police_station=officer_profile.station_name, officer=officer, district=district, risk_level=risk_level, vehicle_type=vehicle_type, vehicle_brand=vehicle_brand, registration_number=registration_number, owner_name=owner_name, verification_status=verification_status, investigation_status=investigation_status, ai_confidence_min=ai_confidence_min, ai_confidence_max=ai_confidence_max, page=1, page_size=10000, sort_by=sort_by, sort_desc=sort_desc),
        export_format=export_format,
    )
    return Response(content=result.content, media_type=result.content_type, headers={"Content-Disposition": f'attachment; filename="{result.filename}"'})


@router.get("/analytics", response_model=ApiResponse[StationAdminAnalyticsData])
def analytics(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminAnalyticsData]:
    _require_station_admin(principal)
    use_case: GetStationAnalyticsUseCase = request.app.state.container.get_station_analytics_use_case
    result = use_case.execute(principal, from_date, to_date)
    return ApiResponse(data=StationAdminAnalyticsData(
        daily_labels=list(result.daily_labels),
        daily_investigations=list(result.daily_investigations),
        weekly_labels=list(result.weekly_labels),
        weekly_trend=list(result.weekly_trend),
        monthly_labels=list(result.monthly_labels),
        monthly_trend=list(result.monthly_trend),
        risk_distribution_labels=list(result.risk_distribution_labels),
        risk_distribution_values=list(result.risk_distribution_values),
        vehicle_type_labels=list(result.vehicle_type_labels),
        vehicle_type_values=list(result.vehicle_type_values),
        vehicle_brand_labels=list(result.vehicle_brand_labels),
        vehicle_brand_values=list(result.vehicle_brand_values),
        officer_performance_labels=list(result.officer_performance_labels),
        officer_performance_values=list(result.officer_performance_values),
        average_investigation_time_minutes=result.average_investigation_time_minutes,
        average_ai_confidence=result.average_ai_confidence,
        average_risk_score=result.average_risk_score,
    ), meta=_meta(request))


@router.get("/notifications", response_model=ApiResponse[StationAdminNotificationsData])
def notifications(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminNotificationsData]:
    _require_station_admin(principal)
    use_case: GetStationNotificationsUseCase = request.app.state.container.get_station_notifications_use_case
    items = use_case.execute(principal, limit)
    return ApiResponse(data=StationAdminNotificationsData(items=[StationAdminNotificationData(**item.__dict__) for item in items]), meta=_meta(request))


@router.get("/profile", response_model=ApiResponse[StationAdminProfileData])
def profile(request: Request, principal: AuthPrincipal = Depends(get_current_principal)) -> ApiResponse[StationAdminProfileData]:
    _require_station_admin(principal)
    use_case: GetStationAdminProfileUseCase = request.app.state.container.get_station_admin_profile_use_case
    profile_data = use_case.execute(principal)
    return ApiResponse(data=StationAdminProfileData(**profile_data.__dict__), meta=_meta(request))


@router.patch("/profile", response_model=ApiResponse[StationAdminProfileData])
def update_profile(
    request: Request,
    body: UpdateOwnProfileRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[StationAdminProfileData]:
    _require_station_admin(principal)
    use_case: UpdateStationAdminProfileUseCase = request.app.state.container.update_station_admin_profile_use_case
    try:
        profile_data = use_case.execute(principal, UpdateOwnProfileCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=StationAdminProfileData(**profile_data.__dict__), meta=_meta(request))


@router.post("/profile/change-password", response_model=ApiResponse[ActionMessageData])
def change_password(
    request: Request,
    body: ChangeOwnPasswordRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    _require_station_admin(principal)
    use_case: ChangeStationAdminPasswordUseCase = request.app.state.container.change_station_admin_password_use_case
    try:
        use_case.execute(principal, ChangeOwnPasswordCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=ActionMessageData(message="Password changed successfully"), meta=_meta(request))
