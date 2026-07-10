"""User management use cases."""

from __future__ import annotations

import uuid

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.user_management_dto import (
    CreateUserCommand,
    QueryUsersResult,
    ResetUserPasswordCommand,
    UpdateUserCommand,
    UserFilters,
    UserMutationResult,
    UserStatusChangeCommand,
)
from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.application.ports.outbound.user_identity_sequence_port import UserIdentitySequencePort
from sentinel_anpr.application.ports.outbound.user_management_repository_port import (
    UserManagementRepositoryPort,
)
from sentinel_anpr.application.services.temporary_password_service import generate_temporary_password
from sentinel_anpr.application.services.user_identity_service import default_username_for_employee_id
from sentinel_anpr.domain.authentication.user_management_errors import (
    SuperAdminRequiredError,
)

_ALLOWED_ROLES = {"SUPER_ADMIN", "STATION_ADMIN", "POLICE_OFFICER"}
_ALLOWED_CREATE_ROLES = {"SUPER_ADMIN", "STATION_ADMIN", "POLICE_OFFICER"}
_ALLOWED_STATUSES = {"active", "inactive", "suspended"}
_HEADQUARTERS = "Headquarters"


def ensure_super_admin(principal: AuthPrincipal) -> None:
    if "super_admin" not in {role.lower() for role in principal.roles}:
        raise SuperAdminRequiredError()


class QueryUsersUseCase:
    def __init__(self, repository: UserManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, filters: UserFilters) -> QueryUsersResult:
        ensure_super_admin(principal)
        if filters.created_from and filters.created_to and filters.created_from > filters.created_to:
            raise ValueError("created_from must be before created_to")
        return self._repository.query_users(filters)


class CreateUserUseCase:
    def __init__(
        self,
        repository: UserManagementRepositoryPort,
        password_hasher: PasswordHasherPort,
        identity_sequences: UserIdentitySequencePort,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._identity_sequences = identity_sequences

    def execute(self, principal: AuthPrincipal, command: CreateUserCommand) -> UserMutationResult:
        ensure_super_admin(principal)
        role = command.role.upper()
        if role not in _ALLOWED_CREATE_ROLES:
            raise ValueError("Invalid role")
        status = command.status.lower()
        if status not in _ALLOWED_STATUSES:
            raise ValueError("Invalid status")
        user_id = self._identity_sequences.next_user_id()
        employee_id = self._identity_sequences.next_employee_id(role)
        username = (
            command.username.strip().lower()
            if command.username and command.username.strip()
            else default_username_for_employee_id(employee_id)
        )
        self._validate_unique(username, command.email, employee_id)
        normalized_station = self._normalize_station(role, command.police_station)
        temporary_password = generate_temporary_password(employee_id)
        password_hash = self._password_hasher.hash(temporary_password)
        normalized_badge = self._normalize_badge(role, command.badge_number, employee_id)
        normalized_rank = self._normalize_rank(role, command.rank)
        normalized = CreateUserCommand(
            user_id=user_id,
            employee_id=employee_id,
            first_name=command.first_name.strip(),
            last_name=command.last_name.strip(),
            username=username,
            email=command.email.strip().lower(),
            phone_number=command.phone_number.strip() if command.phone_number else None,
            badge_number=normalized_badge,
            rank=normalized_rank,
            role=role,
            police_station=normalized_station,
            district=command.district.strip() if command.district else None,
            status=status,
        )
        return self._repository.create_user(
            normalized,
            password_hash,
            temporary_password=temporary_password,
            password_change_required=True,
        )

    def _validate_unique(self, username: str, email: str, employee_id: str) -> None:
        if self._repository.username_exists(username.strip().lower()):
            raise ValueError("Username already exists")
        if self._repository.email_exists(email.strip().lower()):
            raise ValueError("Email already exists")
        if self._repository.employee_id_exists(employee_id.strip().upper()):
            raise ValueError("Employee ID already exists")

    @staticmethod
    def _normalize_station(role: str, police_station: str | None) -> str:
        if role == "SUPER_ADMIN":
            return police_station.strip() if police_station and police_station.strip() else _HEADQUARTERS
        if not police_station or not police_station.strip():
            raise ValueError("Station is required for STATION_ADMIN and POLICE_OFFICER")
        return police_station.strip()

    @staticmethod
    def _normalize_badge(role: str, badge_number: str | None, employee_id: str) -> str:
        if badge_number and badge_number.strip():
            return badge_number.strip().upper()
        if role == "SUPER_ADMIN":
            return employee_id.strip().upper()
        return employee_id.strip().upper()

    @staticmethod
    def _normalize_rank(role: str, rank: str | None) -> str:
        if rank and rank.strip():
            return rank.strip()
        if role == "SUPER_ADMIN":
            return "Super Admin"
        raise ValueError("Rank is required for STATION_ADMIN and POLICE_OFFICER")


class UpdateUserUseCase:
    def __init__(self, repository: UserManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, command: UpdateUserCommand) -> UserMutationResult:
        ensure_super_admin(principal)
        if command.role and command.role.upper() not in _ALLOWED_ROLES:
            raise ValueError("Invalid role")
        if command.status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Invalid status")
        if self._repository.email_exists(command.email.strip().lower(), command.officer_id):
            raise ValueError("Email already exists")
        if self._repository.employee_id_exists(command.employee_id.strip(), command.officer_id):
            raise ValueError("Employee ID already exists")
        normalized_role = command.role.upper() if command.role else None
        normalized = UpdateUserCommand(
            officer_id=command.officer_id,
            employee_id=command.employee_id.strip(),
            first_name=command.first_name.strip(),
            last_name=command.last_name.strip(),
            email=command.email.strip().lower(),
            phone_number=command.phone_number.strip() if command.phone_number else None,
            rank=command.rank.strip(),
            role=normalized_role,
            police_station=CreateUserUseCase._normalize_station(normalized_role or "POLICE_OFFICER", command.police_station),
            district=command.district.strip() if command.district else None,
            status=command.status.lower(),
        )
        return self._repository.update_user(normalized)


class ChangeUserStatusUseCase:
    def __init__(self, repository: UserManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(
        self,
        principal: AuthPrincipal,
        command: UserStatusChangeCommand,
    ) -> UserMutationResult:
        ensure_super_admin(principal)
        if command.status.lower() not in {"active", "inactive"}:
            raise ValueError("Status must be active or inactive")
        return self._repository.change_user_status(
            UserStatusChangeCommand(officer_id=command.officer_id, status=command.status.lower())
        )


class ResetUserPasswordUseCase:
    def __init__(
        self,
        repository: UserManagementRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    def execute(self, principal: AuthPrincipal, command: ResetUserPasswordCommand) -> UserMutationResult:
        ensure_super_admin(principal)
        generated = command.new_password is None
        user = self._repository.get_user(command.officer_id)
        if user is None:
            raise LookupError("User not found")
        temporary_password = command.new_password or generate_temporary_password(user.employee_id)
        password_hash = self._password_hasher.hash(temporary_password)
        self._repository.reset_password(
            ResetUserPasswordCommand(officer_id=command.officer_id, new_password=temporary_password),
            password_hash,
            password_change_required=generated,
        )
        user = self._repository.get_user(command.officer_id)
        if user is None:
            raise LookupError("User not found")
        return UserMutationResult(
            user=user,
            temporary_password=temporary_password if generated else None,
            password_change_required=generated,
        )


class SoftDeleteUserUseCase:
    def __init__(self, repository: UserManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, officer_id: str) -> None:
        ensure_super_admin(principal)
        self._repository.soft_delete_user(officer_id)
