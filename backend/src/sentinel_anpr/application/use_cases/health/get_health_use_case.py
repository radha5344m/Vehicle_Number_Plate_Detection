"""Health check use case."""

from datetime import UTC, datetime

from sentinel_anpr.application.dto.health_dto import HealthCheck, HealthResult
from sentinel_anpr.application.ports.outbound.config_port import ConfigPort
from sentinel_anpr.application.ports.outbound.database_port import DatabasePort
from sentinel_anpr import __version__


class GetHealthUseCase:
    """Return application health status (no business rules)."""

    def __init__(self, config: ConfigPort, database: DatabasePort) -> None:
        self._config = config
        self._database = database

    def execute(self) -> HealthResult:
        checked_at = datetime.now(UTC)
        db_ok = self._database.ping()
        database_status = "connected" if db_ok else "unavailable"
        checks = (
            HealthCheck(
                name="database",
                status="pass" if db_ok else "fail",
                message="Database connection is healthy"
                if db_ok
                else "Database connection failed",
            ),
        )
        ready = db_ok
        status = "ok" if ready else "degraded"
        return HealthResult(
            status=status,
            version=__version__,
            environment=self._config.environment,
            database=database_status,
            ready=ready,
            checked_at=checked_at,
            checks=checks,
        )
