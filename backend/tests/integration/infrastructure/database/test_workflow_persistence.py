"""Workflow persistence integration tests."""

import io
import uuid
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.history_dto import SaveCompletedScanCommand
from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeCommand,
    RenderedReportDto,
    SaveDashboardSnapshotCommand,
    SaveOfficerActivityCommand,
    SaveRiskAssessmentCommand,
    SaveVerificationResultCommand,
)
from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand, OcrResultDto
from sentinel_anpr.infrastructure.database.init_demo_database import initialize_demo_database
from sentinel_anpr.infrastructure.database.models.dashboard.dashboard_snapshot_model import (
    DashboardSnapshotModel,
)
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import (
    OfficerActivityModel,
)
from sentinel_anpr.infrastructure.database.models.risk.risk_assessment_model import RiskAssessmentModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,
)
from sentinel_anpr.infrastructure.database.repositories.dashboard.sqlite_dashboard_snapshot_repository import (
    SqliteDashboardSnapshotRepository,
)
from sentinel_anpr.infrastructure.database.repositories.investigation_reports.sqlite_report_repository import (
    SqliteReportRepository,
)
from sentinel_anpr.infrastructure.database.repositories.officer_activity.sqlite_officer_activity_repository import (
    SqliteOfficerActivityRepository,
)
from sentinel_anpr.infrastructure.database.repositories.risk.sqlite_risk_assessment_repository import (
    SqliteRiskAssessmentRepository,
)
from sentinel_anpr.infrastructure.database.repositories.scan_history.sqlite_scan_repository import (
    SqliteScanRepository,
)
from sentinel_anpr.infrastructure.database.repositories.verification.sqlite_verification_result_repository import (
    SqliteVerificationResultRepository,
)
from sentinel_anpr.infrastructure.database.repositories.workflow.sqlite_workflow_persistence_repository import (
    SqliteWorkflowPersistenceRepository,
)


