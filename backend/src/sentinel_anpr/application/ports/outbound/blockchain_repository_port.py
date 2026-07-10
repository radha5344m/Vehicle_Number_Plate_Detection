"""Port for private evidence blockchain persistence."""

from __future__ import annotations

from typing import Protocol

from sentinel_anpr.application.dto.blockchain_dto import EvidenceBlockDto


class BlockchainRepositoryPort(Protocol):
    """Persist and query evidence blocks."""

    def ensure_genesis_block(self) -> EvidenceBlockDto:
        """Create the genesis block when the chain is empty."""

    def get_latest_block(self) -> EvidenceBlockDto | None:
        """Return the most recently appended block."""

    def append_block(
        self,
        *,
        investigation_id: str,
        report_id: str | None,
        registration_number: str,
        officer_id: str,
        report_sha256_hash: str,
    ) -> EvidenceBlockDto:
        """Append a new evidence block linked to the previous hash."""

    def get_block_by_investigation_id(self, investigation_id: str) -> EvidenceBlockDto | None:
        """Return the evidence block for an investigation."""
