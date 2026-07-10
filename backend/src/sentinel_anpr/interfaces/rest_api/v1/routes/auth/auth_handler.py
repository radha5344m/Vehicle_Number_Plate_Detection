"""Authentication routes."""

from fastapi import APIRouter, Depends, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal, LoginCommand, LogoutCommand
from sentinel_anpr.application.dto.auth_dto import OfficerIdentity
from sentinel_anpr.application.services.auth_permissions import primary_role_for_roles
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)
from sentinel_anpr.application.use_cases.authentication.login_use_case import LoginUseCase
from sentinel_anpr.application.use_cases.authentication.logout_use_case import LogoutUseCase
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.schemas.requests.auth.login_request import LoginRequest
from sentinel_anpr.interfaces.schemas.requests.auth.logout_request import LogoutRequest
from sentinel_anpr.interfaces.schemas.responses.auth.auth_response import (
    LoginResponseData,
    LogoutResponseData,
    MeResponseData,
    OfficerSummaryData,
    StationSummaryData,
    TokenData,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta

router = APIRouter(prefix="/auth", tags=["auth"])


def _officer_summary(officer: OfficerIdentity) -> OfficerSummaryData:
    return OfficerSummaryData(
        officer_id=officer.officer_id,
        user_id=officer.user_id,
        employee_id=officer.employee_id,
        badge_number=officer.badge_number,
        username=officer.username,
        email=officer.email,
        phone_number=officer.phone_number,
        first_name=officer.first_name,
        last_name=officer.last_name,
        rank=officer.rank,
        station_id=officer.station_id,
        station_code=officer.station_code,
        station_name=officer.station_name,
        district=officer.district,
        roles=list(officer.roles),
    )


def _station_summary(officer: OfficerIdentity) -> StationSummaryData:
    return StationSummaryData(
        station_id=officer.station_id,
        station_code=officer.station_code,
        station_name=officer.station_name,
    )


@router.post("/login", response_model=ApiResponse[LoginResponseData])
def login(request: Request, body: LoginRequest) -> ApiResponse[LoginResponseData]:
    """Authenticate officer and issue JWT tokens."""
    use_case: LoginUseCase = request.app.state.container.login_use_case
    result = use_case.execute(
        LoginCommand(
            identifier=body.identifier,
            password=body.password,
            station_code=body.station_code,
        )
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    officer = _officer_summary(result.officer)
    return ApiResponse(
        data=LoginResponseData(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
            expires_in=result.expires_in,
            officer=officer,
            user=officer,
            role=result.role,
            permissions=list(result.permissions),
            station=_station_summary(result.officer),
            token=TokenData(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type=result.token_type,
                expires_in=result.expires_in,
            ),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/logout", response_model=ApiResponse[LogoutResponseData])
def logout(
    request: Request,
    body: LogoutRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[LogoutResponseData]:
    """Revoke refresh token and end session."""
    use_case: LogoutUseCase = request.app.state.container.logout_use_case
    use_case.execute(
        LogoutCommand(refresh_token=body.refresh_token, principal=principal)
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=LogoutResponseData(message="Logged out successfully"),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.get("/me", response_model=ApiResponse[MeResponseData])
def me(
    request: Request,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[MeResponseData]:
    """Return current authenticated officer profile."""
    use_case: GetCurrentOfficerUseCase = request.app.state.container.get_current_officer_use_case
    result = use_case.execute(principal)
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=MeResponseData(
            officer=_officer_summary(result.officer),
            user=_officer_summary(result.officer),
            role=principal.role or primary_role_for_roles(result.officer.roles),
            permissions=list(result.permissions),
            station=_station_summary(result.officer),
            session_id=result.session_id,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
