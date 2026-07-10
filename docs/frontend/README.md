# Frontend Architecture — SentinelANPR AI

**Stack:** React · TypeScript · Tailwind CSS  
**Status:** Architecture only — no implementation

---

## Purpose

Single-page application for police officers and supervisors to perform vehicle scans, review verification outcomes, manage alerts, generate reports, and view analytics — consuming the SentinelANPR REST API (`/v1`).

---

## Design Principles

| Principle | Application |
|-----------|-------------|
| **Feature-oriented structure** | Pages and components grouped by domain feature |
| **Separation of concerns** | UI components do not call `fetch` directly — services do |
| **Server state vs client state** | API data in query cache; auth/UI preferences in stores |
| **Role-based access** | Routes and UI gated by `officer`, `supervisor`, `admin` |
| **API contract alignment** | TypeScript types mirror backend DTOs |
| **Composition** | Small components; pages orchestrate features |

---

## Documents

| File | Description |
|------|-------------|
| [folder-structure.md](folder-structure.md) | Complete directory tree |
| [pages.md](pages.md) | Page catalog and responsibilities |
| [layouts.md](layouts.md) | Layout components |
| [components.md](components.md) | Component hierarchy and SRP |
| [hooks.md](hooks.md) | Custom hooks catalog |
| [services.md](services.md) | API service layer |
| [state-management.md](state-management.md) | Stores and server cache strategy |
| [routing.md](routing.md) | Routes, guards, lazy loading |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
├─────────────────────────────────────────────────────────────┤
│  Pages (route targets)                                       │
│    └── Layouts (shell, nav, auth wrapper)                   │
│          └── Feature Components + UI Primitives              │
│                └── Hooks (logic binding)                       │
│                      └── Services (HTTP → REST API)            │
├─────────────────────────────────────────────────────────────┤
│  State Layer                                                 │
│    ├── Server State (TanStack Query) — scans, dashboard…    │
│    └── Client State (Zustand) — auth session, UI prefs      │
├─────────────────────────────────────────────────────────────┤
│  Cross-cutting: Router · Auth Guard · Error Boundary · i18n  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS /v1
                    SentinelANPR REST API
```

---

## Technology Choices (_ADR pending implementation_)

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Framework | React 18+ | Component model, ecosystem |
| Language | TypeScript | Type safety aligned with API DTOs |
| Styling | Tailwind CSS | Utility-first; design tokens via config |
| Routing | React Router v6 | Nested layouts, route guards |
| Server state | TanStack Query | Caching, polling (async scans), invalidation |
| Client state | Zustand | Lightweight auth + UI state |
| HTTP | Axios or fetch wrapper | Interceptors for JWT refresh |
| Forms | React Hook Form + Zod | Validation aligned with API rules |
| Charts | Recharts | Analytics dashboards |
| Build | Vite | Fast dev, TypeScript native |

---

## Role-Based UI Matrix

| Feature | Officer | Supervisor | Admin |
|---------|---------|------------|-------|
| Dashboard | Own station | Station | All |
| Vehicle Scan | ✓ | ✓ | ✓ |
| Vehicle Lookup | ✓ | ✓ | ✓ |
| Verification | ✓ | ✓ | ✓ |
| Alerts | ✓ | ✓ | ✓ |
| Reports | Own | Station | All |
| Analytics | — | ✓ | ✓ |
| Audit History | — | ✓ | ✓ |
| API Keys | — | — | ✓ |

---

## Related

- [REST API](../api/contracts-overview.md)
- [Module Architecture](../architecture/modules.md)
- Source tree: [`frontend/`](../../frontend/)
