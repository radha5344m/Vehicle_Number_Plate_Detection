"""Demo scan history seed data."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_anpr.infrastructure.database.models.scan_history.scan_model import ScanModel

_OFFICER_RAVI = "11111111-1111-1111-1111-111111111111"
_OFFICER_SITA = "33333333-3333-3333-3333-333333333333"

_DEMO_SCANS: tuple[dict[str, object], ...] = (
    {
        "scan_id": "scan-0001-aaaa-aaaa-aaaaaaaaaaaa",
        "officer_id": _OFFICER_RAVI,
        "officer_name": "Ravi Kumar",
        "vehicle_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "plate_text": "AP09AB1234",
        "risk_score": 0.0,
        "risk_level": "low",
        "location_label": "Ongole Checkpoint",
        "days_ago": 1,
    },
    {
        "scan_id": "scan-0002-bbbb-bbbb-bbbbbbbbbbbb",
        "officer_id": _OFFICER_SITA,
        "officer_name": "Sita Devi",
        "vehicle_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "plate_text": "AP10CD5678",
        "risk_score": 0.12,
        "risk_level": "low",
        "location_label": "Chirala Toll Plaza",
        "days_ago": 2,
    },
    {
        "scan_id": "scan-0003-cccc-cccc-cccccccccccc",
        "officer_id": _OFFICER_RAVI,
        "officer_name": "Ravi Kumar",
        "vehicle_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "plate_text": "AP11EF9012",
        "risk_score": 0.55,
        "risk_level": "critical",
        "location_label": "Ongole Market Road",
        "days_ago": 3,
    },
    {
        "scan_id": "scan-0004-dddd-dddd-dddddddddddd",
        "officer_id": _OFFICER_SITA,
        "officer_name": "Sita Devi",
        "vehicle_id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "plate_text": "AP12GH3456",
        "risk_score": 0.35,
        "risk_level": "medium",
        "location_label": "Kandukur Highway",
        "days_ago": 4,
    },
    {
        "scan_id": "scan-0005-eeee-eeee-eeeeeeeeeeee",
        "officer_id": _OFFICER_RAVI,
        "officer_name": "Ravi Kumar",
        "vehicle_id": None,
        "plate_text": "AP99ZZ9999",
        "risk_score": 0.35,
        "risk_level": "medium",
        "location_label": "Ongole Bus Stand",
        "days_ago": 5,
    },
    {
        "scan_id": "scan-0006-ffff-ffff-ffffffffffff",
        "officer_id": _OFFICER_SITA,
        "officer_name": "Sita Devi",
        "vehicle_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "plate_text": "AP09AB1234",
        "risk_score": 0.52,
        "risk_level": "high",
        "location_label": "Addanki Junction",
        "days_ago": 6,
    },
    {
        "scan_id": "scan-0007-1111-1111-111111111111",
        "officer_id": _OFFICER_RAVI,
        "officer_name": "Ravi Kumar",
        "vehicle_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "plate_text": "AP10CD5678",
        "risk_score": 0.28,
        "risk_level": "medium",
        "location_label": "Ongole Railway Station",
        "days_ago": 7,
    },
    {
        "scan_id": "scan-0008-2222-2222-222222222222",
        "officer_id": _OFFICER_SITA,
        "officer_name": "Sita Devi",
        "vehicle_id": None,
        "plate_text": "AP88XY4321",
        "risk_score": 0.35,
        "risk_level": "medium",
        "location_label": "Martur Check Post",
        "days_ago": 8,
    },
)


def seed_demo_scans(session: Session) -> None:
    """Insert demo scan history when the table is empty."""
    count = session.scalar(select(func.count()).select_from(ScanModel))
    if count and count > 0:
        return

    now = datetime.now(UTC)
    for record in _DEMO_SCANS:
        scanned_at = now - timedelta(days=int(record["days_ago"]))  # type: ignore[arg-type]
        session.add(
            ScanModel(
                scan_id=str(record["scan_id"]),
                officer_id=str(record["officer_id"]),
                officer_name=str(record["officer_name"]),
                vehicle_id=str(record["vehicle_id"]) if record["vehicle_id"] else None,
                plate_text=str(record["plate_text"]),
                risk_score=float(record["risk_score"]),  # type: ignore[arg-type]
                risk_level=str(record["risk_level"]),
                processing_status="completed",
                location_label=str(record["location_label"]),
                scanned_at=scanned_at,
                completed_at=scanned_at + timedelta(minutes=2),
                created_at=scanned_at,
            )
        )
