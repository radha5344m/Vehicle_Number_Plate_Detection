"""Scan history data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


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
