"""Police officer portal routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.investigation_reports_dto import (
    ExportFormat,
    InvestigationReportsFilters,
    InvestigationSortBy,
)
from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.police_officer_portal_dto import ChangeOwnPasswordCommand
from sentinel_anpr.application.use_cases.authentication.police_officer_portal_use_cases import (
    ChangePoliceOfficerPasswordUseCase,
    GetPoliceOfficerDashboardUseCase,
    GetPoliceOfficerNotificationsUseCase,
    GetPoliceOfficerProfileUseCase,
    UpdatePoliceOfficerProfileUseCase,
    ensure_police_officer,
)
from sentinel_anpr.application.use_cases.reporting.export_investigation_reports_use_case import (
    ExportInvestigationReportsUseCase,
)
from sentinel_anpr.application.use_cases.reporting.query_investigation_reports_use_case import (
    QueryInvestigationReportsUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.schemas.requests.profile.update_own_profile_request import (
    UpdateOwnProfileRequest,
)
from sentinel_anpr.interfaces.schemas.requests.station_admin.station_admin_request import (
    ChangeOwnPasswordRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.police_officer.police_officer_response import (
    ActionMessageData,
    PoliceOfficerDashboardData,
    PoliceOfficerNotificationData,
    PoliceOfficerNotificationsData,
    PoliceOfficerProfileData,
    PoliceOfficerRecentActivityData,
    PoliceOfficerRecentInvestigationData,
    PoliceOfficerSummaryData,
)
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

router = APIRouter(prefix="/police-officer", tags=["police-officer"])


def _meta(request: Request) -> ResponseMeta:
    return ResponseMeta(correlation_id=getattr(request.state, "correlation_id", None))


def _require_police_officer(principal: AuthPrincipal) -> None:
    try:
        ensure_police_officer(principal)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


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
        risk_distribution=[
            DistributionItemData(label=item.label, value=item.value)
            for item in result.analytics.risk_distribution
        ],
        vehicle_type_distribution=[
            DistributionItemData(label=item.label, value=item.value)
            for item in result.analytics.vehicle_type_distribution
        ],
        brand_distribution=[
            DistributionItemData(label=item.label, value=item.value)
            for item in result.analytics.brand_distribution
        ],
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
        verification_status_distribution=[
            DistributionItemData(label=item.label, value=item.value)
            for item in result.analytics.verification_status_distribution
        ],
        daily_investigation_trend=[
            DailyInvestigationTrendPointData(
                date=item.date,
                investigations=item.investigations,
            )
            for item in result.analytics.daily_investigation_trend
        ],
        weekly_investigation_trend=[
            PeriodInvestigationTrendPointData(period=item.period, investigations=item.investigations)
            for item in result.analytics.weekly_investigation_trend
        ],
        monthly_investigation_trend=[
            PeriodInvestigationTrendPointData(period=item.period, investigations=item.investigations)
            for item in result.analytics.monthly_investigation_trend
        ],
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


@router.get("/dashboard", response_model=ApiResponse[PoliceOfficerDashboardData])
def dashboard(
    request: Request,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[PoliceOfficerDashboardData]:
    _require_police_officer(principal)
    use_case: GetPoliceOfficerDashboardUseCase = (
        request.app.state.container.get_police_officer_dashboard_use_case
    )
    result = use_case.execute(principal)
    return ApiResponse(
        data=PoliceOfficerDashboardData(
            summary=PoliceOfficerSummaryData(**result.summary.__dict__),
            recent_investigations=[
                PoliceOfficerRecentInvestigationData(**item.__dict__)
                for item in result.recent_investigations
            ],
            recent_activity=[
                PoliceOfficerRecentActivityData(**item.__dict__)
                for item in result.recent_activity
            ],
        ),
        meta=_meta(request),
    )


@router.get("/investigations", response_model=ApiResponse[InvestigationReportsData])
def investigations(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
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
    _require_police_officer(principal)
    use_case: QueryInvestigationReportsUseCase = (
        request.app.state.container.query_investigation_reports_use_case
    )
    result = use_case.execute(
        InvestigationReportsFilters(
            from_date=from_date,
            to_date=to_date,
            search=search,
            officer_id=principal.officer_id,
            risk_level=risk_level,
            vehicle_type=vehicle_type,
            registration_number=registration_number,
            owner_name=owner_name,
            verification_status=verification_status,
            investigation_status=investigation_status,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
    )
    return ApiResponse(data=_investigation_response(result), meta=_meta(request))


@router.get("/reports", response_model=ApiResponse[InvestigationReportsData])
def reports(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
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
    _require_police_officer(principal)
    use_case: QueryInvestigationReportsUseCase = (
        request.app.state.container.query_investigation_reports_use_case
    )
    result = use_case.execute(
        InvestigationReportsFilters(
            from_date=from_date,
            to_date=to_date,
            search=search,
            officer_id=principal.officer_id,
            risk_level=risk_level,
            vehicle_type=vehicle_type,
            vehicle_brand=vehicle_brand,
            registration_number=registration_number,
            owner_name=owner_name,
            verification_status=verification_status,
            investigation_status=investigation_status,
            ai_confidence_min=ai_confidence_min,
            ai_confidence_max=ai_confidence_max,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
    )
    return ApiResponse(data=_investigation_response(result), meta=_meta(request))


@router.get("/reports/export/{export_format}")
def export_reports(
    request: Request,
    export_format: ExportFormat,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    search: str | None = Query(default=None),
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
    _require_police_officer(principal)
    use_case: ExportInvestigationReportsUseCase = (
        request.app.state.container.export_investigation_reports_use_case
    )
    result = use_case.execute(
        filters=InvestigationReportsFilters(
            from_date=from_date,
            to_date=to_date,
            search=search,
            officer_id=principal.officer_id,
            officer=principal.badge_number,
            risk_level=risk_level,
            vehicle_type=vehicle_type,
            vehicle_brand=vehicle_brand,
            registration_number=registration_number,
            owner_name=owner_name,
            verification_status=verification_status,
            investigation_status=investigation_status,
            ai_confidence_min=ai_confidence_min,
            ai_confidence_max=ai_confidence_max,
            page=1,
            page_size=10000,
            sort_by=sort_by,
            sort_desc=sort_desc,
        ),
        export_format=export_format,
    )
    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("/notifications", response_model=ApiResponse[PoliceOfficerNotificationsData])
def notifications(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[PoliceOfficerNotificationsData]:
    _require_police_officer(principal)
    use_case: GetPoliceOfficerNotificationsUseCase = (
        request.app.state.container.get_police_officer_notifications_use_case
    )
    items = use_case.execute(principal, limit)
    return ApiResponse(
        data=PoliceOfficerNotificationsData(
            items=[PoliceOfficerNotificationData(**item.__dict__) for item in items]
        ),
        meta=_meta(request),
    )


@router.get("/profile", response_model=ApiResponse[PoliceOfficerProfileData])
def profile(
    request: Request,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[PoliceOfficerProfileData]:
    _require_police_officer(principal)
    use_case: GetPoliceOfficerProfileUseCase = (
        request.app.state.container.get_police_officer_profile_use_case
    )
    result = use_case.execute(principal)
    return ApiResponse(data=PoliceOfficerProfileData(**result.__dict__), meta=_meta(request))


@router.patch("/profile", response_model=ApiResponse[PoliceOfficerProfileData])
def update_profile(
    request: Request,
    body: UpdateOwnProfileRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[PoliceOfficerProfileData]:
    _require_police_officer(principal)
    use_case: UpdatePoliceOfficerProfileUseCase = (
        request.app.state.container.update_police_officer_profile_use_case
    )
    try:
        result = use_case.execute(principal, UpdateOwnProfileCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=PoliceOfficerProfileData(**result.__dict__), meta=_meta(request))


@router.post("/profile/change-password", response_model=ApiResponse[ActionMessageData])
def change_password(
    request: Request,
    body: ChangeOwnPasswordRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    _require_police_officer(principal)
    use_case: ChangePoliceOfficerPasswordUseCase = (
        request.app.state.container.change_police_officer_password_use_case
    )
    try:
        use_case.execute(principal, ChangeOwnPasswordCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(
        data=ActionMessageData(message="Password changed successfully"),
        meta=_meta(request),
    )
