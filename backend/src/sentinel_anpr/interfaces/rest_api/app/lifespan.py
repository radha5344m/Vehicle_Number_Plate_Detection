"""FastAPI application lifespan."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container


@asynccontextmanager
async def     lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup: wire DI container. Shutdown: dispose database engine."""
    container = build_container()
    app.state.container = container
    yield
    container.engine.dispose()
