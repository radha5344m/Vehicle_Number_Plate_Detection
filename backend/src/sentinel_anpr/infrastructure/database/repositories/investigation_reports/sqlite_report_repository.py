"""SQLite investigation report repository."""

import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportResult, ReportReferenceDto
from sentinel_anpr.application.ports.outbound.report_repository_port import ReportRepositoryPort
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.infrastructure.database.mappers.report_mapper import to_report_reference_dto
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel


class SqliteReportRepository(ReportRepositoryPort):
    """Persist investigation report metadata and PDF files."""

    def __init__(self, session_factory: sessionmaker[Session], storage_dir: str) -> None:
        self._session_factory = session_factory
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def save_report(
        self,
        *,
        officer_id: str,
        officer_name: str,
        plate_text: str,
        risk_score: float,
        risk_level: str,
        title: str,
        pdf_bytes: bytes,
        checksum_sha256: str,
        generated_at: datetime,
        scan_id: str | None = None,
        transaction: TransactionHandlePort | None = None,
        report_id: str | None = None,
    ) -> GenerateInvestigationReportResult:
        resolved_report_id = report_id or str(uuid.uuid4())
        file_name = f"{resolved_report_id}.pdf"
        file_path = self._storage_dir / file_name
        file_path.write_bytes(pdf_bytes)

        try:
            model = ReportModel(
                report_id=resolved_report_id,
                scan_id=scan_id,
                officer_id=officer_id,
                officer_name=officer_name,
                plate_text=plate_text,
                risk_score=risk_score,
                risk_level=risk_level.lower(),
                title=title,
                file_path=str(file_path),
                file_size_bytes=len(pdf_bytes),
                checksum_sha256=checksum_sha256,
                generated_at=generated_at,
                created_at=datetime.now(UTC),
            )

            if transaction is not None:
                session = transaction  # type: ignore[assignment]
                session.add(model)
            else:
                with self._session_factory() as session:
                    session.add(model)
                    session.commit()
        except Exception:
            if file_path.exists():
                file_path.unlink(missing_ok=True)
            raise

        return GenerateInvestigationReportResult(
            report_id=resolved_report_id,
            title=title,
            file_size_bytes=len(pdf_bytes),
            checksum_sha256=checksum_sha256,
            generated_at=generated_at,
        )

    def get_report(self, report_id: str) -> ReportReferenceDto | None:
        with self._session_factory() as session:
            report = session.scalar(select(ReportModel).where(ReportModel.report_id == report_id))
            if report is None:
                return None
            return to_report_reference_dto(report)

    def load_pdf_bytes(self, report: ReportReferenceDto) -> bytes:
        return Path(report.file_path).read_bytes()

    @staticmethod
    def checksum(pdf_bytes: bytes) -> str:
        """Compute SHA-256 checksum for stored PDF integrity."""
        return hashlib.sha256(pdf_bytes).hexdigest()
