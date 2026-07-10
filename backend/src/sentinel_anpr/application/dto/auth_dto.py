"""Authentication data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OfficerIdentity:
    """Officer profile returned after successful authentication."""

    officer_id: str
    user_id: str
    badge_number: str
    employee_id: str
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
    roles: tuple[str, ...]
    status: str
    created_at: datetime | None = None
    last_login_at: datetime | None = None


@dataclass(frozen=True)
class LoginCommand:
    """Officer login request."""

    identifier: str
    password: str
    station_code: str | None = None


@dataclass(frozen=True)
class LoginResult:
    """Tokens and officer profile after login."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    officer: OfficerIdentity
    role: str
    permissions: tuple[str, ...]
    session_id: str


@dataclass(frozen=True)
class AuthPrincipal:
    """Authenticated caller resolved from a JWT."""

    officer_id: str
    badge_number: str
    station_id: str
    roles: tuple[str, ...]
    role: str
    permissions: tuple[str, ...]
    session_id: str


@dataclass(frozen=True)
class LogoutCommand:
    """Logout request."""

    refresh_token: str
    principal: AuthPrincipal


@dataclass(frozen=True)
class MeResult:
    """Current officer session details."""

    officer: OfficerIdentity
    permissions: tuple[str, ...]
    session_id: str
