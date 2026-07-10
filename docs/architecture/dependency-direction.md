# Dependency Direction

Strict rules for import and dependency flow in SentinelANPR AI.

---

## The Dependency Rule

> Source code dependencies must point **inward** toward higher-level policies (the domain).

---

## Allowed Dependencies Matrix

| From ↓ / To → | domain | application | infrastructure | adapters |
|---------------|--------|-------------|----------------|----------|
| **domain** | ✓ | ✗ | ✗ | ✗ |
| **application** | ✓ | ✓ | ✗ | ✗ |
| **infrastructure** | ✓ | ✓ | ✓ | ✗ |
| **adapters** | ✓* | ✓ | ✗** | ✓ |

\* Adapters should prefer depending only on application ports, not domain directly.  
\** Adapters must NOT depend on infrastructure; wiring happens at composition root.

---

## Layer-by-Layer Rules

### Domain

- **MUST NOT** import: `application`, `infrastructure`, `adapters`
- **MUST NOT** import: HTTP clients, ORM, ML frameworks, config loaders
- **MAY** import: standard library, pure utility libraries (if ADR-approved)

### Application

- **MAY** import: `domain`
- **MUST NOT** import: `infrastructure`, `adapters`
- **MUST** depend on outbound abstractions (ports), not implementations

### Infrastructure

- **MAY** import: `domain`, `application` (ports, DTOs)
- **MUST** implement outbound ports defined in `application/ports/outbound/`
- **MUST NOT** import: `adapters`

### Adapters (Inbound)

- **MAY** import: `application` (use cases, inbound ports, DTOs)
- **SHOULD NOT** import: `domain` directly (route through use cases)
- **MUST NOT** import: `infrastructure` (no direct DB/ML in handlers)

---

## Composition Root Exception

The single **composition root** module (entry point) is the only place allowed to:

- Instantiate concrete infrastructure adapters
- Inject implementations into use cases
- Bind configuration to implementations

_Location: `src/sentinel_anpr/__main__.py` or dedicated `bootstrap/` — _TBD via ADR._

---

## Cross-Context Rules (Within Domain)

- Contexts **should not** import each other's internal entities directly
- Prefer: application orchestration, domain events, or shared kernel (`domain/common/`)
- Anti-corruption layers for external registry models live in `infrastructure/external/`

---

## Enforcement (Planned)

| Mechanism | Status |
|-----------|--------|
| ArchUnit / import-linter / custom script | _TBD_ |
| CI gate on PR | _TBD_ |
| Code review checklist | See [development/conventions.md](../development/conventions.md) |

---

## Related

- [Clean Architecture Layers](clean-architecture-layers.md)
- [Hexagonal Ports & Adapters](hexagonal-ports-adapters.md)
