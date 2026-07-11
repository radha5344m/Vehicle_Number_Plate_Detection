"""Detect vehicles in an uploaded scene image."""

from __future__ import annotations

from sentinel_anpr.application.dto.vehicle_detection_dto import DetectVehiclesCommand, DetectVehiclesResult
from sentinel_anpr.application.ports.intelligent_scene_detection_service import IntelligentSceneDetectionService
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort


class DetectVehiclesUseCase:
    """Run intelligent vehicle and plate detection without OCR or registry lookup."""

    def __init__(
        self,
        scene_detection_service: IntelligentSceneDetectionService,
        logger: LoggingPort,
    ) -> None:
        self._detection = scene_detection_service
        self._logger = logger

    def execute(self, command: DetectVehiclesCommand) -> DetectVehiclesResult:
        scene_context = self._detection.analyze_scene(command.image_bytes)
        vehicles = self._detection.detect_vehicles(command.image_bytes)
        visible_plate_count = len(scene_context.raw_plates)
        self._logger.info(
            "vehicle_detection_completed",
            vehicle_count=len(vehicles),
            visible_plate_count=visible_plate_count,
            detail="Intelligent vehicle and plate detection completed",
        )
        return DetectVehiclesResult(
            vehicles=vehicles,
            visible_plate_count=visible_plate_count,
        )
