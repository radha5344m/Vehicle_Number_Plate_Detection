"""Dashboard routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.use_cases.dashboard.export_executive_dashboard_use_case import (
    ExportExecutiveDashboardUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_executive_dashboard_use_case import (
    GetExecutiveDashboardUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_dashboard_summary_use_case import (
    GetDashboardSummaryUseCase,
)
from sentinel_anpr.application.use_cases.dashboard.get_recent_activity_use_case import (
    GetRecentActivityUseCase,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.dashboard.activity_response import (
    RecentActivityData,
    RecentActivityItemData,
)
from sentinel_anpr.interfaces.schemas.responses.dashboard.summary_response import (
    DashboardSummaryData,
)
from sentinel_anpr.interfaces.schemas.responses.dashboard.executive_dashboard_response import (
    ActivityFeedItemData,
    ChartPointData,
    ExecutiveConnectionStatusData,
    ExecutiveDashboardData,
    ExecutiveInsightData,
    LeaderboardItemData,
    MetricCardData,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=ApiResponse[DashboardSummaryData])
def dashboard_summary(
    request: Request,
    principal: AuthPrincipal = Depends(require_permission("dashboard")),
) -> ApiResponse[DashboardSummaryData]:
    """Operational dashboard KPIs."""
    use_case: GetDashboardSummaryUseCase = (
        request.app.state.container.get_dashboard_summary_use_case
    )
    result = use_case.execute(
        station_id=principal.station_id if principal.role == "STATION_ADMIN" else None,
        officer_id=principal.officer_id if principal.role == "POLICE_OFFICER" else None,
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=DashboardSummaryData(
            total_scans=result.total_scans,
            verified_vehicles=result.verified_vehicles,
            suspicious_vehicles=result.suspicious_vehicles,
            pending_verification=result.pending_verification,
            last_updated_at=result.last_updated_at,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/recent-activity", response_model=ApiResponse[RecentActivityData])
def recent_activity(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
    principal: AuthPrincipal = Depends(require_permission("dashboard")),
) -> ApiResponse[RecentActivityData]:
    """Recent scan and verification activity."""
    use_case: GetRecentActivityUseCase = request.app.state.container.get_recent_activity_use_case
    result = use_case.execute(
        limit=limit,
        station_id=principal.station_id if principal.role == "STATION_ADMIN" else None,
        officer_id=principal.officer_id if principal.role == "POLICE_OFFICER" else None,
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=RecentActivityData(
            items=[
                RecentActivityItemData(
                    id=item.id,
                    plate_text=item.plate_text,
                    activity_type=item.activity_type,
                    description=item.description,
                    status=item.status,
                    occurred_at=item.occurred_at,
                )
                for item in result.items
            ]
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/executive", response_model=ApiResponse[ExecutiveDashboardData])
def executive_dashboard(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    district: str | None = Query(default=None),
    station: str | None = Query(default=None),
    officer: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    principal: AuthPrincipal = Depends(require_permission("dashboard")),
) -> ApiResponse[ExecutiveDashboardData]:
    """Executive command center analytics."""
    use_case: GetExecutiveDashboardUseCase = (
        request.app.state.container.get_executive_dashboard_use_case
    )
    try:
        result = use_case.execute(
            from_date=from_date,
            to_date=to_date,
            district=district,
            station=station,
            officer=officer,
            vehicle_type=vehicle_type,
            risk_level=risk_level,
            brand=brand,
            station_id=principal.station_id if principal.role == "STATION_ADMIN" else None,
            officer_id=principal.officer_id if principal.role == "POLICE_OFFICER" else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=ExecutiveDashboardData(
            scope_label=result.scope_label,
            kpis=[MetricCardData(**item.__dict__) for item in result.kpis],
            daily_trend=[ChartPointData(**item.__dict__) for item in result.daily_trend],
            weekly_trend=[ChartPointData(**item.__dict__) for item in result.weekly_trend],
            monthly_trend=[ChartPointData(**item.__dict__) for item in result.monthly_trend],
            hourly_activity=[ChartPointData(**item.__dict__) for item in result.hourly_activity],
            investigation_status_distribution=[
                ChartPointData(**item.__dict__) for item in result.investigation_status_distribution
            ],
            risk_distribution=[ChartPointData(**item.__dict__) for item in result.risk_distribution],
            risk_trend=[ChartPointData(**item.__dict__) for item in result.risk_trend],
            top_high_risk_registrations=[
                ChartPointData(**item.__dict__) for item in result.top_high_risk_registrations
            ],
            frequent_suspicious_vehicles=[
                ChartPointData(**item.__dict__) for item in result.frequent_suspicious_vehicles
            ],
            vehicle_type_distribution=[
                ChartPointData(**item.__dict__) for item in result.vehicle_type_distribution
            ],
            vehicle_brand_distribution=[
                ChartPointData(**item.__dict__) for item in result.vehicle_brand_distribution
            ],
            vehicle_color_distribution=[
                ChartPointData(**item.__dict__) for item in result.vehicle_color_distribution
            ],
            registration_state_distribution=[
                ChartPointData(**item.__dict__) for item in result.registration_state_distribution
            ],
            common_vehicle_models=[
                ChartPointData(**item.__dict__) for item in result.common_vehicle_models
            ],
            top_performing_officers=[
                LeaderboardItemData(**item.__dict__) for item in result.top_performing_officers
            ],
            most_active_officers=[
                LeaderboardItemData(**item.__dict__) for item in result.most_active_officers
            ],
            officer_leaderboard=[
                LeaderboardItemData(**item.__dict__) for item in result.officer_leaderboard
            ],
            top_performing_stations=[
                LeaderboardItemData(**item.__dict__) for item in result.top_performing_stations
            ],
            recent_investigations=[
                ActivityFeedItemData(**item.__dict__) for item in result.recent_investigations
            ],
            recent_high_risk_alerts=[
                ActivityFeedItemData(**item.__dict__) for item in result.recent_high_risk_alerts
            ],
            recent_officer_activity=[
                ActivityFeedItemData(**item.__dict__) for item in result.recent_officer_activity
            ],
            recent_reports_generated=[
                ActivityFeedItemData(**item.__dict__) for item in result.recent_reports_generated
            ],
            ai_metrics=[MetricCardData(**item.__dict__) for item in result.ai_metrics],
            insights=[ExecutiveInsightData(**item.__dict__) for item in result.insights],
            connection_status=ExecutiveConnectionStatusData(**result.connection_status.__dict__),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/executive/export/{export_format}")
def export_executive_dashboard(
    request: Request,
    export_format: str,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    district: str | None = Query(default=None),
    station: str | None = Query(default=None),
    officer: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    principal: AuthPrincipal = Depends(require_permission("dashboard")),
) -> Response:
    """Export executive command center data."""
    use_case: ExportExecutiveDashboardUseCase = (
        request.app.state.container.export_executive_dashboard_use_case
    )
    normalized_format = export_format.strip().lower()
    try:
        result = use_case.execute(
            export_format=normalized_format,
            from_date=from_date,
            to_date=to_date,
            district=district,
            station=station,
            officer=officer,
            vehicle_type=vehicle_type,
            risk_level=risk_level,
            brand=brand,
            station_id=principal.station_id if principal.role == "STATION_ADMIN" else None,
            officer_id=principal.officer_id if principal.role == "POLICE_OFFICER" else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
