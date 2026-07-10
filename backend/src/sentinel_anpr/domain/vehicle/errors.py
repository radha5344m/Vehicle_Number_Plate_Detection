"""Vehicle domain errors."""


class VehicleError(Exception):
    """Base vehicle module failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InvalidPlateError(VehicleError):
    """Registration number is missing or invalid."""

    def __init__(self) -> None:
        super().__init__("VALIDATION_ERROR", "Registration number is required")
