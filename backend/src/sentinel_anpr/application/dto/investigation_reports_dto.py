"""Investigation reports read-model DTOs."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class InvestigationSortBy(StrEnum):
    """Supported sort columns for investigation reports."""

    SCANNED_AT = "scanned_at"
    RISK_SCORE = "risk_score"
    AI_CONFIDENCE = "ai_confidence"
    OFFICER_NAME = "officer_name"
    REGISTRATION_NUMBER = "registration_number"
    POLICE_STATION = "police_station"


class ExportFormat(StrEnum):
    """Supported department report export formats."""

    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


@dataclass(frozen=True)
class InvestigationReportsFilters:
    """Filter inputs for the Investigation Reports module."""

    from_date: datetime | None = None
    to_date: datetime | None = None
    search: str | None = None
    station_id: str | None = None
    officer_id: str | None = None
    officer: str | None = None
    police_station: str | None = None
    district: str | None = None
    risk_level: str | None = None
    vehicle_type: str | None = None
    vehicle_brand: str | None = None
    registration_number: str | None = None
    owner_name: str | None = None
    verification_status: str | None = None
    investigation_status: str | None = None
    ai_confidence_min: float | None = None
    ai_confidence_max: float | None = None
    page: int = 1
    page_size: int = 20
    sort_by: InvestigationSortBy = InvestigationSortBy.SCANNED_AT
    sort_desc: bool = True


@dataclass(frozen=True)
class InvestigationReportsPaginationDto:
    """Pagination metadata for report listings."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class DistributionItemDto:
    """Simple name/value distribution item."""

    label: str
    value: int


@dataclass(frozen=True)
class DailyInvestigationTrendPointDto:
    """Daily investigation trend point."""

    date: str
    investigations: int


@dataclass(frozen=True)
class PeriodInvestigationTrendPointDto:
    """Weekly or monthly investigation trend point."""

    period: str
    investigations: int


@dataclass(frozen=True)
class OfficerPerformanceItemDto:
    """Officer-level investigation volume/performance summary."""

    officer_id: str
    officer_name: str
    investigations: int
    verified_vehicles: int
    high_risk_vehicles: int
    average_risk_score: float
    average_ai_confidence: float | None


@dataclass(frozen=True)
class StationPerformanceItemDto:
    """Station-level investigation volume/performance summary."""

    station_name: str
    investigations: int
    verified_vehicles: int
    high_risk_vehicles: int
    average_risk_score: float
    average_ai_confidence: float | None


@dataclass(frozen=True)
class InvestigationSummaryDto:
    """Top summary metrics for filtered investigations."""

    total_investigations: int
    verified_vehicles: int
    suspicious_vehicles: int
    high_risk_vehicles: int
    average_risk_score: float | None
    average_ai_confidence: float | None
    average_investigation_time_minutes: float | None
    top_vehicle_type: str | None
    top_vehicle_brand: str | None
    most_active_officer: str | None
    most_active_station: str | None


@dataclass(frozen=True)
class InvestigationReportsAnalyticsDto:
    """Aggregated analytics shown above the investigation table."""

    investigation_summary: str
    totals: InvestigationSummaryDto
    risk_distribution: tuple[DistributionItemDto, ...] = field(default_factory=tuple)
    vehicle_type_distribution: tuple[DistributionItemDto, ...] = field(default_factory=tuple)
    brand_distribution: tuple[DistributionItemDto, ...] = field(default_factory=tuple)
    officer_performance: tuple[OfficerPerformanceItemDto, ...] = field(default_factory=tuple)
    station_performance: tuple[StationPerformanceItemDto, ...] = field(default_factory=tuple)
    verification_status_distribution: tuple[DistributionItemDto, ...] = field(default_factory=tuple)
    daily_investigation_trend: tuple[DailyInvestigationTrendPointDto, ...] = field(
        default_factory=tuple
    )
    weekly_investigation_trend: tuple[PeriodInvestigationTrendPointDto, ...] = field(
        default_factory=tuple
    )
    monthly_investigation_trend: tuple[PeriodInvestigationTrendPointDto, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class InvestigationReportListItemDto:
    """Single investigation row in the department reporting table."""

    scanned_at: datetime
    completed_at: datetime
    investigation_id: str
    registration_number: str
    owner: str | None
    vehicle: str | None
    brand: str | None
    model: str | None
    officer_id: str
    officer_name: str
    station_name: str | None
    district: str | None
    police_station: str | None
    risk_score: float
    risk_level: str
    investigation_status: str
    verification_status: str | None
    ai_confidence: float | None
    report_id: str | None
    report_download_url: str | None
    vehicle_type: str | None = None
    verification_message: str | None = None


@dataclass(frozen=True)
class InvestigationReportsQueryResult:
    """Full page payload for the Investigation Reports screen."""

    analytics: InvestigationReportsAnalyticsDto
    items: tuple[InvestigationReportListItemDto, ...]
    pagination: InvestigationReportsPaginationDto
    generated_at: datetime


@dataclass(frozen=True)
class InvestigationReportExportRowDto:
    """Flattened export row for CSV/Excel/PDF table sections."""

    date: str
    time: str
    investigation_id: str
    registration_number: str
    owner: str
    vehicle: str
    brand: str
    model: str
    officer: str
    district: str
    police_station: str
    risk_score: str
    risk_level: str
    investigation_status: str
    verification_status: str
    ai_confidence: str
    report_download: str


@dataclass(frozen=True)
class InvestigationReportExportBundleDto:
    """Export payload bundle for department-level report generation."""

    filters: InvestigationReportsFilters
    analytics: InvestigationReportsAnalyticsDto
    rows: tuple[InvestigationReportExportRowDto, ...]
    generated_at: datetime


@dataclass(frozen=True)
class InvestigationReportExportResult:
    """Binary export output."""

    filename: str
    content_type: str
    content: bytes
