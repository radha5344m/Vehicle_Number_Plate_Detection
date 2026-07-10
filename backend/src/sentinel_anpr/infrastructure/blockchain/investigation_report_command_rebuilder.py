"""Rebuild investigation report commands for integrity verification."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.history_dto import RegistryScanSnapshot, VisionScanSnapshot
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
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel
from sentinel_anpr.infrastructure.database.models.risk.risk_assessment_model import RiskAssessmentModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,
)


class InvestigationReportCommandRebuilder:
    """Rebuild report commands from persisted investigation data."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        upload_storage_dir: str,
    ) -> None:
        self._session_factory = session_factory
        self._upload_storage_dir = Path(upload_storage_dir)

    def rebuild(self, investigation_id: str) -> GenerateInvestigationReportCommand | None:
        with self._session_factory() as session:
            scan = session.get(ScanModel, investigation_id)
            if scan is None:
                return None

            report = session.execute(
                select(ReportModel)
                .where(ReportModel.scan_id == investigation_id)
                .order_by(ReportModel.generated_at.desc())
            ).scalar_one_or_none()
            verification = session.execute(
                select(VerificationResultModel).where(
                    VerificationResultModel.scan_id == investigation_id
                )
            ).scalar_one_or_none()
            risk = session.execute(
                select(RiskAssessmentModel).where(RiskAssessmentModel.scan_id == investigation_id)
            ).scalar_one_or_none()

            vision = self._parse_vision_snapshot(scan.vision_snapshot_json)
            registry = self._parse_registry_snapshot(scan.registry_snapshot_json)
            image_bytes = self._load_image_bytes(scan.image_storage_key)

            vehicle_details = None
            if registry is not None:
                vehicle_details = VehicleDetailsDto(
                    plate_number=registry.plate_number,
                    make=registry.make,
                    model=registry.model,
                    color=registry.color,
                    vehicle_type=registry.vehicle_type,
                    registration_status=registry.registration_status,
                    registered_owner=registry.registered_owner,
                    jurisdiction=registry.jurisdiction,
                    year=registry.year,
                )

            vision_analysis = None
            if vision is not None:
                vision_analysis = VisionAnalysisDto(
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
                    model_version=None,
                )

            return GenerateInvestigationReportCommand(
                officer_id=scan.officer_id,
                officer_name=scan.officer_name,
                badge_number="",
                officer_rank="",
                vehicle_image_bytes=image_bytes,
                detected_plate=scan.plate_text,
                ocr_result=OcrResultDto(
                    registration_number=scan.plate_text,
                    detected_plate_text=scan.plate_text,
                    ocr_confidence=scan.ocr_confidence or 0.0,
                ),
                vehicle_details=vehicle_details,
                risk_score=scan.risk_score,
                risk_level=scan.risk_level,
                recommendation=risk.recommendation if risk is not None else "",
                title=report.title if report is not None else None,
                vision_analysis=vision_analysis,
                attribute_comparison=AttributeComparisonReportDto(items=(), overall_match=None),
                risk_signals=(),
                timeline=(),
                workflow_id=scan.correlation_id,
                scan_id=scan.scan_id,
                location_label=scan.location_label,
                lookup_status=registry.lookup_status if registry else verification.lookup_status if verification else None,
                verification_message=registry.message if registry else verification.message if verification else None,
                risk_explanation=risk.explanation if risk is not None else None,
                investigation_summary=None,
                total_duration_ms=None,
            )

    def _load_image_bytes(self, storage_key: str | None) -> bytes:
        if not storage_key:
            return b""
        path = self._upload_storage_dir / storage_key
        if not path.exists():
            return b""
        return path.read_bytes()

    @staticmethod
    def _parse_vision_snapshot(raw: str | None) -> VisionScanSnapshot | None:
        if not raw:
            return None
        payload = json.loads(raw)
        return VisionScanSnapshot(
            registration_number=payload.get("registration_number"),
            brand=payload.get("brand"),
            model=payload.get("model"),
            color=payload.get("color"),
            vehicle_type=payload.get("vehicle_type"),
            confidence=payload.get("confidence"),
            brand_confidence=payload.get("brand_confidence"),
            color_confidence=payload.get("color_confidence"),
            vehicle_type_confidence=payload.get("vehicle_type_confidence"),
            explanation=payload.get("explanation"),
        )

    @staticmethod
    def _parse_registry_snapshot(raw: str | None) -> RegistryScanSnapshot | None:
        if not raw:
            return None
        payload = json.loads(raw)
        return RegistryScanSnapshot(
            lookup_status=payload.get("lookup_status"),
            message=payload.get("message"),
            vehicle_id=payload.get("vehicle_id"),
            plate_number=payload.get("plate_number"),
            make=payload.get("make"),
            model=payload.get("model"),
            color=payload.get("color"),
            vehicle_type=payload.get("vehicle_type"),
            year=payload.get("year"),
            registration_status=payload.get("registration_status"),
            registered_owner=payload.get("registered_owner"),
            jurisdiction=payload.get("jurisdiction"),
        )
