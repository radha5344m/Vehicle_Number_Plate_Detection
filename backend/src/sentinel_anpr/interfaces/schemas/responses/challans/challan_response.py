"""Challan response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ViolationMasterData(BaseModel):
    violation_code: str
    violation_name: str
    default_fine_amount: float
    amount_editable: bool


class ChallanItemData(BaseModel):
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


class ChallanDetailData(ChallanItemData):
    investigation_id: str | None
    vehicle_id: str | None
    remarks: str | None
    location_label: str | None
    gps_coordinates: str | None
    evidence_image_path: str | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ChallanPaginationData(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ChallansListData(BaseModel):
    items: list[ChallanItemData]
    pagination: ChallanPaginationData


class ChallanMutationData(BaseModel):
    challan: ChallanDetailData
    pdf_download_url: str | None = None


class ChallanSummaryData(BaseModel):
    outstanding_fine_inr: float
    pending_challans_count: int
    latest_violation: str | None


class VehicleChallanSearchData(BaseModel):
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
    previous_violations: list[str]
    existing_challans: list[ChallanItemData]
    challan_summary: ChallanSummaryData


class DistributionItemData(BaseModel):
    label: str
    value: int


class MonthlyFineCollectionData(BaseModel):
    month: str
    collected_fine_inr: float
    issued_count: int


class ChallanAnalyticsData(BaseModel):
    total_challans: int
    todays_challans: int
    pending_challans: int
    paid_challans: int
    collected_fine_inr: float
    outstanding_fine_inr: float
    most_common_violation: str | None
    top_issuing_officer: str | None
    top_station: str | None
    violation_distribution: list[DistributionItemData]
    monthly_fine_collection: list[MonthlyFineCollectionData]
