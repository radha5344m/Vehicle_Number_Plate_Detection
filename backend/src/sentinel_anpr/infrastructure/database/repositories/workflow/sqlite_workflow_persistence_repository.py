"""Transactional workflow persistence repository."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from dataclasses import replace
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.persistence_dto import (
    PersistWorkflowOutcomeCommand,
    PersistWorkflowOutcomeResult,
    SaveDashboardSnapshotCommand,
)
from sentinel_anpr.application.ports.outbound.dashboard_snapshot_repository_port import (
    DashboardSnapshotRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.officer_activity_repository_port import (
    OfficerActivityRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.report_repository_port import ReportRepositoryPort
from sentinel_anpr.application.ports.outbound.risk_assessment_repository_port import (
    RiskAssessmentRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.scan_repository_port import ScanRepositoryPort
from sentinel_anpr.application.ports.outbound.verification_result_repository_port import (
    VerificationResultRepositoryPort,
)
from sentinel_anpr.application.ports.outbound.workflow_persistence_port import WorkflowPersistencePort
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel

_SUSPICIOUS_LEVELS = ("high", "critical")


class SqliteWorkflowPersistenceRepository(WorkflowPersistencePort):
    """Persist workflow artifacts atomically using repository ports."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        scan_repository: ScanRepositoryPort,
        verification_repository: VerificationResultRepositoryPort,
        risk_assessment_repository: RiskAssessmentRepositoryPort,
        officer_activity_repository: OfficerActivityRepositoryPort,
        dashboard_snapshot_repository: DashboardSnapshotRepositoryPort,
        report_repository: ReportRepositoryPort,
        report_storage_dir: str,
    ) -> None:
        self._session_factory = session_factory
        self._scan_repository = scan_repository
        self._verification_repository = verification_repository
        self._risk_assessment_repository = risk_assessment_repository
        self._officer_activity_repository = officer_activity_repository
        self._dashboard_snapshot_repository = dashboard_snapshot_repository
        self._report_repository = report_repository
        self._report_storage_dir = Path(report_storage_dir)

    def persist_workflow_outcome(
        self,
        command: PersistWorkflowOutcomeCommand,
    ) -> PersistWorkflowOutcomeResult:
        scan_id = command.scan_id or str(uuid.uuid4())
        verification_id = str(uuid.uuid4())
        assessment_id = str(uuid.uuid4())
        snapshot_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4()) if command.report is not None else None
        pdf_path: Path | None = None
        resolved_scan_id = scan_id

        if report_id is not None:
            pdf_path = self._report_storage_dir / f"{report_id}.pdf"

        try:
            with self._session_factory() as session:
                with session.begin():
                    scan_result = self._scan_repository.save_completed(
                        command.scan,
                        transaction=session,
                        scan_id=scan_id,
                    )
                    resolved_scan_id = scan_result.scan_id

                    self._verification_repository.save_verification_result(
                        replace(command.verification, scan_id=resolved_scan_id),
                        transaction=session,
                        verification_id=verification_id,
                    )

                    self._risk_assessment_repository.save_risk_assessment(
                        replace(command.risk, scan_id=resolved_scan_id),
                        transaction=session,
                        assessment_id=assessment_id,
                    )

                    activities = tuple(
                        replace(activity, scan_id=resolved_scan_id)
                        for activity in command.officer_activities
                    )
                    self._officer_activity_repository.save_activities(
                        activities,
                        transaction=session,
                    )

                    snapshot = self._build_dashboard_snapshot(session)
                    self._dashboard_snapshot_repository.save_snapshot(
                        snapshot,
                        transaction=session,
                        snapshot_id=snapshot_id,
                    )

                    if command.report is not None and command.report_command is not None:
                        report_result = self._report_repository.save_report(
                            officer_id=command.report_command.officer_id,
                            officer_name=command.report_command.officer_name,
                            plate_text=command.report.plate_text,
                            risk_score=command.report.risk_score,
                            risk_level=command.report.risk_level,
                            title=command.report.title,
                            pdf_bytes=command.report.pdf_bytes,
                            checksum_sha256=command.report.checksum_sha256,
                            generated_at=command.report.generated_at,
                            scan_id=resolved_scan_id,
                            transaction=session,
                            report_id=report_id,
                        )
                        report_id = report_result.report_id
        except Exception:
            if pdf_path is not None and pdf_path.exists():
                pdf_path.unlink(missing_ok=True)
            raise

        return PersistWorkflowOutcomeResult(
            scan_id=resolved_scan_id,
            report_id=report_id,
            verification_id=verification_id,
            risk_assessment_id=assessment_id,
            snapshot_id=snapshot_id,
        )

    def _build_dashboard_snapshot(self, session: Session) -> SaveDashboardSnapshotCommand:
        total_scans = session.scalar(
            select(func.count()).select_from(ScanModel).where(
                ScanModel.processing_status == "completed"
            )
        ) or 0
        verified_vehicles = session.scalar(
            select(func.count()).select_from(ScanModel).where(
                ScanModel.processing_status == "completed",
                ScanModel.vehicle_id.is_not(None),
            )
        ) or 0
        suspicious_vehicles = session.scalar(
            select(func.count()).select_from(ScanModel).where(
                ScanModel.processing_status == "completed",
                ScanModel.risk_level.in_(_SUSPICIOUS_LEVELS),
            )
        ) or 0
        pending_verification = session.scalar(
            select(func.count()).select_from(ScanModel).where(
                ScanModel.processing_status == "completed",
                ScanModel.vehicle_id.is_(None),
            )
        ) or 0

        return SaveDashboardSnapshotCommand(
            total_scans=total_scans,
            verified_vehicles=verified_vehicles,
            suspicious_vehicles=suspicious_vehicles,
            pending_verification=pending_verification,
            snapshot_at=datetime.now(UTC),
        )
