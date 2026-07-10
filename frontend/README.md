# SentinelANPR AI — Frontend

React + TypeScript + Tailwind CSS single-page application.

**Status:** Architecture only — no dependencies or implementation code.

---

## Stack

| Technology | Purpose |
|------------|---------|
| React 18+ | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| React Router v6 | Routing |
| TanStack Query | Server state |
| Zustand | Client state (auth, UI) |
| Vite | Build tool |

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/frontend/README.md](../docs/frontend/README.md) | Architecture overview |
| [docs/frontend/folder-structure.md](../docs/frontend/folder-structure.md) | Complete directory tree |
| [docs/frontend/pages.md](../docs/frontend/pages.md) | Page catalog |
| [docs/frontend/routing.md](../docs/frontend/routing.md) | Routes and guards |
| [docs/frontend/components.md](../docs/frontend/components.md) | Component tiers |
| [docs/frontend/hooks.md](../docs/frontend/hooks.md) | Custom hooks |
| [docs/frontend/services.md](../docs/frontend/services.md) | API services |
| [docs/frontend/state-management.md](../docs/frontend/state-management.md) | State strategy |

---

## Source Layout

```
src/
├── app/          # Providers, router
├── pages/        # Route pages
├── layouts/      # Shell layouts
├── components/   # ui · shared · features
├── hooks/        # Custom hooks
├── services/     # API layer
├── stores/       # Zustand stores
├── types/        # TypeScript DTOs
├── routes/       # Path constants, guards
├── config/       # Environment config
├── utils/        # Pure utilities
└── styles/       # Global CSS, Tailwind
```

---

## API Backend

Consumes SentinelANPR REST API at `/v1`. See [docs/api/](../docs/api/).

---

## Environment Variables (Planned)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API base URL |
| `VITE_APP_ENV` | `development` \| `staging` \| `production` |

---

## Not Included (Foundation Phase)

- No `package.json` or installed dependencies
- No React/TypeScript source files
- No build configuration files (stubs planned)
