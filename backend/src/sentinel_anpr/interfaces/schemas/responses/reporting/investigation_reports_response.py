"""Investigation reports response schemas."""

from datetime import datetime

from pydantic import BaseModel


class DistributionItemData(BaseModel):
    label: str
    value: int


class OfficerPerformanceItemData(BaseModel):
    officer_id: str
    officer_name: str
    investigations: int
    verified_vehicles: int
    high_risk_vehicles: int
    average_risk_score: float
    average_ai_confidence: float | None


class DailyInvestigationTrendPointData(BaseModel):
    date: str
    investigations: int


class PeriodInvestigationTrendPointData(BaseModel):
    period: str
    investigations: int


class InvestigationSummaryData(BaseModel):
    investigation_summary: str
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


class StationPerformanceItemData(BaseModel):
    station_name: str
    investigations: int
    verified_vehicles: int
    high_risk_vehicles: int
    average_risk_score: float
    average_ai_confidence: float | None


class InvestigationReportListItemData(BaseModel):
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


class InvestigationReportsPaginationData(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class InvestigationReportsData(BaseModel):
    summary: InvestigationSummaryData
    risk_distribution: list[DistributionItemData]
    vehicle_type_distribution: list[DistributionItemData]
    brand_distribution: list[DistributionItemData]
    officer_performance: list[OfficerPerformanceItemData]
    station_performance: list[StationPerformanceItemData]
    verification_status_distribution: list[DistributionItemData]
    daily_investigation_trend: list[DailyInvestigationTrendPointData]
    weekly_investigation_trend: list[PeriodInvestigationTrendPointData]
    monthly_investigation_trend: list[PeriodInvestigationTrendPointData]
    items: list[InvestigationReportListItemData]
    pagination: InvestigationReportsPaginationData
    generated_at: datetime
