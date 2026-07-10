"""SQLite-backed credential store."""

from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.auth_dto import OfficerIdentity
from sentinel_anpr.application.ports.outbound.credential_store_port import (
    CredentialStorePort,
    StoredCredential,
)
from sentinel_anpr.application.services.auth_permissions import normalize_roles
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,
)


class SqliteCredentialStore(CredentialStorePort):
    """Load login accounts from the SQLite auth table."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_identifier(self, identifier: str) -> StoredCredential | None:
        normalized = identifier.strip()
        if not normalized:
            return None
        with self._session_factory() as session:
            model = session.scalar(
                select(OfficerAuthModel).where(
                    or_(
                        OfficerAuthModel.badge_number == normalized.upper(),
                        OfficerAuthModel.username == normalized.lower(),
                        OfficerAuthModel.employee_id == normalized.upper(),
                        OfficerAuthModel.user_id == normalized.upper(),
                    )
                )
            )
        return self._to_stored_credential(model)

    def find_by_id(self, officer_id: str) -> StoredCredential | None:
        with self._session_factory() as session:
            model = session.get(OfficerAuthModel, officer_id)
        return self._to_stored_credential(model)

    @staticmethod
    def _to_stored_credential(model: OfficerAuthModel | None) -> StoredCredential | None:
        if model is None:
            return None
        roles = normalize_roles(
            tuple(role.strip() for role in model.roles_csv.split(",") if role.strip())
        )
        return StoredCredential(
            officer=OfficerIdentity(
                officer_id=model.officer_id,
                user_id=model.user_id,
                badge_number=model.badge_number,
                employee_id=model.employee_id,
                username=model.username,
                email=model.email,
                phone_number=model.phone_number,
                first_name=model.first_name,
                last_name=model.last_name,
                rank=model.rank,
                station_id=model.station_id,
                station_code=model.station_code,
                station_name=model.station_name,
                district=model.district,
                roles=roles,
                status=model.status,
                created_at=model.created_at,
                last_login_at=model.last_login_at,
            ),
            password_hash=model.password_hash,
        )

    def record_successful_login(self, officer_id: str) -> None:
        with self._session_factory() as session:
            model = session.get(OfficerAuthModel, officer_id)
            if model is None:
                return
            model.last_login_at = datetime.now(UTC)
            session.add(model)
            session.commit()
