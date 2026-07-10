"""Ingestion domain errors."""


class IngestionError(Exception):
    """Base ingestion failure."""

    def __init__(self, code: str, message: str, field: str | None = None) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(message)


class InvalidImageError(IngestionError):
    """Vehicle image failed validation."""

    def __init__(self, message: str, field: str = "image") -> None:
        super().__init__("VALIDATION_ERROR", message, field)
