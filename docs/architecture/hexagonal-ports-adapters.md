# Hexagonal Architecture — Ports & Adapters

Inventory of planned ports and adapter placements. **Interfaces only at foundation stage.**

---

## Port Types

| Type | Direction | Defined In | Implemented By |
|------|-----------|------------|----------------|
| **Inbound (Driving)** | External → Application | `application/ports/inbound/` | `adapters/inbound/*` |
| **Outbound (Driven)** | Application → External | `application/ports/outbound/` | `infrastructure/*` |

---

## Inbound Ports (Driving)

Interfaces that use cases expose to the outside world.

| Port (planned name) | Use Case Area | Adapter(s) |
|---------------------|---------------|------------|
| `ProcessImageCommandPort` | Ingestion + Recognition | HTTP, CLI, Messaging |
| `VerifyPlateQueryPort` | Verification | HTTP, gRPC |
| `DetectCloneCommandPort` | Clone Detection | HTTP, Messaging |
| `HealthCheckPort` | Operations | HTTP |

_Placeholder files: `src/sentinel_anpr/application/ports/inbound/`._

---

## Outbound Ports (Driven)

Interfaces the application needs from the outside world.

| Port (planned name) | Purpose | Adapter (Infrastructure) |
|---------------------|---------|--------------------------|
| `PlateRecognizerPort` | ANPR / OCR inference | `infrastructure/ml/` |
| `PlateDetectorPort` | Plate region localization | `infrastructure/ml/` |
| `VehicleRegistryPort` | Official plate–vehicle lookup | `infrastructure/external/` |
| `SightingRepositoryPort` | Persist/query sightings | `infrastructure/persistence/` |
| `AlertPublisherPort` | Emit clone/verification alerts | `infrastructure/messaging/` |
| `ImageStoragePort` | Store/retrieve raw images | `infrastructure/persistence/` or object store |
| `ClockPort` | Testable time | `infrastructure/common/` |
| `ConfigPort` | Typed configuration access | `infrastructure/config/` |

_Placeholder files: `src/sentinel_anpr/application/ports/outbound/`._

---

## Adapter Matrix

```
                    INBOUND ADAPTERS
                 ┌──────┬──────┬──────┬──────────┐
                 │ HTTP │ CLI  │ gRPC │ Messaging│
ProcessImage     │  ✓   │  ✓   │  ✓   │    ✓     │
VerifyPlate      │  ✓   │  ✓   │  ✓   │    —     │
DetectClone      │  ✓   │  —   │  ✓   │    ✓     │
HealthCheck      │  ✓   │  —   │  —   │    —     │
                 └──────┴──────┴──────┴──────────┘

                    OUTBOUND ADAPTERS
                 ┌────────────┬──────────┬──────────┐
                 │ Persistence│ ML       │ External │
PlateRecognizer  │     —      │    ✓     │    —     │
VehicleRegistry  │     —      │    —     │    ✓     │
SightingRepo     │     ✓      │    —     │    —     │
AlertPublisher   │     —      │    —     │  msg ✓   │
ImageStorage     │     ✓      │    —     │  opt ✓   │
```

---

## Composition Root

The **composition root** (wiring dependencies) will live at application entry — _exact module TBD via ADR_. Rules:

- Only the composition root references concrete infrastructure classes
- All other modules depend on abstractions (ports)

---

## Testing with Ports

| Test Type | Strategy |
|-----------|----------|
| Unit (domain) | Pure logic, no ports |
| Unit (application) | Fake/stub outbound ports |
| Integration | Real adapter against test doubles (DB, wiremock) |
| E2E | Full adapter stack |

---

## Related

- [Module Map](module-map.md)
- [Testability Strategy](testability-strategy.md)
