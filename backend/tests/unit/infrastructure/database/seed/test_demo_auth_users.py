"""Authentication seed tests."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_anpr.infrastructure.authentication.password.bcrypt_hasher import BcryptPasswordHasher
from sentinel_anpr.infrastructure.database.connection.engine import create_db_engine
from sentinel_anpr.infrastructure.database.init_demo_database import initialize_demo_database
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import (
    OfficerAuthModel,
)


def test_initialize_demo_database_seeds_super_admin_once(tmp_path) -> None:
    database_path = tmp_path / "auth-seed.sqlite3"
    engine = create_db_engine(f"sqlite:///{database_path}")
    password_hasher = BcryptPasswordHasher()

    initialize_demo_database(engine, password_hasher=password_hasher)
    initialize_demo_database(engine, password_hasher=password_hasher)

    with Session(engine) as session:
        count = session.scalar(
            select(func.count())
            .select_from(OfficerAuthModel)
            .where(OfficerAuthModel.username == "superadmin")
        )
        super_admin = session.scalar(
            select(OfficerAuthModel).where(OfficerAuthModel.username == "superadmin")
        )

    assert count == 1
    assert super_admin is not None
    assert super_admin.email == "admin@sentinelanpr.ai"
    assert super_admin.station_name == "Headquarters"
    assert super_admin.password_hash != "Admin@123"
