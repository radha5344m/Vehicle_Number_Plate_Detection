"""Station admin portal repository port."""

from typing import Protocol

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
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


class StationAdminPortalRepositoryPort(Protocol):
    def get_dashboard(self, station_id: str) -> StationAdminDashboardResult: ...

    def query_officers(self, station_id: str, filters: StationAdminOfficerFilters) -> StationAdminOfficerQueryResult: ...

    def create_officer(
        self,
        station_id: str,
        command: CreatePoliceOfficerCommand,
        password_hash: str,
        *,
        password_change_required: bool = False,
    ) -> StationAdminOfficerMutationResult: ...

    def update_officer(
        self,
        station_id: str,
        command: UpdatePoliceOfficerCommand,
    ) -> StationAdminOfficerMutationResult: ...

    def change_officer_status(
        self,
        station_id: str,
        officer_id: str,
        status: str,
    ) -> StationAdminOfficerMutationResult: ...

    def reset_officer_password(
        self,
        station_id: str,
        officer_id: str,
        password_hash: str,
    ) -> None: ...

    def soft_delete_officer(self, station_id: str, officer_id: str) -> None: ...

    def update_station_details(self, station_id: str, command: UpdateStationDetailsCommand) -> None: ...

    def query_investigations(
        self,
        station_id: str,
        filters: StationAdminInvestigationFilters,
    ) -> StationAdminInvestigationQueryResult: ...

    def query_reports(
        self,
        station_id: str,
        filters: StationAdminInvestigationFilters,
    ) -> StationAdminReportsResult: ...

    def get_analytics(
        self,
        station_id: str,
        from_date,
        to_date,
    ) -> StationAdminAnalyticsResult: ...

    def get_notifications(self, station_id: str, limit: int) -> tuple[StationAdminNotificationDto, ...]: ...

    def get_profile(self, station_id: str, officer_id: str) -> StationAdminProfileDto: ...

    def update_own_profile(
        self,
        station_id: str,
        officer_id: str,
        command: UpdateOwnProfileCommand,
    ) -> StationAdminProfileDto: ...

    def username_exists(self, username: str) -> bool: ...

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool: ...

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool: ...

    def get_officer_password_hash(self, officer_id: str) -> str | None: ...

    def change_own_password(self, officer_id: str, password_hash: str) -> None: ...
