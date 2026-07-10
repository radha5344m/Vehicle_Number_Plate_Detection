# SentinelANPR AI

**AI-Powered Vehicle Number Plate Verification & Cloned Plate Detection System**

> Architecture frozen at foundation stage. No implementation code in this repository yet.

---

## Purpose

SentinelANPR AI is a production-oriented system for:

1. **Automatic Number Plate Recognition (ANPR)** from images and video streams
2. **Plate verification** against authoritative vehicle registries
3. **Cloned plate detection** using multi-signal fraud analysis

This repository currently contains **only the project foundation**: folder structure, placeholder files, and documentation skeletons aligned with **Clean Architecture**, **SOLID**, and **Hexagonal (Ports & Adapters)** principles.

---

## Engineering Pillars

| Pillar | How It Is Addressed |
|--------|---------------------|
| Architecture | Clean + Hexagonal layering; bounded contexts in `domain/` |
| Modularity | Feature-aligned packages; adapters swappable per port |
| Separation of Concerns | Domain, application, infrastructure, and adapters are isolated |
| Dependency Direction | Dependencies point inward; domain has zero outward deps |
| Interfaces | Ports defined in `application/ports/`; adapters implement them |
| Configuration Management | Environment-specific config under `config/` |
| Error Handling | Domain errors in domain; application error mapping planned in docs |
| Testability | Mirror structure under `tests/`; ports enable mocking |
| Documentation | `docs/` with ADRs, architecture, API contracts skeleton |
| Evolvability | ADR process; bounded contexts allow independent evolution |

---

## Repository Layout

```
sentinel-anpr-ai/
├── README.md                 ← You are here
├── docs/                     ← Architecture, ADRs, API contracts, runbooks
├── frontend/                 ← React SPA (TypeScript, Tailwind)
└── backend/                  ← Python backend (FastAPI, Clean / Hexagonal)
    ├── pyproject.toml        ← Packaging, tooling, pytest config
    ├── requirements.txt      ← Runtime dependencies
    ├── config/               ← Environment-specific configuration (no secrets)
    ├── data/                 ← SQLite DB, uploads, generated reports
    ├── scripts/              ← Operational and dev helper scripts (placeholders)
    ├── src/sentinel_anpr/    ← Source root (Clean / Hexagonal layers)
    └── tests/                ← Unit, integration, e2e (mirrors src layout)
```

---

## Source Layer Map (`backend/src/sentinel_anpr/`)

| Folder | Layer | Responsibility |
|--------|-------|----------------|
| `domain/` | **Domain** (innermost) | Entities, value objects, domain services, domain events — pure business rules |
| `application/` | **Application** | Use cases, DTOs, **ports** (inbound/outbound interfaces) |
| `infrastructure/` | **Driven adapters** | Persistence, ML inference, external APIs, messaging implementations |
| `adapters/` | **Driving adapters** | HTTP, CLI, gRPC, message consumers — entry points |

### Bounded Contexts (under `domain/`)

| Context | Purpose |
|---------|---------|
| `plate_recognition` | OCR/ANPR, plate localization, character extraction |
| `plate_verification` | Registry lookup, validity rules, vehicle–plate binding |
| `clone_detection` | Fraud signals, duplicate sightings, anomaly scoring |
| `ingestion` | Image/video intake, metadata, stream handling |
| `alerting` | Notifications, escalation, audit trail triggers |
| `common` | Shared kernel: base types, errors, identifiers |

---

## Dependency Rules (Summary)

```
adapters (inbound)  →  application  →  domain
infrastructure      →  application  →  domain
domain              →  (nothing external)
```

- **Domain** must not import from application, infrastructure, or adapters.
- **Application** defines ports; it must not import concrete adapters.
- **Infrastructure** implements outbound ports.
- **Adapters** implement inbound ports and delegate to use cases.

See [docs/architecture/dependency-direction.md](docs/architecture/dependency-direction.md) for full rules.

---

## Environment (Vision AI)

Copy `backend/.env.example` → `backend/.env`. Vision uses **Google Gemini** (not OpenAI):

```env
SENTINEL_VISION_PROVIDER=gemini
GEMINI_API_KEY=
SENTINEL_GEMINI_MODEL=gemini-2.5-flash
```

Local without a cloud key: `SENTINEL_VISION_PROVIDER=stub`. See [getting-started](docs/development/getting-started.md).

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [docs/README.md](docs/README.md) | Documentation hub |
| [docs/architecture/overview.md](docs/architecture/overview.md) | System architecture overview |
| [docs/architecture/clean-architecture-layers.md](docs/architecture/clean-architecture-layers.md) | Clean Architecture mapping |
| [docs/architecture/hexagonal-ports-adapters.md](docs/architecture/hexagonal-ports-adapters.md) | Ports & adapters catalog |
| [docs/architecture/bounded-contexts.md](docs/architecture/bounded-contexts.md) | Context boundaries and interactions |
| [docs/adr/README.md](docs/adr/README.md) | Architecture Decision Records |
| [docs/development/conventions.md](docs/development/conventions.md) | Naming and coding conventions (skeleton) |

---

## What Is NOT in This Foundation

- No React, FastAPI, or other framework application code
- No installed dependencies or lockfiles
- No ML models, training pipelines, or inference implementations
- No database schemas or migrations

---

## Next Steps (Post-Foundation)

1. Review and approve architecture documents in `docs/architecture/`
2. Record decisions via ADRs in `docs/adr/`
3. Define API contracts in `docs/api/`
4. Begin implementation **only after** architecture sign-off

---

## License

_To be determined._
