"""Role-based challan access rules."""

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.challan_dto import ChallanAccessScope
from sentinel_anpr.application.services.auth_permissions import normalize_roles
from sentinel_anpr.domain.challans.errors import ChallanAccessDeniedError


def resolve_challan_access_scope(principal: AuthPrincipal, station_id: str) -> ChallanAccessScope:
    roles = normalize_roles(principal.roles)
    if "super_admin" in roles:
        return ChallanAccessScope(all_access=True)
    if "station_admin" in roles:
        return ChallanAccessScope(station_id=station_id)
    if "police_officer" in roles:
        return ChallanAccessScope(officer_id=principal.officer_id)
    raise ChallanAccessDeniedError("Challan access denied")


def can_delete_challans(principal: AuthPrincipal) -> bool:
    return "super_admin" in normalize_roles(principal.roles)


def can_edit_challan(
    principal: AuthPrincipal,
    *,
    officer_id: str,
    station_id: str,
    caller_station_id: str,
) -> bool:
    roles = normalize_roles(principal.roles)
    if "super_admin" in roles:
        return True
    if "station_admin" in roles:
        return station_id == caller_station_id
    if "police_officer" in roles:
        return officer_id == principal.officer_id
    return False
