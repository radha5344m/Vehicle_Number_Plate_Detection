# Development Conventions

Coding and structural conventions for SentinelANPR AI.

**Status:** Skeleton — expand during implementation.

---

## Package Naming

| Element | Convention | Example |
|---------|------------|---------|
| Package | `snake_case` | `plate_recognition` |
| Module | `snake_case` | `verify_plate.py` |
| Class | `PascalCase` | `VerifyPlateUseCase` |
| Port interface | `PascalCase` + `Port` suffix | `VehicleRegistryPort` |
| Use case | Verb phrase + `UseCase` | `DetectCloneUseCase` |

---

## File Placement Rules

| Artifact | Location |
|----------|----------|
| Entity | `domain/<context>/entities/` |
| Value object | `domain/<context>/value_objects/` |
| Domain service | `domain/<context>/services/` |
| Use case | `application/use_cases/<context>/` |
| Inbound port | `application/ports/inbound/` |
| Outbound port | `application/ports/outbound/` |
| DTO | `application/dto/` |
| Repository impl | `infrastructure/persistence/repositories/` |
| HTTP handler | `adapters/inbound/http/handlers/` |

---

## Dependency Checklist (PR Review)

- [ ] Domain has no outward imports
- [ ] Application has no infrastructure/adapter imports
- [ ] New outbound integration has a port in `application/ports/outbound/`
- [ ] Tests added/updated in mirrored `tests/` path
- [ ] ADR created if technology or boundary changed

---

## Documentation

- Public APIs: docstrings _TBD format_
- Architecture changes: update `docs/architecture/` + ADR

---

## Related

- [Dependency Direction](../architecture/dependency-direction.md)
