"""Health endpoint response schema."""

from datetime import datetime

from pydantic import BaseModel


class HealthCheckData(BaseModel):
    """Single health probe."""

    name: str
    status: str
    message: str


class HealthResponseData(BaseModel):
    """Health check payload."""

    status: str
    version: str
    environment: str
    database: str
    ready: bool
    checked_at: datetime
    checks: list[HealthCheckData]
