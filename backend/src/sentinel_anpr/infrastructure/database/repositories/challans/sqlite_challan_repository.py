"""SQLite challan repository."""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.challan_dto import (
    ChallanAccessScope,
    ChallanAnalyticsResult,
    ChallanDetailDto,
    ChallanFilters,
    ChallanListItemDto,
    ChallanPaginationDto,
    ChallanSummaryDto,
    CreateChallanCommand,
    DistributionItemDto,
    MonthlyFineCollectionDto,
    QueryChallansResult,
    UpdateChallanCommand,
    ViolationMasterDto,
)
from sentinel_anpr.application.ports.outbound.challan_repository_port import ChallanRepositoryPort
from sentinel_anpr.domain.challans.challan_status import ChallanPaymentStatus
from sentinel_anpr.domain.common.value_objects.plate_text_normalizer import (
    normalize_registration_number,
)
from sentinel_anpr.infrastructure.database.models.challans.challan_model import ChallanModel
from sentinel_anpr.infrastructure.database.models.challans.violation_master_model import (
    ViolationMasterModel,
)
from sentinel_anpr.infrastructure.database.models.officers.identity_sequence_model import (
    IdentitySequenceModel,
)

_CHALLAN_SEQUENCE_KEY = "challan_number:2026"


class SqliteChallanRepository(ChallanRepositoryPort):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_violations(self) -> tuple[ViolationMasterDto, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(ViolationMasterModel)
                .where(ViolationMasterModel.active.is_(True))
                .order_by(ViolationMasterModel.violation_name.asc())
            ).all()
        return tuple(self._to_violation(row) for row in rows)

    def next_challan_number(self) -> str:
        with self._session_factory() as session:
            sequence = self._next_sequence_value(session, _CHALLAN_SEQUENCE_KEY)
            session.commit()
            return f"CH-2026-{sequence:06d}"

    def create_challan(self, command: CreateChallanCommand, challan_number: str) -> ChallanDetailDto:
        now = datetime.now(UTC)
        registration = normalize_registration_number(command.registration_number)
        model = ChallanModel(
            id=str(uuid.uuid4()),
            challan_number=challan_number,
            investigation_id=command.investigation_id,
            registration_number=registration,
            vehicle_id=command.vehicle_id,
            owner_name=command.owner_name,
            officer_id=command.officer_id,
            officer_name=command.officer_name,
            station_id=command.station_id,
            station_name=command.station_name,
            violation_type=command.violation_type,
            violation_description=command.violation_description,
            fine_amount=command.fine_amount,
            remarks=command.remarks,
            status=ChallanPaymentStatus.PENDING.value,
            payment_status=ChallanPaymentStatus.PENDING.value,
            location_label=command.location_label,
            gps_coordinates=command.gps_coordinates,
            evidence_image_path=command.evidence_image_path,
            issued_at=now,
            paid_at=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_detail(model)

    def get_challan(self, challan_id: str) -> ChallanDetailDto | None:
        with self._session_factory() as session:
            model = session.get(ChallanModel, challan_id)
            if model is None or model.deleted_at is not None:
                return None
            return self._to_detail(model)

    def query_challans(self, filters: ChallanFilters, scope: ChallanAccessScope) -> QueryChallansResult:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)
        with self._session_factory() as session:
            statement = self._scoped_statement(scope)
            count_statement = select(func.count()).select_from(ChallanModel).where(
                ChallanModel.deleted_at.is_(None)
            )
            statement = self._apply_filters(statement, filters)
            count_statement = self._apply_scope(count_statement, scope)
            count_statement = self._apply_filters(count_statement, filters)
            total_items = session.scalar(count_statement) or 0
            total_pages = math.ceil(total_items / page_size) if total_items else 0
            rows = session.scalars(
                statement.order_by(ChallanModel.issued_at.desc()).offset((page - 1) * page_size).limit(page_size)
            ).all()
        return QueryChallansResult(
            items=tuple(self._to_list_item(row) for row in rows),
            pagination=ChallanPaginationDto(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def update_challan(self, command: UpdateChallanCommand) -> ChallanDetailDto:
        with self._session_factory() as session:
            model = self._load_or_raise(session, command.challan_id)
            if command.violation_type:
                model.violation_type = command.violation_type
            if command.violation_description is not None:
                model.violation_description = command.violation_description
            if command.fine_amount is not None:
                model.fine_amount = command.fine_amount
            if command.remarks is not None:
                model.remarks = command.remarks
            if command.location_label is not None:
                model.location_label = command.location_label
            if command.gps_coordinates is not None:
                model.gps_coordinates = command.gps_coordinates
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_detail(model)

    def set_payment_status(self, challan_id: str, payment_status: str) -> ChallanDetailDto:
        with self._session_factory() as session:
            model = self._load_or_raise(session, challan_id)
            model.payment_status = payment_status
            model.status = payment_status
            model.paid_at = datetime.now(UTC) if payment_status == ChallanPaymentStatus.PAID.value else None
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_detail(model)

    def soft_delete_challan(self, challan_id: str) -> None:
        with self._session_factory() as session:
            model = self._load_or_raise(session, challan_id)
            model.deleted_at = datetime.now(UTC)
            model.updated_at = datetime.now(UTC)
            session.add(model)
            session.commit()

    def summarize_by_registration(self, registration_number: str) -> ChallanSummaryDto:
        registration = normalize_registration_number(registration_number)
        with self._session_factory() as session:
            rows = session.scalars(
                select(ChallanModel)
                .where(
                    ChallanModel.registration_number == registration,
                    ChallanModel.deleted_at.is_(None),
                    ChallanModel.payment_status == ChallanPaymentStatus.PENDING.value,
                )
                .order_by(ChallanModel.issued_at.desc())
            ).all()
        outstanding = sum(float(row.fine_amount) for row in rows)
        latest = rows[0].violation_type if rows else None
        return ChallanSummaryDto(
            outstanding_fine_inr=outstanding,
            pending_challans_count=len(rows),
            latest_violation=latest,
        )

    def list_by_registration(
        self,
        registration_number: str,
        *,
        pending_only: bool = False,
    ) -> tuple[ChallanDetailDto, ...]:
        registration = normalize_registration_number(registration_number)
        with self._session_factory() as session:
            statement = select(ChallanModel).where(
                ChallanModel.registration_number == registration,
                ChallanModel.deleted_at.is_(None),
            )
            if pending_only:
                statement = statement.where(
                    ChallanModel.payment_status == ChallanPaymentStatus.PENDING.value
                )
            rows = session.scalars(statement.order_by(ChallanModel.issued_at.desc())).all()
        return tuple(self._to_detail(row) for row in rows)

    def get_analytics(self, scope: ChallanAccessScope) -> ChallanAnalyticsResult:
        with self._session_factory() as session:
            base = self._scoped_statement(scope)
            rows = session.scalars(base).all()
        today = datetime.now(UTC).date()
        pending = [row for row in rows if row.payment_status == ChallanPaymentStatus.PENDING.value]
        paid = [row for row in rows if row.payment_status == ChallanPaymentStatus.PAID.value]
        todays = [row for row in rows if row.issued_at.astimezone(UTC).date() == today]
        violation_counts: dict[str, int] = {}
        officer_counts: dict[str, int] = {}
        station_counts: dict[str, int] = {}
        monthly: dict[str, dict[str, float | int]] = {}
        for row in rows:
            violation_counts[row.violation_type] = violation_counts.get(row.violation_type, 0) + 1
            officer_counts[row.officer_name] = officer_counts.get(row.officer_name, 0) + 1
            station_counts[row.station_name] = station_counts.get(row.station_name, 0) + 1
            month_key = row.issued_at.astimezone(UTC).strftime("%Y-%m")
            bucket = monthly.setdefault(month_key, {"collected": 0.0, "issued": 0})
            bucket["issued"] = int(bucket["issued"]) + 1
            if row.payment_status == ChallanPaymentStatus.PAID.value:
                bucket["collected"] = float(bucket["collected"]) + float(row.fine_amount)
        most_common = max(violation_counts, key=violation_counts.get) if violation_counts else None
        top_officer = max(officer_counts, key=officer_counts.get) if officer_counts else None
        top_station = max(station_counts, key=station_counts.get) if station_counts else None
        return ChallanAnalyticsResult(
            total_challans=len(rows),
            todays_challans=len(todays),
            pending_challans=len(pending),
            paid_challans=len(paid),
            collected_fine_inr=sum(float(row.fine_amount) for row in paid),
            outstanding_fine_inr=sum(float(row.fine_amount) for row in pending),
            most_common_violation=most_common,
            top_issuing_officer=top_officer,
            top_station=top_station,
            violation_distribution=tuple(
                DistributionItemDto(label=label, value=count)
                for label, count in sorted(violation_counts.items(), key=lambda item: item[1], reverse=True)
            ),
            monthly_fine_collection=tuple(
                MonthlyFineCollectionDto(
                    month=month,
                    collected_fine_inr=float(values["collected"]),
                    issued_count=int(values["issued"]),
                )
                for month, values in sorted(monthly.items())
            ),
        )

    def get_violation(self, violation_code: str) -> ViolationMasterDto | None:
        with self._session_factory() as session:
            model = session.get(ViolationMasterModel, violation_code)
            if model is None or not model.active:
                return None
            return self._to_violation(model)

    @staticmethod
    def _next_sequence_value(session: Session, sequence_key: str) -> int:
        model = session.get(IdentitySequenceModel, sequence_key, with_for_update=True)
        if model is None:
            model = IdentitySequenceModel(sequence_key=sequence_key, last_value=0)
            session.add(model)
            session.flush()
        model.last_value += 1
        session.add(model)
        return model.last_value

    @staticmethod
    def _scoped_statement(scope: ChallanAccessScope) -> Select:
        statement = select(ChallanModel).where(ChallanModel.deleted_at.is_(None))
        if scope.all_access:
            return statement
        if scope.station_id:
            return statement.where(ChallanModel.station_id == scope.station_id)
        if scope.officer_id:
            return statement.where(ChallanModel.officer_id == scope.officer_id)
        return statement.where(ChallanModel.id == "__denied__")

    @staticmethod
    def _apply_scope(statement: Select, scope: ChallanAccessScope) -> Select:
        statement = statement.select_from(ChallanModel).where(ChallanModel.deleted_at.is_(None))
        if scope.all_access:
            return statement
        if scope.station_id:
            return statement.where(ChallanModel.station_id == scope.station_id)
        if scope.officer_id:
            return statement.where(ChallanModel.officer_id == scope.officer_id)
        return statement.where(ChallanModel.id == "__denied__")

    @staticmethod
    def _apply_filters(statement: Select, filters: ChallanFilters) -> Select:
        if filters.pending_only:
            statement = statement.where(ChallanModel.payment_status == ChallanPaymentStatus.PENDING.value)
        if filters.payment_status:
            statement = statement.where(ChallanModel.payment_status == filters.payment_status.lower())
        if filters.registration_number:
            statement = statement.where(
                ChallanModel.registration_number == normalize_registration_number(filters.registration_number)
            )
        if filters.challan_number:
            statement = statement.where(ChallanModel.challan_number.ilike(f"%{filters.challan_number.strip()}%"))
        if filters.owner_name:
            statement = statement.where(ChallanModel.owner_name.ilike(f"%{filters.owner_name.strip()}%"))
        if filters.officer_id:
            statement = statement.where(ChallanModel.officer_id == filters.officer_id)
        if filters.station_id:
            statement = statement.where(ChallanModel.station_id == filters.station_id)
        if filters.violation_type:
            statement = statement.where(ChallanModel.violation_type == filters.violation_type)
        if filters.issued_from:
            statement = statement.where(ChallanModel.issued_at >= filters.issued_from)
        if filters.issued_to:
            statement = statement.where(ChallanModel.issued_at <= filters.issued_to)
        if filters.search:
            q = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(
                    ChallanModel.registration_number.ilike(q),
                    ChallanModel.challan_number.ilike(q),
                    ChallanModel.owner_name.ilike(q),
                    ChallanModel.officer_name.ilike(q),
                )
            )
        return statement

    @staticmethod
    def _load_or_raise(session: Session, challan_id: str) -> ChallanModel:
        model = session.get(ChallanModel, challan_id)
        if model is None or model.deleted_at is not None:
            raise LookupError("Challan not found")
        return model

    @staticmethod
    def _to_violation(model: ViolationMasterModel) -> ViolationMasterDto:
        return ViolationMasterDto(
            violation_code=model.violation_code,
            violation_name=model.violation_name,
            default_fine_amount=float(model.default_fine_amount),
            amount_editable=bool(model.amount_editable),
        )

    @classmethod
    def _to_list_item(cls, model: ChallanModel) -> ChallanListItemDto:
        return ChallanListItemDto(
            id=model.id,
            challan_number=model.challan_number,
            registration_number=model.registration_number,
            owner_name=model.owner_name,
            violation_type=model.violation_type,
            violation_description=model.violation_description,
            fine_amount=float(model.fine_amount),
            payment_status=model.payment_status,
            officer_id=model.officer_id,
            officer_name=model.officer_name,
            station_id=model.station_id,
            station_name=model.station_name,
            issued_at=model.issued_at.astimezone(UTC),
        )

    @classmethod
    def _to_detail(cls, model: ChallanModel) -> ChallanDetailDto:
        base = cls._to_list_item(model)
        return ChallanDetailDto(
            **base.__dict__,
            investigation_id=model.investigation_id,
            vehicle_id=model.vehicle_id,
            remarks=model.remarks,
            location_label=model.location_label,
            gps_coordinates=model.gps_coordinates,
            evidence_image_path=model.evidence_image_path,
            paid_at=(model.paid_at.astimezone(UTC) if model.paid_at else None),
            created_at=model.created_at.astimezone(UTC),
            updated_at=model.updated_at.astimezone(UTC),
        )
