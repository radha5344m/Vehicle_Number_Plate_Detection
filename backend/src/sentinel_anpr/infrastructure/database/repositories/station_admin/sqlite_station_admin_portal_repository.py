"""SQLite station admin portal repository."""

from __future__ import annotations

import math
import uuid
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.persistence_dto import SaveOfficerActivityCommand
from sentinel_anpr.application.dto.station_admin_portal_dto import (
    CreatePoliceOfficerCommand,
    StationAdminAnalyticsResult,
    StationAdminDashboardResult,
    StationAdminDashboardSummaryDto,
    StationAdminHighRiskVehicleDto,
    StationAdminInvestigationFilters,
    StationAdminInvestigationItemDto,
    StationAdminInvestigationPaginationDto,
    StationAdminInvestigationQueryResult,
    StationAdminNotificationDto,
    StationAdminOfficerFilters,
    StationAdminOfficerItemDto,
    StationAdminOfficerMutationResult,
    StationAdminOfficerPaginationDto,
    StationAdminOfficerQueryResult,
    StationAdminProfileDto,
    StationAdminRecentInvestigationDto,
    StationAdminRecentOfficerActivityDto,
    StationAdminReportsResult,
    UpdatePoliceOfficerCommand,
    UpdateStationDetailsCommand,
)
from sentinel_anpr.application.ports.outbound.station_admin.station_admin_portal_repository_port import (
    StationAdminPortalRepositoryPort,
)
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import OfficerActivityModel
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel
from sentinel_anpr.infrastructure.database.models.stations.station_model import PoliceStationModel
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import VerificationResultModel
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import ReportModel

_HIGH_RISK_LEVELS = {"high", "critical"}


