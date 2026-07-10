"""Police officer portal use cases."""

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.police_officer_portal_dto import (
    ChangeOwnPasswordCommand,
    PoliceOfficerDashboardResult,
    PoliceOfficerNotificationDto,
    PoliceOfficerProfileDto,
)
from sentinel_anpr.application.ports.outbound.credential_store_port import CredentialStorePort
from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.application.ports.outbound.police_officer.police_officer_portal_repository_port import (
    PoliceOfficerPortalRepositoryPort,
)
from sentinel_anpr.application.use_cases.authentication.get_current_officer_use_case import (
    GetCurrentOfficerUseCase,
)


def ensure_police_officer(principal: AuthPrincipal) -> None:
    if "police_officer" not in {role.lower() for role in principal.roles}:
        raise PermissionError("Police officer access required")


class PoliceOfficerPortalContext:
    def __init__(self, get_current_officer_use_case: GetCurrentOfficerUseCase) -> None:
        self._get_current_officer_use_case = get_current_officer_use_case

    def officer(self, principal: AuthPrincipal):
        ensure_police_officer(principal)
        return self._get_current_officer_use_case.execute(principal).officer


class GetPoliceOfficerDashboardUseCase:
    def __init__(
        self,
        repository: PoliceOfficerPortalRepositoryPort,
        context: PoliceOfficerPortalContext,
    ) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal) -> PoliceOfficerDashboardResult:
        officer = self._context.officer(principal)
        return self._repository.get_dashboard(officer.officer_id)


class GetPoliceOfficerNotificationsUseCase:
    def __init__(
        self,
        repository: PoliceOfficerPortalRepositoryPort,
        context: PoliceOfficerPortalContext,
    ) -> None:
        self._repository = repository
        self._context = context

    def execute(
        self,
        principal: AuthPrincipal,
        limit: int = 20,
    ) -> tuple[PoliceOfficerNotificationDto, ...]:
        officer = self._context.officer(principal)
        return self._repository.get_notifications(officer.officer_id, limit)


class GetPoliceOfficerProfileUseCase:
    def __init__(
        self,
        repository: PoliceOfficerPortalRepositoryPort,
        context: PoliceOfficerPortalContext,
    ) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal) -> PoliceOfficerProfileDto:
        officer = self._context.officer(principal)
        return self._repository.get_profile(officer.officer_id)


class UpdatePoliceOfficerProfileUseCase:
    def __init__(
        self,
        repository: PoliceOfficerPortalRepositoryPort,
        context: PoliceOfficerPortalContext,
    ) -> None:
        self._repository = repository
        self._context = context

    def execute(self, principal: AuthPrincipal, command: UpdateOwnProfileCommand) -> PoliceOfficerProfileDto:
        officer = self._context.officer(principal)
        if self._repository.email_exists(command.email.strip().lower(), officer.officer_id):
            raise ValueError("Email already exists")
        if self._repository.employee_id_exists(command.employee_id.strip(), officer.officer_id):
            raise ValueError("Employee ID already exists")
        return self._repository.update_own_profile(
            officer.officer_id,
            UpdateOwnProfileCommand(
                first_name=command.first_name.strip(),
                last_name=command.last_name.strip(),
                email=command.email.strip().lower(),
                phone_number=command.phone_number.strip() if command.phone_number else None,
                employee_id=command.employee_id.strip(),
            ),
        )


class ChangePoliceOfficerPasswordUseCase:
    def __init__(
        self,
        repository: PoliceOfficerPortalRepositoryPort,
        context: PoliceOfficerPortalContext,
        credential_store: CredentialStorePort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._repository = repository
        self._context = context
        self._credential_store = credential_store
        self._password_hasher = password_hasher

    def execute(self, principal: AuthPrincipal, command: ChangeOwnPasswordCommand) -> None:
        officer = self._context.officer(principal)
        stored = self._credential_store.find_by_id(officer.officer_id)
        if stored is None:
            raise LookupError("Officer not found")
        if not self._password_hasher.verify(command.current_password, stored.password_hash):
            raise ValueError("Current password is incorrect")
        self._repository.change_own_password(
            officer.officer_id,
            self._password_hasher.hash(command.new_password),
        )
