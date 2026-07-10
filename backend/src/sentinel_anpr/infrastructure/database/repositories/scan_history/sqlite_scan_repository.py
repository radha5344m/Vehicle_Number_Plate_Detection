"""SQLite scan history repository."""

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.history_dto import (
    PaginationDto,
    QueryScanHistoryResult,
    SaveCompletedScanCommand,
    SaveCompletedScanResult,
    ScanHistoryFilters,
)
from sentinel_anpr.application.ports.outbound.scan_repository_port import ScanRepositoryPort
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.infrastructure.database.mappers.scan_mapper import to_scan_history_item_dto
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel


class SqliteScanRepository(ScanRepositoryPort):
    """Persist and query scan history in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_completed(
        self,
        command: SaveCompletedScanCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        scan_id: str | None = None,
    ) -> SaveCompletedScanResult:
        now = datetime.now(UTC)
        scanned_at = command.scanned_at or now
        completed_at = now
        plate_text = normalize_registration_number(command.plate_text)
        resolved_scan_id = scan_id or str(uuid.uuid4())

        model = ScanModel(
            scan_id=resolved_scan_id,
            officer_id=command.officer_id,
            officer_name=command.officer_name,
            vehicle_id=command.vehicle_id,
            plate_text=plate_text,
            risk_score=command.risk_score,
            risk_level=command.risk_level.lower(),
            processing_status="completed",
            location_label=command.location_label,
            correlation_id=command.correlation_id,
            ocr_confidence=command.ocr_confidence,
            image_storage_key=command.image_storage_key,
            scanned_at=scanned_at,
            completed_at=completed_at,
            created_at=now,
        )

        if transaction is not None:
            session = transaction  # type: ignore[assignment]
            session.add(model)
        else:
            with self._session_factory() as session:
                session.add(model)
                session.commit()

        return SaveCompletedScanResult(
            scan_id=resolved_scan_id,
            plate_text=plate_text,
            scanned_at=scanned_at,
            completed_at=completed_at,
        )

    def list_scans(self, filters: ScanHistoryFilters) -> QueryScanHistoryResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)

        with self._session_factory() as session:
            statement = select(ScanModel).join(
                OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id
            )
            count_statement = (
                select(func.count())
                .select_from(ScanModel)
                .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
            )

            if filters.plate:
                plate = normalize_registration_number(filters.plate)
                statement = statement.where(ScanModel.plate_text == plate)
                count_statement = count_statement.where(ScanModel.plate_text == plate)

            if filters.officer_id:
                statement = statement.where(ScanModel.officer_id == filters.officer_id)
                count_statement = count_statement.where(
                    ScanModel.officer_id == filters.officer_id
                )

            if filters.station_id:
                statement = statement.where(OfficerAuthModel.station_id == filters.station_id)
                count_statement = count_statement.where(
                    OfficerAuthModel.station_id == filters.station_id
                )

            if filters.risk_level:
                risk_level = filters.risk_level.lower()
                statement = statement.where(ScanModel.risk_level == risk_level)
                count_statement = count_statement.where(ScanModel.risk_level == risk_level)

            if filters.from_date:
                statement = statement.where(ScanModel.scanned_at >= filters.from_date)
                count_statement = count_statement.where(
                    ScanModel.scanned_at >= filters.from_date
                )

            if filters.to_date:
                statement = statement.where(ScanModel.scanned_at <= filters.to_date)
                count_statement = count_statement.where(ScanModel.scanned_at <= filters.to_date)

            total_items = session.scalar(count_statement) or 0
            total_pages = max(1, math.ceil(total_items / page_size)) if total_items else 0
            offset = (page - 1) * page_size

            rows = session.scalars(
                statement.order_by(ScanModel.scanned_at.desc()).offset(offset).limit(page_size)
            ).all()

        return QueryScanHistoryResult(
            items=tuple(to_scan_history_item_dto(row) for row in rows),
            pagination=PaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages if total_items else 0,
            ),
        )
