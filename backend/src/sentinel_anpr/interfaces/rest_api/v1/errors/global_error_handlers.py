"""Global and infrastructure exception handlers."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from sentinel_anpr.domain.common.errors import InfrastructureError
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response

_logger = logging.getLogger("sentinel_anpr.errors")


def register_global_exception_handlers(app: FastAPI) -> None:
    """Catch unhandled exceptions and normalize HTTPException responses."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, str):
            message = detail
            details: list[dict[str, str]] = []
        elif isinstance(detail, list):
            message = "Request validation failed"
            details = [
                {
                    "field": ".".join(str(part) for part in item.get("loc", ())),
                    "code": item.get("type", "validation_error"),
                    "message": item.get("msg", "Invalid value"),
                }
                for item in detail
                if isinstance(item, dict)
            ]
        else:
            message = "Request could not be processed"
            details = []

        code = "NOT_FOUND" if exc.status_code == 404 else "VALIDATION_ERROR"
        if isinstance(detail, str) and exc.status_code == 400:
            code = "INVALID_REQUEST"
        if exc.status_code >= 500:
            code = "INTERNAL_ERROR"

        return build_error_response(
            request,
            exc.status_code,
            code,
            message,
            details=details,
            log_level="warning" if exc.status_code < 500 else "error",
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        _logger.error(
            "database_error",
            extra={
                "path": request.url.path,
                "method": request.method,
                "correlation_id": getattr(request.state, "correlation_id", None),
            },
            exc_info=exc,
        )
        return build_error_response(
            request,
            503,
            "DATABASE_ERROR",
            "Database service is temporarily unavailable. Please try again later.",
            log_level=None,
            exc=exc,
        )

    @app.exception_handler(InfrastructureError)
    async def infrastructure_exception_handler(
        request: Request,
        exc: InfrastructureError,
    ) -> JSONResponse:
        status_code = 504 if exc.code == "AI_TIMEOUT" else 503
        if exc.code == "INTERNAL_ERROR":
            status_code = 500
        return build_error_response(
            request,
            status_code,
            exc.code,
            exc.message,
            log_level="error" if status_code >= 500 else "warning",
            exc=exc,
        )

    @app.exception_handler(LookupError)
    async def lookup_error_handler(request: Request, exc: LookupError) -> JSONResponse:
        return build_error_response(
            request,
            404,
            "NOT_FOUND",
            str(exc) or "Resource not found",
            log_level="warning",
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        _logger.error(
            "unhandled_exception",
            extra={
                "path": request.url.path,
                "method": request.method,
                "correlation_id": getattr(request.state, "correlation_id", None),
                "error_type": type(exc).__name__,
            },
            exc_info=exc,
        )
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "An unexpected error occurred. Please try again or contact support.",
            log_level=None,
            exc=exc,
        )
