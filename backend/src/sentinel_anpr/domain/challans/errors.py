"""Challan domain errors."""


class ChallanAccessDeniedError(PermissionError):
    """Caller is not allowed to access the requested challan."""


class ChallanNotFoundError(LookupError):
    """Requested challan does not exist."""
