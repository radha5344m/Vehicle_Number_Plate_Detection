# Module Map

Folder-to-responsibility reference for `src/sentinel_anpr/`.

---

## Root

| Path | Description |
|------|-------------|
| `src/sentinel_anpr/` | Python package root; composition root _TBD_ |
| `src/sentinel_anpr/README.md` | Source tree guide |

---

## Domain (`domain/`)

| Path | Bounded Context | Planned Contents |
|------|-----------------|------------------|
| `domain/common/` | Shared kernel | Base errors, IDs, `PlateNumber` VO |
| `domain/ingestion/` | Ingestion | `Capture`, `MediaSource` entities |
| `domain/plate_recognition/` | Recognition | `RecognitionResult`, confidence rules |
| `domain/plate_verification/` | Verification | `VerificationOutcome`, registry rules |
| `domain/clone_detection/` | Clone detection | `CloneRiskAssessment`, policies |
| `domain/alerting/` | Alerting | `Alert`, severity, escalation rules |

---

## Application (`application/`)

| Path | Description |
|------|-------------|
| `application/ports/inbound/` | Driving port interfaces |
| `application/ports/outbound/` | Driven port interfaces |
| `application/use_cases/plate_recognition/` | Recognize plate use cases |
| `application/use_cases/plate_verification/` | Verify plate use cases |
| `application/use_cases/clone_detection/` | Detect clone use cases |
| `application/use_cases/ingestion/` | Ingest media use cases |
| `application/use_cases/orchestration/` | Multi-step pipelines |
| `application/dto/` | Request/response data structures |
| `application/services/` | Application services (if needed beyond use cases) |

---

## Infrastructure (`infrastructure/`)

| Path | Adapter Type | Implements |
|------|--------------|------------|
| `infrastructure/persistence/` | Driven | Repository, image storage ports |
| `infrastructure/ml/` | Driven | Detector, recognizer ports |
| `infrastructure/external/` | Driven | Vehicle registry port |
| `infrastructure/messaging/` | Driven | Alert publisher port |
| `infrastructure/config/` | Driven | Config port |
| `infrastructure/common/` | Driven | Clock, logging adapters |

---

## Adapters (`adapters/`)

| Path | Adapter Type | Implements |
|------|--------------|------------|
| `adapters/inbound/http/` | Driving | REST handlers |
| `adapters/inbound/cli/` | Driving | CLI commands |
| `adapters/inbound/grpc/` | Driving | gRPC services |
| `adapters/inbound/messaging/` | Driving | Queue consumers |

---

## Tests Mirror

| Source | Test Location |
|--------|---------------|
| `domain/*` | `tests/unit/domain/*` |
| `application/*` | `tests/unit/application/*` |
| `infrastructure/*` | `tests/integration/infrastructure/*` |
| `adapters/*` | `tests/integration/adapters/*` |
| Full flows | `tests/e2e/*` |

---

## Config

| Path | Environment |
|------|-------------|
| `config/default/` | Base settings |
| `config/development/` | Local dev overrides |
| `config/staging/` | Staging overrides |
| `config/production/` | Production overrides |

---

## Related

- [Bounded Contexts](bounded-contexts.md)
- [Hexagonal Ports & Adapters](hexagonal-ports-adapters.md)
