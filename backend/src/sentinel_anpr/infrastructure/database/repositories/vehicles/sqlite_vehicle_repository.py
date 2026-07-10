"""SQLite vehicle repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.vehicle_dto import VehicleRecordDto
from sentinel_anpr.application.ports.outbound.vehicle_repository_port import VehicleRepositoryPort
from sentinel_anpr.infrastructure.database.mappers.vehicle_mapper import to_vehicle_record_dto
from sentinel_anpr.infrastructure.database.models.vehicles.vehicle_model import VehicleModel


class SqliteVehicleRepository(VehicleRepositoryPort):
    """Query vehicles from the demo SQLite database."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_plate(
        self,
        plate_number: str,
        jurisdiction: str | None = None,
    ) -> VehicleRecordDto | None:
        with self._session_factory() as session:
            statement = select(VehicleModel).where(
                VehicleModel.plate_number == plate_number,
                VehicleModel.deleted_at.is_(None),
            )
            if jurisdiction:
                statement = statement.where(VehicleModel.jurisdiction == jurisdiction.upper())
            vehicle = session.scalar(statement)
            if vehicle is None:
                return None
            return to_vehicle_record_dto(vehicle)
