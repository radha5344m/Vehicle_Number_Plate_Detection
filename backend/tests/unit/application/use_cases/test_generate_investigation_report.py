"""Generate investigation report use case unit tests."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.report_dto import (
    GenerateInvestigationReportCommand,
    GenerateInvestigationReportResult,
    OcrResultDto,
    VehicleDetailsDto,
)
from sentinel_anpr.application.use_cases.reporting.generate_investigation_report_use_case import (
    GenerateInvestigationReportUseCase,
)


class _FakePdfGenerator:
    def generate_investigation_report(self, content) -> bytes:
        del content
        return b"%PDF-1.4 fake"


class _FakeReportRepository:
    def save_report(self, **kwargs) -> GenerateInvestigationReportResult:
        return GenerateInvestigationReportResult(
            report_id="report-123",
            title=kwargs["title"],
            file_size_bytes=len(kwargs["pdf_bytes"]),
            checksum_sha256="abc123",
            generated_at=datetime.now(UTC),
        )

    def get_report(self, report_id: str):
        del report_id
        return None

    def load_pdf_bytes(self, report):
        del report
        return b""


def test_generate_investigation_report() -> None:
    use_case = GenerateInvestigationReportUseCase(
        pdf_generator=_FakePdfGenerator(),
        report_repository=_FakeReportRepository(),
    )
    result = use_case.execute(
        GenerateInvestigationReportCommand(
            officer_id="officer-1",
            officer_name="Ravi Kumar",
            badge_number="AP001",
            officer_rank="Sub-Inspector",
            vehicle_image_bytes=b"image-bytes",
            detected_plate="AP09AB1234",
            ocr_result=OcrResultDto(
                registration_number="AP09AB1234",
                detected_plate_text="AP09AB1234",
                ocr_confidence=0.9,
            ),
            vehicle_details=VehicleDetailsDto(
                make="Toyota",
                model="Innova Crysta",
                color="White",
            ),
            risk_score=0.1,
            risk_level="low",
            recommendation="Proceed with routine checks.",
        )
    )
    assert result.report_id == "report-123"
    assert result.file_size_bytes > 0
