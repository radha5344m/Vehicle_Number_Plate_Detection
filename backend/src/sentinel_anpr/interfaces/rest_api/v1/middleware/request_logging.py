"""Structured request logging middleware."""

import logging
import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from sentinel_anpr.infrastructure.logging.context import correlation_id_var

_logger = logging.getLogger("sentinel_anpr.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests with correlation ID and duration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        started = time.perf_counter()
        correlation_id = getattr(request.state, "correlation_id", None)
        token = correlation_id_var.set(correlation_id)

        _logger.info(
            "request_started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
            },
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            _logger.error(
                "request_failed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
                exc_info=True,
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            _logger.info(
                "request_completed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response
        finally:
            correlation_id_var.reset(token)
