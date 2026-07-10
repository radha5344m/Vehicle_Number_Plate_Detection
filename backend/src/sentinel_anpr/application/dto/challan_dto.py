"""Challan management DTOs."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ViolationMasterDto:
    violation_code: str
    violation_name: str
    default_fine_amount: float
    amount_editable: bool


@dataclass(frozen=True)
class ChallanListItemDto:
    id: str
    challan_number: str
    registration_number: str
    owner_name: str | None
    violation_type: str
    violation_description: str | None
    fine_amount: float
    payment_status: str
    officer_id: str
    officer_name: str
    station_id: str
    station_name: str
    issued_at: datetime


@dataclass(frozen=True)
class ChallanDetailDto(ChallanListItemDto):
    investigation_id: str | None
    vehicle_id: str | None
    remarks: str | None
    location_label: str | None
    gps_coordinates: str | None
    evidence_image_path: str | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChallanFilters:
    registration_number: str | None = None
    challan_number: str | None = None
    owner_name: str | None = None
    officer_id: str | None = None
    station_id: str | None = None
    violation_type: str | None = None
    payment_status: str | None = None
    pending_only: bool = False
    issued_from: datetime | None = None
    issued_to: datetime | None = None
    search: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class ChallanPaginationDto:
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True)
class QueryChallansResult:
    items: tuple[ChallanListItemDto, ...]
    pagination: ChallanPaginationDto


@dataclass(frozen=True)
class ChallanSummaryDto:
    outstanding_fine_inr: float
    pending_challans_count: int
    latest_violation: str | None


@dataclass(frozen=True)
class VehicleChallanSearchResult:
    registration_number: str
    vehicle_found: bool
    owner_name: str | None
    vehicle_name: str | None
    brand: str | None
    model: str | None
    color: str | None
    vehicle_type: str | None
    rc_status: str | None
    insurance_status: str
    pollution_status: str
    risk_level: str | None
    outstanding_fine_inr: float
    pending_challans_count: int
    previous_violations: tuple[str, ...]
    existing_challans: tuple[ChallanListItemDto, ...]
    challan_summary: ChallanSummaryDto


@dataclass(frozen=True)
class CreateChallanCommand:
    registration_number: str
    owner_name: str | None
    vehicle_id: str | None
    investigation_id: str | None
    violation_type: str
    violation_description: str | None
    fine_amount: float
    remarks: str | None
    location_label: str | None
    gps_coordinates: str | None
    evidence_image_path: str | None
    officer_id: str
    officer_name: str
    station_id: str
    station_name: str


@dataclass(frozen=True)
class UpdateChallanCommand:
    challan_id: str
    violation_type: str | None
    violation_description: str | None
    fine_amount: float | None
    remarks: str | None
    location_label: str | None
    gps_coordinates: str | None


@dataclass(frozen=True)
class ChallanMutationResult:
    challan: ChallanDetailDto
    pdf_download_url: str | None = None


@dataclass(frozen=True)
class ChallanAccessScope:
    all_access: bool = False
    station_id: str | None = None
    officer_id: str | None = None


@dataclass(frozen=True)
class DistributionItemDto:
    label: str
    value: int


@dataclass(frozen=True)
class MonthlyFineCollectionDto:
    month: str
    collected_fine_inr: float
    issued_count: int


@dataclass(frozen=True)
class ChallanAnalyticsResult:
    total_challans: int
    todays_challans: int
    pending_challans: int
    paid_challans: int
    collected_fine_inr: float
    outstanding_fine_inr: float
    most_common_violation: str | None
    top_issuing_officer: str | None
    top_station: str | None
    violation_distribution: tuple[DistributionItemDto, ...]
    monthly_fine_collection: tuple[MonthlyFineCollectionDto, ...]
