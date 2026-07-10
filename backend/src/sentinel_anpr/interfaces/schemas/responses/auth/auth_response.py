"""Authentication response schemas."""

from pydantic import BaseModel


class OfficerSummaryData(BaseModel):
    """Officer profile summary."""

    officer_id: str
    user_id: str
    employee_id: str
    badge_number: str
    username: str
    email: str
    phone_number: str | None
    first_name: str
    last_name: str
    rank: str
    station_id: str
    station_code: str
    station_name: str
    district: str | None
    roles: list[str]


class StationSummaryData(BaseModel):
    """Authenticated station summary."""

    station_id: str
    station_code: str
    station_name: str


class TokenData(BaseModel):
    """Issued access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class LoginResponseData(BaseModel):
    """Login success payload."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    officer: OfficerSummaryData
    user: OfficerSummaryData
    role: str
    permissions: list[str]
    station: StationSummaryData
    token: TokenData


class LogoutResponseData(BaseModel):
    """Logout success payload."""

    message: str


class MeResponseData(BaseModel):
    """Current officer session payload."""

    officer: OfficerSummaryData
    user: OfficerSummaryData
    role: str
    permissions: list[str]
    station: StationSummaryData
    session_id: str
