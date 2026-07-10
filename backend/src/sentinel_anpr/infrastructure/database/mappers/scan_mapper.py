"""Scan history ORM mappers."""

from sentinel_anpr.application.dto.history_dto import ScanHistoryItemDto
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel


def to_scan_history_item_dto(model: ScanModel) -> ScanHistoryItemDto:
    """Map ORM scan row to application DTO."""
    return ScanHistoryItemDto(
        scan_id=model.scan_id,
        plate_text=model.plate_text,
        vehicle_id=model.vehicle_id,
        officer_id=model.officer_id,
        officer_name=model.officer_name,
        risk_score=model.risk_score,
        risk_level=model.risk_level,
        location_label=model.location_label,
        scanned_at=model.scanned_at,
        completed_at=model.completed_at,
    )
