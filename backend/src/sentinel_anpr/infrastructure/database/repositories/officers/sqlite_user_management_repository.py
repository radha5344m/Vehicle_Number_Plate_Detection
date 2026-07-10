"""SQLite user management repository."""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.user_management_dto import (
    CreateUserCommand,
    QueryUsersResult,
    ResetUserPasswordCommand,
    UpdateUserCommand,
    UserDetailDto,
    UserFilters,
    UserListItemDto,
    UserMutationResult,
    UserStatusChangeCommand,
    UsersSummaryDto,
    UsersPaginationDto,
)
from sentinel_anpr.application.ports.outbound.user_management_repository_port import (
    UserManagementRepositoryPort,
)
from sentinel_anpr.application.services.auth_permissions import normalize_role
from sentinel_anpr.infrastructure.database.models.officers.officer_auth_model import OfficerAuthModel
from sentinel_anpr.infrastructure.database.models.stations.station_model import PoliceStationModel

_CANONICAL_ROLE_LABELS = {
    "super_admin": "SUPER_ADMIN",
    "station_admin": "STATION_ADMIN",
    "police_officer": "POLICE_OFFICER",
}

_ROLE_FILTER_VALUES = {
    "super_admin": ("super_admin",),
    "station_admin": ("station_admin", "admin", "supervisor"),
    "police_officer": ("police_officer", "officer"),
}


