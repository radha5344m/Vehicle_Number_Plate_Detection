"""Generate an investigation report PDF."""

from datetime import UTC, datetime
import hashlib

from sentinel_anpr.application.dto.persistence_dto import RenderedReportDto
from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand
from sentinel_anpr.application.ports.outbound.pdf_generator_port import PdfGeneratorPort
from sentinel_anpr.application.ports.outbound.report_repository_port import ReportRepositoryPort
from sentinel_anpr.application.services.investigation_report_reasoning import (
    compose_investigation_reasoning,
)
from sentinel_anpr.application.services.report_checksum import checksum_pdf
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.domain.reporting.entities.investigation_report_content import (
    AttributeComparisonItemSection,
    AttributeComparisonSection,
    InvestigationMetadataSection,
    InvestigationReportContent,
    OcrReportSection,
    OfficerReportSection,
    RiskSignalSection,
    TimelineStepSection,
    VehicleDetailsSection,
    VisionAnalysisSection,
)
from sentinel_anpr.domain.reporting.services.investigation_report_policy import (
    InvestigationReportPolicy,
)


class GenerateInvestigationReportUseCase:
    """Aggregate investigation data and render a professional PDF."""

    def __init__(
        self,
        pdf_generator: PdfGeneratorPort,
        report_repository: ReportRepositoryPort,
        report_policy: InvestigationReportPolicy | None = None,
    ) -> None:
        self._pdf_generator = pdf_generator
        self._report_repository = report_repository
        self._report_policy = report_policy or InvestigationReportPolicy()

    def execute(self, command: GenerateInvestigationReportCommand):
        rendered = self.render_pdf(command)
        return self._report_repository.save_report(
            officer_id=command.officer_id,
            officer_name=command.officer_name,
            plate_text=rendered.plate_text,
            risk_score=rendered.risk_score,
            risk_level=rendered.risk_level,
            title=rendered.title,
            pdf_bytes=rendered.pdf_bytes,
            checksum_sha256=rendered.checksum_sha256,
            generated_at=rendered.generated_at,
        )

    def render_pdf(self, command: GenerateInvestigationReportCommand) -> RenderedReportDto:
        """Validate content and render PDF without persisting."""
        generated_at = datetime.now(UTC)
        plate_text = normalize_registration_number(command.detected_plate)
        title = command.title or f"Police Investigation Report — {plate_text}"
        evidence_checksum = hashlib.sha256(command.vehicle_image_bytes).hexdigest()

        vehicle_details = None
        if command.vehicle_details is not None:
            details = command.vehicle_details
            vehicle_details = VehicleDetailsSection(
                plate_number=details.plate_number,
                make=details.make,
                model=details.model,
                color=details.color,
                vehicle_type=details.vehicle_type,
                registration_status=details.registration_status,
                registered_owner=details.registered_owner,
                jurisdiction=details.jurisdiction,
                year=details.year,
            )

        vision_analysis = None
        if command.vision_analysis is not None:
            vision = command.vision_analysis
            vision_analysis = VisionAnalysisSection(
                registration_number=vision.registration_number,
                brand=vision.brand,
                model=vision.model,
                color=vision.color,
                vehicle_type=vision.vehicle_type,
                confidence=vision.confidence,
                explanation=vision.explanation,
                color_confidence=vision.color_confidence,
                vehicle_type_confidence=vision.vehicle_type_confidence,
                brand_confidence=vision.brand_confidence,
                model_version=vision.model_version,
            )

        attribute_comparison = None
        if command.attribute_comparison is not None:
            attribute_comparison = AttributeComparisonSection(
                items=tuple(
                    AttributeComparisonItemSection(
                        attribute=item.attribute,
                        observed=item.observed,
                        registered=item.registered,
                        matches=item.matches,
                        confidence=item.confidence,
                    )
                    for item in command.attribute_comparison.items
                ),
                overall_match=command.attribute_comparison.overall_match,
            )

        risk_signals = tuple(
            RiskSignalSection(name=signal.name, weight=signal.weight, detail=signal.detail)
            for signal in command.risk_signals
        )
        timeline = tuple(
            TimelineStepSection(
                stage=step.stage,
                status=step.status,
                message=step.message,
                duration_ms=step.duration_ms,
            )
            for step in command.timeline
        )

        reasoning = compose_investigation_reasoning(command)

        content = InvestigationReportContent(
            title=title,
            generated_at=generated_at,
            officer=OfficerReportSection(
                officer_id=command.officer_id,
                officer_name=command.officer_name,
                badge_number=command.badge_number,
                rank=command.officer_rank,
            ),
            detected_plate=plate_text,
            ocr_result=OcrReportSection(
                registration_number=normalize_registration_number(
                    command.ocr_result.registration_number
                ),
                detected_plate_text=command.ocr_result.detected_plate_text,
                ocr_confidence=command.ocr_result.ocr_confidence,
            ),
            vehicle_details=vehicle_details,
            risk_score=round(command.risk_score, 4),
            risk_level=command.risk_level.lower(),
            recommendation=command.recommendation.strip(),
            vehicle_image_bytes=command.vehicle_image_bytes,
            vision_analysis=vision_analysis,
            attribute_comparison=attribute_comparison,
            risk_signals=risk_signals,
            timeline=timeline,
            metadata=InvestigationMetadataSection(
                workflow_id=command.workflow_id,
                scan_id=command.scan_id,
                location_label=command.location_label,
                lookup_status=command.lookup_status,
                verification_message=command.verification_message,
                risk_explanation=command.risk_explanation,
                investigation_summary=command.investigation_summary,
                total_duration_ms=command.total_duration_ms,
                evidence_checksum_sha256=evidence_checksum,
            ),
            ai_reasoning=reasoning,
        )

        self._report_policy.validate(content)
        pdf_bytes = self._pdf_generator.generate_investigation_report(content)
        checksum = checksum_pdf(pdf_bytes)

        return RenderedReportDto(
            pdf_bytes=pdf_bytes,
            title=title,
            checksum_sha256=checksum,
            generated_at=generated_at,
            plate_text=plate_text,
            risk_score=content.risk_score,
            risk_level=content.risk_level,
        )
