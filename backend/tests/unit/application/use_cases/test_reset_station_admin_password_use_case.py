"""ResetStationAdminPasswordUseCase tests."""

from datetime import UTC, datetime

import pytest

from sentinel_anpr.application.dto.persistence_dto import SaveOfficerActivityCommand
from sentinel_anpr.application.dto.user_management_dto import (
    ResetStationAdminPasswordCommand,
    UserDetailDto,
    UserMutationResult,
)
from sentinel_anpr.application.use_cases.authentication.user_management_use_cases import (
    ResetStationAdminPasswordUseCase,
)
from sentinel_anpr.domain.authentication.user_management_errors import SuperAdminRequiredError


class _FakeLogger:
    def info(self, message: str, **context) -> None:
        del message, context


class _FakeHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"


class _FakeRepository:
    def __init__(self, user: UserDetailDto | None) -> None:
        self._user = user
        self.password_change_required: bool | None = None
        self.last_hash: str | None = None

    def get_user(self, officer_id: str) -> UserDetailDto | None:
        del officer_id
        return self._user

    def reset_password(self, command, password_hash: str, *, password_change_required: bool = False) -> None:
        del command
        self.last_hash = password_hash
        self.password_change_required = password_change_required


class _FakeOfficerActivity:
    def __init__(self) -> None:
        self.saved: tuple[SaveOfficerActivityCommand, ...] = ()

    def save_activities(self, commands: tuple[SaveOfficerActivityCommand, ...], *, transaction=None):
        del transaction
        self.saved = commands
        return tuple(f"activity-{index}" for index, _ in enumerate(commands))


def _station_admin() -> UserDetailDto:
    return UserDetailDto(
        officer_id="station-admin-1",
        user_id="AP-01-01",
        employee_id="STA001",
        first_name="Station",
        last_name="Admin",
        full_name="Station Admin",
        username="sta001",
        email="admin@example.com",
        phone_number=None,
        badge_number="STA001",
        rank="Inspector",
        role="STATION_ADMIN",
        police_station="Markapur Town",
        station_code="MKP",
        station_id="station-1",
        district="Prakasam",
        status="active",
        created_at=datetime.now(UTC),
        last_login_at=None,
    )


def _super_admin_principal():
    from sentinel_anpr.application.dto.auth_dto import AuthPrincipal

    return AuthPrincipal(
        officer_id="super-admin-1",
        badge_number="ADMIN001",
        station_id="hq",
        roles=("super_admin",),
        role="super_admin",
        permissions=("users",),
        session_id="session-1",
    )


def test_reset_station_admin_password_hashes_and_sets_change_required() -> None:
    repository = _FakeRepository(_station_admin())
    activity = _FakeOfficerActivity()
    use_case = ResetStationAdminPasswordUseCase(
        repository=repository,
        password_hasher=_FakeHasher(),
        officer_activity_repository=activity,
        logger=_FakeLogger(),
    )

    result = use_case.execute(
        _super_admin_principal(),
        ResetStationAdminPasswordCommand(
            officer_id="station-admin-1",
            new_password="TempPass@123",
            confirm_password="TempPass@123",
        ),
    )

    assert repository.last_hash == "hashed:TempPass@123"
    assert repository.password_change_required is True
    assert result.password_change_required is True
    assert result.temporary_password is None
    assert len(activity.saved) == 1
    assert activity.saved[0].activity_type == "PASSWORD_RESET"
    assert activity.saved[0].officer_id == "station-admin-1"
    assert activity.saved[0].correlation_id == "super-admin-1"


def test_reset_station_admin_password_rejects_mismatched_passwords() -> None:
    use_case = ResetStationAdminPasswordUseCase(
        repository=_FakeRepository(_station_admin()),
        password_hasher=_FakeHasher(),
        officer_activity_repository=_FakeOfficerActivity(),
        logger=_FakeLogger(),
    )

    with pytest.raises(ValueError, match="must match"):
        use_case.execute(
            _super_admin_principal(),
            ResetStationAdminPasswordCommand(
                officer_id="station-admin-1",
                new_password="TempPass@123",
                confirm_password="OtherPass@123",
            ),
        )


def test_reset_station_admin_password_rejects_non_station_admin_target() -> None:
    user = _station_admin()
    police_officer = UserDetailDto(
        **{**user.__dict__, "role": "POLICE_OFFICER", "officer_id": "officer-1"}
    )
    use_case = ResetStationAdminPasswordUseCase(
        repository=_FakeRepository(police_officer),
        password_hasher=_FakeHasher(),
        officer_activity_repository=_FakeOfficerActivity(),
        logger=_FakeLogger(),
    )

    with pytest.raises(ValueError, match="Only Police Station Admin"):
        use_case.execute(
            _super_admin_principal(),
            ResetStationAdminPasswordCommand(
                officer_id="officer-1",
                new_password="TempPass@123",
                confirm_password="TempPass@123",
            ),
        )


def test_reset_station_admin_password_requires_super_admin() -> None:
    from sentinel_anpr.application.dto.auth_dto import AuthPrincipal

    use_case = ResetStationAdminPasswordUseCase(
        repository=_FakeRepository(_station_admin()),
        password_hasher=_FakeHasher(),
        officer_activity_repository=_FakeOfficerActivity(),
        logger=_FakeLogger(),
    )
    station_admin_principal = AuthPrincipal(
        officer_id="station-admin-2",
        badge_number="STA002",
        station_id="station-1",
        roles=("station_admin",),
        role="station_admin",
        permissions=("officers",),
        session_id="session-2",
    )

    with pytest.raises(SuperAdminRequiredError):
        use_case.execute(
            station_admin_principal,
            ResetStationAdminPasswordCommand(
                officer_id="station-admin-1",
                new_password="TempPass@123",
                confirm_password="TempPass@123",
            ),
        )
