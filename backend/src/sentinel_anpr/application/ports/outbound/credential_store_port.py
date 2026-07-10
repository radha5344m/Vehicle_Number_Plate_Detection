"""Officer credential lookup port."""

from dataclasses import dataclass
from typing import Protocol

from sentinel_anpr.application.dto.auth_dto import OfficerIdentity


@dataclass(frozen=True)
class StoredCredential:
    """Officer identity with password hash for authentication."""

    officer: OfficerIdentity
    password_hash: str


class CredentialStorePort(Protocol):
    """Read-only credential store for authentication."""

    def find_by_identifier(self, identifier: str) -> StoredCredential | None: ...

    def find_by_id(self, officer_id: str) -> StoredCredential | None: ...

    def record_successful_login(self, officer_id: str) -> None: ...
