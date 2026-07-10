"""Anchor completed investigations on the evidence blockchain."""

from __future__ import annotations

from sentinel_anpr.application.dto.blockchain_dto import AnchorEvidenceCommand, AnchorEvidenceResult
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.infrastructure.blockchain.blockchain_service import BlockchainService
from sentinel_anpr.infrastructure.blockchain.report_json_hasher import hash_investigation_report_json


class AnchorEvidenceBlockUseCase:
    """Hash investigation report JSON and append an evidence block."""

    def __init__(self, blockchain_service: BlockchainService, logger: LoggingPort) -> None:
        self._blockchain = blockchain_service
        self._logger = logger

    def execute(self, command: AnchorEvidenceCommand) -> AnchorEvidenceResult:
        report_sha256_hash = hash_investigation_report_json(command.report_command)
        block = self._blockchain.anchor_investigation(
            investigation_id=command.investigation_id,
            report_id=command.report_id,
            registration_number=command.registration_number,
            officer_id=command.officer_id,
            report_sha256_hash=report_sha256_hash,
        )
        self._logger.info(
            "evidence_block_anchored",
            investigation_id=command.investigation_id,
            report_id=command.report_id,
            block_number=block.block_number,
            current_hash=block.current_hash,
            detail="Investigation evidence anchored on private blockchain",
        )
        return AnchorEvidenceResult(block=block, integrity_verified=True)
