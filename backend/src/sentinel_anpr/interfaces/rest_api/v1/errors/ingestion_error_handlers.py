"""Ingestion error handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sentinel_anpr.domain.ingestion.errors import IngestionError
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response


def register_ingestion_exception_handlers(app: FastAPI) -> None:
    """Map ingestion validation errors to API envelopes."""

    @app.exception_handler(IngestionError)
    async def ingestion_error_handler(
        request: Request,
        exc: IngestionError,
    ) -> JSONResponse:
        details = []
        if exc.field:
            details.append(
                {
                    "field": exc.field,
                    "code": exc.code.lower(),
                    "message": exc.message,
                }
            )
        return build_error_response(
            request,
            400,
            exc.code,
            exc.message,
            details=details,
        )
