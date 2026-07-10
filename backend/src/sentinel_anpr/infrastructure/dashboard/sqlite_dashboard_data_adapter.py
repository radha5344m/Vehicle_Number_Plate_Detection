"""Dashboard metrics derived from stored scan history and snapshots."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.dashboard_dto import (
    DashboardSummaryResult,
    RecentActivityItem,
    RecentActivityResult,
)
from sentinel_anpr.application.ports.outbound.dashboard_data_port import DashboardDataPort
from sentinel_anpr.infrastructure.database.models.dashboard.dashboard_snapshot_model import (
    DashboardSnapshotModel,
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,
)
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import (
    OfficerActivityModel,
)
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel

_SUSPICIOUS_LEVELS = ("high", "critical")


class SqliteDashboardDataAdapter(DashboardDataPort):
    """Dashboard metrics from snapshots with live scan fallback."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_summary(
        self,
        *,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> DashboardSummaryResult:
        with self._session_factory() as session:
            snapshot = None
            if station_id is None and officer_id is None:
                snapshot = session.scalar(
                    select(DashboardSnapshotModel).order_by(DashboardSnapshotModel.snapshot_at.desc())
                )
            if snapshot is not None:
                return DashboardSummaryResult(
                    total_scans=snapshot.total_scans,
                    verified_vehicles=snapshot.verified_vehicles,
                    suspicious_vehicles=snapshot.suspicious_vehicles,
                    pending_verification=snapshot.pending_verification,
                    last_updated_at=snapshot.snapshot_at,
                )

            base = (
                select(func.count())
                .select_from(ScanModel)
                .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
                .where(ScanModel.processing_status == "completed")
            )
            total_scans = session.scalar(self._scope(base, station_id=station_id, officer_id=officer_id)) or 0
            verified_vehicles = session.scalar(
                self._scope(
                    base.where(ScanModel.vehicle_id.is_not(None)),
                    station_id=station_id,
                    officer_id=officer_id,
                )
            ) or 0
            suspicious_vehicles = session.scalar(
                self._scope(
                    base.where(ScanModel.risk_level.in_(_SUSPICIOUS_LEVELS)),
                    station_id=station_id,
                    officer_id=officer_id,
                )
            ) or 0
            pending_verification = session.scalar(
                self._scope(
                    base.where(ScanModel.vehicle_id.is_(None)),
                    station_id=station_id,
                    officer_id=officer_id,
                )
            ) or 0

        return DashboardSummaryResult(
            total_scans=total_scans,
            verified_vehicles=verified_vehicles,
            suspicious_vehicles=suspicious_vehicles,
            pending_verification=pending_verification,
            last_updated_at=datetime.now(UTC),
        )

    def get_recent_activity(
        self,
        *,
        limit: int = 10,
        station_id: str | None = None,
        officer_id: str | None = None,
    ) -> RecentActivityResult:
        with self._session_factory() as session:
            activity_query = (
                select(OfficerActivityModel)
                .join(OfficerAuthModel, OfficerAuthModel.officer_id == OfficerActivityModel.officer_id)
                .order_by(OfficerActivityModel.occurred_at.desc())
                .limit(limit)
            )
            activities = session.scalars(
                self._scope(activity_query, station_id=station_id, officer_id=officer_id)
            ).all()

            if activities:
                scan_ids = {activity.scan_id for activity in activities if activity.scan_id}
                plates_by_scan: dict[str, str] = {}
                if scan_ids:
                    scans = session.scalars(
                        select(ScanModel).where(ScanModel.scan_id.in_(scan_ids))
                    ).all()
                    plates_by_scan = {scan.scan_id: scan.plate_text for scan in scans}

                items = tuple(
                    RecentActivityItem(
                        id=activity.activity_id,
                        plate_text=plates_by_scan.get(activity.scan_id or "", ""),
                        activity_type=activity.activity_type,
                        description=activity.description,
                        status=activity.status,
                        occurred_at=activity.occurred_at,
                    )
                    for activity in activities
                )
                return RecentActivityResult(items=items)

            scans = session.scalars(
                self._scope(
                    select(ScanModel)
                    .join(OfficerAuthModel, OfficerAuthModel.officer_id == ScanModel.officer_id)
                    .where(ScanModel.processing_status == "completed")
                    .order_by(ScanModel.scanned_at.desc())
                    .limit(limit),
                    station_id=station_id,
                    officer_id=officer_id,
                )
            ).all()

        items = tuple(
            RecentActivityItem(
                id=scan.scan_id,
                plate_text=scan.plate_text,
                activity_type="scan",
                description=(
                    f"Workflow scan at {scan.location_label}"
                    if scan.location_label
                    else "Vehicle verification workflow completed"
                ),
                status=_activity_status(scan.risk_level),
                occurred_at=scan.scanned_at,
            )
            for scan in scans
        )
        return RecentActivityResult(items=items)

    @staticmethod
    def _scope(statement, *, station_id: str | None, officer_id: str | None):  # noqa: ANN001
        if station_id:
            statement = statement.where(OfficerAuthModel.station_id == station_id)
        if officer_id:
            statement = statement.where(OfficerAuthModel.officer_id == officer_id)
        return statement


def _activity_status(risk_level: str) -> str:
    if risk_level in _SUSPICIOUS_LEVELS:
        return "suspicious"
    if risk_level == "medium":
        return "pending"
    return "completed"
