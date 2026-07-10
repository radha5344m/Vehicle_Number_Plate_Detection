# Application Layer

**Application business rules** — orchestrates domain objects via use cases.

---

## Responsibilities

- Define **use cases** (one intent per class)
- Define **ports** (inbound and outbound interfaces)
- Define **DTOs** for crossing boundaries
- **No** framework or I/O code

---

## Structure

| Path | Purpose |
|------|---------|
| `ports/inbound/` | Driving port interfaces |
| `ports/outbound/` | Driven port interfaces |
| `use_cases/` | Application services / use cases |
| `dto/` | Request/response structures |
| `services/` | Cross-cutting application services _if needed_ |

---

## Dependency Rules

- May import `domain`
- Must **not** import `infrastructure` or `adapters`
- Depends on outbound **port abstractions** only

---

## Related

- [Hexagonal Ports & Adapters](../../../docs/architecture/hexagonal-ports-adapters.md)
