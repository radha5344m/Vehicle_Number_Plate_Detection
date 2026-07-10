"""Selected vehicle verification orchestration tests."""

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
from sentinel_anpr.application.dto.plate_detection_dto import DetectedPlateDto
from sentinel_anpr.application.dto.scene_analysis_dto import PlateAssignmentDto, SceneAnalysisContextDto
from sentinel_anpr.application.dto.vehicle_detection_dto import (
    DetectedVehicleDto,
    SelectedVehicleRegionDto,
)
from sentinel_anpr.application.dto.vehicle_dto import (
    LookupStatus,
    LookupVehicleResult,
    VehicleRecordDto,
)
from sentinel_anpr.application.dto.workflow_dto import (
    RunVehicleVerificationWorkflowCommand,
    WorkflowStatus,
)
from sentinel_anpr.application.ports.vision_ai_service import VisionAnalysisResult
from sentinel_anpr.application.use_cases.orchestration.run_selected_vehicles_verification_workflow_use_case import (
    RunSelectedVehiclesVerificationWorkflowUseCase,
)
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
    def __init__(self) -> None:
        self.received_sizes: list[int] = []
        self.calls = 0

    def analyze_vehicle_image(self, image_bytes: bytes) -> VisionAnalysisResult:
        self.calls += 1
        self.received_sizes.append(len(image_bytes))
        return VisionAnalysisResult(
            registration_number="AP09AB1234",
            vehicle_color="white",
            vehicle_type="car",
            brand="Toyota",
            model="Innova",
            confidence=0.88,
            explanation="Analyzed cropped region",
        )


class _FakeLookup:
    def execute(self, command):
        return LookupVehicleResult(
            lookup_status=LookupStatus.FOUND,
            vehicle=VehicleRecordDto(
                vehicle_id="veh-1",
                plate_number=command.plate,
                jurisdiction="AP",
                make="Toyota",
                model="Innova",
                color="White",
                year=2020,
                vehicle_type="car",
                registration_status="active",
                registered_owner="Owner",
                registry_external_id="RTO-1",
                registry_synced_at=datetime.now(UTC),
            ),
            message="Vehicle found",
        )


class _FakeRisk:
    def execute(self, command):
        del command
        return AssessRiskResult(
            risk_score=0.1,
            risk_level=RiskLevel.LOW,
            explanation="Low risk",
            recommendation="Routine check",
            policy_version="risk-engine-v1",
            signals=(),
        )


class _FakePersist:
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
            risk_score=0.1,
            risk_level="low",
        )


class _FakeSceneDetection:
    def analyze_scene(self, image_bytes: bytes) -> SceneAnalysisContextDto:
        del image_bytes
        return SceneAnalysisContextDto(
            raw_vehicles=(
                DetectedVehicleDto("vehicle-1", 0.1, 0.1, 0.35, 0.5, 0.9, "car"),
                DetectedVehicleDto("vehicle-2", 0.55, 0.15, 0.3, 0.45, 0.88, "suv"),
            ),
            raw_plates=(
                DetectedPlateDto("plate-1", 0.18, 0.5, 0.14, 0.05, 0.9, None),
                DetectedPlateDto("plate-2", 0.62, 0.52, 0.13, 0.05, 0.88, None),
            ),
            assignments=(
                PlateAssignmentDto("plate-1", "vehicle-1"),
                PlateAssignmentDto("plate-2", "vehicle-2"),
            ),
            image_width=1280,
            image_height=960,
        )

    def detect_vehicles(self, image_bytes: bytes) -> tuple[DetectedVehicleDto, ...]:
        del image_bytes
        return (
            DetectedVehicleDto("detected-1", 0.1, 0.1, 0.35, 0.5, 0.9, "car"),
            DetectedVehicleDto("detected-2", 0.55, 0.15, 0.3, 0.45, 0.88, "suv"),
        )

    def mask_regions_for_selection(
        self,
        image_bytes: bytes,
        selected_vehicle_id: str,
        scene_context: SceneAnalysisContextDto | None = None,
    ) -> tuple[SelectedVehicleRegionDto, ...]:
        del image_bytes, scene_context
        if selected_vehicle_id == "vehicle-1":
            return (
                SelectedVehicleRegionDto("vehicle-2", 0.55, 0.15, 0.3, 0.45),
                SelectedVehicleRegionDto("plate-2", 0.62, 0.52, 0.13, 0.05),
            )
        return (
            SelectedVehicleRegionDto("vehicle-1", 0.1, 0.1, 0.35, 0.5),
            SelectedVehicleRegionDto("plate-1", 0.18, 0.5, 0.14, 0.05),
        )