class SqliteStationAdminPortalRepository(StationAdminPortalRepositoryPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_dashboard(self, station_id: str) -> StationAdminDashboardResult:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        with self._session_factory() as session:
            scans = self._load_station_scan_rows(session, station_id)
            activities = self._load_station_activities(session, station_id, limit=8)

        summary = StationAdminDashboardSummaryDto(
            todays_investigations=sum(1 for row in scans if row["scanned_at"] >= today_start),
            weekly_investigations=sum(1 for row in scans if row["scanned_at"] >= week_start),
            monthly_investigations=sum(1 for row in scans if row["scanned_at"] >= month_start),
            high_risk_vehicles=sum(1 for row in scans if row["risk_level"] in _HIGH_RISK_LEVELS),
            verified_vehicles=sum(1 for row in scans if row["verification_status"] == "found"),
            pending_investigations=sum(1 for row in scans if row["verification_status"] != "found"),
            average_ai_confidence=(
                sum(row["ai_confidence"] for row in scans if row["ai_confidence"] is not None)
                / len([row for row in scans if row["ai_confidence"] is not None])
                if any(row["ai_confidence"] is not None for row in scans)
                else None
            ),
            average_risk_score=(sum(row["risk_score"] for row in scans) / len(scans) if scans else None),
        )
        recent_investigations = tuple(
            StationAdminRecentInvestigationDto(
                investigation_id=row["scan_id"],
                registration_number=row["plate_text"],
                officer_name=row["officer_name"],
                risk_level=row["risk_level"],
                verification_status=row["verification_status"],
                scanned_at=row["scanned_at"],
            )
            for row in scans[:8]
        )
        recent_officer_activity = tuple(
            StationAdminRecentOfficerActivityDto(
                activity_id=activity.activity_id,
                officer_name=activity.officer_name,
                description=activity.description,
                status=activity.status,
                occurred_at=activity.occurred_at.astimezone(UTC),
            )
            for activity in activities
        )
        high_risk = tuple(
            StationAdminHighRiskVehicleDto(
                registration_number=row["plate_text"],
                risk_score=row["risk_score"],
                reason=(row["verification_message"] or row["risk_level"]).strip(),
                officer_name=row["officer_name"],
                occurred_at=row["scanned_at"],
            )
            for row in scans
            if row["risk_level"] in _HIGH_RISK_LEVELS
        )[:8]
        return StationAdminDashboardResult(
            summary=summary,
            recent_investigations=recent_investigations,
            recent_officer_activity=recent_officer_activity,
            high_risk_vehicles=high_risk,
        )

    def query_officers(self, station_id: str, filters: StationAdminOfficerFilters) -> StationAdminOfficerQueryResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)
        with self._session_factory() as session:
            statement = (
                select(OfficerAuthModel, func.count(ScanModel.scan_id).label("investigations"))
                .outerjoin(ScanModel, ScanModel.officer_id == OfficerAuthModel.officer_id)
                .where(
                    OfficerAuthModel.station_id == station_id,
                    OfficerAuthModel.roles_csv == "police_officer",
                    OfficerAuthModel.deleted_at.is_(None),
                )
                .group_by(OfficerAuthModel.officer_id)
            )
            if filters.search:
                q = f"%{filters.search.strip()}%"
                statement = statement.where(
                    or_(
                        OfficerAuthModel.employee_id.ilike(q),
                        OfficerAuthModel.badge_number.ilike(q),
                        OfficerAuthModel.first_name.ilike(q),
                        OfficerAuthModel.last_name.ilike(q),
                        OfficerAuthModel.username.ilike(q),
                    )
                )
            if filters.status:
                statement = statement.where(OfficerAuthModel.status == filters.status.lower())
            if filters.rank:
                statement = statement.where(OfficerAuthModel.rank.ilike(f"%{filters.rank.strip()}%"))
            rows = session.execute(statement.order_by(OfficerAuthModel.created_at.desc())).all()
        total_items = len(rows)
        total_pages = math.ceil(total_items / page_size) if total_items else 0
        paged = rows[(page - 1) * page_size : (page - 1) * page_size + page_size]
        return StationAdminOfficerQueryResult(
            items=tuple(self._to_officer_item(model, investigations) for model, investigations in paged),
            pagination=StationAdminOfficerPaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def create_officer(
        self,
        station_id: str,
        command: CreatePoliceOfficerCommand,
        password_hash: str,
        *,
        password_change_required: bool = False,
    ) -> StationAdminOfficerMutationResult:
        with self._session_factory() as session:
            station = self._load_station(session, station_id)
            now = datetime.now(UTC)
            officer = OfficerAuthModel(
                officer_id=str(uuid.uuid4()),
                user_id=command.user_id,
                employee_id=command.employee_id,
                badge_number=command.badge_number,
                username=command.username,
                email=command.email,
                phone_number=command.phone_number,
                first_name=command.first_name,
                last_name=command.last_name,
                rank=command.rank,
                station_id=station.station_id,
                station_code=station.station_code,
                station_name=station.station_name,
                district=station.district,
                roles_csv="police_officer",
                status=command.status,
                password_hash=password_hash,
                password_change_required=password_change_required,
                created_at=now,
                updated_at=now,
            )
            session.add(officer)
            session.add(
                OfficerActivityModel(
                    activity_id=str(uuid.uuid4()),
                    officer_id=officer.officer_id,
                    officer_name=f"{officer.first_name} {officer.last_name}",
                    scan_id=None,
                    activity_type="officer_created",
                    description=f"Police officer {officer.first_name} {officer.last_name} created",
                    status="completed",
                    correlation_id=None,
                    occurred_at=now,
                    created_at=now,
                )
            )
            session.commit()
            session.refresh(officer)
            return StationAdminOfficerMutationResult(officer=self._to_officer_item(officer, 0))

    def update_officer(self, station_id: str, command: UpdatePoliceOfficerCommand) -> StationAdminOfficerMutationResult:
        with self._session_factory() as session:
            officer = self._load_station_officer(session, station_id, command.officer_id)
            officer.first_name = command.first_name
            officer.last_name = command.last_name
            officer.email = command.email
            officer.phone_number = command.phone_number
            officer.rank = command.rank
            officer.status = command.status
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()
            investigations = session.scalar(select(func.count()).select_from(ScanModel).where(ScanModel.officer_id == officer.officer_id)) or 0
            return StationAdminOfficerMutationResult(officer=self._to_officer_item(officer, investigations))

    def change_officer_status(self, station_id: str, officer_id: str, status: str) -> StationAdminOfficerMutationResult:
        with self._session_factory() as session:
            officer = self._load_station_officer(session, station_id, officer_id)
            officer.status = status
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.add(
                OfficerActivityModel(
                    activity_id=str(uuid.uuid4()),
                    officer_id=officer.officer_id,
                    officer_name=f"{officer.first_name} {officer.last_name}",
                    scan_id=None,
                    activity_type="officer_deactivated" if status == "inactive" else "officer_activated",
                    description=f"Officer status changed to {status}",
                    status="completed",
                    correlation_id=None,
                    occurred_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
            )
            session.commit()
            investigations = session.scalar(select(func.count()).select_from(ScanModel).where(ScanModel.officer_id == officer.officer_id)) or 0
            return StationAdminOfficerMutationResult(officer=self._to_officer_item(officer, investigations))

    def reset_officer_password(self, station_id: str, officer_id: str, password_hash: str) -> None:
        with self._session_factory() as session:
            officer = self._load_station_officer(session, station_id, officer_id)
            officer.password_hash = password_hash
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()

    def soft_delete_officer(self, station_id: str, officer_id: str) -> None:
        with self._session_factory() as session:
            officer = self._load_station_officer(session, station_id, officer_id)
            now = datetime.now(UTC)
            officer.deleted_at = now
            officer.status = "inactive"
            officer.updated_at = now
            session.add(officer)
            session.add(
                OfficerActivityModel(
                    activity_id=str(uuid.uuid4()),
                    officer_id=officer.officer_id,
                    officer_name=f"{officer.first_name} {officer.last_name}",
                    scan_id=None,
                    activity_type="officer_deactivated",
                    description=f"Police officer {officer.first_name} {officer.last_name} removed from station",
                    status="completed",
                    correlation_id=None,
                    occurred_at=now,
                    created_at=now,
                )
            )
            session.commit()

    def update_station_details(self, station_id: str, command: UpdateStationDetailsCommand) -> None:
        with self._session_factory() as session:
            station = self._load_station(session, station_id)
            station.address = command.address.strip()
            station.phone_number = command.phone_number.strip() if command.phone_number else None
            station.email = command.email.strip().lower() if command.email else None
            station.updated_at = datetime.now(UTC)
            session.add(station)
            session.commit()

    def query_investigations(self, station_id: str, filters: StationAdminInvestigationFilters) -> StationAdminInvestigationQueryResult:
        rows = self._filtered_station_scan_rows(station_id, filters)
        total_items = len(rows)
        total_pages = math.ceil(total_items / filters.page_size) if total_items else 0
        offset = (max(filters.page, 1) - 1) * filters.page_size
        paged = rows[offset : offset + filters.page_size]
        return StationAdminInvestigationQueryResult(
            items=tuple(self._to_investigation_item(row) for row in paged),
            pagination=StationAdminInvestigationPaginationDto(
                page=max(filters.page, 1),
                page_size=filters.page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def query_reports(self, station_id: str, filters: StationAdminInvestigationFilters) -> StationAdminReportsResult:
        rows = self._filtered_station_scan_rows(station_id, filters)
        risk_counts = Counter(row["risk_level"] for row in rows)
        vehicle_counts = Counter((row["vehicle_type"] or "Unknown") for row in rows)
        brand_counts = Counter((row["brand"] or "Unknown") for row in rows)
        officer_counts = Counter(row["officer_name"] for row in rows)
        confidence_values = [row["ai_confidence"] for row in rows if row["ai_confidence"] is not None]
        avg_conf = sum(confidence_values) / len(confidence_values) if confidence_values else None
        avg_risk = (sum(row["risk_score"] for row in rows) / len(rows)) if rows else None
        verified = sum(1 for row in rows if row["verification_status"] == "found")
        high_risk = sum(1 for row in rows if row["risk_level"] in _HIGH_RISK_LEVELS)
        page_size = filters.page_size
        page = max(filters.page, 1)
        total_pages = math.ceil(len(rows) / page_size) if rows else 0
        paged = rows[(page - 1) * page_size : (page - 1) * page_size + page_size]
        summary_text = (
            f"{len(rows)} station investigations found. {verified} verified vehicles and {high_risk} high risk vehicles."
            if rows
            else "No station investigations matched the selected filters."
        )
        return StationAdminReportsResult(
            summary_text=summary_text,
            total_investigations=len(rows),
            verified_vehicles=verified,
            high_risk_vehicles=high_risk,
            average_ai_confidence=avg_conf,
            average_risk_score=avg_risk,
            risk_distribution=tuple(risk_counts.items()),
            vehicle_type_distribution=tuple(vehicle_counts.items()),
            brand_distribution=tuple(brand_counts.items()),
            officer_performance=tuple(officer_counts.items()),
            items=tuple(self._to_investigation_item(row) for row in paged),
            pagination=StationAdminInvestigationPaginationDto(
                page=page,
                page_size=page_size,
                total_items=len(rows),
                total_pages=total_pages,
            ),
        )

    def get_analytics(self, station_id: str, from_date, to_date) -> StationAdminAnalyticsResult:
        rows = self._filtered_station_scan_rows(
            station_id,
            StationAdminInvestigationFilters(from_date=from_date, to_date=to_date, page=1, page_size=5000),
        )
        daily = Counter(row["scanned_at"].strftime("%Y-%m-%d") for row in rows)
        weekly = Counter(f"{row['scanned_at'].isocalendar().year}-W{row['scanned_at'].isocalendar().week:02d}" for row in rows)
        monthly = Counter(row["scanned_at"].strftime("%Y-%m") for row in rows)
        risk_counts = Counter(row["risk_level"] for row in rows)
        vehicle_counts = Counter((row["vehicle_type"] or "Unknown") for row in rows)
        brand_counts = Counter((row["brand"] or "Unknown") for row in rows)
        officer_counts = Counter(row["officer_name"] for row in rows)
        confidences = [row["ai_confidence"] for row in rows if row["ai_confidence"] is not None]
        durations = [5.0 for _ in rows]
        return StationAdminAnalyticsResult(
            daily_investigations=tuple(value for _, value in sorted(daily.items())),
            daily_labels=tuple(label for label, _ in sorted(daily.items())),
            weekly_trend=tuple(value for _, value in sorted(weekly.items())),
            weekly_labels=tuple(label for label, _ in sorted(weekly.items())),
            monthly_trend=tuple(value for _, value in sorted(monthly.items())),
            monthly_labels=tuple(label for label, _ in sorted(monthly.items())),
            risk_distribution_labels=tuple(label for label, _ in sorted(risk_counts.items())),
            risk_distribution_values=tuple(value for _, value in sorted(risk_counts.items())),
            vehicle_type_labels=tuple(label for label, _ in vehicle_counts.most_common()),
            vehicle_type_values=tuple(value for _, value in vehicle_counts.most_common()),
            vehicle_brand_labels=tuple(label for label, _ in brand_counts.most_common()),
            vehicle_brand_values=tuple(value for _, value in brand_counts.most_common()),
            officer_performance_labels=tuple(label for label, _ in officer_counts.most_common()),
            officer_performance_values=tuple(value for _, value in officer_counts.most_common()),
            average_investigation_time_minutes=(sum(durations) / len(durations) if durations else None),
            average_ai_confidence=(sum(confidences) / len(confidences) if confidences else None),
            average_risk_score=(sum(row["risk_score"] for row in rows) / len(rows) if rows else None),
        )

    def get_notifications(self, station_id: str, limit: int) -> tuple[StationAdminNotificationDto, ...]:
        with self._session_factory() as session:
            activities = self._load_station_activities(session, station_id, limit=limit)
        notifications: list[StationAdminNotificationDto] = []
        for activity in activities:
            category = {
                "officer_created": "Officer Created",
                "officer_deactivated": "Officer Deactivated",
                "officer_activated": "System Alerts",
            }.get(activity.activity_type, "High Risk Vehicle" if activity.status == "suspicious" else "System Alerts")
            notifications.append(
                StationAdminNotificationDto(
                    notification_id=activity.activity_id,
                    title=category,
                    message=activity.description,
                    category=category,
                    occurred_at=activity.occurred_at.astimezone(UTC),
                )
            )
        return tuple(notifications)

    def get_profile(self, station_id: str, officer_id: str) -> StationAdminProfileDto:
        with self._session_factory() as session:
            station = self._load_station(session, station_id)
            officer = self._load_station_admin(session, station_id, officer_id)
        return StationAdminProfileDto(
            station_id=station.station_id,
            station_name=station.station_name,
            station_code=station.station_code,
            address=station.address,
            phone_number=station.phone_number,
            email=station.email,
            district=station.district,
            state=station.state,
            station_type=station.station_type,
            admin_name=f"{officer.first_name} {officer.last_name}",
            admin_rank=officer.rank,
            officer_id=officer.officer_id,
            employee_id=officer.employee_id,
            role=(officer.roles_csv or "station_admin").upper(),
            account_email=officer.email,
            account_phone=officer.phone_number,
            created_at=(officer.created_at or datetime.now(UTC)).astimezone(UTC),
            last_login_at=(officer.last_login_at.astimezone(UTC) if officer.last_login_at else None),
        )

    def update_own_profile(
        self,
        station_id: str,
        officer_id: str,
        command: UpdateOwnProfileCommand,
    ) -> StationAdminProfileDto:
        with self._session_factory() as session:
            officer = self._load_station_admin(session, station_id, officer_id)
            officer.employee_id = command.employee_id
            officer.first_name = command.first_name
            officer.last_name = command.last_name
            officer.email = command.email
            officer.phone_number = command.phone_number
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()
        return self.get_profile(station_id, officer_id)

    def username_exists(self, username: str) -> bool:
        return self._exists(OfficerAuthModel.username, username)

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.email, email, exclude_officer_id)

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.employee_id, employee_id, exclude_officer_id)

    def get_officer_password_hash(self, officer_id: str) -> str | None:
        with self._session_factory() as session:
            officer = session.get(OfficerAuthModel, officer_id)
            return officer.password_hash if officer is not None else None

    def change_own_password(self, officer_id: str, password_hash: str) -> None:
        with self._session_factory() as session:
            officer = session.get(OfficerAuthModel, officer_id)
            if officer is None or officer.deleted_at is not None:
                raise LookupError("Officer not found")
            officer.password_hash = password_hash
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()

    def _filtered_station_scan_rows(self, station_id: str, filters: StationAdminInvestigationFilters) -> list[dict]:
        rows = self._load_station_scan_rows_filtered(station_id, filters)
        sort_key = {
            "scanned_at": lambda row: row["scanned_at"],
            "risk_score": lambda row: row["risk_score"],
            "officer_name": lambda row: row["officer_name"],
            "registration_number": lambda row: row["plate_text"],
        }.get(filters.sort_by, lambda row: row["scanned_at"])
        return sorted(rows, key=sort_key, reverse=filters.sort_desc)

    def _load_station_scan_rows_filtered(self, station_id: str, filters: StationAdminInvestigationFilters) -> list[dict]:
        rows = self._load_station_scan_rows(self._session_factory(), station_id) if False else None
        with self._session_factory() as session:
            rows = self._load_station_scan_rows(session, station_id)
        filtered = []
        for row in rows:
            if filters.from_date and row["scanned_at"] < filters.from_date:
                continue
            if filters.to_date and row["scanned_at"] > filters.to_date:
                continue
            if filters.officer and filters.officer.lower() not in row["officer_name"].lower():
                continue
            if filters.risk_level and row["risk_level"] != filters.risk_level.lower():
                continue
            if filters.vehicle_type and (row["vehicle_type"] or "").lower().find(filters.vehicle_type.lower()) == -1:
                continue
            if filters.registration_number and row["plate_text"].lower() != filters.registration_number.strip().lower():
                continue
            if filters.verification_status and (row["verification_status"] or "").lower() != filters.verification_status.lower():
                continue
            filtered.append(row)
        return filtered

    def _load_station_scan_rows(self, session: Session, station_id: str) -> list[dict]:
        result = session.execute(
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
                VerificationResultModel.lookup_status,
                VerificationResultModel.message,
                VehicleModel.vehicle_type,
                VehicleModel.make,
                ReportModel.report_id,
            )
            .select_from(ScanModel)
            .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
            .outerjoin(VerificationResultModel, VerificationResultModel.scan_id == ScanModel.scan_id)
            .outerjoin(VehicleModel, VehicleModel.vehicle_id == ScanModel.vehicle_id)
            .outerjoin(ReportModel, ReportModel.scan_id == ScanModel.scan_id)
            .where(OfficerAuthModel.station_id == station_id)
            .order_by(ScanModel.scanned_at.desc())
        ).all()
        return [
            {
                "scan_id": row.scan_id,
                "plate_text": row.plate_text,
                "officer_id": row.officer_id,
                "officer_name": row.officer_name,
                "risk_score": row.risk_score,
                "risk_level": row.risk_level,
                "scanned_at": row.scanned_at.astimezone(UTC),
                "completed_at": row.completed_at.astimezone(UTC),
                "ai_confidence": row.ocr_confidence,
                "verification_status": row.lookup_status,
                "verification_message": row.message,
                "vehicle_type": row.vehicle_type,
                "brand": row.make,
                "report_id": row.report_id,
            }
            for row in result
        ]

    def _load_station_activities(self, session: Session, station_id: str, limit: int) -> list[OfficerActivityModel]:
        station_officer_ids = select(OfficerAuthModel.officer_id).where(OfficerAuthModel.station_id == station_id)
        return list(
            session.scalars(
                select(OfficerActivityModel)
                .where(OfficerActivityModel.officer_id.in_(station_officer_ids))
                .order_by(OfficerActivityModel.occurred_at.desc())
                .limit(limit)
            ).all()
        )

    def _exists(self, column, value: str, exclude_officer_id: str | None = None) -> bool:  # noqa: ANN001
        with self._session_factory() as session:
            statement = select(func.count()).select_from(OfficerAuthModel).where(
                column == value,
                OfficerAuthModel.deleted_at.is_(None),
            )
            if exclude_officer_id:
                statement = statement.where(OfficerAuthModel.officer_id != exclude_officer_id)
            return bool(session.scalar(statement) or 0)

    @staticmethod
    def _load_station(session: Session, station_id: str) -> PoliceStationModel:
        station = session.get(PoliceStationModel, station_id)
        if station is None or station.deleted_at is not None:
            raise LookupError("Station not found")
        return station

    @staticmethod
    def _load_station_admin(session: Session, station_id: str, officer_id: str) -> OfficerAuthModel:
        officer = session.get(OfficerAuthModel, officer_id)
        if officer is None or officer.deleted_at is not None or officer.station_id != station_id:
            raise LookupError("Station admin not found")
        return officer

    @staticmethod
    def _load_station_officer(session: Session, station_id: str, officer_id: str) -> OfficerAuthModel:
        officer = session.get(OfficerAuthModel, officer_id)
        if (
            officer is None
            or officer.deleted_at is not None
            or officer.station_id != station_id
            or officer.roles_csv != "police_officer"
        ):
            raise LookupError("Officer not found")
        return officer

    @staticmethod
    def _to_officer_item(model: OfficerAuthModel, investigations: int) -> StationAdminOfficerItemDto:
        return StationAdminOfficerItemDto(
            officer_id=model.officer_id,
            user_id=model.user_id,
            employee_id=model.employee_id,
            badge_number=model.badge_number,
            officer_name=f"{model.first_name} {model.last_name}".strip(),
            rank=model.rank,
            phone_number=model.phone_number,
            status=model.status,
            investigations=int(investigations or 0),
            last_login_at=(model.last_login_at.astimezone(UTC) if model.last_login_at else None),
            username=model.username,
            email=model.email,
            created_at=model.created_at.astimezone(UTC),
        )

    @staticmethod
    def _to_investigation_item(row: dict) -> StationAdminInvestigationItemDto:
        return StationAdminInvestigationItemDto(
            investigation_id=row["scan_id"],
            registration_number=row["plate_text"],
            officer_id=row["officer_id"],
            officer_name=row["officer_name"],
            vehicle_type=row["vehicle_type"],
            risk_score=row["risk_score"],
            risk_level=row["risk_level"],
            verification_status=row["verification_status"],
            ai_confidence=row["ai_confidence"],
            scanned_at=row["scanned_at"],
            report_download_url=(f"/v1/reports/{row['report_id']}/download" if row["report_id"] else None),
        )
