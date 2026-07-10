"""Private evidence blockchain orchestration."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sentinel_anpr.application.dto.blockchain_dto import EvidenceBlockDto
from sentinel_anpr.application.ports.outbound.blockchain_repository_port import BlockchainRepositoryPort
from sentinel_anpr.domain.blockchain.services.evidence_block_hash_policy import compute_block_hash


class BlockchainService:
    """Create linked evidence blocks with deterministic hashes."""

    def __init__(self, repository: BlockchainRepositoryPort) -> None:
        self._repository = repository

    def anchor_investigation(
        self,
        *,
        investigation_id: str,
        report_id: str,
        registration_number: str,
        officer_id: str,
        report_sha256_hash: str,
    ) -> EvidenceBlockDto:
        self._repository.ensure_genesis_block()
        return self._repository.append_block(
            investigation_id=investigation_id,
            report_id=report_id,
            registration_number=registration_number,
            officer_id=officer_id,
            report_sha256_hash=report_sha256_hash,
        )

    @staticmethod
    def verify_block_hash(block: EvidenceBlockDto) -> bool:
        expected = compute_block_hash(
            block_number=block.block_number,
            block_timestamp=block.block_timestamp,
            investigation_id=block.investigation_id,
            registration_number=block.registration_number,
            officer_id=block.officer_id,
            previous_hash=block.previous_hash,
            report_sha256_hash=block.report_sha256_hash,
        )
        return expected == block.current_hash
