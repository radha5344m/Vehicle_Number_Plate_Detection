"""Health check route."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from sentinel_anpr.application.use_cases.health.get_health_use_case import GetHealthUseCase
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.health_response import (
    HealthCheckData,
    HealthResponseData,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthResponseData])
def health_check(request: Request) -> JSONResponse:
    """Liveness and readiness probe."""
    use_case: GetHealthUseCase = request.app.state.container.get_health_use_case
    result = use_case.execute()
    correlation_id = getattr(request.state, "correlation_id", None)
    body = ApiResponse(
        data=HealthResponseData(
            status=result.status,
            version=result.version,
            environment=result.environment,
            database=result.database,
            ready=result.ready,
            checked_at=result.checked_at,
            checks=[
                HealthCheckData(
                    name=check.name,
                    status=check.status,
                    message=check.message,
                )
                for check in result.checks
            ],
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
    status_code = 200 if result.ready else 503
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))
