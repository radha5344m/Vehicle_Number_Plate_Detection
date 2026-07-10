"""Vehicle repository port."""

from typing import Protocol

from sentinel_anpr.application.dto.vehicle_dto import VehicleRecordDto


class VehicleRepositoryPort(Protocol):
    """Read registered vehicles from the demo database."""

    def find_by_plate(
        self,
        plate_number: str,
        jurisdiction: str | None = None,
    ) -> VehicleRecordDto | None: ...
