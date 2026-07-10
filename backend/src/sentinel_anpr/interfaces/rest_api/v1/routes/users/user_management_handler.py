"""User management routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.user_management_dto import (
    CreateUserCommand,
    ResetUserPasswordCommand,
    UpdateUserCommand,
    UserFilters,
    UserStatusChangeCommand,
)
from sentinel_anpr.application.use_cases.authentication.user_management_use_cases import (
    ChangeUserStatusUseCase,
    CreateUserUseCase,
    QueryUsersUseCase,
    ResetUserPasswordUseCase,
    SoftDeleteUserUseCase,
    UpdateUserUseCase,
)
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.schemas.requests.users.user_management_request import (
    CreateUserRequest,
    ResetPasswordRequest,
    UpdateUserRequest,
)
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.users.user_management_response import (
    ActionMessageData,
    UserItemData,
    UserMutationData,
    UserPaginationData,
    UsersListData,
    UsersSummaryData,
)

router = APIRouter(prefix="/users", tags=["users"])


def _map_user(item) -> UserItemData:  # noqa: ANN001
    return UserItemData(
        officer_id=item.officer_id,
        user_id=item.user_id,
        employee_id=item.employee_id,
        full_name=item.full_name,
        username=item.username,
        email=item.email,
        phone_number=item.phone_number,
        badge_number=item.badge_number,
        rank=item.rank,
        role=item.role,
        police_station=item.police_station,
        district=item.district,
        status=item.status,
        created_at=item.created_at,
        last_login_at=item.last_login_at,
    )


@router.get("", response_model=ApiResponse[UsersListData])
def list_users(
    request: Request,
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    station: str | None = Query(default=None),
    status: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_desc: bool = Query(default=True),
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UsersListData]:
    use_case: QueryUsersUseCase = request.app.state.container.query_users_use_case
    try:
        result = use_case.execute(
            principal,
            UserFilters(
                search=search,
                role=role,
                station=station,
                status=status,
                created_from=created_from,
                created_to=created_to,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UsersListData(
            items=[_map_user(item) for item in result.items],
            pagination=UserPaginationData(
                page=result.pagination.page,
                page_size=result.pagination.page_size,
                total_items=result.pagination.total_items,
                total_pages=result.pagination.total_pages,
            ),
            summary=UsersSummaryData(**result.summary.__dict__),
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("", response_model=ApiResponse[UserMutationData], status_code=201)
def create_user(
    request: Request,
    body: CreateUserRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UserMutationData]:
    use_case: CreateUserUseCase = request.app.state.container.create_user_use_case
    try:
        result = use_case.execute(
            principal,
            CreateUserCommand(
                first_name=body.first_name,
                last_name=body.last_name,
                username=body.username,
                email=body.email,
                phone_number=body.phone_number,
                badge_number=body.badge_number,
                rank=body.rank,
                role=body.role,
                police_station=body.police_station,
                district=body.district,
                status=body.status,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UserMutationData(
            user=_map_user(result.user),
            temporary_password=result.temporary_password,
            password_change_required=result.password_change_required,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.patch("/{officer_id}", response_model=ApiResponse[UserMutationData])
def update_user(
    request: Request,
    officer_id: str,
    body: UpdateUserRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UserMutationData]:
    use_case: UpdateUserUseCase = request.app.state.container.update_user_use_case
    try:
        result = use_case.execute(
            principal,
            UpdateUserCommand(
                officer_id=officer_id,
                employee_id=body.employee_id,
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.email,
                phone_number=body.phone_number,
                rank=body.rank,
                role=body.role,
                police_station=body.police_station,
                district=body.district,
                status=body.status,
            ),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UserMutationData(
            user=_map_user(result.user),
            temporary_password=result.temporary_password,
            password_change_required=result.password_change_required,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/{officer_id}/activate", response_model=ApiResponse[UserMutationData])
def activate_user(
    request: Request,
    officer_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UserMutationData]:
    use_case: ChangeUserStatusUseCase = request.app.state.container.change_user_status_use_case
    result = use_case.execute(principal, UserStatusChangeCommand(officer_id=officer_id, status="active"))
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UserMutationData(
            user=_map_user(result.user),
            temporary_password=result.temporary_password,
            password_change_required=result.password_change_required,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/{officer_id}/deactivate", response_model=ApiResponse[UserMutationData])
def deactivate_user(
    request: Request,
    officer_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UserMutationData]:
    use_case: ChangeUserStatusUseCase = request.app.state.container.change_user_status_use_case
    result = use_case.execute(principal, UserStatusChangeCommand(officer_id=officer_id, status="inactive"))
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UserMutationData(
            user=_map_user(result.user),
            temporary_password=result.temporary_password,
            password_change_required=result.password_change_required,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.post("/{officer_id}/reset-password", response_model=ApiResponse[UserMutationData])
def reset_password(
    request: Request,
    officer_id: str,
    body: ResetPasswordRequest | None = None,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[UserMutationData]:
    use_case: ResetUserPasswordUseCase = request.app.state.container.reset_user_password_use_case
    try:
        result = use_case.execute(
            principal,
            ResetUserPasswordCommand(
                officer_id=officer_id,
                new_password=body.new_password if body else None,
            ),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=UserMutationData(
            user=_map_user(result.user),
            temporary_password=result.temporary_password,
            password_change_required=result.password_change_required,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )


@router.delete("/{officer_id}", response_model=ApiResponse[ActionMessageData])
def soft_delete_user(
    request: Request,
    officer_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ActionMessageData]:
    use_case: SoftDeleteUserUseCase = request.app.state.container.soft_delete_user_use_case
    try:
        use_case.execute(principal, officer_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(data=ActionMessageData(message="User deleted successfully"), meta=ResponseMeta(correlation_id=correlation_id))
