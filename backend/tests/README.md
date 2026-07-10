# Tests

Test suite structure for SentinelANPR AI — mirrors `src/sentinel_anpr/`.

---

## Layout

| Directory | Scope |
|-----------|-------|
| `unit/domain/` | Pure domain logic |
| `unit/application/` | Use cases with port fakes |
| `integration/infrastructure/` | Real adapters (test DB, fixtures) |
| `integration/adapters/` | HTTP/CLI adapter contracts |
| `e2e/scenarios/` | Full pipeline scenarios |
| `fixtures/data/` | Sample images, registry JSON |
| `fixtures/fakes/` | In-memory port implementations |

---

## Principles

- **Fast unit tests** for domain and application (majority)
- **Integration tests** at infrastructure boundaries
- **E2E** sparingly — expensive, flaky if overused

---

## Related

- [Testability Strategy](../docs/architecture/testability-strategy.md)
