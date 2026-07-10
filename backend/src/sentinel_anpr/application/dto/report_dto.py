"""Investigation report data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OcrResultDto:
    """Registration readout included in the report."""

    registration_number: str
    detected_plate_text: str
    ocr_confidence: float


@dataclass(frozen=True)
class VehicleDetailsDto:
    """Vehicle registry details included in the report."""

    plate_number: str | None = None
    make: str | None = None
    model: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    registration_status: str | None = None
    registered_owner: str | None = None
    jurisdiction: str | None = None
    year: int | None = None


@dataclass(frozen=True)
class VisionAnalysisDto:
    """Vision AI observations for the report."""

    registration_number: str | None = None
    brand: str | None = None
    model: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    confidence: float | None = None
    explanation: str | None = None
    color_confidence: float | None = None
    vehicle_type_confidence: float | None = None
    brand_confidence: float | None = None
    model_version: str | None = None


@dataclass(frozen=True)
class AttributeComparisonItemReportDto:
    """Observed vs registered attribute row."""

    attribute: str
    observed: str
    registered: str | None
    matches: bool | None
    confidence: float | None


@dataclass(frozen=True)
class AttributeComparisonReportDto:
    """Attribute comparison block for the report."""

    items: tuple[AttributeComparisonItemReportDto, ...]
    overall_match: bool | None


@dataclass(frozen=True)
class RiskSignalReportDto:
    """Risk signal for the report."""

    name: str
    weight: float
    detail: str


@dataclass(frozen=True)
class TimelineStepReportDto:
    """Investigation timeline step."""

    stage: str
    status: str
    message: str
    duration_ms: int | None = None


@dataclass(frozen=True)
class GenerateInvestigationReportCommand:
    """Inputs for investigation PDF generation."""

    officer_id: str
    officer_name: str
    badge_number: str
    officer_rank: str
    vehicle_image_bytes: bytes
    detected_plate: str
    ocr_result: OcrResultDto
    vehicle_details: VehicleDetailsDto | None
    risk_score: float
    risk_level: str
    recommendation: str
    title: str | None = None
    vision_analysis: VisionAnalysisDto | None = None
    attribute_comparison: AttributeComparisonReportDto | None = None
    risk_signals: tuple[RiskSignalReportDto, ...] = field(default_factory=tuple)
    timeline: tuple[TimelineStepReportDto, ...] = field(default_factory=tuple)
    workflow_id: str | None = None
    scan_id: str | None = None
    location_label: str | None = None
    lookup_status: str | None = None
    verification_message: str | None = None
    risk_explanation: str | None = None
    investigation_summary: str | None = None
    total_duration_ms: int | None = None


@dataclass(frozen=True)
class GenerateInvestigationReportResult:
    """Generated report metadata."""

    report_id: str
    title: str
    file_size_bytes: int
    checksum_sha256: str
    generated_at: datetime


@dataclass(frozen=True)
class ReportReferenceDto:
    """Stored report metadata."""

    report_id: str
    title: str
    officer_id: str
    officer_name: str
    plate_text: str
    risk_score: float
    risk_level: str
    file_path: str
    file_size_bytes: int
    checksum_sha256: str
    generated_at: datetime


@dataclass(frozen=True)
class DownloadInvestigationReportResult:
    """PDF download payload."""

    report_id: str
    filename: str
    content_type: str
    pdf_bytes: bytes
