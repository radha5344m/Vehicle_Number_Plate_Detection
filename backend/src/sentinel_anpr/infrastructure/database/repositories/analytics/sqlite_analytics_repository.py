"""SQLite analytics repository."""

from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.analytics_dto import (
    AnalyticsDateRange,
    AnalyticsOverviewDto,
    ChartSeriesDto,
    SuspiciousVehicleItemDto,
)
from sentinel_anpr.application.ports.outbound.analytics_repository_port import AnalyticsRepositoryPort
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel

_SUSPICIOUS_LEVELS = {"high", "critical"}


class SqliteAnalyticsRepository(AnalyticsRepositoryPort):
    """Aggregate analytics from stored scan history."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_overview(self, date_range: AnalyticsDateRange) -> AnalyticsOverviewDto:
        with self._session_factory() as session:
            scans = self._load_scans(session, date_range)

        daily_counts: dict[str, int] = defaultdict(int)
        risk_counts: dict[str, int] = defaultdict(int)
        officer_counts: dict[str, int] = defaultdict(int)
        vehicle_type_counts: dict[str, int] = defaultdict(int)
        suspicious_by_plate: dict[str, dict[str, float | int | str]] = {}

        vehicle_types = self._vehicle_type_lookup(scans)

        for scan in scans:
            day_label = scan.scanned_at.astimezone(UTC).strftime("%Y-%m-%d")
            daily_counts[day_label] += 1
            risk_counts[scan.risk_level] += 1
            officer_counts[scan.officer_name] += 1

            vehicle_type = vehicle_types.get(scan.vehicle_id, "unknown")
            vehicle_type_counts[vehicle_type] += 1

            if scan.risk_level in _SUSPICIOUS_LEVELS or scan.risk_score >= 0.5:
                entry = suspicious_by_plate.setdefault(
                    scan.plate_text,
                    {"scan_count": 0, "max_risk_score": 0.0, "risk_level": scan.risk_level},
                )
                entry["scan_count"] = int(entry["scan_count"]) + 1
                entry["max_risk_score"] = max(float(entry["max_risk_score"]), scan.risk_score)
                if scan.risk_level in _SUSPICIOUS_LEVELS:
                    entry["risk_level"] = scan.risk_level

        daily_labels = tuple(sorted(daily_counts.keys()))
        daily_values = tuple(daily_counts[label] for label in daily_labels)

        risk_order = ("low", "medium", "high", "critical")
        risk_labels = tuple(level for level in risk_order if level in risk_counts)
        risk_values = tuple(risk_counts[label] for label in risk_labels)

        vehicle_labels = tuple(sorted(vehicle_type_counts.keys()))
        vehicle_values = tuple(vehicle_type_counts[label] for label in vehicle_labels)

        officer_labels = tuple(sorted(officer_counts.keys(), key=lambda name: officer_counts[name], reverse=True))
        officer_values = tuple(officer_counts[label] for label in officer_labels)

        suspicious_items = tuple(
            SuspiciousVehicleItemDto(
                plate_text=plate,
                scan_count=int(data["scan_count"]),
                max_risk_score=float(data["max_risk_score"]),
                risk_level=str(data["risk_level"]),
            )
            for plate, data in sorted(
                suspicious_by_plate.items(),
                key=lambda item: (int(item[1]["scan_count"]), float(item[1]["max_risk_score"])),
                reverse=True,
            )
        )

        return AnalyticsOverviewDto(
            daily_scans=ChartSeriesDto(labels=daily_labels, values=daily_values),
            risk_distribution=ChartSeriesDto(labels=risk_labels, values=risk_values),
            vehicle_types=ChartSeriesDto(labels=vehicle_labels, values=vehicle_values),
            suspicious_vehicles=suspicious_items,
            officer_activity=ChartSeriesDto(labels=officer_labels, values=officer_values),
            total_scans=len(scans),
            generated_at=datetime.now(UTC),
        )

    def _load_scans(self, session: Session, date_range: AnalyticsDateRange) -> list[ScanModel]:
        statement = (
            select(ScanModel)
            .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
            .where(ScanModel.processing_status == "completed")
        )
        if date_range.from_date:
            statement = statement.where(ScanModel.scanned_at >= date_range.from_date)
        if date_range.to_date:
            statement = statement.where(ScanModel.scanned_at <= date_range.to_date)
        if date_range.station_id:
            statement = statement.where(OfficerAuthModel.station_id == date_range.station_id)
        if date_range.officer_id:
            statement = statement.where(OfficerAuthModel.officer_id == date_range.officer_id)
        return list(session.scalars(statement.order_by(ScanModel.scanned_at.asc())))

    def _vehicle_type_lookup(self, scans: list[ScanModel]) -> dict[str | None, str]:
        vehicle_ids = {scan.vehicle_id for scan in scans if scan.vehicle_id}
        if not vehicle_ids:
            return {}

        with self._session_factory() as session:
            rows = session.execute(
                select(VehicleModel.vehicle_id, VehicleModel.vehicle_type).where(
                    VehicleModel.vehicle_id.in_(vehicle_ids)
                )
            ).all()

        return {vehicle_id: vehicle_type for vehicle_id, vehicle_type in rows}
