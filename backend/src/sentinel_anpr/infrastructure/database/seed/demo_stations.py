"""Demo police station seed data."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_anpr.infrastructure.database.models.stations.station_model import PoliceStationModel

_DEMO_STATIONS: tuple[dict[str, str], ...] = (
    {
        "station_id": "88888888-8888-8888-8888-888888888888",
        "station_name": "Headquarters",
        "station_code": "HQ",
        "district": "Prakasam",
        "state": "Andhra Pradesh",
        "address": "Police Headquarters, Prakasam District",
        "pincode": "523001",
        "phone_number": "9000000000",
        "email": "hq@sentinelanpr.ai",
        "station_type": "headquarters",
        "status": "active",
    },
    {
        "station_id": "22222222-2222-2222-2222-222222222222",
        "station_name": "Ongole Town",
        "station_code": "ONG01",
        "district": "Prakasam",
        "state": "Andhra Pradesh",
        "address": "Ongole Town Police Station",
        "pincode": "523001",
        "phone_number": "9000000001",
        "email": "ongole.town@sentinelanpr.ai",
        "station_type": "town",
        "status": "active",
    },
    {
        "station_id": "33333333-3333-3333-3333-333333333333",
        "station_name": "Ongole Rural",
        "station_code": "ONG02",
        "district": "Prakasam",
        "state": "Andhra Pradesh",
        "address": "Ongole Rural Police Station",
        "pincode": "523001",
        "phone_number": "9000000002",
        "email": "ongole.rural@sentinelanpr.ai",
        "station_type": "rural",
        "status": "active",
    },
    {
        "station_id": "44444444-4444-4444-4444-444444444444",
        "station_name": "Markapur Town",
        "station_code": "MRK01",
        "district": "Prakasam",
        "state": "Andhra Pradesh",
        "address": "Markapur Town Police Station",
        "pincode": "523316",
        "phone_number": "9000000003",
        "email": "markapur.town@sentinelanpr.ai",
        "station_type": "town",
        "status": "active",
    },
)


def seed_demo_stations(session: Session) -> None:
    """Insert default stations if they are missing."""
    now = datetime.now(UTC)
    for record in _DEMO_STATIONS:
        existing = session.scalar(
            select(PoliceStationModel).where(
                PoliceStationModel.station_code == record["station_code"]
            )
        )
        if existing is not None:
            changed = False
            if existing.deleted_at is not None:
                existing.deleted_at = None
                changed = True
            if existing.status != record["status"]:
                existing.status = record["status"]
                changed = True
            if changed:
                existing.updated_at = now
                session.add(existing)
            continue
        session.add(
            PoliceStationModel(
                station_id=record["station_id"],
                station_name=record["station_name"],
                station_code=record["station_code"],
                district=record["district"],
                state=record["state"],
                address=record["address"],
                pincode=record["pincode"],
                phone_number=record["phone_number"],
                email=record["email"],
                station_type=record["station_type"],
                status=record["status"],
                created_at=now,
                updated_at=now,
            )
        )
