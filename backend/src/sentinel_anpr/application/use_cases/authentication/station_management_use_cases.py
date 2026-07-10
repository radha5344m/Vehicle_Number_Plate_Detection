"""Police station management use cases."""

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.station_management_dto import (
    CreateStationCommand,
    QueryStationsResult,
    StationFilters,
    StationMutationResult,
    StationStatusCommand,
    UpdateStationCommand,
)
from sentinel_anpr.application.ports.outbound.station_management_repository_port import (
    StationManagementRepositoryPort,
)
from sentinel_anpr.application.use_cases.authentication.user_management_use_cases import (
    ensure_super_admin,
)

_ALLOWED_STATUSES = {"active", "inactive"}


class QueryStationsUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, filters: StationFilters) -> QueryStationsResult:
        ensure_super_admin(principal)
        return self._repository.query_stations(filters)


class GetStationUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, station_id: str):
        ensure_super_admin(principal)
        station = self._repository.get_station(station_id)
        if station is None:
            raise LookupError("Station not found")
        return station


class CreateStationUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, command: CreateStationCommand) -> StationMutationResult:
        ensure_super_admin(principal)
        self._validate_unique(command.station_name, command.station_code)
        if command.status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Invalid station status")
        normalized = CreateStationCommand(
            station_name=command.station_name.strip(),
            station_code=command.station_code.strip().upper(),
            district=command.district.strip(),
            state=command.state.strip(),
            address=command.address.strip(),
            pincode=command.pincode.strip(),
            phone_number=command.phone_number.strip() if command.phone_number else None,
            email=command.email.strip().lower() if command.email else None,
            station_type=command.station_type.strip().lower(),
            status=command.status.strip().lower(),
        )
        return self._repository.create_station(normalized)

    def _validate_unique(self, station_name: str, station_code: str) -> None:
        if self._repository.station_name_exists(station_name.strip()):
            raise ValueError("Station name already exists")
        if self._repository.station_code_exists(station_code.strip().upper()):
            raise ValueError("Station code already exists")


class UpdateStationUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, command: UpdateStationCommand) -> StationMutationResult:
        ensure_super_admin(principal)
        if self._repository.station_name_exists(command.station_name.strip(), command.station_id):
            raise ValueError("Station name already exists")
        if command.status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Invalid station status")
        normalized = UpdateStationCommand(
            station_id=command.station_id,
            station_name=command.station_name.strip(),
            district=command.district.strip(),
            state=command.state.strip(),
            address=command.address.strip(),
            pincode=command.pincode.strip(),
            phone_number=command.phone_number.strip() if command.phone_number else None,
            email=command.email.strip().lower() if command.email else None,
            station_type=command.station_type.strip().lower(),
            status=command.status.strip().lower(),
        )
        return self._repository.update_station(normalized)


class ChangeStationStatusUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, command: StationStatusCommand) -> StationMutationResult:
        ensure_super_admin(principal)
        if command.status.lower() not in _ALLOWED_STATUSES:
            raise ValueError("Invalid station status")
        return self._repository.change_status(
            StationStatusCommand(station_id=command.station_id, status=command.status.lower())
        )


class DeleteStationUseCase:
    def __init__(self, repository: StationManagementRepositoryPort) -> None:
        self._repository = repository

    def execute(self, principal: AuthPrincipal, station_id: str) -> None:
        ensure_super_admin(principal)
        self._repository.soft_delete_station(station_id)
