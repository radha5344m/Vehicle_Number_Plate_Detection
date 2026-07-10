"""Station admin portal use cases."""

from datetime import datetime

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.station_admin_portal_dto import (
    ChangeOwnPasswordCommand,
    CreatePoliceOfficerCommand,
    StationAdminAnalyticsResult,
    StationAdminDashboardResult,
    StationAdminInvestigationFilters,
    StationAdminInvestigationQueryResult,
    StationAdminNotificationDto,
    StationAdminOfficerFilters,
    StationAdminOfficerMutationResult,
    StationAdminOfficerQueryResult,
    StationAdminProfileDto,
    StationAdminReportsResult,
    UpdatePoliceOfficerCommand,
    UpdateStationDetailsCommand,
)
from sentinel_anpr.application.ports.outbound.credential_store_port import CredentialStorePort
from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.application.ports.outbound.station_admin.station_admin_portal_repository_port import (
    StationAdminPortalRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.user_identity_sequence_port import UserIdentitySequencePort
from sentinel_anpr.application.services.temporary_password_service import generate_temporary_password
from sentinel_anpr.application.services.user_identity_service import default_username_for_employee_id
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import GetCurrentOfficerUseCase

_ALLOWED_STATUSES = {"active", "inactive"}


def ensure_station_admin(principal: AuthPrincipal) -> None:
    if "station_admin" not in {role.lower() for role in principal.roles}:
        raise PermissionError("Station admin access required")


class StationAdminPortalContext:
    def __init__(self, get_current_officer_use_case: GetCurrentOfficerUseCase) -> None:
        self._get_current_officer_use_case = get_current_officer_use_case

    def station_and_officer(self, principal: AuthPrincipal):
        ensure_station_admin(principal)
        officer = self._get_current_officer_use_case.execute(principal).officer
        return officer.station_id, officer


class GetStationAdminDashboardUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal) -> StationAdminDashboardResult:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.get_dashboard(station_id)


class QueryStationOfficersUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, filters: StationAdminOfficerFilters) -> StationAdminOfficerQueryResult:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.query_officers(station_id, filters)


class CreateStationOfficerUseCase:
    def __init__(
        self,
        repository: StationAdminPortalRepositoryPort,
        context: StationAdminPortalContext,
        password_hasher: PasswordHasherPort,
        identity_sequences: UserIdentitySequencePort,
    ) -> None:
        self._repository = repository
        self._context = context
        self._password_hasher = password_hasher
        self._identity_sequences = identity_sequences

    def execute(self, principal: AuthPrincipal, command: CreatePoliceOfficerCommand) -> StationAdminOfficerMutationResult:
        station_id, _ = self._context.station_and_officer(principal)
        status = command.status.lower()
        if status not in _ALLOWED_STATUSES:
            raise ValueError("Status must be active or inactive")
        user_id = self._identity_sequences.next_user_id()
        employee_id = self._identity_sequences.next_employee_id("POLICE_OFFICER")
        username = (
            command.username.strip().lower()
            if command.username and command.username.strip()
            else default_username_for_employee_id(employee_id)
        )
        if self._repository.username_exists(username):
            raise ValueError("Username already exists")
        if self._repository.email_exists(command.email.strip().lower()):
            raise ValueError("Email already exists")
        if self._repository.employee_id_exists(employee_id):
            raise ValueError("Employee ID already exists")
        temporary_password = generate_temporary_password(employee_id)
        password_hash = self._password_hasher.hash(temporary_password)
        badge_number = (
            command.badge_number.strip().upper()
            if command.badge_number and command.badge_number.strip()
            else employee_id
        )
        normalized = CreatePoliceOfficerCommand(
            user_id=user_id,
            employee_id=employee_id,
            first_name=command.first_name.strip(),
            last_name=command.last_name.strip(),
            username=username,
            email=command.email.strip().lower(),
            phone_number=command.phone_number.strip() if command.phone_number else None,
            badge_number=badge_number,
            rank=command.rank.strip(),
            status=status,
        )
        result = self._repository.create_officer(
            station_id,
            normalized,
            password_hash,
            password_change_required=True,
        )
        return StationAdminOfficerMutationResult(
            officer=result.officer,
            temporary_password=temporary_password,
            password_change_required=True,
        )


class UpdateStationOfficerUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: UpdatePoliceOfficerCommand) -> StationAdminOfficerMutationResult:
        station_id, _ = self._context.station_and_officer(principal)
        if command.status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Status must be active or inactive")
        if self._repository.email_exists(command.email.strip().lower(), command.officer_id):
            raise ValueError("Email already exists")
        return self._repository.update_officer(
            station_id,
            UpdatePoliceOfficerCommand(
                officer_id=command.officer_id,
                first_name=command.first_name.strip(),
                last_name=command.last_name.strip(),
                email=command.email.strip().lower(),
                phone_number=command.phone_number.strip() if command.phone_number else None,
                rank=command.rank.strip(),
                status=command.status.lower(),
            ),
        )


class ChangeStationOfficerStatusUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, officer_id: str, status: str) -> StationAdminOfficerMutationResult:
        station_id, _ = self._context.station_and_officer(principal)
        if status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Status must be active or inactive")
        return self._repository.change_officer_status(station_id, officer_id, status.lower())


class ResetStationOfficerPasswordUseCase:
    def __init__(
        self,
        repository: StationAdminPortalRepositoryPort,
        context: StationAdminPortalContext,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._repository = repository
        self._context = context
        self._password_hasher = password_hasher

    def execute(self, principal: AuthPrincipal, officer_id: str, new_password: str) -> None:
        station_id, _ = self._context.station_and_officer(principal)
        self._repository.reset_officer_password(station_id, officer_id, self._password_hasher.hash(new_password))


class SoftDeleteStationOfficerUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, officer_id: str) -> None:
        station_id, _ = self._context.station_and_officer(principal)
        self._repository.soft_delete_officer(station_id, officer_id)


class UpdateStationDetailsUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: UpdateStationDetailsCommand) -> StationAdminProfileDto:
        station_id, officer = self._context.station_and_officer(principal)
        self._repository.update_station_details(station_id, command)
        return self._repository.get_profile(station_id, officer.officer_id)


class QueryStationInvestigationsUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, filters: StationAdminInvestigationFilters) -> StationAdminInvestigationQueryResult:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.query_investigations(station_id, filters)


class QueryStationReportsUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, filters: StationAdminInvestigationFilters) -> StationAdminReportsResult:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.query_reports(station_id, filters)


class GetStationAnalyticsUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, from_date: datetime | None, to_date: datetime | None) -> StationAdminAnalyticsResult:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.get_analytics(station_id, from_date, to_date)


class GetStationNotificationsUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, limit: int = 20) -> tuple[StationAdminNotificationDto, ...]:
        station_id, _ = self._context.station_and_officer(principal)
        return self._repository.get_notifications(station_id, limit)


class GetStationAdminProfileUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal) -> StationAdminProfileDto:
        station_id, officer = self._context.station_and_officer(principal)
        return self._repository.get_profile(station_id, officer.officer_id)


class UpdateStationAdminProfileUseCase:
    def __init__(self, repository: StationAdminPortalRepositoryPort, context: StationAdminPortalContext) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: UpdateOwnProfileCommand) -> StationAdminProfileDto:
        station_id, officer = self._context.station_and_officer(principal)
        if self._repository.email_exists(command.email.strip().lower(), officer.officer_id):
            raise ValueError("Email already exists")
        if self._repository.employee_id_exists(command.employee_id.strip(), officer.officer_id):
            raise ValueError("Employee ID already exists")
        return self._repository.update_own_profile(
            station_id,
            officer.officer_id,
            UpdateOwnProfileCommand(
                first_name=command.first_name.strip(),
                last_name=command.last_name.strip(),
                email=command.email.strip().lower(),
                phone_number=command.phone_number.strip() if command.phone_number else None,
                employee_id=command.employee_id.strip(),
            ),
        )


class ChangeStationAdminPasswordUseCase:
    def __init__(
        self,
        repository: StationAdminPortalRepositoryPort,
        context: StationAdminPortalContext,
        credential_store: CredentialStorePort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._repository = repository
        self._context = context
        self._credential_store = credential_store
        self._password_hasher = password_hasher

    def execute(self, principal: AuthPrincipal, command: ChangeOwnPasswordCommand) -> None:
        _, officer = self._context.station_and_officer(principal)
        stored = self._credential_store.find_by_id(officer.officer_id)
        if stored is None:
            raise LookupError("Officer not found")
        if not self._password_hasher.verify(command.current_password, stored.password_hash):
            raise ValueError("Current password is incorrect")
        self._repository.change_own_password(
            officer.officer_id,
            self._password_hasher.hash(command.new_password),
        )
