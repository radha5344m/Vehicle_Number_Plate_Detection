# Routing

React Router v6 configuration with authentication and role guards.

---

## Route Tree

```
/  (RootLayout)
├── /login                    (GuestGuard → AuthLayout → LoginPage)
├── /forbidden                (AuthLayout → ForbiddenPage)
│
└── /  (AuthGuard → AppLayout)
    ├── /                       DashboardPage
    ├── /scan                   ScanPage
    ├── /scans                  ScanListPage
    ├── /scans/:scanId          ScanDetailPage
    ├── /vehicles/lookup        VehicleLookupPage
    ├── /vehicles/:vehicleId    VehicleDetailPage
    ├── /verification           VerificationPage
    ├── /alerts                 AlertsPage
    ├── /reports                ReportsPage
    ├── /reports/:reportId      ReportDetailPage
    │
    ├── /analytics              (RoleGuard: supervisor+) AnalyticsPage
    ├── /history/scans          ScanHistoryPage
    ├── /history/audit          (RoleGuard: supervisor+) AuditLogPage
    ├── /history/plate/:plate   PlateSightingsPage
    │
    └── *                       NotFoundPage
```

---

## Path Constants (`routes/paths.ts`)

| Constant | Path |
|----------|------|
| `PATHS.LOGIN` | `/login` |
| `PATHS.DASHBOARD` | `/` |
| `PATHS.SCAN` | `/scan` |
| `PATHS.SCANS` | `/scans` |
| `PATHS.SCAN_DETAIL` | `/scans/:scanId` |
| `PATHS.VEHICLE_LOOKUP` | `/vehicles/lookup` |
| `PATHS.VEHICLE_DETAIL` | `/vehicles/:vehicleId` |
| `PATHS.VERIFICATION` | `/verification` |
| `PATHS.ALERTS` | `/alerts` |
| `PATHS.REPORTS` | `/reports` |
| `PATHS.REPORT_DETAIL` | `/reports/:reportId` |
| `PATHS.ANALYTICS` | `/analytics` |
| `PATHS.HISTORY_SCANS` | `/history/scans` |
| `PATHS.HISTORY_AUDIT` | `/history/audit` |
| `PATHS.HISTORY_PLATE` | `/history/plate/:plate` |
| `PATHS.FORBIDDEN` | `/forbidden` |

---

## Route Guards

### AuthGuard

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Redirect unauthenticated users to `/login` |
| **Check** | `authStore.isAuthenticated` |
| **Redirect** | `/login?redirect={currentPath}` |
| **Wraps** | All `AppLayout` routes |

### GuestGuard

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Redirect authenticated users away from login |
| **Check** | If authenticated → redirect to `/` |
| **Wraps** | `/login` |

### RoleGuard

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Block routes by role |
| **Props** | `allowedRoles: ['supervisor', 'admin']` |
| **On deny** | Redirect to `/forbidden` |
| **Routes** | `/analytics`, `/history/audit` |

---

## Lazy Loading

Pages loaded via `React.lazy()` for code splitting:

| Chunk | Pages |
|-------|-------|
| `auth` | LoginPage |
| `dashboard` | DashboardPage |
| `scan` | ScanPage, ScanDetailPage, ScanListPage |
| `vehicles` | VehicleLookupPage, VehicleDetailPage |
| `verification` | VerificationPage |
| `alerts` | AlertsPage |
| `reports` | ReportsPage, ReportDetailPage |
| `analytics` | AnalyticsPage |
| `history` | ScanHistoryPage, AuditLogPage, PlateSightingsPage |

Each lazy page wrapped in `<Suspense fallback={<LoadingOverlay />}>`.

---

## Navigation Config (Sidebar)

| Label | Path | Icon | Roles |
|-------|------|------|-------|
| Dashboard | `/` | Home | All |
| New Scan | `/scan` | Camera | All |
| Scans | `/scans` | List | All |
| Lookup | `/vehicles/lookup` | Search | All |
| Verify | `/verification` | Check | All |
| Alerts | `/alerts` | Bell | All |
| Reports | `/reports` | File | All |
| Analytics | `/analytics` | Chart | Supervisor+ |
| History | `/history/scans` | Clock | All |
| Audit Log | `/history/audit` | Shield | Supervisor+ |

---

## URL State Sync

| Page | URL Params | Purpose |
|------|------------|---------|
| ScanListPage | `?plate=&decision=&from=&to=&page=` | Sharable filters |
| AnalyticsPage | `?from=&to=&group_by=` | Chart date range |
| AuditLogPage | `?entity_type=&event_type=&page=` | Audit filters |
| VerificationPage | `?scan_id=` | Pre-link to scan |

Implemented via `useSearchParams` in hooks (`usePagination`).

---

## Post-Login Redirect

```
/login?redirect=/scans/abc-123
  → on success → navigate(redirect || '/')
```

---

## Error Routes

| Route | Trigger |
|-------|---------|
| `/forbidden` | RoleGuard denial, 403 from API |
| `*` (NotFoundPage) | Unknown paths |

---

## Router File Structure

```
app/router/
├── AppRouter.tsx       # BrowserRouter + route definitions
└── routeConfig.ts      # Route object array (path, element, guards, lazy)

routes/
├── paths.ts            # Path constants
└── guards/
    ├── AuthGuard.tsx
    ├── RoleGuard.tsx
    └── GuestGuard.tsx
```

---

## Related

- [Pages](pages.md)
- [Layouts](layouts.md)
