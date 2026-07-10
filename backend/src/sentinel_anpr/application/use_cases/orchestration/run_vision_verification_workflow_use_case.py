"""Vision-driven vehicle verification workflow orchestration.

Performs a single :class:`VisionAiService` analysis of the uploaded image.
The registration number returned by the
vision model drives the vehicle-repository lookup and verification, and the
color/type/brand it reports feed attribute comparison and the risk engine.

The application layer depends only on the ``VisionAiService`` port; it is
unaware of the concrete implementation (Gemini, stub, etc.). Repositories and
domain entities are reused unchanged.
"""

import time
import traceback
import uuid
from datetime import UTC, datetime

from sentinel_anpr.application.dto.attribute_dto import VehicleAttributesResult
from sentinel_anpr.application.dto.history_dto import SaveCompletedScanCommand
from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeCommand,
    SaveDashboardSnapshotCommand,
    SaveOfficerActivityCommand,
    SaveRiskAssessmentCommand,
    SaveVerificationResultCommand,
)
from sentinel_anpr.application.dto.recognition_dto import RecognizePlateResult
from sentinel_anpr.application.dto.report_dto import (
    AttributeComparisonItemReportDto,
    AttributeComparisonReportDto,
    GenerateInvestigationReportCommand,
    OcrResultDto,
    RiskSignalReportDto,
    TimelineStepReportDto,
    VehicleDetailsDto,
    VisionAnalysisDto,
)
from sentinel_anpr.application.dto.risk_dto import AssessRiskCommand, RiskSignalDto
from sentinel_anpr.application.dto.upload_dto import UploadImageCommand
from sentinel_anpr.application.dto.vehicle_dto import LookupVehicleCommand
from sentinel_anpr.application.dto.workflow_dto import (
    AttributeComparisonDto,
    AttributeComparisonItemDto,
    RunVehicleVerificationWorkflowCommand,
    RunVehicleVerificationWorkflowResult,
    VerificationResultDto,
    WorkflowStatus,
    WorkflowStepLog,
)
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.application.ports.vision_ai_service import (
    VisionAiService,
    VisionAnalysisResult,
)
from sentinel_anpr.application.use_cases.ingestion.upload_vehicle_image_use_case import (
    UploadVehicleImageUseCase,
)
from sentinel_anpr.application.use_cases.persistence.persist_workflow_outcome_use_case import (
    PersistWorkflowOutcomeUseCase,
)
from sentinel_anpr.application.use_cases.reporting.generate_investigation_report_use_case import (
    GenerateInvestigationReportUseCase,
)
from sentinel_anpr.application.use_cases.risk.assess_risk_use_case import AssessRiskUseCase
from sentinel_anpr.application.use_cases.vehicle.lookup_vehicle_use_case import LookupVehicleUseCase
from sentinel_anpr.application.use_cases.challans.challan_use_cases import (
    LookupChallansByRegistrationUseCase,
)
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.domain.verification.services.attribute_comparison_policy import (
    AttributeComparisonPolicy,
)
from sentinel_anpr.domain.verification.services.investigation_summary_policy import (
    InvestigationSummaryInput,
    InvestigationSummaryPolicy,
)

_VISION_MODEL_VERSION = "vision-ai"
_UNKNOWN_ATTRIBUTE = "unknown"

STAGE_UPLOAD = "upload"
STAGE_VISION_ANALYSIS = "vision_analysis"
STAGE_REGISTRY_VERIFICATION = "registry_verification"
STAGE_RISK_ASSESSMENT = "risk_assessment"
STAGE_SAVE_INVESTIGATION = "save_investigation"
STAGE_REPORT_GENERATION = "report_generation"


