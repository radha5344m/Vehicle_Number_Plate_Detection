"""SQLite database health adapter."""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from sentinel_anpr.application.ports.outbound.database_port import DatabasePort


class SqliteDatabaseAdapter(DatabasePort):
    """Probes database connectivity without ORM models."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def ping(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
