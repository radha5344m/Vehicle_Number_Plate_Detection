"""Apply incremental SQLite schema migrations."""

from collections.abc import Callable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

MigrationFn = Callable[[Engine], None]

MIGRATIONS: tuple[tuple[str, MigrationFn], ...] = (
    (
        "001_persistence_tables",
        lambda engine: _migration_001_persistence_tables(engine),
    ),
    (
        "002_user_management_fields",
        lambda engine: _migration_002_user_management_fields(engine),
    ),
    (
        "003_police_station_management",
        lambda engine: _migration_003_police_station_management(engine),
    ),
    (
        "004_user_identity_sequences",
        lambda engine: _migration_004_user_identity_sequences(engine),
    ),
    (
        "005_e_challan_tables",
        lambda engine: _migration_005_e_challan_tables(engine),
    ),
    (
        "006_scan_vision_registry_snapshots",
        lambda engine: _migration_006_scan_vision_registry_snapshots(engine),
    ),
)


def run_pending_migrations(engine: Engine) -> None:
    """Apply migrations that have not yet been recorded."""
    _ensure_migration_table(engine)
    applied = _applied_migrations(engine)

    for migration_id, migration_fn in MIGRATIONS:
        if migration_id in applied:
            continue
        migration_fn(engine)
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO schema_migrations (migration_id) VALUES (:migration_id)"),
                {"migration_id": migration_id},
            )


def _ensure_migration_table(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    migration_id VARCHAR(64) PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


def _applied_migrations(engine: Engine) -> set[str]:
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT migration_id FROM schema_migrations")).all()
    return {row[0] for row in rows}


def _table_exists(engine: Engine, table_name: str) -> bool:
    return table_name in inspect(engine).get_table_names()


def _column_names(engine: Engine, table_name: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table_name)}


def _add_column_if_missing(engine: Engine, table_name: str, column_name: str, ddl: str) -> None:
    if not _table_exists(engine, table_name):
        return
    if column_name in _column_names(engine, table_name):
        return
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))


def _migration_001_persistence_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS verification_results (
                    verification_id VARCHAR(36) PRIMARY KEY,
                    scan_id VARCHAR(36) NOT NULL UNIQUE,
                    lookup_status VARCHAR(16) NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    vehicle_id VARCHAR(36),
                    verified_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    assessment_id VARCHAR(36) PRIMARY KEY,
                    scan_id VARCHAR(36) NOT NULL UNIQUE,
                    risk_score FLOAT NOT NULL,
                    risk_level VARCHAR(16) NOT NULL,
                    explanation TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    policy_version VARCHAR(32) NOT NULL,
                    assessed_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS officer_activity_events (
                    activity_id VARCHAR(36) PRIMARY KEY,
                    officer_id VARCHAR(36) NOT NULL,
                    officer_name VARCHAR(200) NOT NULL,
                    scan_id VARCHAR(36),
                    activity_type VARCHAR(32) NOT NULL,
                    description VARCHAR(255) NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    correlation_id VARCHAR(36),
                    occurred_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS dashboard_snapshots (
                    snapshot_id VARCHAR(36) PRIMARY KEY,
                    total_scans INTEGER NOT NULL,
                    verified_vehicles INTEGER NOT NULL,
                    suspicious_vehicles INTEGER NOT NULL,
                    pending_verification INTEGER NOT NULL,
                    snapshot_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )
        )

    _add_column_if_missing(engine, "scan_history", "correlation_id", "correlation_id VARCHAR(36)")
    _add_column_if_missing(engine, "scan_history", "ocr_confidence", "ocr_confidence FLOAT")
    _add_column_if_missing(
        engine,
        "scan_history",
        "image_storage_key",
        "image_storage_key VARCHAR(512)",
    )
    _add_column_if_missing(engine, "investigation_reports", "scan_id", "scan_id VARCHAR(36)")

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_scan_correlation_id ON scan_history (correlation_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_officer_activity_scan_id "
                "ON officer_activity_events (scan_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_officer_activity_correlation_id "
                "ON officer_activity_events (correlation_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_dashboard_snapshot_at "
                "ON dashboard_snapshots (snapshot_at)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_investigation_reports_scan_id "
                "ON investigation_reports (scan_id)"
            )
        )


