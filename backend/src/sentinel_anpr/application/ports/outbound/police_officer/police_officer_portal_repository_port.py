"""Police officer portal repository port."""

from typing import Protocol

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.police_officer_portal_dto import (
    PoliceOfficerDashboardResult,
    PoliceOfficerNotificationDto,
    PoliceOfficerProfileDto,
)


class PoliceOfficerPortalRepositoryPort(Protocol):
    def get_dashboard(self, officer_id: str) -> PoliceOfficerDashboardResult: ...

    def get_notifications(
        self,
        officer_id: str,
        limit: int,
    ) -> tuple[PoliceOfficerNotificationDto, ...]: ...

    def get_profile(self, officer_id: str) -> PoliceOfficerProfileDto: ...

    def update_own_profile(self, officer_id: str, command: UpdateOwnProfileCommand) -> PoliceOfficerProfileDto: ...

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool: ...

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool: ...

    def change_own_password(self, officer_id: str, password_hash: str) -> None: ...
