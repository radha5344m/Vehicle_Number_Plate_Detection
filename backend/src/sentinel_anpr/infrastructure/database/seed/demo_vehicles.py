"""Demo vehicle seed data."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel

_DEMO_VEHICLES: tuple[dict[str, object], ...] = (
    {
        "vehicle_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "plate_number": "AP09AB1234",
        "jurisdiction": "AP",
        "make": "Toyota",
        "model": "Innova Crysta",
        "color": "White",
        "year": 2020,
        "vehicle_type": "car",
        "registration_status": "active",
        "registered_owner": "Ravi Kumar",
        "registry_external_id": "RTO-ONG-1001",
    },
    {
        "vehicle_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "plate_number": "AP10CD5678",
        "jurisdiction": "AP",
        "make": "Hyundai",
        "model": "Creta",
        "color": "Black",
        "year": 2022,
        "vehicle_type": "car",
        "registration_status": "active",
        "registered_owner": "Sita Devi",
        "registry_external_id": "RTO-ONG-1002",
    },
    {
        "vehicle_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "plate_number": "AP11EF9012",
        "jurisdiction": "AP",
        "make": "Honda",
        "model": "Activa",
        "color": "Red",
        "year": 2019,
        "vehicle_type": "motorcycle",
        "registration_status": "stolen",
        "registered_owner": "Unknown",
        "registry_external_id": "RTO-ONG-1003",
    },
    {
        "vehicle_id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "plate_number": "AP12GH3456",
        "jurisdiction": "AP",
        "make": "Tata",
        "model": "Ace",
        "color": "Blue",
        "year": 2018,
        "vehicle_type": "truck",
        "registration_status": "suspended",
        "registered_owner": "Prakash Transport",
        "registry_external_id": "RTO-ONG-1004",
    },
)


def seed_demo_vehicles(session: Session) -> None:
    """Insert demo vehicles when the table is empty."""
    count = session.scalar(select(func.count()).select_from(VehicleModel))
    if count and count > 0:
        return

    now = datetime.now(UTC)
    for record in _DEMO_VEHICLES:
        session.add(
            VehicleModel(
                vehicle_id=str(record["vehicle_id"]),
                plate_number=str(record["plate_number"]),
                jurisdiction=str(record["jurisdiction"]),
                make=str(record["make"]),
                model=str(record["model"]),
                color=str(record["color"]),
                year=int(record["year"]),  # type: ignore[arg-type]
                vehicle_type=str(record["vehicle_type"]),
                registration_status=str(record["registration_status"]),
                registered_owner=str(record["registered_owner"]),
                registry_external_id=str(record["registry_external_id"]),
                registry_synced_at=now,
                created_at=now,
                updated_at=now,
            )
        )
