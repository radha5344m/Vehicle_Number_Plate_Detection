"""Shared API response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Response metadata."""

    correlation_id: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard success envelope."""

    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
