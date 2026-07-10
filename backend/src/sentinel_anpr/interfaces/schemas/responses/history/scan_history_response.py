"""Scan history response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ScanHistoryItemData(BaseModel):
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


class PaginationData(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class ScanHistoryListData(BaseModel):
    """Paginated scan history list."""

    items: list[ScanHistoryItemData]
    pagination: PaginationData


class SaveCompletedScanData(BaseModel):
    """Saved scan reference."""

    scan_id: str
    plate_text: str
    scanned_at: datetime
    completed_at: datetime
