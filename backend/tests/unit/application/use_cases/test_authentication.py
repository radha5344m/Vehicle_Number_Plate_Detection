"""Authentication use case unit tests."""

import pytest

from sentinel_anpr.application.dto.auth_dto import LoginCommand
from sentinel_anpr.application.use_cases.authentication.login_use_case import LoginUseCase
from sentinel_anpr.domain.authentication.errors import InvalidCredentialsError
from sentinel_anpr.infrastructure.authentication.jwt.jwt_token_provider import JwtTokenProvider
from sentinel_anpr.infrastructure.authentication.password.bcrypt_hasher import BcryptPasswordHasher
from sentinel_anpr.infrastructure.authentication.stores.in_memory_credential_store import (
    InMemoryCredentialStore,
)
from sentinel_anpr.infrastructure.authentication.stores.in_memory_refresh_token_store import (
    InMemoryRefreshTokenStore,
)


def _login_use_case() -> LoginUseCase:
    password_hasher = BcryptPasswordHasher()
    credential_store = InMemoryCredentialStore(password_hasher=password_hasher)
    token_provider = JwtTokenProvider(
        secret="test-secret",
        issuer="test-issuer",
        access_token_ttl_seconds=900,
        refresh_token_ttl_seconds=604800,
    )
    return LoginUseCase(
        credential_store=credential_store,
        password_hasher=password_hasher,
        token_provider=token_provider,
        refresh_token_store=InMemoryRefreshTokenStore(),
    )


def test_login_success() -> None:
    use_case = _login_use_case()
    result = use_case.execute(
        LoginCommand(identifier="ap001", password="Officer@123")
    )
    assert result.token_type == "Bearer"
    assert result.officer.badge_number == "AP001"
    assert result.role == "POLICE_OFFICER"
    assert "vehicle_verification" in result.permissions
    assert result.access_token
    assert result.refresh_token


def test_login_invalid_password() -> None:
    use_case = _login_use_case()
    with pytest.raises(InvalidCredentialsError):
        use_case.execute(LoginCommand(identifier="ap001", password="wrong-password"))


def test_login_with_employee_id() -> None:
    use_case = _login_use_case()
    result = use_case.execute(
        LoginCommand(identifier="OFF001", password="Officer@123")
    )
    assert result.officer.employee_id == "OFF001"