class SqliteUserManagementRepository(UserManagementRepositoryPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def query_users(self, filters: UserFilters) -> QueryUsersResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)
        with self._session_factory() as session:
            statement = self._base_statement()
            count_statement = select(func.count()).select_from(OfficerAuthModel).where(
                OfficerAuthModel.deleted_at.is_(None)
            )
            statement = self._apply_filters(statement, filters)
            count_statement = self._apply_count_filters(count_statement, filters)
            total_items = session.scalar(count_statement) or 0
            total_pages = math.ceil(total_items / page_size) if total_items else 0
            offset = (page - 1) * page_size
            rows = session.scalars(
                self._apply_sort(statement, filters).offset(offset).limit(page_size)
            ).all()
            summary_rows = session.execute(
                select(OfficerAuthModel.roles_csv, func.count())
                .where(OfficerAuthModel.deleted_at.is_(None))
                .group_by(OfficerAuthModel.roles_csv)
            ).all()
        role_counts = {"super_admin": 0, "station_admin": 0, "police_officer": 0}
        for role, count in summary_rows:
            normalized = normalize_role(str(role))
            if normalized in role_counts:
                role_counts[normalized] += int(count)
        return QueryUsersResult(
            items=tuple(self._to_list_item(row) for row in rows),
            pagination=UsersPaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
            summary=UsersSummaryDto(
                total_users=sum(role_counts.values()),
                super_admins=role_counts["super_admin"],
                station_admins=role_counts["station_admin"],
                police_officers=role_counts["police_officer"],
            ),
        )

    def get_user(self, officer_id: str) -> UserDetailDto | None:
        with self._session_factory() as session:
            model = session.get(OfficerAuthModel, officer_id)
            if model is None or model.deleted_at is not None:
                return None
            return self._to_detail(model)

    def create_user(
        self,
        command: CreateUserCommand,
        password_hash: str,
        *,
        temporary_password: str | None = None,
        password_change_required: bool = False,
    ) -> UserMutationResult:
        if not command.user_id or not command.employee_id or not command.username:
            raise ValueError("Generated identity fields are required")
        now = datetime.now(UTC)
        officer_id = str(uuid.uuid4())
        with self._session_factory() as session:
            station = self._resolve_active_station(session, command.police_station)
            model = OfficerAuthModel(
                officer_id=officer_id,
                user_id=command.user_id,
                employee_id=command.employee_id,
                badge_number=command.badge_number,
                username=command.username,
                email=command.email,
                phone_number=command.phone_number,
                first_name=command.first_name,
                last_name=command.last_name,
                rank=command.rank,
                station_id=station.station_id,
                station_code=station.station_code,
                station_name=station.station_name,
                district=station.district,
                roles_csv=command.role.lower(),
                status=command.status,
                password_hash=password_hash,
                password_change_required=password_change_required,
                created_at=now,
                updated_at=now,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return UserMutationResult(
                user=self._to_detail(model),
                temporary_password=temporary_password,
                password_change_required=password_change_required,
            )

    def update_user(self, command: UpdateUserCommand) -> UserMutationResult:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.officer_id)
            station = self._resolve_active_station(session, command.police_station)
            model.employee_id = command.employee_id
            model.first_name = command.first_name
            model.last_name = command.last_name
            model.email = command.email
            model.phone_number = command.phone_number
            model.rank = command.rank
            model.station_name = station.station_name
            model.station_code = station.station_code
            model.station_id = station.station_id
            model.district = station.district
            model.status = command.status
            if command.role:
                model.roles_csv = command.role.lower()
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return UserMutationResult(user=self._to_detail(model))

    def change_user_status(self, command: UserStatusChangeCommand) -> UserMutationResult:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.officer_id)
            model.status = command.status
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return UserMutationResult(user=self._to_detail(model))

    def reset_password(
        self,
        command: ResetUserPasswordCommand,
        password_hash: str,
        *,
        password_change_required: bool = False,
    ) -> None:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.officer_id)
            model.password_hash = password_hash
            model.password_change_required = password_change_required
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()

    def soft_delete_user(self, officer_id: str) -> None:
        with self._session_factory() as session:
            model = self._load_or_raise(session, officer_id)
            model.deleted_at = datetime.now(UTC)
            model.status = "inactive"
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()

    def username_exists(self, username: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.username, username, exclude_officer_id)

    def email_exists(self, email: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.email, email, exclude_officer_id)

    def employee_id_exists(self, employee_id: str, exclude_officer_id: str | None = None) -> bool:
        return self._exists(OfficerAuthModel.employee_id, employee_id, exclude_officer_id)

    @staticmethod
    def _base_statement() -> Select:
        return select(OfficerAuthModel).where(OfficerAuthModel.deleted_at.is_(None))

    @staticmethod
    def _apply_filters(statement: Select, filters: UserFilters) -> Select:
        if filters.search:
            q = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(
                    OfficerAuthModel.first_name.ilike(q),
                    OfficerAuthModel.last_name.ilike(q),
                    OfficerAuthModel.username.ilike(q),
                    OfficerAuthModel.user_id.ilike(q),
                    OfficerAuthModel.employee_id.ilike(q),
                    OfficerAuthModel.badge_number.ilike(q),
                )
            )
        if filters.role:
            filter_key = normalize_role(filters.role)
            role_values = _ROLE_FILTER_VALUES.get(filter_key, (filter_key,))
            statement = statement.where(OfficerAuthModel.roles_csv.in_(role_values))
        if filters.station:
            statement = statement.where(OfficerAuthModel.station_name.ilike(f"%{filters.station.strip()}%"))
        if filters.status:
            statement = statement.where(OfficerAuthModel.status == filters.status.lower())
        if filters.created_from:
            statement = statement.where(OfficerAuthModel.created_at >= filters.created_from)
        if filters.created_to:
            statement = statement.where(OfficerAuthModel.created_at <= filters.created_to)
        return statement

    @staticmethod
    def _apply_count_filters(statement: Select, filters: UserFilters) -> Select:
        return SqliteUserManagementRepository._apply_filters(statement, filters)

    @staticmethod
    def _apply_sort(statement: Select, filters: UserFilters) -> Select:
        sort_column = {
            "created_at": OfficerAuthModel.created_at,
            "last_login_at": OfficerAuthModel.last_login_at,
            "employee_id": OfficerAuthModel.employee_id,
            "full_name": OfficerAuthModel.first_name,
            "role": OfficerAuthModel.roles_csv,
            "status": OfficerAuthModel.status,
            "station_name": OfficerAuthModel.station_name,
        }.get(filters.sort_by, OfficerAuthModel.created_at)
        order = sort_column.desc() if filters.sort_desc else sort_column.asc()
        return statement.order_by(order, OfficerAuthModel.created_at.desc())

    def _exists(self, column, value: str, exclude_officer_id: str | None) -> bool:  # noqa: ANN001
        with self._session_factory() as session:
            statement = select(func.count()).select_from(OfficerAuthModel).where(
                column == value,
                OfficerAuthModel.deleted_at.is_(None),
            )
            if exclude_officer_id:
                statement = statement.where(OfficerAuthModel.officer_id != exclude_officer_id)
            return bool(session.scalar(statement) or 0)

    @staticmethod
    def _load_or_raise(session: Session, officer_id: str) -> OfficerAuthModel:
        model = session.get(OfficerAuthModel, officer_id)
        if model is None or model.deleted_at is not None:
            raise LookupError("User not found")
        return model

    @staticmethod
    def _resolve_active_station(session: Session, station_name: str | None) -> PoliceStationModel:
        if not station_name:
            raise ValueError("Users can only be assigned to active stations")
        station = session.scalar(
            select(PoliceStationModel).where(
                PoliceStationModel.station_name == station_name,
                PoliceStationModel.status == "active",
                PoliceStationModel.deleted_at.is_(None),
            )
        )
        if station is None:
            raise ValueError("Users can only be assigned to active stations")
        return station

    @classmethod
    def _role(cls, model: OfficerAuthModel) -> str:
        normalized = normalize_role(model.roles_csv)
        return _CANONICAL_ROLE_LABELS.get(normalized, model.roles_csv.upper())

    @staticmethod
    def _full_name(model: OfficerAuthModel) -> str:
        return f"{model.first_name} {model.last_name}".strip()

    @classmethod
    def _to_list_item(cls, model: OfficerAuthModel) -> UserListItemDto:
        return UserListItemDto(
            officer_id=model.officer_id,
            user_id=model.user_id,
            employee_id=model.employee_id,
            full_name=cls._full_name(model),
            username=model.username,
            email=model.email,
            phone_number=model.phone_number,
            badge_number=model.badge_number,
            rank=model.rank,
            role=cls._role(model),
            police_station=model.station_name,
            district=model.district,
            status=model.status,
            created_at=model.created_at.astimezone(UTC),
            last_login_at=(model.last_login_at.astimezone(UTC) if model.last_login_at else None),
        )

    @classmethod
    def _to_detail(cls, model: OfficerAuthModel) -> UserDetailDto:
        return UserDetailDto(
            officer_id=model.officer_id,
            user_id=model.user_id,
            employee_id=model.employee_id,
            first_name=model.first_name,
            last_name=model.last_name,
            full_name=cls._full_name(model),
            username=model.username,
            email=model.email,
            phone_number=model.phone_number,
            badge_number=model.badge_number,
            rank=model.rank,
            role=cls._role(model),
            police_station=model.station_name,
            station_code=model.station_code,
            station_id=model.station_id,
            district=model.district,
            status=model.status,
            created_at=model.created_at.astimezone(UTC),
            last_login_at=(model.last_login_at.astimezone(UTC) if model.last_login_at else None),
        )
