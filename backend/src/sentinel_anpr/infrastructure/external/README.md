# Infrastructure — External

Driven adapters for third-party systems.

---

## Subpackages

| Path | Purpose |
|------|---------|
| `registry/` | Vehicle registration authority client |

---

## Placeholders

| File | Implements |
|------|------------|
| `registry/vehicle_registry_client.placeholder` | `VehicleRegistryPort` |

---

## Anti-Corruption Layer

External API models are translated to domain/DTO types here — never leak into domain.
