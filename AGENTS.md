# SentinelANPR AI — Agent Instructions

Guidance for AI coding agents working in this repository.

## Architecture

Clean Architecture + Hexagonal (Ports & Adapters). Four backend layers:

`domain` → `application` → `infrastructure` + `interfaces`

Read `docs/architecture/overview.md` and `.cursor/rules/` before implementing.

## Non-Negotiables

1. **Domain purity** — no FastAPI, SQLAlchemy, OpenCV, PaddleOCR, YOLO, DB, or framework imports in `domain/`.
2. **Dependency direction** — inward only; composition root wires concrete classes.
3. **Thin interfaces** — no business logic or SQL in route handlers.
4. **Ports first** — define application ports before infrastructure adapters.
5. **Configuration** — environment variables via `ConfigurationPort`; no hardcoded secrets.
6. **Errors** — domain errors in domain; HTTP mapping in interfaces only.
7. **DI** — inject dependencies; instantiate concretes only in `bootstrap/` or `interfaces/dependency_injection/`.
8. **SRP** — one responsibility per file; keep functions small.
9. **Tests** — mirror `src/` under `tests/`; domain tests need zero mocks.

## Key Docs

| Topic | Path |
|-------|------|
| Modules | `docs/architecture/modules.md` |
| Database | `docs/database/schema-design.md` |
| AI Pipeline | `docs/ai-pipeline/pipeline-stages.md` |
| REST API | `docs/api/contracts-overview.md` |
| Frontend | `docs/frontend/README.md` |

## Cursor Rules

Enforcement rules: `.cursor/rules/*.mdc`
