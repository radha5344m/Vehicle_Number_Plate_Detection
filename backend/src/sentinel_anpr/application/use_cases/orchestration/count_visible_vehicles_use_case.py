"""Count visible vehicles in an uploaded image using vision AI only."""

from __future__ import annotations

from sentinel_anpr.application.dto.visible_vehicle_count_dto import (
    CountVisibleVehiclesCommand,
    CountVisibleVehiclesResult,
    VisibleVehicleTypeDto,
)
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import VisionAiService


class CountVisibleVehiclesUseCase:
    """Run a vision-only vehicle count before upload investigation routing."""

    def __init__(self, vision_ai_service: VisionAiService, logger: LoggingPort) -> None:
        self._vision = vision_ai_service
        self._logger = logger

    def execute(self, command: CountVisibleVehiclesCommand) -> CountVisibleVehiclesResult:
        count_result = self._vision.count_visible_vehicles(command.image_bytes)
        vehicles = tuple(
            VisibleVehicleTypeDto(type=vehicle_type) for vehicle_type in count_result.vehicles
        )
        self._logger.info(
            "visible_vehicle_count_completed",
            vehicle_count=count_result.vehicle_count,
            vehicle_types=[item.type for item in vehicles],
            detail="Vision-only visible vehicle count completed for upload routing",
        )
        return CountVisibleVehiclesResult(
            vehicle_count=count_result.vehicle_count,
            vehicles=vehicles,
        )
