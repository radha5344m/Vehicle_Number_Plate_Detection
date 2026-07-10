"""Vehicle verification routes."""

from fastapi import APIRouter, Depends, Query, Request

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.vehicle_dto import LookupVehicleCommand, VehicleRecordDto
from sentinel_anpr.application.use_cases.vehicle.lookup_vehicle_use_case import LookupVehicleUseCase
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import require_permission
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.vehicle.vehicle_response import (
    VehicleLookupResponseData,
    VehicleRecordData,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def _vehicle_data(vehicle: VehicleRecordDto) -> VehicleRecordData:
    return VehicleRecordData(
        vehicle_id=vehicle.vehicle_id,
        plate_number=vehicle.plate_number,
        jurisdiction=vehicle.jurisdiction,
        make=vehicle.make,
        model=vehicle.model,
        color=vehicle.color,
        year=vehicle.year,
        vehicle_type=vehicle.vehicle_type,
        registration_status=vehicle.registration_status,
        registered_owner=vehicle.registered_owner,
    )


@router.get("/lookup", response_model=ApiResponse[VehicleLookupResponseData])
def lookup_vehicle(
    request: Request,
    plate: str = Query(..., min_length=1, max_length=16),
    jurisdiction: str | None = Query(default=None, max_length=8),
    principal: AuthPrincipal = Depends(require_permission("vehicle_verification")),
) -> ApiResponse[VehicleLookupResponseData]:
    """Verify vehicle registration number against the demo database."""
    use_case: LookupVehicleUseCase = request.app.state.container.lookup_vehicle_use_case
    result = use_case.execute(
        LookupVehicleCommand(plate=plate, jurisdiction=jurisdiction)
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    return ApiResponse(
        data=VehicleLookupResponseData(
            lookup_status=result.lookup_status.value,
            message=result.message,
            vehicle=_vehicle_data(result.vehicle) if result.vehicle else None,
            registry_synced_at=result.registry_synced_at,
            registry_external_id=result.registry_external_id,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
