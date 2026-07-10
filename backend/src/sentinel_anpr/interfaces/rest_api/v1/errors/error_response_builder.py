"""Build standardized API error responses."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from sentinel_anpr.application.services.error_mapper import to_user_message
from sentinel_anpr.infrastructure.logging.context import correlation_id_var
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ResponseMeta
from sentinel_anpr.interfaces.schemas.responses.common.error_envelope import (
    ApiErrorResponse,
    ErrorBody,
)

_logger = logging.getLogger("sentinel_anpr.errors")


def build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    *,
    details: list[dict[str, str]] | None = None,
    log_level: str | None = None,
    exc: Exception | None = None,
) -> JSONResponse:
    """Return a consistent error envelope with a user-friendly message."""
    correlation_id = getattr(request.state, "correlation_id", None) or correlation_id_var.get()
    user_message = to_user_message(code, message)

    if log_level:
        log_fn = getattr(_logger, log_level, _logger.error)
        log_fn(
            "api_error",
            extra={
                "error_code": code,
                "status_code": status_code,
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "detail": message,
            },
            exc_info=exc if log_level == "error" else None,
        )

    body = ApiErrorResponse(
        error=ErrorBody(
            code=code,
            message=user_message,
            details=details or [],
            exception=f"{type(exc).__name__}: {exc}" if exc is not None else None,
        ),
        meta=ResponseMeta(correlation_id=correlation_id),
    )
    payload = body.model_dump()
    if correlation_id:
        payload["trace_id"] = correlation_id
    return JSONResponse(status_code=status_code, content=payload)
