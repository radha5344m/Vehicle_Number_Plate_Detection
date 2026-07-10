"""Tests for intelligent scene detection."""

import io

from PIL import Image

from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.dto.vehicle_detection_dto import DetectedVehicleDto, SelectedVehicleRegionDto
from sentinel_anpr.infrastructure.ai.intelligent_scene_detection_service import DefaultIntelligentSceneDetectionService


class _FakeLogger:
    def info(self, message: str, **context) -> None:
        del message, context


class _FakeVehicleDetection:
    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        del image_bytes
        return (
            DetectedVehicleDto("vehicle-1", 0.1, 0.2, 0.3, 0.4, 0.9, "car"),
            DetectedVehicleDto("vehicle-2", 0.55, 0.2, 0.3, 0.4, 0.88, "suv"),
        )


class _FakePlateDetection:
    def detect_plates(self, image_bytes: bytes) -> tuple[DetectedPlateDto, ...]:
        del image_bytes
        return (
            DetectedPlateDto("plate-1", 0.18, 0.5, 0.14, 0.05, 0.9, None),
            DetectedPlateDto("plate-2", 0.62, 0.52, 0.13, 0.05, 0.88, None),
        )


def _image_bytes() -> bytes:
    image = Image.new("RGB", (1280, 960), color=(30, 30, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_intelligent_detection_expands_vehicle_box_to_include_plate() -> None:
    service = DefaultIntelligentSceneDetectionService(
        vehicle_detection_service=_FakeVehicleDetection(),
        license_plate_detection_service=_FakePlateDetection(),
        logger=_FakeLogger(),
    )

    vehicles = service.detect_vehicles(_image_bytes())

    assert len(vehicles) == 2
    assert vehicles[0].height >= 0.4
    assert vehicles[0].y <= 0.2


def test_mask_regions_for_selection_excludes_assigned_plate() -> None:
    service = DefaultIntelligentSceneDetectionService(
        vehicle_detection_service=_FakeVehicleDetection(),
        license_plate_detection_service=_FakePlateDetection(),
        logger=_FakeLogger(),
    )

    mask_regions = service.mask_regions_for_selection(_image_bytes(), "vehicle-1")

    assert any(region.vehicle_id == "vehicle-2" for region in mask_regions)
    assert any(region.vehicle_id == "plate-2" for region in mask_regions)
    assert not any(region.vehicle_id == "plate-1" for region in mask_regions)


def test_mask_regions_reuses_scene_context_without_redetecting() -> None:
    class _CountingVehicleDetection(_FakeVehicleDetection):
        def __init__(self) -> None:
            self.calls = 0

        def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
            self.calls += 1
            return super().detect_vehicles(image_bytes)

    class _CountingPlateDetection(_FakePlateDetection):
        def __init__(self) -> None:
            self.calls = 0

        def detect_plates(self, image_bytes: bytes) -> tuple[DetectedPlateDto, ...]:
            self.calls += 1
            return super().detect_plates(image_bytes)

    vehicles = _CountingVehicleDetection()
    plates = _CountingPlateDetection()
    service = DefaultIntelligentSceneDetectionService(
        vehicle_detection_service=vehicles,
        license_plate_detection_service=plates,
        logger=_FakeLogger(),
    )
    image = _image_bytes()
    scene = service.analyze_scene(image)

    service.mask_regions_for_selection(image, "vehicle-1", scene_context=scene)
    service.mask_regions_for_selection(image, "vehicle-2", scene_context=scene)

    assert vehicles.calls == 1
    assert plates.calls == 1
