"""Intelligent vehicle + plate scene detection adapter."""

from __future__ import annotations

import io

from PIL import Image

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.dto.scene_analysis_dto import PlateAssignmentDto, SceneAnalysisContextDto
from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto, SelectedVehicleRegionDto
from sentinel_anpr.application.ports.intelligent_scene_detection_service import IntelligentSceneDetectionService
from sentinel_anpr.application.ports.license_plate_detection_service import LicensePlateDetectionService
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vehicle_detection_service import VehicleDetectionService
from sentinel_anpr.domain.vision.services.plate_to_vehicle_assignment_policy import (
    PlateDetectionInput,
    PlateToVehicleAssignmentPolicy,
    VehicleDetectionInput,
)
from sentinel_anpr.domain.vision.services.vehicle_plate_box_merger import build_vehicle_crop_box
from sentinel_anpr.domain.vision.value_objects.normalized_bounding_box import NormalizedBoundingBox


class DefaultIntelligentSceneDetectionService(IntelligentSceneDetectionService):
    """Detect vehicles and plates, assign plates to vehicles, and merge crop boxes."""

    def __init__(
        self,
        vehicle_detection_service: VehicleDetectionService,
        license_plate_detection_service: LicensePlateDetectionService,
        logger: LoggingPort,
    ) -> None:
        self._vehicles = vehicle_detection_service
        self._plates = license_plate_detection_service
        self._assignment = PlateToVehicleAssignmentPolicy()
        self._logger = logger

    def analyze_scene(self, image_bytes: bytes) -> SceneAnalysisContextDto:
        raw_vehicles = self._vehicles.detect_vehicles(image_bytes)
        raw_plates = self._plates.detect_plates(image_bytes)
        image_width, image_height = self._image_size(image_bytes)

        vehicle_inputs = tuple(
            VehicleDetectionInput(
                vehicle_id=vehicle.vehicle_id,
                box=NormalizedBoundingBox(
                    x=vehicle.x,
                    y=vehicle.y,
                    width=vehicle.width,
                    height=vehicle.height,
                ),
            )
            for vehicle in raw_vehicles
        )
        plate_inputs = tuple(
            PlateDetectionInput(
                plate_id=plate.plate_id,
                box=NormalizedBoundingBox(
                    x=plate.x,
                    y=plate.y,
                    width=plate.width,
                    height=plate.height,
                ),
                confidence=plate.confidence,
            )
            for plate in raw_plates
        )
        assignments = self._assignment.assign(
            vehicle_inputs,
            plate_inputs,
            image_width=image_width,
            image_height=image_height,
        )

        return SceneAnalysisContextDto(
            raw_vehicles=raw_vehicles,
            raw_plates=raw_plates,
            assignments=tuple(
                PlateAssignmentDto(
                    plate_id=assignment.plate_id,
                    vehicle_id=assignment.vehicle_id,
                )
                for assignment in assignments
            ),
            image_width=image_width,
            image_height=image_height,
        )

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        scene = self.analyze_scene(image_bytes)
        intelligent_vehicles = self._build_intelligent_vehicles(scene)

        vehicle_plate_map = {
            assignment.vehicle_id: assignment.plate_id
            for assignment in scene.assignments
            if assignment.vehicle_id is not None
        }
        unassigned_count = sum(1 for assignment in scene.assignments if assignment.vehicle_id is None)
        self._logger.info(
            "intelligent_scene_detection_completed",
            vehicle_count=len(intelligent_vehicles),
            plate_count=len(scene.raw_plates),
            assigned_plates=len(vehicle_plate_map),
            unassigned_plates=unassigned_count,
            detail="Intelligent vehicle and plate detection completed",
        )
        return intelligent_vehicles

    def mask_regions_for_selection(
        self,
        image_bytes: bytes,
        selected_vehicle_id: str,
        scene_context: SceneAnalysisContextDto | None = None,
    ) -> tuple[SelectedVehicleRegionDto, ...]:
        scene = scene_context or self.analyze_scene(image_bytes)
        assigned_plate_for_selected = next(
            (
                assignment.plate_id
                for assignment in scene.assignments
                if assignment.vehicle_id == selected_vehicle_id
            ),
            None,
        )

        mask_regions: list[SelectedVehicleRegionDto] = []
        for vehicle in scene.raw_vehicles:
            if vehicle.vehicle_id == selected_vehicle_id:
                continue
            mask_regions.append(self._to_selected_region(vehicle))

        for plate in scene.raw_plates:
            if plate.plate_id == assigned_plate_for_selected:
                continue
            mask_regions.append(
                SelectedVehicleRegionDto(
                    vehicle_id=plate.plate_id,
                    x=plate.x,
                    y=plate.y,
                    width=plate.width,
                    height=plate.height,
                )
            )

        return tuple(mask_regions)

    def _build_intelligent_vehicles(self, scene: SceneAnalysisContextDto) -> tuple[DetectedVehicleDto, ...]:
        plate_by_id = {plate.plate_id: plate for plate in scene.raw_plates}
        vehicle_plate_map = {
            assignment.vehicle_id: plate_by_id[assignment.plate_id]
            for assignment in scene.assignments
            if assignment.vehicle_id is not None and assignment.plate_id in plate_by_id
        }

        intelligent_vehicles: list[DetectedVehicleDto] = []
        for vehicle in scene.raw_vehicles:
            vehicle_box = NormalizedBoundingBox(
                x=vehicle.x,
                y=vehicle.y,
                width=vehicle.width,
                height=vehicle.height,
            )
            assigned_plate = vehicle_plate_map.get(vehicle.vehicle_id)
            plate_box = (
                NormalizedBoundingBox(
                    x=assigned_plate.x,
                    y=assigned_plate.y,
                    width=assigned_plate.width,
                    height=assigned_plate.height,
                )
                if assigned_plate is not None
                else None
            )
            crop_box = build_vehicle_crop_box(
                vehicle_box,
                plate_box,
                image_width=scene.image_width,
                image_height=scene.image_height,
            )
            confidence = vehicle.confidence
            if assigned_plate is not None:
                confidence = min(0.98, (vehicle.confidence + assigned_plate.confidence) / 2 + 0.05)

            intelligent_vehicles.append(
                DetectedVehicleDto(
                    vehicle_id=vehicle.vehicle_id,
                    x=crop_box.x,
                    y=crop_box.y,
                    width=crop_box.width,
                    height=crop_box.height,
                    confidence=round(confidence, 4),
                    vehicle_type=vehicle.vehicle_type,
                )
            )

        return tuple(intelligent_vehicles)

    @staticmethod
    def _to_selected_region(vehicle: DetectedVehicleDto) -> SelectedVehicleRegionDto:
        return SelectedVehicleRegionDto(
            vehicle_id=vehicle.vehicle_id,
            x=vehicle.x,
            y=vehicle.y,
            width=vehicle.width,
            height=vehicle.height,
        )

    @staticmethod
    def _image_size(image_bytes: bytes) -> tuple[int, int]:
        with Image.open(io.BytesIO(image_bytes)) as image:
            return image.size
