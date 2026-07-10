"""SQLite joined investigation reporting repository."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.investigation_reports_dto import (
    DailyInvestigationTrendPointDto,
    DistributionItemDto,
    InvestigationReportExportBundleDto,
    InvestigationReportExportRowDto,
    InvestigationReportListItemDto,
    InvestigationReportsAnalyticsDto,
    InvestigationReportsFilters,
    InvestigationReportsPaginationDto,
    InvestigationReportsQueryResult,
    InvestigationSummaryDto,
    OfficerPerformanceItemDto,
    PeriodInvestigationTrendPointDto,
    StationPerformanceItemDto,
)
from sentinel_anpr.application.ports.outbound.investigation_reports_query_port import (
    InvestigationReportsQueryPort,
)
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import (
    ReportModel,
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,
)
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,
)
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel

_HIGH_RISK_LEVELS = {"high", "critical"}
_SUSPICIOUS_STATUSES = {"not_found"}


@dataclass(frozen=True)
class _InvestigationRow:
    scanned_at: datetime
    completed_at: datetime
    investigation_id: str
    registration_number: str
    owner: str | None
    brand: str | None
    model: str | None
    year: int | None
    officer_id: str
    officer_name: str
    station_name: str | None
    district: str | None
    police_station: str | None
    risk_score: float
    risk_level: str
    investigation_status: str
    verification_status: str | None
    verification_message: str | None
    ai_confidence: float | None
    report_id: str | None
    vehicle_type: str | None


class SqliteInvestigationReportsQueryRepository(InvestigationReportsQueryPort):
    """Read-only reporting queries over persisted investigations."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def query_investigation_reports(
        self, filters: InvestigationReportsFilters
    ) -> InvestigationReportsQueryResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)
        rows = self._load_rows(filters)
        analytics = self._build_analytics(rows)
        total_items = len(rows)
        total_pages = math.ceil(total_items / page_size) if total_items else 0
        offset = (page - 1) * page_size
        paged_rows = rows[offset : offset + page_size]
        return InvestigationReportsQueryResult(
            analytics=analytics,
            items=tuple(self._to_list_item(row) for row in paged_rows),
            pagination=InvestigationReportsPaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
            generated_at=datetime.now(UTC),
        )

    def export_investigation_reports(
        self, filters: InvestigationReportsFilters
    ) -> InvestigationReportExportBundleDto:
        rows = self._load_rows(filters)
        analytics = self._build_analytics(rows)
        return InvestigationReportExportBundleDto(
            filters=filters,
            analytics=analytics,
            rows=tuple(self._to_export_row(row) for row in rows),
            generated_at=datetime.now(UTC),
        )

    def _load_rows(self, filters: InvestigationReportsFilters) -> list[_InvestigationRow]:
        with self._session_factory() as session:
            statement = self._base_statement()
            statement = self._apply_filters(statement, filters)
            statement = self._apply_sort(statement, filters)
            result = session.execute(statement).all()
        return [self._map_row(row) for row in result]

    @staticmethod
    def _base_statement() -> Select:
        return (
            select(
                ScanModel.scanned_at,
                ScanModel.completed_at,
                ScanModel.scan_id,
                ScanModel.plate_text,
                ScanModel.officer_id,
                ScanModel.officer_name,
                ScanModel.location_label,
                ScanModel.risk_score,
                ScanModel.risk_level,
                ScanModel.ocr_confidence,
                OfficerAuthModel.station_name,
                OfficerAuthModel.district,
                VerificationResultModel.lookup_status,
                VerificationResultModel.message,
                ReportModel.report_id,
                VehicleModel.registered_owner,
                VehicleModel.make,
                VehicleModel.model,
                VehicleModel.year,
                VehicleModel.vehicle_type,
            )
            .select_from(ScanModel)
            .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
            .outerjoin(
                VerificationResultModel,
                VerificationResultModel.scan_id == ScanModel.scan_id,
            )
            .outerjoin(ReportModel, ReportModel.scan_id == ScanModel.scan_id)
            .outerjoin(VehicleModel, VehicleModel.vehicle_id == ScanModel.vehicle_id)
        )

    @staticmethod
    def _apply_filters(statement: Select, filters: InvestigationReportsFilters) -> Select:
        if filters.station_id:
            statement = statement.where(OfficerAuthModel.station_id == filters.station_id)
        if filters.officer_id:
            statement = statement.where(ScanModel.officer_id == filters.officer_id)
        if filters.from_date:
            statement = statement.where(ScanModel.scanned_at >= filters.from_date)
        if filters.to_date:
            statement = statement.where(ScanModel.scanned_at <= filters.to_date)
        if filters.search:
            q = f"%{filters.search.strip()}%"
            statement = statement.where(
                ScanModel.scan_id.ilike(q)
                | ScanModel.plate_text.ilike(q)
                | ScanModel.officer_name.ilike(q)
                | VehicleModel.registered_owner.ilike(q)
                | VehicleModel.make.ilike(q)
                | VehicleModel.model.ilike(q)
            )
        if filters.officer:
            statement = statement.where(ScanModel.officer_name.ilike(f"%{filters.officer.strip()}%"))
        if filters.police_station:
            statement = statement.where(
                OfficerAuthModel.station_name.ilike(f"%{filters.police_station.strip()}%")
            )
        if filters.district:
            statement = statement.where(
                OfficerAuthModel.district.ilike(f"%{filters.district.strip()}%")
            )
        if filters.risk_level:
            statement = statement.where(ScanModel.risk_level == filters.risk_level.lower())
        if filters.vehicle_type:
            statement = statement.where(
                VehicleModel.vehicle_type.ilike(f"%{filters.vehicle_type.strip()}%")
            )
        if filters.vehicle_brand:
            statement = statement.where(
                VehicleModel.make.ilike(f"%{filters.vehicle_brand.strip()}%")
            )
        if filters.registration_number:
            plate = normalize_registration_number(filters.registration_number)
            statement = statement.where(ScanModel.plate_text == plate)
        if filters.owner_name:
            statement = statement.where(
                VehicleModel.registered_owner.ilike(f"%{filters.owner_name.strip()}%")
            )
        if filters.verification_status:
            statement = statement.where(
                VerificationResultModel.lookup_status == filters.verification_status.lower()
            )
        if filters.investigation_status:
            if filters.investigation_status.lower() == "completed":
                statement = statement.where(ScanModel.completed_at.is_not(None))
            elif filters.investigation_status.lower() == "pending":
                statement = statement.where(ScanModel.completed_at.is_(None))
        if filters.ai_confidence_min is not None:
            statement = statement.where(ScanModel.ocr_confidence >= filters.ai_confidence_min)
        if filters.ai_confidence_max is not None:
            statement = statement.where(ScanModel.ocr_confidence <= filters.ai_confidence_max)
        return statement

    @staticmethod
    def _apply_sort(statement: Select, filters: InvestigationReportsFilters) -> Select:
        sort_column = {
            "risk_score": ScanModel.risk_score,
            "ai_confidence": ScanModel.ocr_confidence,
            "officer_name": ScanModel.officer_name,
            "scanned_at": ScanModel.scanned_at,
            "registration_number": ScanModel.plate_text,
            "police_station": OfficerAuthModel.station_name,
        }.get(filters.sort_by.value, ScanModel.scanned_at)
        order = sort_column.desc() if filters.sort_desc else sort_column.asc()
        return statement.order_by(order, ScanModel.scan_id.desc())

    @staticmethod
    def _map_row(row) -> _InvestigationRow:  # noqa: ANN001
        return _InvestigationRow(
            scanned_at=row.scanned_at.astimezone(UTC),
            completed_at=row.completed_at.astimezone(UTC),
            investigation_id=row.scan_id,
            registration_number=row.plate_text,
            owner=row.registered_owner,
            brand=row.make,
            model=row.model,
            year=row.year,
            officer_id=row.officer_id,
            officer_name=row.officer_name,
            station_name=row.station_name,
            district=row.district,
            police_station=row.station_name or row.location_label,
            risk_score=row.risk_score,
            risk_level=row.risk_level,
            investigation_status="completed" if row.completed_at is not None else "pending",
            verification_status=row.lookup_status,
            verification_message=row.message,
            ai_confidence=row.ocr_confidence,
            report_id=row.report_id,
            vehicle_type=row.vehicle_type,
        )

    def _build_analytics(
        self, rows: list[_InvestigationRow]
    ) -> InvestigationReportsAnalyticsDto:
        total = len(rows)
        verified = sum(1 for row in rows if row.verification_status == "found")
        suspicious = sum(
            1
            for row in rows
            if row.risk_level in _HIGH_RISK_LEVELS
            or row.verification_status in _SUSPICIOUS_STATUSES
            or row.risk_score >= 0.5
        )
        high_risk = sum(1 for row in rows if row.risk_level in _HIGH_RISK_LEVELS)
        avg_risk = (sum(row.risk_score for row in rows) / total) if total else None
        confidence_values = [row.ai_confidence for row in rows if row.ai_confidence is not None]
        avg_conf = sum(confidence_values) / len(confidence_values) if confidence_values else None

        risk_counts = Counter(row.risk_level for row in rows if row.risk_level)
        vehicle_type_counts = Counter((row.vehicle_type or "Unknown") for row in rows)
        brand_counts = Counter((row.brand or "Unknown") for row in rows)
        station_counts = Counter((row.station_name or "Unknown") for row in rows)
        verification_status_counts = Counter(
            (row.verification_status or "unknown") for row in rows
        )
        by_day: dict[str, int] = defaultdict(int)
        by_week: dict[str, int] = defaultdict(int)
        by_month: dict[str, int] = defaultdict(int)
        by_officer: dict[tuple[str, str], list[_InvestigationRow]] = defaultdict(list)
        by_station: dict[str, list[_InvestigationRow]] = defaultdict(list)
        investigation_durations = []
        for row in rows:
            by_day[row.scanned_at.strftime("%Y-%m-%d")] += 1
            iso = row.scanned_at.isocalendar()
            by_week[f"{iso.year}-W{iso.week:02d}"] += 1
            by_month[row.scanned_at.strftime("%Y-%m")] += 1
            by_officer[(row.officer_id, row.officer_name)].append(row)
            by_station[row.station_name or "Unknown"].append(row)
            if row.completed_at is not None:
                investigation_durations.append(
                    (row.completed_at - row.scanned_at).total_seconds() / 60
                )

        officer_performance = []
        for (officer_id, officer_name), items in sorted(
            by_officer.items(), key=lambda pair: len(pair[1]), reverse=True
        ):
            confidences = [item.ai_confidence for item in items if item.ai_confidence is not None]
            officer_performance.append(
                OfficerPerformanceItemDto(
                    officer_id=officer_id,
                    officer_name=officer_name,
                    investigations=len(items),
                    verified_vehicles=sum(
                        1 for item in items if item.verification_status == "found"
                    ),
                    high_risk_vehicles=sum(
                        1 for item in items if item.risk_level in _HIGH_RISK_LEVELS
                    ),
                    average_risk_score=sum(item.risk_score for item in items) / len(items),
                    average_ai_confidence=(
                        sum(confidences) / len(confidences) if confidences else None
                    ),
                )
            )

        station_performance = []
        for station_name, items in sorted(
            by_station.items(), key=lambda pair: len(pair[1]), reverse=True
        ):
            confidences = [item.ai_confidence for item in items if item.ai_confidence is not None]
            station_performance.append(
                StationPerformanceItemDto(
                    station_name=station_name,
                    investigations=len(items),
                    verified_vehicles=sum(
                        1 for item in items if item.verification_status == "found"
                    ),
                    high_risk_vehicles=sum(
                        1 for item in items if item.risk_level in _HIGH_RISK_LEVELS
                    ),
                    average_risk_score=sum(item.risk_score for item in items) / len(items),
                    average_ai_confidence=(
                        sum(confidences) / len(confidences) if confidences else None
                    ),
                )
            )

        top_vehicle_type = vehicle_type_counts.most_common(1)[0][0] if vehicle_type_counts else None
        top_vehicle_brand = brand_counts.most_common(1)[0][0] if brand_counts else None
        most_active_officer = officer_performance[0].officer_name if officer_performance else None
        most_active_station = station_performance[0].station_name if station_performance else None
        average_investigation_time = (
            sum(investigation_durations) / len(investigation_durations)
            if investigation_durations
            else None
        )

        return InvestigationReportsAnalyticsDto(
            investigation_summary=self._summary_text(
                total=total,
                verified=verified,
                suspicious=suspicious,
                high_risk=high_risk,
                avg_risk=avg_risk,
                avg_confidence=avg_conf,
            ),
            totals=InvestigationSummaryDto(
                total_investigations=total,
                verified_vehicles=verified,
                suspicious_vehicles=suspicious,
                high_risk_vehicles=high_risk,
                average_risk_score=avg_risk,
                average_ai_confidence=avg_conf,
                average_investigation_time_minutes=average_investigation_time,
                top_vehicle_type=top_vehicle_type,
                top_vehicle_brand=top_vehicle_brand,
                most_active_officer=most_active_officer,
                most_active_station=most_active_station,
            ),
            risk_distribution=tuple(
                DistributionItemDto(label=label, value=value)
                for label, value in sorted(
                    risk_counts.items(),
                    key=lambda item: (self._risk_order(item[0]), item[0]),
                )
            ),
            vehicle_type_distribution=tuple(
                DistributionItemDto(label=label, value=value)
                for label, value in vehicle_type_counts.most_common()
            ),
            brand_distribution=tuple(
                DistributionItemDto(label=label, value=value)
                for label, value in brand_counts.most_common()
            ),
            officer_performance=tuple(officer_performance),
            station_performance=tuple(station_performance),
            verification_status_distribution=tuple(
                DistributionItemDto(label=label, value=value)
                for label, value in sorted(verification_status_counts.items())
            ),
            daily_investigation_trend=tuple(
                DailyInvestigationTrendPointDto(date=day, investigations=count)
                for day, count in sorted(by_day.items())
            ),
            weekly_investigation_trend=tuple(
                PeriodInvestigationTrendPointDto(period=period, investigations=count)
                for period, count in sorted(by_week.items())
            ),
            monthly_investigation_trend=tuple(
                PeriodInvestigationTrendPointDto(period=period, investigations=count)
                for period, count in sorted(by_month.items())
            ),
        )

    @staticmethod
    def _summary_text(
        *,
        total: int,
        verified: int,
        suspicious: int,
        high_risk: int,
        avg_risk: float | None,
        avg_confidence: float | None,
    ) -> str:
        if total == 0:
            return "No investigations matched the selected filters."
        avg_risk_text = (
            f"{avg_risk * 100:.1f}%" if avg_risk is not None else "not available"
        )
        avg_confidence_text = (
            f"{avg_confidence * 100:.1f}%"
            if avg_confidence is not None
            else "not available"
        )
        return (
            f"{total} investigations matched the selected filters. "
            f"{verified} were registry-verified, {suspicious} were flagged as suspicious, and {high_risk} were classified as high risk. "
            f"Average risk score is {avg_risk_text} and average AI confidence is {avg_confidence_text}."
        )

    @staticmethod
    def _risk_order(level: str) -> int:
        return {"low": 0, "medium": 1, "high": 2, "critical": 3}.get(level, 99)

    @staticmethod
    def _to_list_item(row: _InvestigationRow) -> InvestigationReportListItemDto:
        vehicle = " ".join(
            part for part in [row.brand, row.model, str(row.year) if row.year else None] if part
        ) or None
        return InvestigationReportListItemDto(
            scanned_at=row.scanned_at,
            completed_at=row.completed_at,
            investigation_id=row.investigation_id,
            registration_number=row.registration_number,
            owner=row.owner,
            vehicle=vehicle,
            brand=row.brand,
            model=row.model,
            officer_id=row.officer_id,
            officer_name=row.officer_name,
            station_name=row.station_name,
            district=row.district,
            police_station=row.police_station,
            risk_score=row.risk_score,
            risk_level=row.risk_level,
            investigation_status=row.investigation_status,
            verification_status=row.verification_status,
            ai_confidence=row.ai_confidence,
            report_id=row.report_id,
            report_download_url=(
                f"/v1/reports/{row.report_id}/download" if row.report_id else None
            ),
            vehicle_type=row.vehicle_type,
            verification_message=row.verification_message,
        )

    @staticmethod
    def _to_export_row(row: _InvestigationRow) -> InvestigationReportExportRowDto:
        vehicle = " ".join(
            part for part in [row.brand, row.model, str(row.year) if row.year else None] if part
        )
        return InvestigationReportExportRowDto(
            date=row.scanned_at.strftime("%Y-%m-%d"),
            time=row.scanned_at.strftime("%H:%M:%S"),
            investigation_id=row.investigation_id,
            registration_number=row.registration_number,
            owner=row.owner or "-",
            vehicle=vehicle or "-",
            brand=row.brand or "-",
            model=row.model or "-",
            officer=row.officer_name,
            district=row.district or "-",
            police_station=row.police_station or "-",
            risk_score=f"{row.risk_score:.2f}",
            risk_level=row.risk_level.upper(),
            investigation_status=row.investigation_status.upper(),
            verification_status=(row.verification_status or "UNKNOWN").upper(),
            ai_confidence=(
                f"{row.ai_confidence:.0%}" if row.ai_confidence is not None else "-"
            ),
            report_download=(
                f"/v1/reports/{row.report_id}/download" if row.report_id else "-"
            ),
        )