def _image_bytes() -> bytes:
    image = Image.new("RGB", (1280, 960), color=(30, 90, 180))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _single_workflow(vision: _FakeVision) -> RunVisionVerificationWorkflowUseCase:
    return RunVisionVerificationWorkflowUseCase(
        upload_vehicle_image_use_case=_FakeUpload(),
        vision_ai_service=vision,
        lookup_vehicle_use_case=_FakeLookup(),
        assess_risk_use_case=_FakeRisk(),
        persist_workflow_outcome_use_case=_FakePersist(),
        generate_investigation_report_use_case=_FakeReport(),
        lookup_challans_use_case=_FakeChallanLookup(),
        logger=_FakeLogger(),
        workflow_progress=None,
    )


def test_selected_vehicle_workflow_analyzes_scene_once_for_batch() -> None:
    class _CountingSceneDetection(_FakeSceneDetection):
        def __init__(self) -> None:
            self.analyze_calls = 0

        def analyze_scene(self, image_bytes: bytes) -> SceneAnalysisContextDto:
            self.analyze_calls += 1
            return super().analyze_scene(image_bytes)

    scene = _CountingSceneDetection()
    vision = _FakeVision()
    use_case = RunSelectedVehiclesVerificationWorkflowUseCase(
        single_vehicle_workflow=_single_workflow(vision),
        scene_detection_service=scene,
        logger=_FakeLogger(),
    )
    command = RunVehicleVerificationWorkflowCommand(
        officer_id="officer-1",
        officer_name="Test Officer",
        badge_number="AP001",
        officer_rank="Constable",
        image_bytes=_image_bytes(),
        content_type="image/jpeg",
        original_filename="scene.jpg",
        selected_regions=(
            SelectedVehicleRegionDto("vehicle-1", 0.1, 0.1, 0.35, 0.5),
            SelectedVehicleRegionDto("vehicle-2", 0.55, 0.15, 0.3, 0.45),
        ),
    )

    use_case.execute(command)

    assert scene.analyze_calls == 1


def test_selected_vehicle_workflow_crops_and_runs_one_vision_call_per_region() -> None:
    vision = _FakeVision()
    use_case = RunSelectedVehiclesVerificationWorkflowUseCase(
        single_vehicle_workflow=_single_workflow(vision),
        scene_detection_service=_FakeSceneDetection(),
        logger=_FakeLogger(),
    )
    full_image = _image_bytes()
    command = RunVehicleVerificationWorkflowCommand(
        officer_id="officer-1",
        officer_name="Test Officer",
        badge_number="AP001",
        officer_rank="Constable",
        image_bytes=full_image,
        content_type="image/jpeg",
        original_filename="scene.jpg",
        selected_regions=(
            SelectedVehicleRegionDto("vehicle-1", 0.1, 0.1, 0.35, 0.5),
            SelectedVehicleRegionDto("vehicle-2", 0.55, 0.15, 0.3, 0.45),
        ),
    )

    result = use_case.execute(command)

    assert len(result.investigations) == 2
    assert vision.calls == 2
    assert all(item.status == WorkflowStatus.COMPLETED for item in result.investigations)
    assert all(size < len(full_image) for size in vision.received_sizes)
