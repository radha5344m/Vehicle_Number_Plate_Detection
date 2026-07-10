"""SQLite police officer portal repository."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.account_profile_dto import UpdateOwnProfileCommand
from sentinel_anpr.application.dto.police_officer_portal_dto import (
    PoliceOfficerDashboardResult,
    PoliceOfficerDashboardSummaryDto,
    PoliceOfficerNotificationDto,
    PoliceOfficerProfileDto,
    PoliceOfficerRecentActivityDto,
    PoliceOfficerRecentInvestigationDto,
)
from sentinel_anpr.application.ports.outbound.police_officer.police_officer_portal_repository_port import (
    PoliceOfficerPortalRepositoryPort,
)
from sentinel_anpr.application.services.auth_permissions import primary_role_for_roles, roles_csv_includes
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

_HIGH_RISK_LEVELS = {"high", "critical"}


class SqlitePoliceOfficerPortalRepository(PoliceOfficerPortalRepositoryPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_dashboard(self, officer_id: str) -> PoliceOfficerDashboardResult:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        with self._session_factory() as session:
            rows = self._load_officer_scan_rows(session, officer_id)
            activities = self._load_activities(session, officer_id, limit=8)

        confidence_values = [row["ai_confidence"] for row in rows if row["ai_confidence"] is not None]
        summary = PoliceOfficerDashboardSummaryDto(
            todays_verifications=sum(1 for row in rows if row["scanned_at"] >= today_start),
            weekly_verifications=sum(1 for row in rows if row["scanned_at"] >= week_start),
            monthly_verifications=sum(1 for row in rows if row["scanned_at"] >= month_start),
            high_risk_vehicles_found=sum(1 for row in rows if row["risk_level"] in _HIGH_RISK_LEVELS),
            average_ai_confidence=(
                sum(confidence_values) / len(confidence_values) if confidence_values else None
            ),
            average_risk_score=(sum(row["risk_score"] for row in rows) / len(rows) if rows else None),
        )
        recent_investigations = tuple(
            PoliceOfficerRecentInvestigationDto(
                investigation_id=row["scan_id"],
                registration_number=row["plate_text"],
                vehicle_type=row["vehicle_type"],
                risk_level=row["risk_level"],
                verification_status=row["verification_status"],
                scanned_at=row["scanned_at"],
                report_download_url=(
                    f"/v1/reports/{row['report_id']}/download" if row["report_id"] else None
                ),
            )
            for row in rows[:8]
        )
        recent_activity = tuple(
            PoliceOfficerRecentActivityDto(
                activity_id=activity.activity_id,
                description=activity.description,
                status=activity.status,
                occurred_at=activity.occurred_at.astimezone(UTC),
            )
            for activity in activities
        )
        return PoliceOfficerDashboardResult(
            summary=summary,
            recent_investigations=recent_investigations,
            recent_activity=recent_activity,
        )

    def get_notifications(
        self,
        officer_id: str,
        limit: int,
    ) -> tuple[PoliceOfficerNotificationDto, ...]:
        with self._session_factory() as session:
            activities = self._load_activities(session, officer_id, limit=limit)

        notifications: list[PoliceOfficerNotificationDto] = []
        for activity in activities:
            category = self._category_for_activity(activity)
            title = {
                "Investigation Completed": "Investigation Completed",
                "High Risk Vehicle Alert": "High Risk Vehicle Alert",
                "System Announcements": "System Announcement",
            }[category]
            notifications.append(
                PoliceOfficerNotificationDto(
                    notification_id=activity.activity_id,
                    title=title,
                    message=activity.description,
                    category=category,
                    occurred_at=activity.occurred_at.astimezone(UTC),
                )
            )
        return tuple(notifications)

    def get_profile(self, officer_id: str) -> PoliceOfficerProfileDto:
        with self._session_factory() as session:
            officer = self._load_officer(session, officer_id)
        return PoliceOfficerProfileDto(
            officer_id=officer.officer_id,
            employee_id=officer.employee_id,
            officer_name=f"{officer.first_name} {officer.last_name}".strip(),
            badge_number=officer.badge_number,
            rank=officer.rank,
            station_name=officer.station_name,
            station_code=officer.station_code,
            phone_number=officer.phone_number,
            email=officer.email,
            username=officer.username,
            role=primary_role_for_roles(
                tuple(role.strip() for role in officer.roles_csv.split(",") if role.strip())
            ),
            created_at=(officer.created_at or datetime.now(UTC)).astimezone(UTC),
            last_login_at=(officer.last_login_at.astimezone(UTC) if officer.last_login_at else None),
        )

    def update_own_profile(self, officer_id: str, command: UpdateOwnProfileCommand) -> PoliceOfficerProfileDto:
        with self._session_factory() as session:
            officer = self._load_officer(session, officer_id)
            officer.employee_id = command.employee_id
            officer.first_name = command.first_name
            officer.last_name = command.last_name
            officer.email = command.email
            officer.phone_number = command.phone_number
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()
            session.refresh(officer)
        return self.get_profile(officer_id)

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.email, email, exclude_officer_id)

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.employee_id, employee_id, exclude_officer_id)

    def change_own_password(self, officer_id: str, password_hash: str) -> None:
        with self._session_factory() as session:
            officer = self._load_officer(session, officer_id)
            officer.password_hash = password_hash
            officer.updated_at = datetime.now(UTC)
            session.add(officer)
            session.commit()

    def _load_officer_scan_rows(self, session: Session, officer_id: str) -> list[dict]:
        result = session.execute(
            select(
                ScanModel.scan_id,
                ScanModel.plate_text,
                ScanModel.risk_score,
                ScanModel.risk_level,
                ScanModel.scanned_at,
                VerificationResultModel.lookup_status,
                VerificationResultModel.message,
                VehicleModel.vehicle_type,
                ReportModel.report_id,
                ScanModel.ocr_confidence,
            )
            .select_from(ScanModel)
            .outerjoin(VerificationResultModel, VerificationResultModel.scan_id == ScanModel.scan_id)
            .outerjoin(VehicleModel, VehicleModel.vehicle_id == ScanModel.vehicle_id)
            .outerjoin(ReportModel, ReportModel.scan_id == ScanModel.scan_id)
            .where(ScanModel.officer_id == officer_id)
            .order_by(ScanModel.scanned_at.desc())
        ).all()
        return [
            {
                "scan_id": row.scan_id,
                "plate_text": row.plate_text,
                "risk_score": row.risk_score,
                "risk_level": row.risk_level,
                "scanned_at": row.scanned_at.astimezone(UTC),
                "verification_status": row.lookup_status,
                "verification_message": row.message,
                "vehicle_type": row.vehicle_type,
                "report_id": row.report_id,
                "ai_confidence": row.ocr_confidence,
            }
            for row in result
        ]

    @staticmethod
    def _load_activities(
        session: Session,
        officer_id: str,
        limit: int,
    ) -> list[OfficerActivityModel]:
        return list(
            session.scalars(
                select(OfficerActivityModel)
                .where(OfficerActivityModel.officer_id == officer_id)
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
    def _load_officer(session: Session, officer_id: str) -> OfficerAuthModel:
        officer = session.get(OfficerAuthModel, officer_id)
        if (
            officer is None
            or officer.deleted_at is not None
            or not roles_csv_includes(officer.roles_csv, "police_officer")
        ):
            raise LookupError("Officer not found")
        return officer

    @staticmethod
    def _category_for_activity(activity: OfficerActivityModel) -> str:
        if activity.status == "suspicious":
            return "High Risk Vehicle Alert"
        if activity.activity_type in {"investigation_completed", "verification_completed"}:
            return "Investigation Completed"
        return "System Announcements"
