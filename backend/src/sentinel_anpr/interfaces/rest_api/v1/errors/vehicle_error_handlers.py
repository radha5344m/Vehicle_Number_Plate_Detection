"""Vehicle error handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sentinel_anpr.domain.vehicle.errors import VehicleError
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response


def register_vehicle_exception_handlers(app: FastAPI) -> None:
    """Map vehicle validation errors to API envelopes."""

    @app.exception_handler(VehicleError)
    async def vehicle_error_handler(
        request: Request,
        exc: VehicleError,
    ) -> JSONResponse:
        return build_error_response(request, 400, exc.code, exc.message)
