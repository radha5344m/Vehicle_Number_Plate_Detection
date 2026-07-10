"""Persist a completed scan."""

from sentinel_anpr.application.dto.history_dto import (
    SaveCompletedScanCommand,
    SaveCompletedScanResult,
)
from sentinel_anpr.application.ports.outbound.scan_repository_port import ScanRepositoryPort
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel
from sentinel_anpr.domain.vehicle.errors import InvalidPlateError
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)


class SaveCompletedScanUseCase:
    """Store a completed scan in history."""

    def __init__(self, scan_repository: ScanRepositoryPort) -> None:
        self._scan_repository = scan_repository

    def execute(self, command: SaveCompletedScanCommand) -> SaveCompletedScanResult:
        plate_text = normalize_registration_number(command.plate_text)
        if not plate_text:
            raise InvalidPlateError()

        risk_level = command.risk_level.lower()
        if risk_level not in {level.value for level in RiskLevel}:
            raise ValueError(f"Invalid risk level: {command.risk_level}")

        if not 0.0 <= command.risk_score <= 1.0:
            raise ValueError("Risk score must be between 0.0 and 1.0")

        return self._scan_repository.save_completed(
            SaveCompletedScanCommand(
                officer_id=command.officer_id,
                officer_name=command.officer_name,
                plate_text=plate_text,
                risk_score=round(command.risk_score, 4),
                risk_level=risk_level,
                vehicle_id=command.vehicle_id,
                location_label=command.location_label,
                scanned_at=command.scanned_at,
            )
        )
