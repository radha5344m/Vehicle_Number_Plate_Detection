# Infrastructure Layer

**Driven adapters** — implements outbound ports.

---

## Responsibilities

- Persistence (repositories, object storage)
- ML model loading and inference
- External API clients (vehicle registry)
- Messaging (publish/subscribe)
- Configuration loading
- Cross-cutting adapters (clock, logging)

---

## Structure

| Package | Purpose |
|---------|---------|
| `persistence/` | Database and file storage |
| `ml/` | Plate detector and recognizer implementations |
| `external/` | Third-party integrations |
| `messaging/` | Event bus adapters |
| `config/` | Config port implementation |
| `common/` | Clock and shared infra utilities |

---

## Dependency Rules

- May import `application` (ports, DTOs) and `domain`
- Must **not** import `adapters`
- Each adapter implements one or more outbound ports

---

## Related

- [Hexagonal Ports & Adapters](../../../docs/architecture/hexagonal-ports-adapters.md)