def _migration_002_user_management_fields(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS officer_auth (
                    officer_id VARCHAR(36) PRIMARY KEY,
                    employee_id VARCHAR(32),
                    badge_number VARCHAR(32) NOT NULL UNIQUE,
                    username VARCHAR(64) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    phone_number VARCHAR(32),
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    rank VARCHAR(100) NOT NULL,
                    station_id VARCHAR(36) NOT NULL,
                    station_code VARCHAR(32) NOT NULL,
                    station_name VARCHAR(200) NOT NULL,
                    district VARCHAR(200),
                    roles_csv TEXT NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    last_login_at TIMESTAMP,
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
                """
            )
        )

    _add_column_if_missing(
        engine,
        "officer_auth",
        "employee_id",
        "employee_id VARCHAR(32)",
    )
    _add_column_if_missing(
        engine,
        "officer_auth",
        "phone_number",
        "phone_number VARCHAR(32)",
    )
    _add_column_if_missing(
        engine,
        "officer_auth",
        "district",
        "district VARCHAR(200)",
    )
    _add_column_if_missing(
        engine,
        "officer_auth",
        "last_login_at",
        "last_login_at TIMESTAMP",
    )
    _add_column_if_missing(
        engine,
        "officer_auth",
        "deleted_at",
        "deleted_at TIMESTAMP",
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_officer_auth_employee_id "
                "ON officer_auth (employee_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_officer_auth_status "
                "ON officer_auth (status)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_officer_auth_station_code "
                "ON officer_auth (station_code)"
            )
        )


def _migration_003_police_station_management(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS police_stations (
                    station_id VARCHAR(36) PRIMARY KEY,
                    station_name VARCHAR(200) NOT NULL UNIQUE,
                    station_code VARCHAR(32) NOT NULL UNIQUE,
                    district VARCHAR(200) NOT NULL,
                    state VARCHAR(200) NOT NULL,
                    address TEXT NOT NULL,
                    pincode VARCHAR(16) NOT NULL,
                    phone_number VARCHAR(32),
                    email VARCHAR(255),
                    station_type VARCHAR(64) NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
                """
            )
        )

    _add_column_if_missing(
        engine, "police_stations", "deleted_at", "deleted_at TIMESTAMP"
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_police_stations_district "
                "ON police_stations (district)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_police_stations_state "
                "ON police_stations (state)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_police_stations_status "
                "ON police_stations (status)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_police_stations_type "
                "ON police_stations (station_type)"
            )
        )


def _migration_004_user_identity_sequences(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS identity_sequences (
                    sequence_key VARCHAR(64) PRIMARY KEY,
                    last_value INTEGER NOT NULL DEFAULT 0
                )
                """
            )
        )

    _add_column_if_missing(engine, "officer_auth", "user_id", "user_id VARCHAR(16)")
    _add_column_if_missing(
        engine,
        "officer_auth",
        "password_change_required",
        "password_change_required INTEGER NOT NULL DEFAULT 0",
    )

    if not _table_exists(engine, "officer_auth"):
        return

    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT officer_id, roles_csv, employee_id
                FROM officer_auth
                ORDER BY created_at ASC, officer_id ASC
                """
            )
        ).all()

        for index, row in enumerate(rows, start=1):
            officer_id = row[0]
            roles_csv = str(row[1] or "")
            employee_id = str(row[2] or "")
            user_id = f"AP-26-{index:02d}" if index < 100 else f"AP-26-{index}"
            connection.execute(
                text("UPDATE officer_auth SET user_id = :user_id WHERE officer_id = :officer_id"),
                {"user_id": user_id, "officer_id": officer_id},
            )

        role_counts = {"super_admin": 0, "station_admin": 0, "police_officer": 0}
        for _, roles_csv, employee_id in rows:
            role = str(roles_csv or "").strip().lower()
            if role in {"admin", "supervisor"}:
                role = "station_admin"
            if role in {"officer"}:
                role = "police_officer"
            if role not in role_counts:
                continue
            prefix = {"super_admin": "ADMIN", "station_admin": "STA", "police_officer": "OFF"}[role]
            if employee_id.upper().startswith(prefix):
                try:
                    role_counts[role] = max(role_counts[role], int(employee_id[len(prefix) :]))
                except ValueError:
                    role_counts[role] += 1
            else:
                role_counts[role] += 1

        user_sequence = len(rows)
        sequences = [
            ("user_id", user_sequence),
            ("employee:SUPER_ADMIN", role_counts["super_admin"]),
            ("employee:STATION_ADMIN", role_counts["station_admin"]),
            ("employee:POLICE_OFFICER", role_counts["police_officer"]),
        ]
        for sequence_key, last_value in sequences:
            connection.execute(
                text(
                    """
                    INSERT INTO identity_sequences (sequence_key, last_value)
                    VALUES (:sequence_key, :last_value)
                    ON CONFLICT(sequence_key) DO UPDATE SET last_value = excluded.last_value
                    """
                ),
                {"sequence_key": sequence_key, "last_value": last_value},
            )

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_officer_auth_user_id "
                "ON officer_auth (user_id)"
            )
        )


