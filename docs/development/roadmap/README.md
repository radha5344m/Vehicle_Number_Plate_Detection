# SentinelANPR AI — Development Roadmap

**Starting point:** Architecture frozen (foundation complete).  
**Goal:** Production-ready ANPR system from zero implementation to deployment.

---

## Implementation Phases

| Phase | Name | Files (approx.) | Exit Criteria |
|-------|------|-----------------|---------------|
| **0** | [Project Bootstrap](00-bootstrap.md) | 8 | Tooling runs; empty package imports |
| **1** | [Domain](01-domain.md) | 45 | All domain unit tests pass; zero outer imports |
| **2** | [Ports](02-ports.md) | 22 | All port protocols defined; mypy clean |
| **3** | [Application](03-application.md) | 38 | Use cases pass with fakes |
| **4** | [Infrastructure](04-infrastructure.md) | 52 | Adapters pass integration tests |
| **5** | [Interfaces](05-interfaces.md) | 48 | REST API matches `docs/api/` |
| **6** | [Frontend](06-frontend.md) | 95 | SPA consumes live API |
| **7** | [Testing](07-testing.md) | 60+ | CI green; coverage targets met |
| **8** | [Deployment](08-deployment.md) | 18 | Staging environment live |

**Total implementable files:** ~386 (excluding docs, `.gitkeep`, placeholders)

---

## Dependency Flow Between Phases

```
Phase 0 (Bootstrap)
    ↓
Phase 1 (Domain) ──────────────────────────────┐
    ↓                                          │
Phase 2 (Ports) ← depends on domain types      │
    ↓                                          │
Phase 3 (Application) ← ports + domain         │
    ↓                                          │
Phase 4 (Infrastructure) ← implements ports    │
    ↓                                          │
Phase 5 (Interfaces) ← use cases + DI          │
    ↓                                          │
Phase 6 (Frontend) ← REST API contracts        │
    ↓                                          │
Phase 7 (Testing) ← validates all layers ──────┘
    ↓
Phase 8 (Deployment)
```

---

## Legend (used in phase documents)

| Column | Meaning |
|--------|---------|
| **Purpose** | Why this file exists |
| **Depends On** | Must exist before implementation |
| **Why This Stage** | Rationale for phase placement |

---

## Critical Path (MVP)

Minimum viable product for field officer scan → decision:

```
Domain: PlateNumber, VerificationOutcome, DecisionPolicy, ScanSession
  → Ports: OcrPort, PlateDetectionPort, VehicleRegistryPort, ...
  → Application: ProcessPlatePipelineUseCase
  → Infrastructure: YOLO, PaddleOCR, DB repos, config, logging
  → Interfaces: POST /v1/scans, GET /v1/scans/{id}, auth
  → Frontend: LoginPage, ScanPage, ScanDetailPage
  → Tests: domain + pipeline e2e
  → Deployment: Docker + staging
```

---

## Phase Documents

| # | Document |
|---|----------|
| 0 | [00-bootstrap.md](00-bootstrap.md) |
| 1 | [01-domain.md](01-domain.md) |
| 2 | [02-ports.md](02-ports.md) |
| 3 | [03-application.md](03-application.md) |
| 4 | [04-infrastructure.md](04-infrastructure.md) |
| 5 | [05-interfaces.md](05-interfaces.md) |
| 6 | [06-frontend.md](06-frontend.md) |
| 7 | [07-testing.md](07-testing.md) |
| 8 | [08-deployment.md](08-deployment.md) |

---

## Rules During Implementation

Follow `.cursor/rules/*.mdc` and `AGENTS.md` at every phase.

---

## Related

- [Architecture Overview](../architecture/overview.md)
- [AI Pipeline](../ai-pipeline/pipeline-stages.md)
- [API Spec](../api/contracts-overview.md)