class RunVisionVerificationWorkflowUseCase:
    """Orchestrate upload -> vision analysis -> verify -> risk -> history -> report."""

    def __init__(
        self,
        upload_vehicle_image_use_case: UploadVehicleImageUseCase,
        vision_ai_service: VisionAiService | None,
        lookup_vehicle_use_case: LookupVehicleUseCase,
        assess_risk_use_case: AssessRiskUseCase,
        persist_workflow_outcome_use_case: PersistWorkflowOutcomeUseCase,
        generate_investigation_report_use_case: GenerateInvestigationReportUseCase,
        lookup_challans_use_case: LookupChallansByRegistrationUseCase,
        logger: LoggingPort,
    ) -> None:
        self._upload = upload_vehicle_image_use_case
        self._vision = vision_ai_service
        self._lookup = lookup_vehicle_use_case
        self._lookup_challans = lookup_challans_use_case
        self._risk = assess_risk_use_case
        self._persist_outcome = persist_workflow_outcome_use_case
        self._generate_report = generate_investigation_report_use_case
        self._logger = logger
        self._attribute_comparison = AttributeComparisonPolicy()
        self._investigation_summary = InvestigationSummaryPolicy()

    def execute(
        self,
        command: RunVehicleVerificationWorkflowCommand,
    ) -> RunVehicleVerificationWorkflowResult:
        workflow_id = command.correlation_id or str(uuid.uuid4())
        workflow_started = time.perf_counter()
        steps: list[WorkflowStepLog] = []
        image_bytes = command.image_bytes
        detected_plate: str | None = None
        analysis_confidence: float | None = None

        image_storage_key: str | None = None

        self._logger.info(
            "workflow_started",
            workflow_id=workflow_id,
            detail="Workflow Started",
        )
        self._logger.info(
            "workflow_image_received",
            workflow_id=workflow_id,
            image_bytes=len(image_bytes),
            detail="Image Received",
        )

        try:
            stage_started = time.perf_counter()
            upload_result = self._upload.execute(
                UploadImageCommand(
                    officer_id=command.officer_id,
                    content=image_bytes,
                    content_type=command.content_type,
                    original_filename=command.original_filename,
                )
            )
            image_storage_key = upload_result.storage_key
            self._record_step(
                steps,
                workflow_id,
                STAGE_UPLOAD,
                "success",
                "Vehicle image stored",
                duration_ms=self._elapsed_ms(stage_started),
            )
        except Exception as exc:
            self._log_exception(workflow_id, STAGE_UPLOAD, exc)
            return self._failed(
                workflow_id,
                steps,
                STAGE_UPLOAD,
                str(exc),
                failed_stage=STAGE_UPLOAD,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )

        try:
            stage_started = time.perf_counter()
            self._logger.info(
                "workflow_vision_analysis_started",
                workflow_id=workflow_id,
                detail="Vision Analysis Started",
            )
            if self._vision is None:
                raise RuntimeError("Vision AI service is not configured")
            analysis = self._vision.analyze_vehicle_image(image_bytes)
            analysis_confidence = analysis.confidence
            detected_plate = normalize_registration_number(analysis.registration_number or "")
            self._logger.info(
                "vision_ai_analysis_result",
                workflow_id=workflow_id,
                detail="Vision AI Analysis",
                registration_number=analysis.registration_number,
                vehicle_color=analysis.vehicle_color,
                vehicle_type=analysis.vehicle_type,
                brand=analysis.brand,
                model=analysis.model,
                confidence=analysis.confidence,
                explanation=analysis.explanation,
            )
            self._logger.info(
                "vision_registration_detected",
                workflow_id=workflow_id,
                detail="Registration Number",
                registration_number=analysis.registration_number,
                normalized_registration_number=detected_plate or None,
            )
            if not detected_plate:
                message = analysis.explanation or "Vision AI could not read a registration number"
                return self._failed(
                    workflow_id,
                    steps,
                    STAGE_VISION_ANALYSIS,
                    message,
                    failed_stage=STAGE_VISION_ANALYSIS,
                    registration_number=analysis.registration_number,
                    vision_confidence=analysis_confidence,
                    vehicle_model=analysis.model,
                    vision_explanation=analysis.explanation,
                    total_duration_ms=self._elapsed_ms(workflow_started),
                )
            self._record_step(
                steps,
                workflow_id,
                STAGE_VISION_ANALYSIS,
                "success",
                self._analysis_message(detected_plate, analysis),
                duration_ms=self._elapsed_ms(stage_started),
            )
        except Exception as exc:
            self._log_exception(workflow_id, STAGE_VISION_ANALYSIS, exc)
            return self._failed(
                workflow_id,
                steps,
                STAGE_VISION_ANALYSIS,
                str(exc),
                failed_stage=STAGE_VISION_ANALYSIS,
                vision_confidence=analysis_confidence,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )

        recognition = self._to_recognition_result(detected_plate, analysis)
        attributes = self._to_attributes(analysis)

        try:
            stage_started = time.perf_counter()
            self._logger.info(
                "workflow_vehicle_verification_started",
                workflow_id=workflow_id,
                detail="Vehicle Verification Started",
            )
            lookup_result = self._lookup.execute(LookupVehicleCommand(plate=detected_plate))
            self._logger.info(
                "vehicle_database_lookup",
                workflow_id=workflow_id,
                detail="Database Lookup",
                database_lookup_key=detected_plate,
                vehicle_found=lookup_result.vehicle is not None,
            )
            verification = VerificationResultDto(
                lookup_status=lookup_result.lookup_status,
                message=lookup_result.message,
            )
            self._record_step(
                steps,
                workflow_id,
                STAGE_REGISTRY_VERIFICATION,
                "success",
                lookup_result.message,
                duration_ms=self._elapsed_ms(stage_started),
            )
        except Exception as exc:
            self._log_exception(workflow_id, STAGE_REGISTRY_VERIFICATION, exc)
            return self._failed(
                workflow_id,
                steps,
                STAGE_REGISTRY_VERIFICATION,
                str(exc),
                failed_stage=STAGE_REGISTRY_VERIFICATION,
                registration_number=detected_plate,
                vision_confidence=analysis_confidence,
                vehicle_attributes=attributes,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )

        registry_vehicle = lookup_result.vehicle
        challan_summary = self._lookup_challans.execute(detected_plate)
        comparison_result = self._attribute_comparison.compare(
            observed_color=attributes.color,
            observed_vehicle_type=attributes.vehicle_type,
            observed_brand=attributes.brand,
            color_confidence=attributes.color_confidence,
            vehicle_type_confidence=attributes.vehicle_type_confidence,
            brand_confidence=attributes.brand_confidence,
            registered_color=registry_vehicle.color if registry_vehicle else None,
            registered_vehicle_type=registry_vehicle.vehicle_type if registry_vehicle else None,
            registered_make=registry_vehicle.make if registry_vehicle else None,
        )
        attribute_comparison = AttributeComparisonDto(
            items=tuple(
                AttributeComparisonItemDto(
                    attribute=item.attribute,
                    observed=item.observed,
                    registered=item.registered,
                    matches=item.matches,
                    confidence=item.confidence,
                )
                for item in comparison_result.items
            ),
            overall_match=comparison_result.overall_match,
        )

        try:
            stage_started = time.perf_counter()
            self._logger.info(
                "workflow_risk_engine_started",
                workflow_id=workflow_id,
                detail="Risk Engine Started",
            )
            risk_result = self._risk.execute(
                AssessRiskCommand(
                    ocr_result=recognition,
                    vehicle_record=lookup_result.vehicle,
                    detected_attributes=attributes,
                )
            )
            self._record_step(
                steps,
                workflow_id,
                STAGE_RISK_ASSESSMENT,
                "success",
                f"Risk level {risk_result.risk_level.value}",
                duration_ms=self._elapsed_ms(stage_started),
            )
        except Exception as exc:
            self._log_exception(workflow_id, STAGE_RISK_ASSESSMENT, exc)
            return self._failed(
                workflow_id,
                steps,
                STAGE_RISK_ASSESSMENT,
                str(exc),
                failed_stage=STAGE_RISK_ASSESSMENT,
                registration_number=detected_plate,
                vision_confidence=analysis_confidence,
                vehicle_information=lookup_result.vehicle,
                vehicle_attributes=attributes,
                attribute_comparison=attribute_comparison,
                verification_result=verification,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )

        risk_signals = tuple(
            RiskSignalDto(name=signal.name, weight=signal.weight, detail=signal.detail)
            for signal in risk_result.signals
        )
        investigation_summary = self._investigation_summary.build(
            InvestigationSummaryInput(
                plate_detected=True,
                detection_confidence=analysis_confidence,
                registration_number=detected_plate,
                ocr_confidence=recognition.ocr_confidence,
                vehicle_found=lookup_result.vehicle is not None,
                registration_status=(
                    lookup_result.vehicle.registration_status if lookup_result.vehicle else None
                ),
                attribute_comparison=comparison_result,
                risk_level=risk_result.risk_level.value,
            )
        )

        scan_id = None
        report_id = None
        now = datetime.now(UTC)
        try:
            stage_started = time.perf_counter()
            self._logger.info(
                "workflow_report_generation_started",
                workflow_id=workflow_id,
                detail="Report Generation Started",
            )
            vehicle = lookup_result.vehicle
            report_command = GenerateInvestigationReportCommand(
                officer_id=command.officer_id,
                officer_name=command.officer_name,
                badge_number=command.badge_number,
                officer_rank=command.officer_rank,
                vehicle_image_bytes=image_bytes,
                detected_plate=detected_plate,
                ocr_result=OcrResultDto(
                    registration_number=recognition.registration_number,
                    detected_plate_text=recognition.detected_plate_text,
                    ocr_confidence=recognition.ocr_confidence,
                ),
                vehicle_details=VehicleDetailsDto(
                    plate_number=vehicle.plate_number if vehicle else None,
                    make=vehicle.make if vehicle else None,
                    model=vehicle.model if vehicle else None,
                    color=vehicle.color if vehicle else None,
                    vehicle_type=vehicle.vehicle_type if vehicle else None,
                    registration_status=vehicle.registration_status if vehicle else None,
                    registered_owner=vehicle.registered_owner if vehicle else None,
                    jurisdiction=vehicle.jurisdiction if vehicle else None,
                    year=vehicle.year if vehicle else None,
                ),
                risk_score=risk_result.risk_score,
                risk_level=risk_result.risk_level.value,
                recommendation=risk_result.recommendation,
                vision_analysis=VisionAnalysisDto(
                    registration_number=detected_plate,
                    brand=attributes.brand,
                    model=analysis.model,
                    color=attributes.color,
                    vehicle_type=attributes.vehicle_type,
                    confidence=analysis_confidence,
                    explanation=analysis.explanation,
                    color_confidence=attributes.color_confidence,
                    vehicle_type_confidence=attributes.vehicle_type_confidence,
                    brand_confidence=attributes.brand_confidence,
                    model_version=attributes.model_version,
                ),
                attribute_comparison=AttributeComparisonReportDto(
                    items=tuple(
                        AttributeComparisonItemReportDto(
                            attribute=item.attribute,
                            observed=item.observed,
                            registered=item.registered,
                            matches=item.matches,
                            confidence=item.confidence,
                        )
                        for item in attribute_comparison.items
                    ),
                    overall_match=attribute_comparison.overall_match,
                ),
                risk_signals=tuple(
                    RiskSignalReportDto(
                        name=signal.name,
                        weight=signal.weight,
                        detail=signal.detail,
                    )
                    for signal in risk_signals
                ),
                timeline=tuple(
                    TimelineStepReportDto(
                        stage=step.stage,
                        status=step.status,
                        message=step.message,
                        duration_ms=step.duration_ms,
                    )
                    for step in steps
                ),
                workflow_id=workflow_id,
                location_label=command.location_label,
                lookup_status=(
                    verification.lookup_status.value
                    if hasattr(verification.lookup_status, "value")
                    else str(verification.lookup_status)
                ),
                verification_message=verification.message,
                risk_explanation=risk_result.explanation,
                investigation_summary=investigation_summary,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )
            rendered_report = self._generate_report.render_pdf(report_command)

            officer_activities = tuple(
                SaveOfficerActivityCommand(
                    officer_id=command.officer_id,
                    officer_name=command.officer_name,
                    scan_id=None,
                    activity_type=step.stage,
                    description=step.message,
                    status=step.status,
                    occurred_at=now,
                    correlation_id=workflow_id,
                )
                for step in steps
            ) + (
                SaveOfficerActivityCommand(
                    officer_id=command.officer_id,
                    officer_name=command.officer_name,
                    scan_id=None,
                    activity_type=STAGE_SAVE_INVESTIGATION,
                    description="Investigation saved",
                    status="success",
                    occurred_at=now,
                    correlation_id=workflow_id,
                ),
                SaveOfficerActivityCommand(
                    officer_id=command.officer_id,
                    officer_name=command.officer_name,
                    scan_id=None,
                    activity_type=STAGE_REPORT_GENERATION,
                    description="Investigation report generated",
                    status="success",
                    occurred_at=now,
                    correlation_id=workflow_id,
                ),
            )

            persist_result = self._persist_outcome.execute(
                PersistWorkflowOutcomeCommand(
                    scan=SaveCompletedScanCommand(
                        officer_id=command.officer_id,
                        officer_name=command.officer_name,
                        plate_text=detected_plate,
                        risk_score=risk_result.risk_score,
                        risk_level=risk_result.risk_level.value,
                        vehicle_id=lookup_result.vehicle.vehicle_id
                        if lookup_result.vehicle
                        else None,
                        location_label=command.location_label,
                        correlation_id=workflow_id,
                        ocr_confidence=recognition.ocr_confidence,
                        image_storage_key=image_storage_key,
                    ),
                    verification=SaveVerificationResultCommand(
                        scan_id="",
                        lookup_status=verification.lookup_status.value,
                        message=verification.message,
                        vehicle_id=lookup_result.vehicle.vehicle_id
                        if lookup_result.vehicle
                        else None,
                        verified_at=now,
                    ),
                    risk=SaveRiskAssessmentCommand(
                        scan_id="",
                        risk_score=risk_result.risk_score,
                        risk_level=risk_result.risk_level.value,
                        explanation=risk_result.explanation,
                        recommendation=risk_result.recommendation,
                        policy_version=risk_result.policy_version,
                        assessed_at=now,
                    ),
                    officer_activities=officer_activities,
                    dashboard_snapshot=SaveDashboardSnapshotCommand(
                        total_scans=0,
                        verified_vehicles=0,
                        suspicious_vehicles=0,
                        pending_verification=0,
                        snapshot_at=now,
                    ),
                    report=rendered_report,
                    report_command=report_command,
                )
            )
            scan_id = persist_result.scan_id
            report_id = persist_result.report_id
            self._record_step(
                steps,
                workflow_id,
                STAGE_SAVE_INVESTIGATION,
                "success",
                "Investigation saved",
                duration_ms=self._elapsed_ms(stage_started),
            )
            self._record_step(
                steps,
                workflow_id,
                STAGE_REPORT_GENERATION,
                "success",
                "Investigation report generated",
                duration_ms=0,
            )
        except Exception as exc:
            self._log_exception(workflow_id, STAGE_SAVE_INVESTIGATION, exc)
            return self._failed(
                workflow_id,
                steps,
                STAGE_SAVE_INVESTIGATION,
                str(exc),
                failed_stage=STAGE_SAVE_INVESTIGATION,
                registration_number=detected_plate,
                vision_confidence=analysis_confidence,
                vehicle_information=lookup_result.vehicle,
                vehicle_attributes=attributes,
                attribute_comparison=attribute_comparison,
                verification_result=verification,
                risk_score=risk_result.risk_score,
                risk_level=risk_result.risk_level.value,
                risk_explanation=risk_result.explanation,
                recommendation=risk_result.recommendation,
                investigation_summary=investigation_summary,
                risk_signals=risk_signals,
                total_duration_ms=self._elapsed_ms(workflow_started),
            )

        total_duration_ms = self._elapsed_ms(workflow_started)
        self._logger.info(
            "workflow_completed",
            workflow_id=workflow_id,
            scan_id=scan_id,
            duration_ms=total_duration_ms,
            detail="Workflow Completed",
        )

        return RunVehicleVerificationWorkflowResult(
            status=WorkflowStatus.COMPLETED,
            workflow_id=workflow_id,
            steps=tuple(steps),
            registration_number=detected_plate,
            vision_confidence=analysis_confidence,
            vehicle_information=lookup_result.vehicle,
            vehicle_attributes=attributes,
            attribute_comparison=attribute_comparison,
            verification_result=verification,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level.value,
            risk_explanation=risk_result.explanation,
            recommendation=risk_result.recommendation,
            investigation_summary=investigation_summary,
            risk_signals=risk_signals,
            scan_id=scan_id,
            report_id=report_id,
            failed_stage=None,
            failure_message=None,
            total_duration_ms=total_duration_ms,
            completed_at=datetime.now(UTC),
            vehicle_model=analysis.model,
            vision_explanation=analysis.explanation,
            outstanding_fine_inr=challan_summary.outstanding_fine_inr,
            pending_challans_count=challan_summary.pending_challans_count,
            latest_violation=challan_summary.latest_violation,
        )

    @staticmethod
    def _analysis_message(detected_plate: str, analysis: VisionAnalysisResult) -> str:
        details = [f"Vision AI read plate {detected_plate}"]
        descriptor = " ".join(
            token
            for token in (analysis.vehicle_color, analysis.brand, analysis.model)
            if token
        ).strip()
        if descriptor:
            details.append(f"({descriptor})")
        return " ".join(details)

    def _to_recognition_result(
        self,
        detected_plate: str,
        analysis: VisionAnalysisResult,
    ) -> RecognizePlateResult:
        confidence = analysis.confidence if analysis.confidence is not None else 0.0
        return RecognizePlateResult(
            registration_number=detected_plate,
            detected_plate_text=analysis.registration_number or detected_plate,
            ocr_confidence=confidence,
            char_confidences=(),
            model_version=_VISION_MODEL_VERSION,
        )

    def _to_attributes(self, analysis: VisionAnalysisResult) -> VehicleAttributesResult:
        confidence = analysis.confidence if analysis.confidence is not None else 0.0
        return VehicleAttributesResult(
            color=analysis.vehicle_color or _UNKNOWN_ATTRIBUTE,
            vehicle_type=analysis.vehicle_type or _UNKNOWN_ATTRIBUTE,
            brand=analysis.brand,
            color_confidence=confidence,
            vehicle_type_confidence=confidence,
            brand_confidence=confidence if analysis.brand else None,
            model_version=_VISION_MODEL_VERSION,
        )

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return int((time.perf_counter() - started_at) * 1000)

    def _log_exception(self, workflow_id: str, stage: str, exc: Exception) -> None:
        self._logger.error(
            "workflow_exception",
            workflow_id=workflow_id,
            stage=stage,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            traceback=traceback.format_exc(),
        )

    def _record_step(
        self,
        steps: list[WorkflowStepLog],
        workflow_id: str,
        stage: str,
        status: str,
        message: str,
        *,
        duration_ms: int | None = None,
    ) -> None:
        steps.append(
            WorkflowStepLog(
                stage=stage,
                status=status,
                message=message,
                duration_ms=duration_ms,
            )
        )
        self._logger.info(
            "workflow_step",
            workflow_id=workflow_id,
            stage=stage,
            status=status,
            detail=message,
            duration_ms=duration_ms,
        )

    def _failed(
        self,
        workflow_id: str,
        steps: list[WorkflowStepLog],
        stage: str,
        message: str,
        *,
        failed_stage: str,
        registration_number: str | None = None,
        vision_confidence: float | None = None,
        vehicle_information=None,
        vehicle_attributes=None,
        attribute_comparison=None,
        verification_result=None,
        risk_score: float | None = None,
        risk_level: str | None = None,
        risk_explanation: str | None = None,
        recommendation: str | None = None,
        investigation_summary: str | None = None,
        risk_signals: tuple[RiskSignalDto, ...] = (),
        total_duration_ms: int | None = None,
        vehicle_model: str | None = None,
        vision_explanation: str | None = None,
    ) -> RunVehicleVerificationWorkflowResult:
        steps.append(WorkflowStepLog(stage=stage, status="failed", message=message))
        self._logger.error(
            "workflow_failed",
            workflow_id=workflow_id,
            stage=failed_stage,
            detail=message,
            duration_ms=total_duration_ms,
        )
        return RunVehicleVerificationWorkflowResult(
            status=WorkflowStatus.FAILED,
            workflow_id=workflow_id,
            steps=tuple(steps),
            registration_number=registration_number,
            vision_confidence=vision_confidence,
            vehicle_information=vehicle_information,
            vehicle_attributes=vehicle_attributes,
            attribute_comparison=attribute_comparison,
            verification_result=verification_result,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_explanation=risk_explanation,
            recommendation=recommendation,
            investigation_summary=investigation_summary,
            risk_signals=risk_signals,
            scan_id=None,
            report_id=None,
            failed_stage=failed_stage,
            failure_message=message,
            total_duration_ms=total_duration_ms,
            completed_at=datetime.now(UTC),
            vehicle_model=vehicle_model,
            vision_explanation=vision_explanation,
        )
