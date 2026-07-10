"""Tests for identity sequence allocation."""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.infrastructure.database.models.base import Base
from sentinel_anpr.infrastructure.database.models.officers.identity_sequence_model import (
    IdentitySequenceModel,
)
from sentinel_anpr.infrastructure.database.repositories.officers.sqlite_user_identity_sequence_repository import (
    SqliteUserIdentitySequenceRepository,
)


def _session_factory(engine) -> sessionmaker[Session]:  # noqa: ANN001
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def test_next_user_and_employee_ids_increment_without_reuse(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'identity.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(IdentitySequenceModel(sequence_key="user_id", last_value=0))
        session.add(IdentitySequenceModel(sequence_key="employee:SUPER_ADMIN", last_value=0))
        session.commit()

    repository = SqliteUserIdentitySequenceRepository(session_factory=_session_factory(engine))
    first_user_id = repository.next_user_id()
    second_user_id = repository.next_user_id()
    first_employee_id = repository.next_employee_id("SUPER_ADMIN")
    second_employee_id = repository.next_employee_id("SUPER_ADMIN")

    assert first_user_id.startswith("AP-")
    assert first_user_id.endswith("-01")
    assert second_user_id.endswith("-02")
    assert first_employee_id == "ADMIN001"
    assert second_employee_id == "ADMIN002"
    assert first_user_id != second_user_id
    assert first_employee_id != second_employee_id


def test_role_specific_employee_sequences_are_independent(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'identity-role.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(IdentitySequenceModel(sequence_key="employee:STATION_ADMIN", last_value=0))
        session.add(IdentitySequenceModel(sequence_key="employee:POLICE_OFFICER", last_value=0))
        session.commit()

    repository = SqliteUserIdentitySequenceRepository(session_factory=_session_factory(engine))
    assert repository.next_employee_id("STATION_ADMIN") == "STA001"
    assert repository.next_employee_id("POLICE_OFFICER") == "OFF001"
    assert repository.next_employee_id("STATION_ADMIN") == "STA002"
