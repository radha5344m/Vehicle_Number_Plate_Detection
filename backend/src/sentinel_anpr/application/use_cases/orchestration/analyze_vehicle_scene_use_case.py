"""Intelligent vehicle + plate detection with plate-to-vehicle assignment."""

from __future__ import annotations

from sentinel_anpr.application.dto.vehicle_detection_dto import (
    DetectedPlateDto,
    DetectedVehicleDto,
    VehicleSceneAnalysisResult,
)
from sentinel_anpr.application.ports.license_plate_detection_service import LicensePlateDetectionService
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vehicle_detection_service import VehicleDetectionService
from sentinel_anpr.domain.vision.services.plate_to_vehicle_assignment_policy import (
    PlateDetectionInput,
    PlateToVehicleAssignmentPolicy,
    VehicleDetectionInput,
)


class AnalyzeVehicleSceneUseCase:
    """Detect vehicles and plates, assign plates to vehicles, and merge bounding boxes."""

    def __init__(
        self,
        vehicle_detection_service: VehicleDetectionService,
        license_plate_detection_service: LicensePlateDetectionService,
        logger: LoggingPort,
        assignment_policy: PlateToVehicleAssignmentPolicy | None = None,
    ) -> None:
        self._vehicle_detection = vehicle_detection_service
        self._plate_detection = license_plate_detection_service
        self._assignment_policy = assignment_policy or PlateToVehicleAssignmentPolicy()
        self._logger = logger

    def execute(self, image_bytes: bytes) -> VehicleSceneAnalysisResult:
        raw_vehicles = self._vehicle_detection.detect_vehicles(image_bytes)
        raw_plates = self._plate_detection.detect_plates(image_bytes)

        vehicle_inputs = tuple(
            VehicleDetectionInput(
                vehicle_id=vehicle.vehicle_id,
                x=vehicle.x,
                y=vehicle.y,
                width=vehicle.width,
                height=vehicle.height,
                confidence=vehicle.confidence,
                vehicle_type=vehicle.vehicle_type,
            )
            for vehicle in raw_vehicles
        )
        plate_inputs = tuple(
            PlateDetectionInput(
                plate_id=plate.plate_id,
                x=plate.x,
                y=plate.y,
                width=plate.width,
                height=plate.height,
                confidence=plate.confidence,
                text=plate.text,
            )
            for plate in raw_plates
        )

        assignment_result = self._assignment_policy.assign(vehicle_inputs, plate_inputs)
        merged_regions = self._assignment_policy.build_vehicle_regions(vehicle_inputs, assignment_result)

        vehicles = tuple(
            DetectedVehicleDto(
                vehicle_id=region.vehicle_id,
                x=region.x,
                y=region.y,
                width=region.width,
                height=region.height,
                confidence=region.confidence,
                vehicle_type=region.vehicle_type,
            )
            for region in merged_regions
        )

        self._logger.info(
            "vehicle_scene_analysis_completed",
            vehicle_count=len(vehicles),
            plate_count=len(raw_plates),
            assigned_plate_count=len(assignment_result.assignments),
            unassigned_plate_count=len(assignment_result.unassigned_plates),
            detail="Intelligent vehicle scene analysis completed",
        )

        return VehicleSceneAnalysisResult(
            vehicles=vehicles,
            plates=raw_plates,
            unassigned_plate_count=len(assignment_result.unassigned_plates),
        )
