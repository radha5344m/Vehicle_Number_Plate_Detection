# Domain Layer

**Enterprise business rules** — innermost layer of Clean Architecture.

---

## Rules

- No imports from `application`, `infrastructure`, or `adapters`
- No I/O, frameworks, or infrastructure concerns
- Pure business logic: entities, value objects, domain services, events

---

## Bounded Contexts

| Package | README | Responsibility |
|---------|--------|----------------|
| `common/` | [common/README.md](common/README.md) | Shared kernel, base errors |
| `ingestion/` | [ingestion/README.md](ingestion/README.md) | Media intake domain |
| `plate_recognition/` | [plate_recognition/README.md](plate_recognition/README.md) | ANPR domain rules |
| `plate_verification/` | [plate_verification/README.md](plate_verification/README.md) | Registry verification rules |
| `clone_detection/` | [clone_detection/README.md](clone_detection/README.md) | Fraud/clone policies |
| `alerting/` | [alerting/README.md](alerting/README.md) | Alert domain rules |

---

## Subfolder Conventions

| Subfolder | Contents |
|-----------|----------|
| `entities/` | Objects with identity |
| `value_objects/` | Immutable value types |
| `services/` | Domain services (stateless logic) |
| `events/` | Domain events |
| `errors/` | Context-specific domain exceptions |

---

## Related

- [Bounded Contexts](../../../docs/architecture/bounded-contexts.md)
