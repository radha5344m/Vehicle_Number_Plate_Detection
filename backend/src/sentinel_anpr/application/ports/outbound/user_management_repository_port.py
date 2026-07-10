"""User management persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.user_management_dto import (
    CreateUserCommand,
    QueryUsersResult,
    ResetUserPasswordCommand,
    UpdateUserCommand,
    UserDetailDto,
    UserFilters,
    UserMutationResult,
    UserStatusChangeCommand,
)


class UserManagementRepositoryPort(Protocol):
    def query_users(self, filters: UserFilters) -> QueryUsersResult: ...

    def get_user(self, officer_id: str) -> UserDetailDto | None: ...

    def create_user(
        self,
        command: CreateUserCommand,
        password_hash: str,
        *,
        temporary_password: str | None = None,
        password_change_required: bool = False,
    ) -> UserMutationResult: ...

    def update_user(self, command: UpdateUserCommand) -> UserMutationResult: ...

    def change_user_status(self, command: UserStatusChangeCommand) -> UserMutationResult: ...

    def reset_password(
        self,
        command: ResetUserPasswordCommand,
        password_hash: str,
        *,
        password_change_required: bool = False,
    ) -> None: ...

    def soft_delete_user(self, officer_id: str) -> None: ...

    def username_exists(self, username: str, exclude_officer_id: str | None = None) -> bool: ...

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool: ...

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool: ...
