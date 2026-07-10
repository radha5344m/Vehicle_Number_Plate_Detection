"""SQLite adapter for the private evidence blockchain."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sentinel_anpr.application.dto.blockchain_dto import EvidenceBlockDto
from sentinel_anpr.application.ports.outbound.blockchain_repository_port import BlockchainRepositoryPort
from sentinel_anpr.domain.blockchain.services.evidence_block_hash_policy import (
    GENESIS_PREVIOUS_HASH,
    compute_block_hash,
)
from sentinel_anpr.infrastructure.database.models.blockchain.evidence_block_model import EvidenceBlockModel


class SqliteBlockchainRepository(BlockchainRepositoryPort):
    """Persist evidence blocks in SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def append_block(
        self,
        *,
        investigation_id: str,
        report_id: str | None,
        registration_number: str,
        officer_id: str,
        report_sha256_hash: str,
    ) -> EvidenceBlockDto:
        with self._session_factory() as session:
            latest = self._get_latest_block(session)
            if latest is None:
                genesis = self._create_genesis_block(session)
                session.commit()
                latest = genesis

            now = datetime.now(UTC)
            block_number = latest.block_number + 1
            current_hash = compute_block_hash(
                block_number=block_number,
                block_timestamp=now,
                investigation_id=investigation_id,
                registration_number=registration_number,
                officer_id=officer_id,
                previous_hash=latest.current_hash,
                report_sha256_hash=report_sha256_hash,
            )
            model = EvidenceBlockModel(
                block_id=str(uuid.uuid4()),
                block_number=block_number,
                block_timestamp=now,
                investigation_id=investigation_id,
                report_id=report_id,
                registration_number=registration_number,
                officer_id=officer_id,
                previous_hash=latest.current_hash,
                current_hash=current_hash,
                report_sha256_hash=report_sha256_hash,
                created_at=now,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_dto(model)

    def ensure_genesis_block(self) -> EvidenceBlockDto:
        with self._session_factory() as session:
            latest = self._get_latest_block(session)
            if latest is not None:
                return self._to_dto(latest)

            model = self._create_genesis_block(session)
            session.commit()
            session.refresh(model)
            return self._to_dto(model)

    @staticmethod
    def _create_genesis_block(session: Session) -> EvidenceBlockModel:
        now = datetime.now(UTC)
        genesis_hash = compute_block_hash(
            block_number=0,
            block_timestamp=now,
            investigation_id="GENESIS",
            registration_number="GENESIS",
            officer_id="SYSTEM",
            previous_hash=GENESIS_PREVIOUS_HASH,
            report_sha256_hash=GENESIS_PREVIOUS_HASH,
        )
        model = EvidenceBlockModel(
            block_id=str(uuid.uuid4()),
            block_number=0,
            block_timestamp=now,
            investigation_id="GENESIS",
            report_id=None,
            registration_number="GENESIS",
            officer_id="SYSTEM",
            previous_hash=GENESIS_PREVIOUS_HASH,
            current_hash=genesis_hash,
            report_sha256_hash=GENESIS_PREVIOUS_HASH,
            created_at=now,
        )
        session.add(model)
        return model

    def get_latest_block(self) -> EvidenceBlockDto | None:
        with self._session_factory() as session:
            latest = self._get_latest_block(session)
            return self._to_dto(latest) if latest is not None else None

    def get_block_by_investigation_id(self, investigation_id: str) -> EvidenceBlockDto | None:
        with self._session_factory() as session:
            row = session.execute(
                select(EvidenceBlockModel)
                .where(EvidenceBlockModel.investigation_id == investigation_id)
                .order_by(EvidenceBlockModel.block_number.desc())
            ).scalar_one_or_none()
            return self._to_dto(row) if row is not None else None

    @staticmethod
    def _get_latest_block(session: Session) -> EvidenceBlockModel | None:
        return session.execute(
            select(EvidenceBlockModel).order_by(EvidenceBlockModel.block_number.desc()).limit(1)
        ).scalar_one_or_none()

    @staticmethod
    def _to_dto(model: EvidenceBlockModel) -> EvidenceBlockDto:
        return EvidenceBlockDto(
            block_id=model.block_id,
            block_number=model.block_number,
            block_timestamp=model.block_timestamp,
            investigation_id=model.investigation_id,
            report_id=model.report_id,
            registration_number=model.registration_number,
            officer_id=model.officer_id,
            previous_hash=model.previous_hash,
            current_hash=model.current_hash,
            report_sha256_hash=model.report_sha256_hash,
        )
