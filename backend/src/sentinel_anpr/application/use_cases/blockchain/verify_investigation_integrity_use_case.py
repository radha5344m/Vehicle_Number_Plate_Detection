"""Verify investigation report integrity against the evidence blockchain."""

from __future__ import annotations

from sentinel_anpr.application.dto.blockchain_dto import (
    VerifyInvestigationIntegrityCommand,
    VerifyInvestigationIntegrityResult,
)
from sentinel_anpr.application.ports.outbound.blockchain_repository_port import BlockchainRepositoryPort
from sentinel_anpr.infrastructure.blockchain.blockchain_service import BlockchainService
from sentinel_anpr.infrastructure.blockchain.investigation_report_command_rebuilder import (
    InvestigationReportCommandRebuilder,
)
from sentinel_anpr.infrastructure.blockchain.report_json_hasher import hash_investigation_report_json


class VerifyInvestigationIntegrityUseCase:
    """Recompute report hash and compare it with the anchored evidence block."""

    def __init__(
        self,
        blockchain_repository: BlockchainRepositoryPort,
        blockchain_service: BlockchainService,
        report_command_rebuilder: InvestigationReportCommandRebuilder | None = None,
    ) -> None:
        self._repository = blockchain_repository
        self._blockchain = blockchain_service
        self._rebuilder = report_command_rebuilder

    def execute_by_scan_id(self, investigation_id: str) -> VerifyInvestigationIntegrityResult:
        if self._rebuilder is None:
            return VerifyInvestigationIntegrityResult(
                investigation_id=investigation_id,
                integrity_verified=False,
                report_sha256_hash="",
                stored_report_sha256_hash=None,
                block=None,
                message="Integrity rebuilder is not configured.",
            )
        command = self._rebuilder.rebuild(investigation_id)
        if command is None:
            return VerifyInvestigationIntegrityResult(
                investigation_id=investigation_id,
                integrity_verified=False,
                report_sha256_hash="",
                stored_report_sha256_hash=None,
                block=None,
                message="Investigation data could not be loaded for integrity verification.",
            )
        return self.execute(
            VerifyInvestigationIntegrityCommand(
                investigation_id=investigation_id,
                report_command=command,
            )
        )

    def execute(self, command: VerifyInvestigationIntegrityCommand) -> VerifyInvestigationIntegrityResult:
        block = self._repository.get_block_by_investigation_id(command.investigation_id)
        if block is None:
            return VerifyInvestigationIntegrityResult(
                investigation_id=command.investigation_id,
                integrity_verified=False,
                report_sha256_hash=hash_investigation_report_json(command.report_command),
                stored_report_sha256_hash=None,
                block=None,
                message="No blockchain evidence found for this investigation.",
            )

        if not self._blockchain.verify_block_hash(block):
            return VerifyInvestigationIntegrityResult(
                investigation_id=command.investigation_id,
                integrity_verified=False,
                report_sha256_hash=hash_investigation_report_json(command.report_command),
                stored_report_sha256_hash=block.report_sha256_hash,
                block=block,
                message="Blockchain block hash is invalid. Evidence chain may be corrupted.",
            )

        current_hash = hash_investigation_report_json(command.report_command)
        verified = current_hash == block.report_sha256_hash
        return VerifyInvestigationIntegrityResult(
            investigation_id=command.investigation_id,
            integrity_verified=verified,
            report_sha256_hash=current_hash,
            stored_report_sha256_hash=block.report_sha256_hash,
            block=block,
            message="Integrity verified." if verified else "Evidence tampered. Report hash mismatch.",
        )
