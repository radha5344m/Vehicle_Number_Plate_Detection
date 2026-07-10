"""Analytics routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.use_cases.analytics.get_analytics_overview_use_case import (
    GetAnalyticsOverviewUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.schemas.responses.analytics.analytics_response import (
    AnalyticsOverviewData,
    ChartSeriesData,
    SuspiciousVehicleItemData,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=ApiResponse[AnalyticsOverviewData])
def analytics_overview(
    request: Request,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    principal: AuthPrincipal = Depends(require_permission("analytics")),
) -> ApiResponse[AnalyticsOverviewData]:
    """Chart data aggregated from stored scan history."""
    use_case: GetAnalyticsOverviewUseCase = request.app.state.container.get_analytics_overview_use_case
    try:
        result = use_case.execute(
            from_date=from_date,
            to_date=to_date,
            station_id=principal.station_id if principal.role == "STATION_ADMIN" else None,
            officer_id=principal.officer_id if principal.role == "POLICE_OFFICER" else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=AnalyticsOverviewData(
            daily_scans=ChartSeriesData(
                labels=list(result.daily_scans.labels),
                values=list(result.daily_scans.values),
            ),
            risk_distribution=ChartSeriesData(
                labels=list(result.risk_distribution.labels),
                values=list(result.risk_distribution.values),
            ),
            vehicle_types=ChartSeriesData(
                labels=list(result.vehicle_types.labels),
                values=list(result.vehicle_types.values),
            ),
            suspicious_vehicles=[
                SuspiciousVehicleItemData(
                    plate_text=item.plate_text,
                    scan_count=item.scan_count,
                    max_risk_score=item.max_risk_score,
                    risk_level=item.risk_level,
                )
                for item in result.suspicious_vehicles
            ],
            officer_activity=ChartSeriesData(
                labels=list(result.officer_activity.labels),
                values=list(result.officer_activity.values),
            ),
            total_scans=result.total_scans,
            generated_at=result.generated_at,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
