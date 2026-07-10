"""Authentication error handlers."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sentinel_anpr.domain.authentication.errors import AuthenticationError
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response


def register_auth_exception_handlers(app: FastAPI) -> None:
    """Map authentication and validation errors to API envelopes."""

    forbidden_codes = {"AUTH_FORBIDDEN", "AUTH_ACCOUNT_INACTIVE"}

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        status_code = 403 if exc.code in forbidden_codes else 401
        return build_error_response(request, status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in error.get("loc", ())),
                "code": error.get("type", "validation_error"),
                "message": error.get("msg", "Invalid value"),
            }
            for error in exc.errors()
        ]
        return build_error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Request validation failed",
            details=details,
        )
