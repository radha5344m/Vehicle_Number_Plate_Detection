"""Vision-driven vehicle verification workflow unit tests."""

import io
from datetime import UTC, datetime

from PIL import Image

from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeResult,
    RenderedReportDto,
)
from sentinel_anpr.application.dto.challan_dto import ChallanSummaryDto
from sentinel_anpr.application.dto.risk_dto import AssessRiskResult
from sentinel_anpr.application.dto.upload_dto import UploadImageResult
from sentinel_anpr.application.dto.vehicle_dto import (
    LookupStatus,
    LookupVehicleResult,
    VehicleRecordDto,
)
from sentinel_anpr.application.dto.workflow_dto import RunVehicleVerificationWorkflowCommand
from sentinel_anpr.application.ports.vision_ai_service import VisionAnalysisResult
from sentinel_anpr.application.use_cases.orchestration.run_vision_verification_workflow_use_case import (
    RunVisionVerificationWorkflowUseCase,
)
from sentinel_anpr.domain.risk.enums.risk_level import RiskLevel


class _FakeLogger:
    def debug(self, message: str, **context) -> None:
        del message, context

    def info(self, message: str, **context) -> None:
        del message, context

    def warning(self, message: str, **context) -> None:
        del message, context

    def error(self, message: str, **context) -> None:
        del message, context


class _FakeChallanLookup:
    def execute(self, registration_number: str) -> ChallanSummaryDto:
        del registration_number
        return ChallanSummaryDto(
            outstanding_fine_inr=0,
            pending_challans_count=0,
            latest_violation=None,
        )


class _FakeUpload:
    def execute(self, command):
        return UploadImageResult(
            upload_id="upload-1",
            storage_key="key",
            original_filename=command.original_filename,
            content_type=command.content_type,
            size_bytes=len(command.content),
            width=640,
            height=360,
            uploaded_at=datetime.now(UTC),
        )


class _FakeVision:
    def __init__(self, registration_number: str | None = "AP09AB1234") -> None:
        self._registration_number = registration_number
        self.calls = 0

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        del image_bytes
        self.calls += 1
        return VisionAnalysisResult(
            registration_number=self._registration_number,
            vehicle_color="white",
            vehicle_type="car",
            brand="Toyota",
            model="Innova",
            confidence=0.88,
            explanation="Analyzed",
        )


class _FakeLookup:
    def __init__(self) -> None:
        self.last_plate: str | None = None

    def execute(self, command):
        self.last_plate = command.plate
        return LookupVehicleResult(
            lookup_status=LookupStatus.FOUND,
            vehicle=VehicleRecordDto(
                vehicle_id="veh-1",
                plate_number="AP09AB1234",
                jurisdiction="AP",
                make="Toyota",
                model="Innova",
                color="White",
                year=2020,
                vehicle_type="car",
                registration_status="active",
                registered_owner="Ravi Kumar",
                registry_external_id="RTO-1",
                registry_synced_at=datetime.now(UTC),
            ),
            message="Found",
        )


class _FakeRisk:
    def execute(self, command):
        del command
        return AssessRiskResult(
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation="Low risk",
            recommendation="Proceed",
            signals=(),
            policy_version="test",
        )


class _FakePersistOutcome:
    def execute(self, command):
        del command
        return PersistWorkflowOutcomeResult(
            scan_id="scan-1",
            report_id="report-1",
            verification_id="verification-1",
            risk_assessment_id="assessment-1",
            snapshot_id="snapshot-1",
        )


class _FakeReport:
    def render_pdf(self, command):
        del command
        return RenderedReportDto(
            pdf_bytes=b"%PDF",
            title="Report",
            checksum_sha256="abc",
            generated_at=datetime.now(UTC),
            plate_text="AP09AB1234",
            risk_score=0.0,
            risk_level="low",
        )


def _jpeg_bytes() -> bytes:
    image = Image.new("RGB", (640, 360), color=(30, 41, 59))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _command() -> RunVehicleVerificationWorkflowCommand:
    return RunVehicleVerificationWorkflowCommand(
        officer_id="officer-1",
        officer_name="Ravi Kumar",
        badge_number="AP001",
        officer_rank="Sub-Inspector",
        image_bytes=_jpeg_bytes(),
        content_type="image/jpeg",
        original_filename="vehicle.jpg",
    )


def _use_case(vision: _FakeVision, lookup: _FakeLookup) -> RunVisionVerificationWorkflowUseCase:
    return RunVisionVerificationWorkflowUseCase(
        upload_vehicle_image_use_case=_FakeUpload(),
        vision_ai_service=vision,
        lookup_vehicle_use_case=lookup,
        assess_risk_use_case=_FakeRisk(),
        persist_workflow_outcome_use_case=_FakePersistOutcome(),
        generate_investigation_report_use_case=_FakeReport(),
        lookup_challans_use_case=_FakeChallanLookup(),
        logger=_FakeLogger(),
    )


def test_vision_workflow_success_uses_vision_output() -> None:
    vision = _FakeVision()
    lookup = _FakeLookup()
    result = _use_case(vision, lookup).execute(_command())

    assert result.status.value == "completed"
    assert vision.calls == 1
    assert lookup.last_plate == "AP09AB1234"
    assert result.registration_number == "AP09AB1234"
    assert result.vision_confidence == 0.88
    assert result.vehicle_attributes is not None
    assert result.vehicle_attributes.color == "white"
    assert result.vehicle_attributes.vehicle_type == "car"
    assert result.vehicle_attributes.brand == "Toyota"
    assert result.vehicle_attributes.model_version == "vision-ai"
    assert result.vehicle_model == "Innova"
    assert result.vision_explanation == "Analyzed"
    assert result.scan_id == "scan-1"
    assert result.report_id == "report-1"
    assert result.investigation_summary is not None
    stages = [step.stage for step in result.steps]
    assert stages[0] == "upload"
    assert stages[1] == "vision_analysis"
    assert "detection" not in stages
    assert "ocr" not in stages
    assert "attributes" not in stages
    assert "analytics" not in stages


def test_vision_workflow_fails_when_no_registration_number() -> None:
    result = _use_case(_FakeVision(registration_number=None), _FakeLookup()).execute(_command())

    assert result.status.value == "failed"
    assert result.failed_stage == "vision_analysis"


def test_vision_workflow_fails_when_service_missing() -> None:
    use_case = RunVisionVerificationWorkflowUseCase(
        upload_vehicle_image_use_case=_FakeUpload(),
        vision_ai_service=None,
        lookup_vehicle_use_case=_FakeLookup(),
        assess_risk_use_case=_FakeRisk(),
        persist_workflow_outcome_use_case=_FakePersistOutcome(),
        generate_investigation_report_use_case=_FakeReport(),
        lookup_challans_use_case=_FakeChallanLookup(),
        logger=_FakeLogger(),
    )
    result = use_case.execute(_command())

    assert result.status.value == "failed"
    assert result.failed_stage == "vision_analysis"