def _migration_005_e_challan_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS violation_master (
                    violation_code VARCHAR(64) PRIMARY KEY,
                    violation_name VARCHAR(200) NOT NULL UNIQUE,
                    default_fine_amount FLOAT NOT NULL,
                    amount_editable INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS challans (
                    id VARCHAR(36) PRIMARY KEY,
                    challan_number VARCHAR(32) NOT NULL UNIQUE,
                    investigation_id VARCHAR(36),
                    registration_number VARCHAR(32) NOT NULL,
                    vehicle_id VARCHAR(36),
                    owner_name VARCHAR(200),
                    officer_id VARCHAR(36) NOT NULL,
                    officer_name VARCHAR(200) NOT NULL,
                    station_id VARCHAR(36) NOT NULL,
                    station_name VARCHAR(200) NOT NULL,
                    violation_type VARCHAR(64) NOT NULL,
                    violation_description TEXT,
                    fine_amount FLOAT NOT NULL,
                    remarks TEXT,
                    status VARCHAR(32) NOT NULL,
                    payment_status VARCHAR(32) NOT NULL,
                    location_label VARCHAR(255),
                    gps_coordinates VARCHAR(64),
                    evidence_image_path VARCHAR(512),
                    issued_at TIMESTAMP NOT NULL,
                    paid_at TIMESTAMP,
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
                """
            )
        )

    violations = (
        ("NO_HELMET", "No Helmet", 500, 0),
        ("SEAT_BELT", "Seat Belt", 1000, 0),
        ("SIGNAL_JUMP", "Signal Jump", 1000, 0),
        ("WRONG_PARKING", "Wrong Parking", 500, 0),
        ("TRIPLE_RIDING", "Triple Riding", 1000, 0),
        ("NO_LICENCE", "Driving Without Licence", 5000, 0),
        ("NO_INSURANCE", "No Insurance", 2000, 0),
        ("EXPIRED_POLLUTION", "Expired Pollution", 1000, 0),
        ("MOBILE_WHILE_DRIVING", "Using Mobile While Driving", 1000, 0),
        ("OVERSPEEDING", "Overspeeding", 2000, 0),
        ("FAKE_PLATE", "Fake Number Plate", 5000, 0),
        ("UNREGISTERED_VEHICLE", "Unregistered Vehicle", 5000, 0),
        ("OTHER", "Other", 0, 1),
    )
    with engine.begin() as connection:
        for code, name, amount, editable in violations:
            connection.execute(
                text(
                    """
                    INSERT INTO violation_master (
                        violation_code, violation_name, default_fine_amount, amount_editable, active
                    ) VALUES (:code, :name, :amount, :editable, 1)
                    ON CONFLICT(violation_code) DO NOTHING
                    """
                ),
                {"code": code, "name": name, "amount": amount, "editable": editable},
            )
        connection.execute(
            text(
                """
                INSERT INTO identity_sequences (sequence_key, last_value)
                VALUES ('challan_number:2026', 0)
                ON CONFLICT(sequence_key) DO NOTHING
                """
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_challans_registration ON challans (registration_number)")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_challans_payment_status ON challans (payment_status)")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_challans_station_id ON challans (station_id)")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_challans_officer_id ON challans (officer_id)")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_challans_issued_at ON challans (issued_at)")
        )


def _migration_006_scan_vision_registry_snapshots(engine: Engine) -> None:
    _add_column_if_missing(
        engine,
        "scan_history",
        "vision_snapshot_json",
        "vision_snapshot_json TEXT",
    )
    _add_column_if_missing(
        engine,
        "scan_history",
        "registry_snapshot_json",
        "registry_snapshot_json TEXT",
    )
