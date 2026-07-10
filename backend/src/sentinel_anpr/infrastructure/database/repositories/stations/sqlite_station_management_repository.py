"""SQLite police station repository."""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.station_management_dto import (
    CreateStationCommand,
    QueryStationsResult,
    StationFilters,
    StationItemDto,
    StationMutationResult,
    StationStatusCommand,
    StationsPaginationDto,
    UpdateStationCommand,
)
from sentinel_anpr.application.ports.outbound.station_management_repository_port import (
    StationManagementRepositoryPort,
)
from sentinel_anpr.infrastructure.database.models.stations.station_model import PoliceStationModel


class SqliteStationManagementRepository(StationManagementRepositoryPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def query_stations(self, filters: StationFilters) -> QueryStationsResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)
        with self._session_factory() as session:
            statement = self._apply_filters(self._base_statement(), filters)
            count_statement = self._apply_filters(
                select(func.count()).select_from(PoliceStationModel).where(
                    PoliceStationModel.deleted_at.is_(None)
                ),
                filters,
            )
            total_items = session.scalar(count_statement) or 0
            total_pages = math.ceil(total_items / page_size) if total_items else 0
            rows = session.scalars(
                self._apply_sort(statement, filters)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        return QueryStationsResult(
            items=tuple(self._to_item(row) for row in rows),
            pagination=StationsPaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def get_station(self, station_id: str) -> StationItemDto | None:
        with self._session_factory() as session:
            model = session.get(PoliceStationModel, station_id)
            if model is None or model.deleted_at is not None:
                return None
            return self._to_item(model)

    def get_active_station_by_name(self, station_name: str) -> StationItemDto | None:
        with self._session_factory() as session:
            model = session.scalar(
                select(PoliceStationModel).where(
                    PoliceStationModel.station_name == station_name,
                    PoliceStationModel.status == "active",
                    PoliceStationModel.deleted_at.is_(None),
                )
            )
            return self._to_item(model) if model is not None else None

    def create_station(self, command: CreateStationCommand) -> StationMutationResult:
        now = datetime.now(UTC)
        model = PoliceStationModel(
            station_id=str(uuid.uuid4()),
            station_name=command.station_name,
            station_code=command.station_code,
            district=command.district,
            state=command.state,
            address=command.address,
            pincode=command.pincode,
            phone_number=command.phone_number,
            email=command.email,
            station_type=command.station_type,
            status=command.status,
            created_at=now,
            updated_at=now,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return StationMutationResult(station=self._to_item(model))

    def update_station(self, command: UpdateStationCommand) -> StationMutationResult:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.station_id)
            model.station_name = command.station_name
            model.district = command.district
            model.state = command.state
            model.address = command.address
            model.pincode = command.pincode
            model.phone_number = command.phone_number
            model.email = command.email
            model.station_type = command.station_type
            model.status = command.status
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return StationMutationResult(station=self._to_item(model))

    def change_status(self, command: StationStatusCommand) -> StationMutationResult:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.station_id)
            model.status = command.status
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return StationMutationResult(station=self._to_item(model))

    def soft_delete_station(self, station_id: str) -> None:
        with self._session_factory() as session:
            model = self._load_or_raise(session, station_id)
            model.deleted_at = datetime.now(UTC)
            model.status = "inactive"
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()

    def station_code_exists(self, station_code: str, exclude_station_id: str | None = None) -> bool:
        return self._exists(PoliceStationModel.station_code, station_code, exclude_station_id)

    def station_name_exists(self, station_name: str, exclude_station_id: str | None = None) -> bool:
        return self._exists(PoliceStationModel.station_name, station_name, exclude_station_id)

    @staticmethod
    def _base_statement() -> Select:
        return select(PoliceStationModel).where(PoliceStationModel.deleted_at.is_(None))

    @staticmethod
    def _apply_filters(statement: Select, filters: StationFilters) -> Select:
        if filters.search:
            q = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(
                    PoliceStationModel.station_name.ilike(q),
                    PoliceStationModel.station_code.ilike(q),
                    PoliceStationModel.district.ilike(q),
                )
            )
        if filters.district:
            statement = statement.where(PoliceStationModel.district.ilike(f"%{filters.district.strip()}%"))
        if filters.state:
            statement = statement.where(PoliceStationModel.state.ilike(f"%{filters.state.strip()}%"))
        if filters.status:
            statement = statement.where(PoliceStationModel.status == filters.status.lower())
        if filters.station_type:
            statement = statement.where(PoliceStationModel.station_type == filters.station_type.lower())
        return statement

    @staticmethod
    def _apply_sort(statement: Select, filters: StationFilters) -> Select:
        sort_column = {
            "created_at": PoliceStationModel.created_at,
            "station_code": PoliceStationModel.station_code,
            "station_name": PoliceStationModel.station_name,
            "district": PoliceStationModel.district,
            "state": PoliceStationModel.state,
            "station_type": PoliceStationModel.station_type,
            "status": PoliceStationModel.status,
        }.get(filters.sort_by, PoliceStationModel.created_at)
        order = sort_column.desc() if filters.sort_desc else sort_column.asc()
        return statement.order_by(order, PoliceStationModel.created_at.desc())

    def _exists(self, column, value: str, exclude_station_id: str | None) -> bool:  # noqa: ANN001
        with self._session_factory() as session:
            statement = select(func.count()).select_from(PoliceStationModel).where(
                column == value,
                PoliceStationModel.deleted_at.is_(None),
            )
            if exclude_station_id:
                statement = statement.where(PoliceStationModel.station_id != exclude_station_id)
            return bool(session.scalar(statement) or 0)

    @staticmethod
    def _load_or_raise(session: Session, station_id: str) -> PoliceStationModel:
        model = session.get(PoliceStationModel, station_id)
        if model is None or model.deleted_at is not None:
            raise LookupError("Station not found")
        return model

    @staticmethod
    def _to_item(model: PoliceStationModel) -> StationItemDto:
        return StationItemDto(
            station_id=model.station_id,
            station_name=model.station_name,
            station_code=model.station_code,
            district=model.district,
            state=model.state,
            address=model.address,
            pincode=model.pincode,
            phone_number=model.phone_number,
            email=model.email,
            station_type=model.station_type,
            status=model.status,
            created_at=model.created_at.astimezone(UTC),
            updated_at=model.updated_at.astimezone(UTC),
        )
