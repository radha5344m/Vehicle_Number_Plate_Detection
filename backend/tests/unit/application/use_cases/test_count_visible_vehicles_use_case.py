"""Unit tests for CountVisibleVehiclesUseCase."""

from sentinel_anpr.application.dto.visible_vehicle_count_dto import CountVisibleVehiclesCommand
from sentinel_anpr.application.ports.vision_ai_service import VisibleVehicleCountResult
from sentinel_anpr.application.use_cases.orchestration.count_visible_vehicles_use_case import (
    CountVisibleVehiclesUseCase,
)


class _FakeLogger:
    def info(self, message: str, **context) -> None:
        del message, context


class _FakeVision:
    def __init__(self, result: VisibleVehicleCountResult) -> None:
        self._result = result
        self.received_bytes: bytes | None = None

    def analyze_vehicle_image(self, image_bytes: bytes):
        del image_bytes
        raise NotImplementedError

    def count_visible_vehicles(self, image_bytes: bytes) -> VisibleVehicleCountResult:
        self.received_bytes = image_bytes
        return self._result


def test_count_visible_vehicles_use_case_maps_vision_result() -> None:
    image_bytes = b"original-upload-image"
    vision = _FakeVision(
        VisibleVehicleCountResult(
            vehicle_count=3,
            vehicles=("motorcycle", "motorcycle", "motorcycle"),
        )
    )
    use_case = CountVisibleVehiclesUseCase(vision_ai_service=vision, logger=_FakeLogger())

    result = use_case.execute(
        CountVisibleVehiclesCommand(
            image_bytes=image_bytes,
            content_type="image/jpeg",
        )
    )

    assert vision.received_bytes == image_bytes
    assert result.vehicle_count == 3
    assert [item.type for item in result.vehicles] == ["motorcycle", "motorcycle", "motorcycle"]
