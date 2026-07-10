"""Look up a vehicle by registration number."""

from sentinel_anpr.application.dto.vehicle_dto import (
    LookupStatus,
    LookupVehicleCommand,
    LookupVehicleResult,
)
from sentinel_anpr.application.ports.outbound.vehicle_repository_port import VehicleRepositoryPort
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.domain.vehicle.errors import InvalidPlateError


class LookupVehicleUseCase:
    """Verify vehicle registration against the demo database."""

    def __init__(self, vehicle_repository: VehicleRepositoryPort) -> None:
        self._vehicle_repository = vehicle_repository

    def execute(self, command: LookupVehicleCommand) -> LookupVehicleResult:
        plate_number = normalize_registration_number(command.plate)
        if not plate_number:
            raise InvalidPlateError()

        vehicle = self._vehicle_repository.find_by_plate(
            plate_number=plate_number,
            jurisdiction=command.jurisdiction,
        )
        if vehicle is None:
            return LookupVehicleResult(
                lookup_status=LookupStatus.NOT_FOUND,
                vehicle=None,
                message="Vehicle not found.",
            )

        return LookupVehicleResult(
            lookup_status=LookupStatus.FOUND,
            vehicle=vehicle,
            message="Found",
            registry_synced_at=vehicle.registry_synced_at,
            registry_external_id=vehicle.registry_external_id,
        )
