"""Role normalization and permission helpers for authorization."""

_ROLE_ALIASES: dict[str, str] = {
    "officer": "police_officer",
    "police_officer": "police_officer",
    "supervisor": "station_admin",
    "admin": "station_admin",
    "station_admin": "station_admin",
    "super_admin": "super_admin",
}

_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "super_admin": (
        "dashboard",
        "vehicle_verification",
        "investigation_history",
        "reports",
        "analytics",
        "users",
        "stations",
        "settings",
        "profile",
        "notifications",
        "officers",
        "station_reports",
        "system_analytics",
        "challans",
    ),
    "station_admin": (
        "dashboard",
        "vehicle_verification",
        "investigation_history",
        "reports",
        "analytics",
        "profile",
        "notifications",
        "officers",
        "station_reports",
        "station_details",
        "challans",
    ),
    "police_officer": (
        "dashboard",
        "vehicle_verification",
        "investigation_history",
        "reports",
        "profile",
        "challans",
    ),
}


def normalize_role(role: str) -> str:
    """Map legacy role names to supported RBAC roles."""
    return _ROLE_ALIASES.get(role.strip().lower(), role.strip().lower())


def normalize_roles(roles: tuple[str, ...]) -> tuple[str, ...]:
    """Return supported RBAC role names in stable order."""
    normalized = {normalize_role(role) for role in roles if role.strip()}
    priority = ("super_admin", "station_admin", "police_officer")
    return tuple(role for role in priority if role in normalized)


def permissions_for_roles(roles: tuple[str, ...]) -> tuple[str, ...]:
    """Return the union of permissions granted to the supplied roles."""
    permissions: set[str] = set()
    for role in normalize_roles(roles):
        permissions.update(_ROLE_PERMISSIONS.get(role, ()))
    return tuple(sorted(permissions))


def primary_role_for_roles(roles: tuple[str, ...]) -> str:
    """Return the highest-priority normalized role."""
    normalized = normalize_roles(roles)
    if not normalized:
        return "POLICE_OFFICER"
    return normalized[0].upper()


def has_permission(roles: tuple[str, ...], permission: str) -> bool:
    """Check whether the supplied roles grant a permission."""
    return permission in permissions_for_roles(roles)


def roles_csv_includes(roles_csv: str, role: str) -> bool:
    """Return True when the stored roles_csv includes the normalized role."""
    raw = tuple(part.strip() for part in roles_csv.split(",") if part.strip())
    return role in normalize_roles(raw)
