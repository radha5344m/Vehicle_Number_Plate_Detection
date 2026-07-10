"""Lookup vehicle use case unit tests."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.vehicle_dto import (
    LookupStatus,
    LookupVehicleCommand,
    VehicleRecordDto,
)
from sentinel_anpr.application.use_cases.vehicle.lookup_vehicle_use_case import LookupVehicleUseCase


class _FakeRepository:
    def find_by_plate(self, plate_number: str, jurisdiction: str | None = None) -> VehicleRecordDto | None:
        del jurisdiction
        if plate_number == "AP09AB1234":
            return VehicleRecordDto(
                vehicle_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                plate_number="AP09AB1234",
                jurisdiction="AP",
                make="Toyota",
                model="Innova Crysta",
                color="White",
                year=2020,
                vehicle_type="car",
                registration_status="active",
                registered_owner="Ravi Kumar",
                registry_external_id="RTO-ONG-1001",
                registry_synced_at=datetime.now(UTC),
            )
        return None


def test_lookup_vehicle_found() -> None:
    use_case = LookupVehicleUseCase(vehicle_repository=_FakeRepository())
    result = use_case.execute(LookupVehicleCommand(plate="ap09 ab 1234"))
    assert result.lookup_status == LookupStatus.FOUND
    assert result.vehicle is not None
    assert result.vehicle.make == "Toyota"


def test_lookup_vehicle_not_found() -> None:
    use_case = LookupVehicleUseCase(vehicle_repository=_FakeRepository())
    result = use_case.execute(LookupVehicleCommand(plate="ZZ99ZZ9999"))
    assert result.lookup_status == LookupStatus.NOT_FOUND
    assert result.message == "Vehicle not found."
    assert result.vehicle is None
