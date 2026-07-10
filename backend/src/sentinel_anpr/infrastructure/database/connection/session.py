"""Database session factory placeholder."""

from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a sessionmaker bound to the engine."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Yield a database session (for future repository use)."""
    session = factory()
    try:
        yield session
    finally:
        session.close()
