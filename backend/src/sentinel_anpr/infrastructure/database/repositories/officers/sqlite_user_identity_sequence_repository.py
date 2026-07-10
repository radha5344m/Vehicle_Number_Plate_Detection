"""SQLite-backed identity sequence allocator."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.ports.outbound.user_identity_sequence_port import UserIdentitySequencePort
from sentinel_anpr.application.services.user_identity_service import (
    format_employee_id,
    format_user_id,
)
from sentinel_anpr.infrastructure.database.models.officers.identity_sequence_model import (
    IdentitySequenceModel,
)
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel

_USER_ID_SEQUENCE_KEY = "user_id"
_EMPLOYEE_SEQUENCE_KEYS = {
    "SUPER_ADMIN": "employee:SUPER_ADMIN",
    "STATION_ADMIN": "employee:STATION_ADMIN",
    "POLICE_OFFICER": "employee:POLICE_OFFICER",
}
_EMPLOYEE_PREFIXES = {
    "SUPER_ADMIN": "ADMIN",
    "STATION_ADMIN": "STA",
    "POLICE_OFFICER": "OFF",
}


class SqliteUserIdentitySequenceRepository(UserIdentitySequencePort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def next_user_id(self) -> str:
        with self._session_factory() as session:
            sequence = self._next_value(session, _USER_ID_SEQUENCE_KEY)
            session.commit()
            return format_user_id(sequence)

    def next_employee_id(self, role: str) -> str:
        normalized_role = role.upper()
        sequence_key = _EMPLOYEE_SEQUENCE_KEYS.get(normalized_role)
        if sequence_key is None:
            raise ValueError("Invalid role")
        with self._session_factory() as session:
            sequence = self._next_value(session, sequence_key)
            session.commit()
            return format_employee_id(normalized_role, sequence)

    @staticmethod
    def _next_value(session: Session, sequence_key: str) -> int:
        model = session.get(IdentitySequenceModel, sequence_key, with_for_update=True)
        if model is None:
            model = IdentitySequenceModel(sequence_key=sequence_key, last_value=0)
            session.add(model)
            session.flush()
        model.last_value += 1
        session.add(model)
        return model.last_value


def sync_identity_sequences(session: Session) -> None:
    """Align sequence counters with persisted officer records."""
    user_count = session.scalar(select(func.count()).select_from(OfficerAuthModel)) or 0
    _upsert_sequence(session, _USER_ID_SEQUENCE_KEY, int(user_count))

    role_map = {
        "super_admin": "SUPER_ADMIN",
        "station_admin": "STATION_ADMIN",
        "admin": "STATION_ADMIN",
        "supervisor": "STATION_ADMIN",
        "police_officer": "POLICE_OFFICER",
        "officer": "POLICE_OFFICER",
    }
    for role_key, canonical_role in role_map.items():
        prefix = _EMPLOYEE_PREFIXES[canonical_role]
        rows = session.scalars(
            select(OfficerAuthModel.employee_id).where(OfficerAuthModel.roles_csv == role_key)
        ).all()
        max_value = 0
        for employee_id in rows:
            if not str(employee_id).upper().startswith(prefix):
                continue
            suffix = str(employee_id)[len(prefix) :]
            if suffix.isdigit():
                max_value = max(max_value, int(suffix))
        sequence_key = _EMPLOYEE_SEQUENCE_KEYS[canonical_role]
        existing = session.get(IdentitySequenceModel, sequence_key)
        current = existing.last_value if existing is not None else 0
        _upsert_sequence(session, sequence_key, max(current, max_value))


def _upsert_sequence(session: Session, sequence_key: str, last_value: int) -> None:
    model = session.get(IdentitySequenceModel, sequence_key)
    if model is None:
        session.add(IdentitySequenceModel(sequence_key=sequence_key, last_value=last_value))
        return
    model.last_value = max(model.last_value, last_value)
    session.add(model)
