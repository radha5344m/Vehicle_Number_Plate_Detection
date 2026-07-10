"""Vehicle ORM to DTO mapper."""

from sentinel_anpr.application.dto.vehicle_dto import VehicleRecordDto
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel


def to_vehicle_record_dto(model: VehicleModel) -> VehicleRecordDto:
    """Map ORM row to application DTO."""
    return VehicleRecordDto(
        vehicle_id=model.vehicle_id,
        plate_number=model.plate_number,
        jurisdiction=model.jurisdiction,
        make=model.make or "",
        model=model.model or "",
        color=model.color or "",
        year=model.year or 0,
        vehicle_type=model.vehicle_type,
        registration_status=model.registration_status,
        registered_owner=model.registered_owner or "",
        registry_external_id=model.registry_external_id,
        registry_synced_at=model.registry_synced_at,
    )
