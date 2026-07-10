# State Management

Two-layer state strategy: **server state** (API data) and **client state** (auth, UI).

---

## Strategy Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Components                      │
├────────────────────────┬────────────────────────────────┤
│   TanStack Query       │         Zustand Stores          │
│   (Server State)       │         (Client State)          │
│                        │                                │
│  • Scans, vehicles     │  • Auth session (tokens, officer)│
│  • Dashboard data      │  • UI preferences              │
│  • Reports, analytics  │  • Sidebar collapsed state     │
│  • History, audit      │  • Selected station (supervisor)│
│                        │                                │
│  Cache · Invalidate    │  Persist to sessionStorage     │
│  Refetch · Polling     │  (auth only)                   │
└────────────────────────┴────────────────────────────────┘
```

**Principle:** Do not duplicate API data in Zustand. TanStack Query is the single source of truth for server data.

---

## Server State — TanStack Query

### Query Key Conventions

| Pattern | Example |
|---------|---------|
| Resource list | `['scans', filters, page]` |
| Resource detail | `['scans', scanId]` |
| Nested resource | `['verification', 'by-scan', scanId]` |
| Dashboard | `['dashboard', 'summary', stationId, date]` |
| Analytics | `['analytics', metric, params]` |

### Cache Policies

| Data Type | `staleTime` | `gcTime` | Refetch |
|-----------|-------------|----------|---------|
| Dashboard summary | 30s | 5min | Interval 30s |
| Scan detail (in progress) | 0 | 5min | Poll 2s |
| Scan detail (completed) | 5min | 30min | On mount |
| Vehicle lookup | 2min | 10min | On demand |
| Analytics | 5min | 30min | On filter change |
| Audit logs | 1min | 10min | On filter change |

### Invalidation Map

| Mutation | Invalidates |
|----------|-------------|
| `createScan` | `['scans']`, `['dashboard']` |
| `acknowledgeAlert` | `['dashboard', 'alerts']`, `['alerts']` |
| `generateReport` | `['reports']` |
| `verifyPlate` | `['verification']` |
| `login` | Full cache clear |
| `logout` | Full cache clear |

### Polling (Async Scans)

When `POST /v1/scans` returns `202` with `processing_status: received`:

1. `useScanPolling` enables `refetchInterval: 2000`
2. Stops when status is `completed` or `failed`
3. On complete: invalidate dashboard queries

---

## Client State — Zustand

### authStore

| Field | Type | Persisted | Description |
|-------|------|-----------|-------------|
| `accessToken` | string \| null | sessionStorage | JWT access token |
| `refreshToken` | string \| null | sessionStorage | JWT refresh token |
| `officer` | OfficerSummary \| null | sessionStorage | Current officer profile |
| `permissions` | string[] | sessionStorage | Resolved permissions |
| `isAuthenticated` | boolean | derived | `!!accessToken` |

| Action | Behavior |
|--------|----------|
| `setAuth(tokens, officer)` | Store tokens + officer on login |
| `clearAuth()` | Clear all on logout |
| `updateOfficer(officer)` | Refresh profile from `/auth/me` |

**Security:** Tokens in `sessionStorage` (cleared on tab close). Never in `localStorage` for police app.

### uiStore

| Field | Type | Persisted | Description |
|-------|------|-----------|-------------|
| `sidebarCollapsed` | boolean | localStorage | Sidebar state |
| `selectedStationId` | UUID \| null | sessionStorage | Supervisor station filter |
| `theme` | `'light' \| 'dark'` | localStorage | Theme preference |

| Action | Behavior |
|--------|----------|
| `toggleSidebar()` | Flip collapsed state |
| `setStation(id)` | Set supervisor dashboard scope |

---

## Provider Setup (`app/providers/`)

```
AppProviders
├── QueryProvider      (TanStack Query client)
├── ThemeProvider      (optional dark mode)
└── children
```

`authStore` does not need a React context provider — Zustand hooks subscribe directly.

---

## State Flow Examples

### Login Flow

```
LoginForm submit
  → useAuth.login()
    → authService.login()
      → authStore.setAuth(tokens, officer)
        → navigate('/')
          → dashboard queries enabled (authenticated)
```

### Scan Flow (Sync)

```
ImageCapture submit
  → useCreateScan.mutate(formData)
    → scanService.createScan()
      → onSuccess: show ScanResultCard
      → invalidate ['scans'], ['dashboard']
```

### Logout Flow

```
Header logout click
  → useAuth.logout()
    → authService.logout()
    → authStore.clearAuth()
    → queryClient.clear()
    → navigate('/login')
```

---

## What NOT to Store

| Data | Why | Use Instead |
|------|-----|-------------|
| Scan list in Zustand | Stale, duplicated | TanStack Query |
| Form field state (login) | Local to form | React Hook Form local state |
| Modal open state | Local to component | `useState` in parent |
| API error messages | Transient | Query `error` or toast |

---

## Related

- [Hooks](hooks.md)
- [Services](services.md)
