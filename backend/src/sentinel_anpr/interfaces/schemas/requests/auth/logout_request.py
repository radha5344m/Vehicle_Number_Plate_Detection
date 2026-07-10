"""Logout request schema."""

from pydantic import BaseModel, Field


class LogoutRequest(BaseModel):
    """Refresh token to revoke on logout."""

    refresh_token: str = Field(min_length=1)
