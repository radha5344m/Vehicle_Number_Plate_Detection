"""Initialize demo database schema and seed data."""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.infrastructure.database.migrations.runner import run_pending_migrations
from sentinel_anpr.infrastructure.database.models.base import Base
from sentinel_anpr.infrastructure.database.models.dashboard.dashboard_snapshot_model import (
    DashboardSnapshotModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.investigation_reports.report_model import (
    ReportModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.officer_activity.officer_activity_model import (
    OfficerActivityModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.risk.risk_assessment_model import (
    RiskAssessmentModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel  # noqa: F401
from sentinel_anpr.infrastructure.database.models.stations.station_model import (
    PoliceStationModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.models.verification.verification_result_model import (
    VerificationResultModel,  # noqa: F401
)
from sentinel_anpr.infrastructure.database.seed.demo_auth_users import seed_demo_auth_users
from sentinel_anpr.infrastructure.database.seed.demo_scans import seed_demo_scans
from sentinel_anpr.infrastructure.database.seed.demo_stations import seed_demo_stations
from sentinel_anpr.infrastructure.database.seed.demo_vehicles import seed_demo_vehicles


def initialize_demo_database(engine: Engine, password_hasher: PasswordHasherPort) -> None:
    """Create tables, apply migrations, and seed demo vehicle records."""
    Base.metadata.create_all(engine)
    run_pending_migrations(engine)
    with Session(engine) as session:
        seed_demo_stations(session)
        seed_demo_auth_users(session, password_hasher)
        seed_demo_vehicles(session)
        seed_demo_scans(session)
        session.commit()
