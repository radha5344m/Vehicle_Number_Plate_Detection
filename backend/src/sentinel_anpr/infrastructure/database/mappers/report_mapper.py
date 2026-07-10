"""Investigation report ORM mappers."""

from sentinel_anpr.application.dto.report_dto import ReportReferenceDto
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel


def to_report_reference_dto(model: ReportModel) -> ReportReferenceDto:
    """Map ORM report row to application DTO."""
    return ReportReferenceDto(
        report_id=model.report_id,
        title=model.title,
        officer_id=model.officer_id,
        officer_name=model.officer_name,
        plate_text=model.plate_text,
        risk_score=model.risk_score,
        risk_level=model.risk_level,
        file_path=model.file_path,
        file_size_bytes=model.file_size_bytes,
        checksum_sha256=model.checksum_sha256,
        generated_at=model.generated_at,
    )
