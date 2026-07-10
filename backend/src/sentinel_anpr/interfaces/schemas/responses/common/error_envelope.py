"""Error response envelope."""

from pydantic import BaseModel, Field

from sentinel_anpr.interfaces.schemas.responses.common.envelope import ResponseMeta


class ErrorBody(BaseModel):
    """Machine-readable error details."""

    code: str
    message: str
    details: list[dict[str, str]] = Field(default_factory=list)
    exception: str | None = None


class ApiErrorResponse(BaseModel):
    """Standard error envelope."""

    success: bool = False
    error: ErrorBody
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
