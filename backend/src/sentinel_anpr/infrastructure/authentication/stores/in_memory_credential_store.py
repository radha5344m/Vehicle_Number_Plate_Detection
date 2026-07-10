"""In-memory officer credential store for development."""

from sentinel_anpr.application.dto.auth_dto import OfficerIdentity
from sentinel_anpr.application.ports.outbound.credential_store_port import (
    CredentialStorePort,
    StoredCredential,
)
from sentinel_anpr.application.ports.outbound.password_hasher_port import PasswordHasherPort
from sentinel_anpr.domain.authentication.officer_status import OfficerStatus


class InMemoryCredentialStore(CredentialStorePort):
    """Placeholder credential store isolated from other modules."""

    def __init__(self, password_hasher: PasswordHasherPort) -> None:
        demo_officer = OfficerIdentity(
            officer_id="11111111-1111-1111-1111-111111111111",
            user_id="AP-26-02",
            employee_id="OFF001",
            badge_number="OFF001",
            username="off001",
            email="ravi.kumar@sentinelanpr.ai",
            phone_number="9000000001",
            first_name="Ravi",
            last_name="Kumar",
            rank="Sub-Inspector",
            station_id="22222222-2222-2222-2222-222222222222",
            station_code="ONG01",
            station_name="Ongole Town",
            district="Prakasam",
            roles=("officer",),
            status=OfficerStatus.ACTIVE,
        )
        self._by_badge = {
            demo_officer.badge_number: StoredCredential(
                officer=demo_officer,
                password_hash=password_hasher.hash("OFF001@2026"),
            )
        }
        self._by_identifier = {
            demo_officer.badge_number.upper(): self._by_badge[demo_officer.badge_number],
            demo_officer.username.lower(): self._by_badge[demo_officer.badge_number],
            demo_officer.employee_id.upper(): self._by_badge[demo_officer.badge_number],
            demo_officer.user_id.upper(): self._by_badge[demo_officer.badge_number],
        }
        self._by_id = {demo_officer.officer_id: self._by_badge[demo_officer.badge_number]}

    def find_by_identifier(self, identifier: str) -> StoredCredential | None:
        normalized = identifier.strip()
        if not normalized:
            return None
        return self._by_identifier.get(normalized.upper()) or self._by_identifier.get(
            normalized.lower()
        )

    def find_by_id(self, officer_id: str) -> StoredCredential | None:
        return self._by_id.get(officer_id)

    def record_successful_login(self, officer_id: str) -> None:
        del officer_id
