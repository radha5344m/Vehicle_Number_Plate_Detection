"""SQLite Executive Command Center repository."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.executive_dashboard_dto import (
    ActivityFeedItemDto,
    ChartPointDto,
    ExecutiveConnectionStatusDto,
    ExecutiveDashboardExportBundleDto,
    ExecutiveDashboardExportRowDto,
    ExecutiveDashboardFilters,
    ExecutiveDashboardResult,
    ExecutiveInsightDto,
    LeaderboardItemDto,
    MetricCardDto,
)
from sentinel_anpr.application.ports.outbound.executive_dashboard_port import (
    ExecutiveDashboardPort,
)
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import (
    OfficerActivityModel,
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,
)
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel


@dataclass(frozen=True)
class _DashboardRow:
    scan_id: str
    plate_text: str
    officer_id: str
    officer_name: str
    station_name: str | None
    district: str | None
    risk_score: float
    risk_level: str
    scanned_at: datetime
    completed_at: datetime | None
    ai_confidence: float | None
    verification_status: str | None
    verification_message: str | None
    vehicle_type: str | None
    brand: str | None
    model: str | None
    color: str | None
    owner: str | None
    report_id: str | None


class SqliteExecutiveDashboardRepository(ExecutiveDashboardPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_dashboard(self, filters: ExecutiveDashboardFilters) -> ExecutiveDashboardResult:
        with self._session_factory() as session:
            rows = self._load_rows(session, filters)
            activities = self._load_activities(session, filters)
        return self._build_dashboard(rows, activities)

    def export_dashboard(
        self,
        filters: ExecutiveDashboardFilters,
    ) -> ExecutiveDashboardExportBundleDto:
        with self._session_factory() as session:
            rows = self._load_rows(session, filters)
            activities = self._load_activities(session, filters)
        dashboard = self._build_dashboard(rows, activities)
        export_rows: list[ExecutiveDashboardExportRowDto] = []
        for card in dashboard.kpis:
            export_rows.append(
                ExecutiveDashboardExportRowDto(
                    section="KPI",
                    label=card.label,
                    value=card.display_value,
                )
            )
        for insight in dashboard.insights:
            export_rows.append(
                ExecutiveDashboardExportRowDto(
                    section="Insight",
                    label=insight.title,
                    value=insight.detail,
                )
            )
        for item in dashboard.top_performing_officers[:5]:
            export_rows.append(
                ExecutiveDashboardExportRowDto(
                    section="Top Officer",
                    label=item.name,
                    value=f"{item.metric}: {item.secondary_value or item.value}",
                )
            )
        for item in dashboard.top_performing_stations[:5]:
            export_rows.append(
                ExecutiveDashboardExportRowDto(
                    section="Top Station",
                    label=item.name,
                    value=f"{item.metric}: {item.secondary_value or item.value}",
                )
            )
        return ExecutiveDashboardExportBundleDto(
            scope_label=dashboard.scope_label,
            filters=filters,
            generated_at=dashboard.connection_status.last_updated_at,
            rows=tuple(export_rows),
        )

    def _load_rows(self, session: Session, filters: ExecutiveDashboardFilters) -> list[_DashboardRow]:
        statement = (
            select(
                ScanModel.scan_id,
                ScanModel.plate_text,
                ScanModel.officer_id,
                ScanModel.officer_name,
                ScanModel.risk_score,
                ScanModel.risk_level,
                ScanModel.scanned_at,
                ScanModel.completed_at,
                ScanModel.ocr_confidence,
                OfficerAuthModel.station_name,
                OfficerAuthModel.district,
                VerificationResultModel.lookup_status,
                VerificationResultModel.message,
                VehicleModel.vehicle_type,
                VehicleModel.make,
                VehicleModel.model,
                VehicleModel.color,
                VehicleModel.registered_owner,
                ReportModel.report_id,
            )
            .select_from(ScanModel)
            .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
            .outerjoin(VerificationResultModel, VerificationResultModel.scan_id == ScanModel.scan_id)
            .outerjoin(VehicleModel, VehicleModel.vehicle_id == ScanModel.vehicle_id)
            .outerjoin(ReportModel, ReportModel.scan_id == ScanModel.scan_id)
            .where(ScanModel.processing_status == "completed")
        )
        if filters.from_date:
            statement = statement.where(ScanModel.scanned_at >= filters.from_date)
        if filters.to_date:
            statement = statement.where(ScanModel.scanned_at <= filters.to_date)
        if filters.station_id:
            statement = statement.where(OfficerAuthModel.station_id == filters.station_id)
        if filters.officer_id:
            statement = statement.where(OfficerAuthModel.officer_id == filters.officer_id)
        if filters.district:
            statement = statement.where(OfficerAuthModel.district.ilike(f"%{filters.district.strip()}%"))
        if filters.station:
            statement = statement.where(
                OfficerAuthModel.station_name.ilike(f"%{filters.station.strip()}%")
            )
        if filters.officer:
            statement = statement.where(ScanModel.officer_name.ilike(f"%{filters.officer.strip()}%"))
        if filters.vehicle_type:
            statement = statement.where(
                VehicleModel.vehicle_type.ilike(f"%{filters.vehicle_type.strip()}%")
            )
        if filters.risk_level:
            statement = statement.where(ScanModel.risk_level == filters.risk_level.lower())
        if filters.brand:
            statement = statement.where(VehicleModel.make.ilike(f"%{filters.brand.strip()}%"))
        result = session.execute(statement.order_by(ScanModel.scanned_at.desc())).all()
        return [
            _DashboardRow(
                scan_id=row.scan_id,
                plate_text=row.plate_text,
                officer_id=row.officer_id,
                officer_name=row.officer_name,
                station_name=row.station_name,
                district=row.district,
                risk_score=row.risk_score,
                risk_level=row.risk_level,
                scanned_at=row.scanned_at.astimezone(UTC),
                completed_at=row.completed_at.astimezone(UTC) if row.completed_at else None,
                ai_confidence=row.ocr_confidence,
                verification_status=row.lookup_status,
                verification_message=row.message,
                vehicle_type=row.vehicle_type,
                brand=row.make,
                model=row.model,
                color=row.color,
                owner=row.registered_owner,
                report_id=row.report_id,
            )
            for row in result
        ]

    def _load_activities(
        self,
        session: Session,
        filters: ExecutiveDashboardFilters,
    ) -> list[OfficerActivityModel]:
        statement = (
            select(OfficerActivityModel)
            .join(OfficerAuthModel, OfficerAuthModel.officer_id == OfficerActivityModel.officer_id)
            .order_by(OfficerActivityModel.occurred_at.desc())
            .limit(20)
        )
        if filters.station_id:
            statement = statement.where(OfficerAuthModel.station_id == filters.station_id)
        if filters.officer_id:
            statement = statement.where(OfficerAuthModel.officer_id == filters.officer_id)
        if filters.district:
            statement = statement.where(OfficerAuthModel.district.ilike(f"%{filters.district.strip()}%"))
        if filters.station:
            statement = statement.where(
                OfficerAuthModel.station_name.ilike(f"%{filters.station.strip()}%")
            )
        return list(session.scalars(statement).all())

    def _build_dashboard(
        self,
        rows: list[_DashboardRow],
        activities: list[OfficerActivityModel],
    ) -> ExecutiveDashboardResult:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        total = len(rows)
        verified = sum(1 for row in rows if row.verification_status == "found")
        high = sum(1 for row in rows if row.risk_level in {"high", "critical"})
        medium = sum(1 for row in rows if row.risk_level == "medium")
        low = sum(1 for row in rows if row.risk_level == "low")
        ai_values = [row.ai_confidence for row in rows if row.ai_confidence is not None]
        risk_values = [row.risk_score for row in rows]
        durations = [
            (row.completed_at - row.scanned_at).total_seconds() / 60
            for row in rows
            if row.completed_at is not None
        ]
        detection_success_rate = (verified / total * 100) if total else 0
        registry_match_rate = detection_success_rate
        unknown_vehicle_rate = (
            sum(1 for row in rows if row.verification_status == "not_found") / total * 100
            if total
            else 0
        )
        vision_success_rate = (
            sum(1 for row in rows if row.ai_confidence is not None) / total * 100 if total else 0
        )

        kpis = (
            self._metric("Total Investigations", total),
            self._metric("Today's Investigations", sum(1 for row in rows if row.scanned_at >= today_start)),
            self._metric("Weekly Investigations", sum(1 for row in rows if row.scanned_at >= week_start)),
            self._metric("Monthly Investigations", sum(1 for row in rows if row.scanned_at >= month_start)),
            self._metric("Verified Vehicles", verified),
            self._metric("High Risk Vehicles", high),
            self._metric("Medium Risk Vehicles", medium),
            self._metric("Low Risk Vehicles", low),
            self._percent_metric("Average AI Confidence", self._average(ai_values)),
            self._score_metric("Average Risk Score", self._average(risk_values)),
            self._time_metric("Average Investigation Time", self._average(durations)),
            self._percent_metric("Detection Success Rate", detection_success_rate / 100),
        )

        daily = Counter(row.scanned_at.strftime("%Y-%m-%d") for row in rows)
        weekly = Counter(
            f"{row.scanned_at.isocalendar().year}-W{row.scanned_at.isocalendar().week:02d}"
            for row in rows
        )
        monthly = Counter(row.scanned_at.strftime("%Y-%m") for row in rows)
        hourly = Counter(row.scanned_at.strftime("%H:00") for row in rows)
        investigation_status = Counter(
            "completed" if row.completed_at is not None else "pending" for row in rows
        )
        risk_distribution = Counter(row.risk_level for row in rows)
        risk_trend = Counter(
            row.scanned_at.strftime("%Y-%m-%d") for row in rows if row.risk_level in {"high", "critical"}
        )
        top_high_risk = Counter(
            row.plate_text for row in rows if row.risk_level in {"high", "critical"}
        )
        suspicious = Counter(
            row.plate_text
            for row in rows
            if row.risk_level in {"high", "critical"} or row.risk_score >= 0.5
        )
        vehicle_types = Counter((row.vehicle_type or "Unknown") for row in rows)
        brands = Counter((row.brand or "Unknown") for row in rows)
        colors = Counter((row.color or "Unknown") for row in rows)
        reg_states = Counter(row.plate_text[:2] if len(row.plate_text) >= 2 else "Unknown" for row in rows)
        models = Counter((row.model or "Unknown") for row in rows)

        by_officer: dict[tuple[str, str], list[_DashboardRow]] = defaultdict(list)
        by_station: dict[str, list[_DashboardRow]] = defaultdict(list)
        for row in rows:
            by_officer[(row.officer_id, row.officer_name)].append(row)
            by_station[row.station_name or "Unknown"].append(row)

        top_performing_officers = tuple(
            self._officer_leaderboard(items, mode="verified")
            for _, items in sorted(
                by_officer.items(),
                key=lambda item: (
                    sum(1 for row in item[1] if row.verification_status == "found"),
                    len(item[1]),
                ),
                reverse=True,
            )[:5]
        )
        most_active_officers = tuple(
            self._officer_leaderboard(items, mode="volume")
            for _, items in sorted(by_officer.items(), key=lambda item: len(item[1]), reverse=True)[:5]
        )
        officer_leaderboard = tuple(
            self._officer_leaderboard(items, mode="risk")
            for _, items in sorted(
                by_officer.items(),
                key=lambda item: (
                    sum(1 for row in item[1] if row.risk_level in {"high", "critical"}),
                    len(item[1]),
                ),
                reverse=True,
            )[:10]
        )
        top_performing_stations = tuple(
            self._station_leaderboard(name, items)
            for name, items in sorted(
                by_station.items(),
                key=lambda item: (
                    sum(1 for row in item[1] if row.verification_status == "found"),
                    len(item[1]),
                ),
                reverse=True,
            )[:5]
        )

        recent_investigations = tuple(
            ActivityFeedItemDto(
                id=row.scan_id,
                title=f"Investigation {row.plate_text}",
                detail=f"{row.officer_name} at {row.station_name or 'Unknown station'}",
                category="investigation",
                occurred_at=row.scanned_at,
            )
            for row in rows[:5]
        )
        recent_high_risk_alerts = tuple(
            ActivityFeedItemDto(
                id=row.scan_id,
                title=f"High Risk {row.plate_text}",
                detail=row.verification_message or row.risk_level,
                category="high_risk",
                occurred_at=row.scanned_at,
            )
            for row in [row for row in rows if row.risk_level in {"high", "critical"}][:5]
        )
        recent_officer_activity = tuple(
            ActivityFeedItemDto(
                id=item.activity_id,
                title=item.officer_name,
                detail=item.description,
                category="officer_activity",
                occurred_at=item.occurred_at.astimezone(UTC),
            )
            for item in activities[:5]
        )
        recent_reports_generated = tuple(
            ActivityFeedItemDto(
                id=row.report_id or row.scan_id,
                title=f"Report generated for {row.plate_text}",
                detail=f"{row.officer_name} · {row.station_name or 'Unknown station'}",
                category="report",
                occurred_at=row.completed_at or row.scanned_at,
            )
            for row in [row for row in rows if row.report_id][:5]
        )

        ai_metrics = (
            self._percent_metric("Average AI Confidence", self._average(ai_values)),
            self._percent_metric("Detection Accuracy", self._average(ai_values)),
            self._percent_metric("Registry Match Rate", registry_match_rate / 100),
            self._percent_metric("Unknown Vehicle Rate", unknown_vehicle_rate / 100),
            self._time_metric("Average Processing Time", self._average(durations)),
            self._percent_metric("Vision Success Rate", vision_success_rate / 100),
        )

        insights = self._build_insights(
            rows=rows,
            high=high,
            brands=brands,
            top_station=top_performing_stations[0].name if top_performing_stations else None,
            registry_match_rate=registry_match_rate,
        )

        scope_label = (
            top_performing_stations[0].name if len(by_station) == 1 and by_station else "System Wide"
        )
        if len(by_officer) == 1 and rows:
            scope_label = rows[0].officer_name

        return ExecutiveDashboardResult(
            scope_label=scope_label,
            kpis=kpis,
            daily_trend=self._chart_points(daily),
            weekly_trend=self._chart_points(weekly),
            monthly_trend=self._chart_points(monthly),
            hourly_activity=self._chart_points(hourly),
            investigation_status_distribution=self._chart_points(investigation_status),
            risk_distribution=self._chart_points(risk_distribution),
            risk_trend=self._chart_points(risk_trend),
            top_high_risk_registrations=self._chart_points(top_high_risk, 8),
            frequent_suspicious_vehicles=self._chart_points(suspicious, 8),
            vehicle_type_distribution=self._chart_points(vehicle_types),
            vehicle_brand_distribution=self._chart_points(brands),
            vehicle_color_distribution=self._chart_points(colors),
            registration_state_distribution=self._chart_points(reg_states),
            common_vehicle_models=self._chart_points(models, 8),
            top_performing_officers=top_performing_officers,
            most_active_officers=most_active_officers,
            officer_leaderboard=officer_leaderboard,
            top_performing_stations=top_performing_stations,
            recent_investigations=recent_investigations,
            recent_high_risk_alerts=recent_high_risk_alerts,
            recent_officer_activity=recent_officer_activity,
            recent_reports_generated=recent_reports_generated,
            ai_metrics=ai_metrics,
            insights=insights,
            connection_status=ExecutiveConnectionStatusDto(
                status="Connected",
                last_updated_at=now,
                auto_refresh_seconds=45,
            ),
        )

    @staticmethod
    def _average(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    @staticmethod
    def _metric(label: str, value: int) -> MetricCardDto:
        return MetricCardDto(label=label, value=float(value), display_value=str(value))

    @staticmethod
    def _percent_metric(label: str, value: float | None) -> MetricCardDto:
        pct = (value or 0) * 100
        return MetricCardDto(label=label, value=pct, display_value=f"{pct:.1f}%")

    @staticmethod
    def _score_metric(label: str, value: float | None) -> MetricCardDto:
        score = (value or 0) * 100
        return MetricCardDto(label=label, value=score, display_value=f"{score:.1f}/100")

    @staticmethod
    def _time_metric(label: str, value: float | None) -> MetricCardDto:
        minutes = value or 0
        return MetricCardDto(label=label, value=minutes, display_value=f"{minutes:.1f} min")

    @staticmethod
    def _chart_points(counter: Counter[str], limit: int | None = None) -> tuple[ChartPointDto, ...]:
        items = counter.most_common(limit) if limit else sorted(counter.items())
        return tuple(ChartPointDto(label=label, value=float(value)) for label, value in items)

    @staticmethod
    def _officer_leaderboard(items: list[_DashboardRow], *, mode: str) -> LeaderboardItemDto:
        officer_name = items[0].officer_name
        if mode == "verified":
            value = sum(1 for row in items if row.verification_status == "found")
            metric = "Verified Vehicles"
        elif mode == "risk":
            value = sum(1 for row in items if row.risk_level in {"high", "critical"})
            metric = "High Risk Detections"
        else:
            value = len(items)
            metric = "Investigations Completed"
        avg_time = [
            (row.completed_at - row.scanned_at).total_seconds() / 60
            for row in items
            if row.completed_at is not None
        ]
        secondary = f"Avg time {sum(avg_time) / len(avg_time):.1f} min" if avg_time else None
        return LeaderboardItemDto(
            name=officer_name,
            metric=metric,
            value=float(value),
            secondary_value=secondary,
        )

    @staticmethod
    def _station_leaderboard(name: str, items: list[_DashboardRow]) -> LeaderboardItemDto:
        verified = sum(1 for row in items if row.verification_status == "found")
        avg_conf = [row.ai_confidence for row in items if row.ai_confidence is not None]
        secondary = (
            f"Avg AI {(sum(avg_conf) / len(avg_conf)) * 100:.1f}%"
            if avg_conf
            else None
        )
        return LeaderboardItemDto(
            name=name,
            metric="Verification Volume",
            value=float(verified),
            secondary_value=secondary,
        )

    @staticmethod
    def _build_insights(
        *,
        rows: list[_DashboardRow],
        high: int,
        brands: Counter[str],
        top_station: str | None,
        registry_match_rate: float,
    ) -> tuple[ExecutiveInsightDto, ...]:
        total = len(rows)
        high_pct = (high / total * 100) if total else 0
        top_brand = brands.most_common(1)[0][0] if brands else "Unknown"
        insights = [
            ExecutiveInsightDto(
                title="High-risk pattern",
                detail=f"High-risk investigations account for {high_pct:.1f}% of the current dashboard scope.",
            ),
            ExecutiveInsightDto(
                title="Top detected brand",
                detail=f"Most detected vehicle brand: {top_brand}.",
            ),
            ExecutiveInsightDto(
                title="Registry match rate",
                detail=f"Vehicle verification accuracy remained at {registry_match_rate:.1f}% for the selected scope.",
            ),
        ]
        if top_station:
            insights.append(
                ExecutiveInsightDto(
                    title="Top station",
                    detail=f"{top_station} completed the highest number of investigations in the current scope.",
                )
            )
        return tuple(insights)
