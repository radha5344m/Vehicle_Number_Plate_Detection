"""Health check data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HealthCheck:
    """Individual health probe result."""

    name: str
    status: str
    message: str


@dataclass(frozen=True)
class HealthResult:
    """Health probe result."""

    status: str
    version: str
    environment: str
    database: str
    ready: bool
    checked_at: datetime
    checks: tuple[HealthCheck, ...]
