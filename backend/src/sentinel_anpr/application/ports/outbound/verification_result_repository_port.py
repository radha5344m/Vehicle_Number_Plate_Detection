"""Vehicle verification result persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.persistence_dto import SaveVerificationResultCommand
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class VerificationResultRepositoryPort(Protocol):
    """Store registry verification outcomes."""

    def save_verification_result(
        self,
        command: SaveVerificationResultCommand,
        *,
        transaction: TransactionHandlePort | None = None,
        verification_id: str | None = None,
    ) -> str:
        """Persist verification outcome and return its identifier."""
        ...
