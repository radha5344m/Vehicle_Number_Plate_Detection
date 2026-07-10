# Testability Strategy

Testing approach aligned with Clean Architecture and ports.

---

## Test Pyramid

```
        ┌─────┐
        │ E2E │  Few — full adapter + infra (test env)
        ├─────┤
        │ Int │  Some — real DB/ML with test fixtures
        ├─────┤
        │ Unit│  Many — domain + application with fakes
        └─────┘
```

---

## Per-Layer Testing

| Layer | What to Test | Dependencies |
|-------|--------------|--------------|
| Domain | Entities, VOs, domain services, policies | None (pure) |
| Application | Use cases with fake outbound ports | Stubs/mocks |
| Infrastructure | Adapter correctness | Test DB, wiremock, sample models |
| Adapters | Request/response mapping | Mock use cases |

---

## Port Fakes

Outbound ports enable **in-memory fakes** for application tests:

| Port | Fake Location (planned) |
|------|-------------------------|
| `SightingRepositoryPort` | `tests/fixtures/fakes/` |
| `VehicleRegistryPort` | `tests/fixtures/fakes/` |
| `PlateRecognizerPort` | `tests/fixtures/fakes/` |

---

## Test Directory Structure

```
tests/
├── unit/
│   ├── domain/
│   └── application/
├── integration/
│   ├── infrastructure/
│   └── adapters/
├── e2e/
└── fixtures/
    ├── data/
    └── fakes/
```

---

## Naming Conventions (Planned)

| Pattern | Example |
|---------|---------|
| Unit test file | `test_<module>.py` |
| Test class | `Test<Subject>` |
| Test method | `test_<behavior>_<expected>` |

---

## CI (Planned)

_TBD — unit on every PR; integration on merge; e2e nightly._

---

## Related

- [tests/README.md](../../tests/README.md)