@pytest.fixture
def persistence_context(tmp_path: Path):
    db_path = tmp_path / "persistence.db"
    engine = create_engine(f"sqlite:///{db_path}")
    initialize_demo_database(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    report_dir = tmp_path / "reports"
    scan_repository = SqliteScanRepository(session_factory=session_factory)
    report_repository = SqliteReportRepository(
        session_factory=session_factory,
        storage_dir=str(report_dir),
    )
    workflow_repository = SqliteWorkflowPersistenceRepository(
        session_factory=session_factory,
        scan_repository=scan_repository,
        verification_repository=SqliteVerificationResultRepository(session_factory),
        risk_assessment_repository=SqliteRiskAssessmentRepository(session_factory),
        officer_activity_repository=SqliteOfficerActivityRepository(session_factory),
        dashboard_snapshot_repository=SqliteDashboardSnapshotRepository(session_factory),
        report_repository=report_repository,
        report_storage_dir=str(report_dir),
    )
    return engine, session_factory, workflow_repository, report_dir


def _jpeg_bytes() -> bytes:
    image = Image.new("RGB", (320, 180), color=(20, 30, 40))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _persist_command(*, include_report: bool = True) -> PersistWorkflowOutcomeCommand:
    now = __import__("datetime").datetime.now(__import__("datetime").UTC)
    scan_id = str(uuid.uuid4())
    report_command = GenerateInvestigationReportCommand(
        officer_id="officer-1",
        officer_name="Officer One",
        badge_number="AP001",
        officer_rank="SI",
        vehicle_image_bytes=_jpeg_bytes(),
        detected_plate="AP99ZZ9999",
        ocr_result=OcrResultDto(
            registration_number="AP99ZZ9999",
            detected_plate_text="AP99ZZ9999",
            ocr_confidence=0.95,
        ),
        vehicle_details=None,
        risk_score=0.1,
        risk_level="low",
        recommendation="Proceed",
    )
    rendered = RenderedReportDto(
        pdf_bytes=b"%PDF-1.4 test",
        title="Investigation Report — AP99ZZ9999",
        checksum_sha256="deadbeef",
        generated_at=now,
        plate_text="AP99ZZ9999",
        risk_score=0.1,
        risk_level="low",
    )
    return PersistWorkflowOutcomeCommand(
        scan=SaveCompletedScanCommand(
            officer_id="officer-1",
            officer_name="Officer One",
            plate_text="AP99ZZ9999",
            risk_score=0.1,
            risk_level="low",
            vehicle_id=None,
            location_label="Checkpoint A",
            correlation_id="workflow-1",
            ocr_confidence=0.95,
            image_storage_key="uploads/test.jpg",
            scanned_at=now,
        ),
        verification=SaveVerificationResultCommand(
            scan_id="",
            lookup_status="not_found",
            message="Vehicle not in registry",
            vehicle_id=None,
            verified_at=now,
        ),
        risk=SaveRiskAssessmentCommand(
            scan_id="",
            risk_score=0.1,
            risk_level="low",
            explanation="Low risk",
            recommendation="Proceed",
            policy_version="risk-engine-v1",
            assessed_at=now,
        ),
        officer_activities=(
            SaveOfficerActivityCommand(
                officer_id="officer-1",
                officer_name="Officer One",
                scan_id=None,
                activity_type="upload",
                description="Vehicle image stored",
                status="success",
                occurred_at=now,
                correlation_id="workflow-1",
            ),
        ),
        dashboard_snapshot=SaveDashboardSnapshotCommand(
            total_scans=0,
            verified_vehicles=0,
            suspicious_vehicles=0,
            pending_verification=0,
            snapshot_at=now,
        ),
        report=rendered if include_report else None,
        report_command=report_command if include_report else None,
        scan_id=scan_id,
    )


def test_persist_workflow_outcome_writes_all_tables(persistence_context) -> None:
    engine, session_factory, workflow_repository, report_dir = persistence_context
    command = _persist_command()
    result = workflow_repository.persist_workflow_outcome(command)

    with Session(engine) as session:
        assert session.get(ScanModel, result.scan_id) is not None
        assert session.scalar(
            select(VerificationResultModel).where(
                VerificationResultModel.scan_id == result.scan_id
            )
        )
        assert session.scalar(
            select(RiskAssessmentModel).where(RiskAssessmentModel.scan_id == result.scan_id)
        )
        assert session.scalar(
            select(OfficerActivityModel).where(OfficerActivityModel.scan_id == result.scan_id)
        )
        assert session.scalar(
            select(DashboardSnapshotModel).where(
                DashboardSnapshotModel.snapshot_id == result.snapshot_id
            )
        )
        report = session.get(ReportModel, result.report_id)
        assert report is not None
        assert report.scan_id == result.scan_id
        assert (report_dir / f"{result.report_id}.pdf").exists()


def test_persist_workflow_outcome_rolls_back_on_failure(persistence_context) -> None:
    engine, session_factory, workflow_repository, report_dir = persistence_context
    command = _persist_command()
    broken_command = PersistWorkflowOutcomeCommand(
        scan=command.scan,
        verification=command.verification,
        risk=command.risk,
        officer_activities=command.officer_activities,
        dashboard_snapshot=command.dashboard_snapshot,
        report=command.report,
        report_command=command.report_command,
        scan_id=command.scan_id,
    )

    class _BrokenReportRepository(SqliteReportRepository):
        def save_report(self, **kwargs):
            raise RuntimeError("simulated report failure")

    broken_repository = SqliteWorkflowPersistenceRepository(
        session_factory=session_factory,
        scan_repository=SqliteScanRepository(session_factory),
        verification_repository=SqliteVerificationResultRepository(session_factory),
        risk_assessment_repository=SqliteRiskAssessmentRepository(session_factory),
        officer_activity_repository=SqliteOfficerActivityRepository(session_factory),
        dashboard_snapshot_repository=SqliteDashboardSnapshotRepository(session_factory),
        report_repository=_BrokenReportRepository(session_factory, str(report_dir)),
        report_storage_dir=str(report_dir),
    )

    with pytest.raises(RuntimeError, match="simulated report failure"):
        broken_repository.persist_workflow_outcome(broken_command)

    with Session(engine) as session:
        assert session.get(ScanModel, command.scan_id) is None
        assert not list(report_dir.glob("*.pdf"))
