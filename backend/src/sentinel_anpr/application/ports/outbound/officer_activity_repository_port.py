"""Officer activity persistence port."""

from typing import Protocol

from sentinel_anpr.application.dto.persistence_dto import SaveOfficerActivityCommand
from sentinel_anpr.application.ports.outbound.transaction_handle_port import TransactionHandlePort


class OfficerActivityRepositoryPort(Protocol):
    """Store officer workflow activity events."""

    def save_activities(
        self,
        commands: tuple[SaveOfficerActivityCommand, ...],
        *,
        transaction: TransactionHandlePort | None = None,
    ) -> tuple[str, ...]:
        """Persist activity events and return their identifiers."""
        ...
