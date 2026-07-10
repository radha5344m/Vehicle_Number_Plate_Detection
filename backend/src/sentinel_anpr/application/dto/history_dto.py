"""Scan history data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VisionScanSnapshot:
    """Raw vision AI output persisted with a scan."""

    registration_number: str | None
    brand: str | None
    model: str | None
    color: str | None
    vehicle_type: str | None
    confidence: float | None
    brand_confidence: float | None
    color_confidence: float | None
    vehicle_type_confidence: float | None
    explanation: str | None


@dataclass(frozen=True)
class RegistryScanSnapshot:
    """Registry lookup output persisted with a scan."""

    lookup_status: str | None
    message: str | None
    vehicle_id: str | None = None
    plate_number: str | None = None
    make: str | None = None
    model: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    year: int | None = None
    registration_status: str | None = None
    registered_owner: str | None = None
    jurisdiction: str | None = None


@dataclass(frozen=True)
class SaveCompletedScanCommand:
    """Persist a completed scan."""

    officer_id: str
    officer_name: str
    plate_text: str
    risk_score: float
    risk_level: str
    vehicle_id: str | None = None
    location_label: str | None = None
    scanned_at: datetime | None = None
    correlation_id: str | None = None
    ocr_confidence: float | None = None
    image_storage_key: str | None = None
    vision_snapshot: VisionScanSnapshot | None = None
    registry_snapshot: RegistryScanSnapshot | None = None


@dataclass(frozen=True)
class SaveCompletedScanResult:
    """Saved scan reference."""

    scan_id: str
    plate_text: str
    scanned_at: datetime
    completed_at: datetime


@dataclass(frozen=True)
class ScanHistoryFilters:
    """Query filters for scan history."""

    plate: str | None = None
    officer_id: str | None = None
    station_id: str | None = None
    risk_level: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class ScanHistoryItemDto:
    """Single scan history row."""

    scan_id: str
    plate_text: str
    vehicle_id: str | None
    officer_id: str
    officer_name: str
    risk_score: float
    risk_level: str
    location_label: str | None
    scanned_at: datetime
    completed_at: datetime


@dataclass(frozen=True)
class PaginationDto:
    """Offset pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class QueryScanHistoryResult:
    """Paginated scan history list."""

    items: tuple[ScanHistoryItemDto, ...]
    pagination: PaginationDto
