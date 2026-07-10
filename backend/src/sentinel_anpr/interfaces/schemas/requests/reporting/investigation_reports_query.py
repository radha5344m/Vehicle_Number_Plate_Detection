"""Investigation reports query request schema."""

from pydantic import BaseModel, Field

from sentinel_anpr.application.dto.investigation_reports_dto import InvestigationSortBy


class InvestigationReportsQueryRequest(BaseModel):
    """Validated query params for the Investigation Reports module."""

    from_date: str | None = Field(default=None, alias="from")
    to_date: str | None = Field(default=None, alias="to")
    officer: str | None = None
    police_station: str | None = None
    risk_level: str | None = None
    vehicle_type: str | None = None
    vehicle_brand: str | None = None
    registration_number: str | None = None
    verification_status: str | None = None
    ai_confidence_min: float | None = Field(default=None, ge=0.0, le=1.0)
    ai_confidence_max: float | None = Field(default=None, ge=0.0, le=1.0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: InvestigationSortBy = InvestigationSortBy.SCANNED_AT
    sort_desc: bool = True
