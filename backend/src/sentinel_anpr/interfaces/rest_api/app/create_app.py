"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sentinel_anpr.infrastructure.config.settings import get_settings, resolve_cors_origins, resolve_cors_origin_regex
from sentinel_anpr.interfaces.rest_api.app.lifespan import lifespan
from sentinel_anpr.interfaces.rest_api.app.static_frontend import (
    register_api_root_route,
    register_frontend_static_routes,
)
from sentinel_anpr.interfaces.rest_api.v1.errors.auth_error_handlers import (
    register_auth_exception_handlers,
)
from sentinel_anpr.interfaces.rest_api.v1.errors.global_error_handlers import (
    register_global_exception_handlers,
)
from sentinel_anpr.interfaces.rest_api.v1.errors.ingestion_error_handlers import (
    register_ingestion_exception_handlers,
)
from sentinel_anpr.interfaces.rest_api.v1.errors.vehicle_error_handlers import (
    register_vehicle_exception_handlers,
)
from sentinel_anpr.interfaces.rest_api.v1.middleware.auth_middleware import AuthMiddleware
from sentinel_anpr.interfaces.rest_api.v1.middleware.correlation_id import CorrelationIdMiddleware
from sentinel_anpr.interfaces.rest_api.v1.middleware.request_logging import RequestLoggingMiddleware
from sentinel_anpr.interfaces.rest_api.v1.routes.router import api_v1_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    cors_origins = resolve_cors_origins(settings)
    cors_origin_regex = resolve_cors_origin_regex(settings)
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    # CORS must be outermost so preflight OPTIONS and error responses include ACAO headers.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_auth_exception_handlers(app)
    register_ingestion_exception_handlers(app)
    register_vehicle_exception_handlers(app)
    register_global_exception_handlers(app)
    app.include_router(api_v1_router)
    register_frontend_static_routes(app)
    register_api_root_route(app)
    return app
