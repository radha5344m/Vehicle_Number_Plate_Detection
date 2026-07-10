# Clean Architecture Layers

Mapping Robert C. Martin's Clean Architecture to SentinelANPR AI folder structure.

---

## Layer Diagram

```
        ┌──────────────────────────────────────────────────┐
        │  Frameworks & Drivers (Adapters + Infrastructure) │
        │  adapters/inbound │ infrastructure/*            │
        └────────────────────────┬─────────────────────────┘
                                 │
        ┌────────────────────────▼─────────────────────────┐
        │  Interface Adapters (partially in adapters/)     │
        │  Request/response mapping, presentation logic    │
        └────────────────────────┬─────────────────────────┘
                                 │
        ┌────────────────────────▼─────────────────────────┐
        │  Application Business Rules                      │
        │  application/use_cases │ application/ports      │
        └────────────────────────┬─────────────────────────┘
                                 │
        ┌────────────────────────▼─────────────────────────┐
        │  Enterprise Business Rules (Domain)              │
        │  domain/* — entities, VOs, domain services       │
        └──────────────────────────────────────────────────┘
```

---

## Layer Definitions

### Domain (`domain/`)

**Enterprise business rules.** Pure Python (or chosen language) with no I/O.

| Artifact | Purpose | Example (future) |
|----------|---------|------------------|
| Entity | Identity + lifecycle | `PlateSighting`, `VehicleRecord` |
| Value Object | Immutable, equality by value | `PlateNumber`, `ConfidenceScore` |
| Domain Service | Logic spanning entities | `CloneDetectionPolicy` |
| Domain Event | Something that happened | `PlateVerified`, `CloneSuspected` |
| Domain Exception | Business rule violations | `InvalidPlateFormatError` |

### Application (`application/`)

**Application business rules.** Orchestrates domain; defines ports.

| Artifact | Purpose |
|----------|---------|
| Use Case | One user/system intent per class |
| Inbound Port | Interface driving adapters call |
| Outbound Port | Interface infrastructure implements |
| DTO | Data crossing layer boundaries |

### Infrastructure (`infrastructure/`)

**Driven adapters.** Implements outbound ports.

| Package | Responsibility |
|---------|----------------|
| `persistence/` | Repositories, ORM mappings |
| `ml/` | Model loading, inference wrappers |
| `external/` | Registry/RTO HTTP clients |
| `messaging/` | Event publish/subscribe |
| `config/` | Config loaders implementing ports |

### Adapters (`adapters/`)

**Driving adapters.** Translate external requests into use case invocations.

| Package | Responsibility |
|---------|----------------|
| `inbound/http/` | REST/HTTP handlers |
| `inbound/cli/` | Command-line interface |
| `inbound/grpc/` | gRPC services |
| `inbound/messaging/` | Queue consumers |

---

## SOLID Mapping

| Principle | Application in SentinelANPR AI |
|-----------|-------------------------------|
| **S** — Single Responsibility | One use case per application service; one adapter per transport |
| **O** — Open/Closed | Extend via new adapters implementing existing ports |
| **L** — Liskov Substitution | All port implementations interchangeable in tests |
| **I** — Interface Segregation | Small focused ports (e.g. `PlateRecognizer` vs monolithic `AIService`) |
| **D** — Dependency Inversion | Application depends on port abstractions, not concrete ML/DB |

---

## Cross-Cutting Concerns (Planned Locations)

| Concern | Primary Layer | Notes |
|---------|---------------|-------|
| Logging | Infrastructure / Adapters | Structured logs at boundaries |
| Validation | Adapters (format) + Domain (rules) | Split syntactic vs semantic |
| AuthN/AuthZ | Adapters + Application | Policy port _TBD_ |
| Correlation IDs | Adapters | Propagate through use case context |

---

## Anti-Patterns to Avoid

- Domain importing SQL, HTTP, or ML libraries
- Use cases calling concrete repository classes directly
- Business rules in HTTP handlers
- God-service combining recognition + verification + alerting

---

## Related

- [Hexagonal Ports & Adapters](hexagonal-ports-adapters.md)
- [Dependency Direction](dependency-direction.md)
