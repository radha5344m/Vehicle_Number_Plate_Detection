"""Save completed scan use case unit tests."""

from sentinel_anpr.application.dto.history_dto import SaveCompletedScanCommand
from sentinel_anpr.application.use_cases.history.save_completed_scan_use_case import (
    SaveCompletedScanUseCase,
)
from sentinel_anpr.domain.vehicle.errors import InvalidPlateError


class _FakeRepository:
    def __init__(self) -> None:
        self.last_command: SaveCompletedScanCommand | None = None

    def save_completed(self, command: SaveCompletedScanCommand):
        from datetime import UTC, datetime

        from sentinel_anpr.application.dto.history_dto import SaveCompletedScanResult

        self.last_command = command
        now = datetime.now(UTC)
        return SaveCompletedScanResult(
            scan_id="scan-test-id",
            plate_text=command.plate_text,
            scanned_at=now,
            completed_at=now,
        )

    def list_scans(self, filters):
        del filters
        raise NotImplementedError


def test_save_completed_scan_normalizes_plate() -> None:
    repository = _FakeRepository()
    use_case = SaveCompletedScanUseCase(scan_repository=repository)
    result = use_case.execute(
        SaveCompletedScanCommand(
            officer_id="officer-1",
            officer_name="Ravi Kumar",
            plate_text="ap09 ab 1234",
            risk_score=0.1,
            risk_level="low",
        )
    )
    assert result.plate_text == "AP09AB1234"
    assert repository.last_command is not None
    assert repository.last_command.plate_text == "AP09AB1234"


def test_save_completed_scan_rejects_invalid_plate() -> None:
    use_case = SaveCompletedScanUseCase(scan_repository=_FakeRepository())
    try:
        use_case.execute(
            SaveCompletedScanCommand(
                officer_id="officer-1",
                officer_name="Ravi Kumar",
                plate_text="   ",
                risk_score=0.1,
                risk_level="low",
            )
        )
        raise AssertionError("expected InvalidPlateError")
    except InvalidPlateError:
        pass
