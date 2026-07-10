"""Investigation report content aggregate."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OcrReportSection:
    """Registration readout embedded in the investigation report."""

    registration_number: str
    detected_plate_text: str
    ocr_confidence: float


@dataclass(frozen=True)
class VehicleDetailsSection:
    """Registry vehicle details for the report."""

    plate_number: str | None
    make: str | None
    model: str | None
    color: str | None
    vehicle_type: str | None
    registration_status: str | None
    registered_owner: str | None
    jurisdiction: str | None = None
    year: int | None = None


@dataclass(frozen=True)
class OfficerReportSection:
    """Officer metadata for the report header."""

    officer_id: str
    officer_name: str
    badge_number: str
    rank: str


@dataclass(frozen=True)
class VisionAnalysisSection:
    """Vision AI observations included in the report."""

    registration_number: str | None
    brand: str | None
    model: str | None
    color: str | None
    vehicle_type: str | None
    confidence: float | None
    explanation: str | None
    color_confidence: float | None = None
    vehicle_type_confidence: float | None = None
    brand_confidence: float | None = None
    model_version: str | None = None


@dataclass(frozen=True)
class AttributeComparisonItemSection:
    """Single observed-vs-registered comparison row."""

    attribute: str
    observed: str
    registered: str | None
    matches: bool | None
    confidence: float | None


@dataclass(frozen=True)
class AttributeComparisonSection:
    """Attribute comparison summary."""

    items: tuple[AttributeComparisonItemSection, ...]
    overall_match: bool | None


@dataclass(frozen=True)
class RiskSignalSection:
    """Risk signal contributed by the risk engine."""

    name: str
    weight: float
    detail: str


@dataclass(frozen=True)
class TimelineStepSection:
    """Investigation timeline step."""

    stage: str
    status: str
    message: str
    duration_ms: int | None = None


@dataclass(frozen=True)
class InvestigationMetadataSection:
    """Case / workflow identifiers and context."""

    workflow_id: str | None = None
    scan_id: str | None = None
    location_label: str | None = None
    lookup_status: str | None = None
    verification_message: str | None = None
    risk_explanation: str | None = None
    investigation_summary: str | None = None
    total_duration_ms: int | None = None
    evidence_checksum_sha256: str | None = None


@dataclass(frozen=True)
class InvestigationReportContent:
    """Validated content rendered into the investigation PDF."""

    title: str
    generated_at: datetime
    officer: OfficerReportSection
    detected_plate: str
    ocr_result: OcrReportSection
    vehicle_details: VehicleDetailsSection | None
    risk_score: float
    risk_level: str
    recommendation: str
    vehicle_image_bytes: bytes
    vision_analysis: VisionAnalysisSection | None = None
    attribute_comparison: AttributeComparisonSection | None = None
    risk_signals: tuple[RiskSignalSection, ...] = field(default_factory=tuple)
    timeline: tuple[TimelineStepSection, ...] = field(default_factory=tuple)
    metadata: InvestigationMetadataSection | None = None
    ai_reasoning: str | None = None
