"""Seed default authentication users."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.application.services.user_identity_service import build_temporary_password
from sentinel_anpr.domain.authentication.officer_status import OfficerStatus
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,
)
from sentinel_anpr.infrastructure.database.repositories.officers.sqlite_user_identity_sequence_repository import (
    sync_identity_sequences,
)

_DEFAULT_USERS: tuple[dict[str, object], ...] = (
    {
        "officer_id": "99999999-9999-9999-9999-999999999999",
        "user_id": "AP-26-01",
        "employee_id": "ADMIN001",
        "badge_number": "ADMIN001",
        "username": "superadmin",
        "email": "admin@sentinelanpr.ai",
        "phone_number": "9000000000",
        "first_name": "System",
        "last_name": "Administrator",
        "rank": "Super Admin",
        "station_id": "88888888-8888-8888-8888-888888888888",
        "station_code": "HQ",
        "station_name": "Headquarters",
        "district": "Prakasam",
        "roles": ("super_admin",),
        "status": OfficerStatus.ACTIVE.value,
        "demo_password": "Admin@123",
    },
    {
        "officer_id": "11111111-1111-1111-1111-111111111111",
        "user_id": "AP-26-02",
        "employee_id": "OFF001",
        "badge_number": "AP001",
        "username": "ap001",
        "email": "ravi.kumar@sentinelanpr.ai",
        "phone_number": "9000000001",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "rank": "Sub-Inspector",
        "station_id": "22222222-2222-2222-2222-222222222222",
        "station_code": "ONG01",
        "station_name": "Ongole Town",
        "district": "Prakasam",
        "roles": ("police_officer",),
        "status": OfficerStatus.ACTIVE.value,
        "demo_password": "Officer@123",
    },
)


def seed_demo_auth_users(session: Session, password_hasher: PasswordHasherPort) -> None:
    """Insert the default officer and super admin accounts if missing."""
    now = datetime.now(UTC)
    for record in _DEFAULT_USERS:
        employee_id = str(record["employee_id"])
        password = str(record.get("demo_password") or build_temporary_password(employee_id))
        officer_id = str(record["officer_id"])
        target_user_id = str(record["user_id"])
        existing = session.get(OfficerAuthModel, officer_id)
        if existing is not None:
            conflict = session.scalar(
                select(OfficerAuthModel).where(
                    OfficerAuthModel.user_id == target_user_id,
                    OfficerAuthModel.officer_id != officer_id,
                )
            )
            if conflict is not None:
                conflict.user_id = f"LEGACY-{conflict.officer_id[:8].upper()}"
                conflict.updated_at = now
                session.add(conflict)
            existing.user_id = target_user_id
            existing.employee_id = employee_id
            existing.badge_number = str(record["badge_number"])
            existing.username = str(record["username"])
            if not existing.phone_number:
                existing.phone_number = str(record["phone_number"])
            if not existing.district:
                existing.district = str(record["district"])
            if not existing.station_name:
                existing.station_name = str(record["station_name"])
            if not existing.station_code:
                existing.station_code = str(record["station_code"])
            existing.password_hash = password_hasher.hash(password)
            existing.updated_at = now
            session.add(existing)
            continue

        session.add(
            OfficerAuthModel(
                officer_id=str(record["officer_id"]),
                user_id=str(record["user_id"]),
                employee_id=employee_id,
                badge_number=str(record["badge_number"]),
                username=str(record["username"]),
                email=str(record["email"]),
                phone_number=str(record["phone_number"]),
                first_name=str(record["first_name"]),
                last_name=str(record["last_name"]),
                rank=str(record["rank"]),
                station_id=str(record["station_id"]),
                station_code=str(record["station_code"]),
                station_name=str(record["station_name"]),
                district=str(record["district"]),
                roles_csv=",".join(record["roles"]),  # type: ignore[arg-type]
                status=str(record["status"]),
                password_hash=password_hasher.hash(password),
                password_change_required=False,
                created_at=now,
                updated_at=now,
            )
        )

    sync_identity_sequences(session)
