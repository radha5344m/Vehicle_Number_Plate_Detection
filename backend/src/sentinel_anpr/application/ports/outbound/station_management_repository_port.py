"""Police station repository port."""

from typing import Protocol

from sentinel_anpr.application.dto.station_management_dto import (
    CreateStationCommand,
    QueryStationsResult,
    StationFilters,
    StationItemDto,
    StationMutationResult,
    StationStatusCommand,
    UpdateStationCommand,
)


class StationManagementRepositoryPort(Protocol):
    def query_stations(self, filters: StationFilters) -> QueryStationsResult: ...

    def get_station(self, station_id: str) -> StationItemDto | None: ...

    def get_active_station_by_name(self, station_name: str) -> StationItemDto | None: ...

    def create_station(self, command: CreateStationCommand) -> StationMutationResult: ...

    def update_station(self, command: UpdateStationCommand) -> StationMutationResult: ...

    def change_status(self, command: StationStatusCommand) -> StationMutationResult: ...

    def soft_delete_station(self, station_id: str) -> None: ...

    def station_code_exists(self, station_code: str, exclude_station_id: str | None = None) -> bool: ...

    def station_name_exists(self, station_name: str, exclude_station_id: str | None = None) -> bool: ...
