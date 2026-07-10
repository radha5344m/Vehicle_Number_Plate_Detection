# Custom Hooks

Hooks bridge **services** and **components**. They own loading/error/data state for features.

---

## Hook Design Rules

| Rule | Detail |
|------|--------|
| Prefix | Always `use*` |
| Return shape | `{ data, isLoading, error, ...actions }` |
| Server data | Prefer TanStack Query wrappers |
| Client data | Read/write `stores/` |
| No JSX | Hooks never return React elements |
| Colocation | Group by feature domain matching `services/` |

---

## Auth Hooks

### `useAuth`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Login, logout, current officer, token state |
| **Store** | `authStore` |
| **Service** | `authService` |
| **Returns** | `{ officer, isAuthenticated, login, logout, isLoading }` |
| **Side effects** | On login: set tokens, redirect; on logout: clear store, redirect `/login` |

### `usePermissions`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Role and permission checks for conditional UI |
| **Returns** | `{ hasRole, canAccess, permissions }` |
| **Usage** | `canAccess('analytics')`, `hasRole('supervisor')` |

---

## Scan Hooks

### `useCreateScan`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Submit image for full pipeline |
| **Service** | `scanService.createScan(formData)` |
| **Returns** | `{ mutate, isPending, data, error }` |
| **Mode** | Supports sync (await result) and async (return scan_id) |

### `useScanDetail`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Fetch single scan by ID |
| **Query key** | `['scans', scanId]` |
| **Service** | `scanService.getScan(scanId)` |
| **Returns** | TanStack Query result |

### `useScanPolling`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Poll scan status until `completed` or `failed` |
| **Query key** | `['scans', scanId, 'poll']` |
| **Interval** | 2s (_configurable_); stops on terminal status |
| **Usage** | Async scan mode on `ScanPage` |

### `useScanList`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Paginated scan list with filters |
| **Query key** | `['scans', filters, page]` |
| **Service** | `scanService.listScans(params)` |

### `useRetryScan`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Retry failed scan |
| **Service** | `scanService.retryScan(scanId)` |
| **On success** | Invalidate scan queries |

---

## Dashboard Hooks

### `useDashboardSummary`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['dashboard', 'summary', stationId, date]` |
| **Service** | `dashboardService.getSummary()` |
| **Refetch** | `refetchInterval: 30000` |

### `useRecentFlags`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['dashboard', 'recent-flags', params]` |
| **Service** | `dashboardService.getRecentFlags()` |

### `useDashboardAlerts`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['dashboard', 'alerts', params]` |
| **Service** | `dashboardService.getAlerts()` |

---

## Vehicle Hooks

### `useVehicleLookup`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Search vehicle by plate |
| **Trigger** | Manual (not auto-fetch on mount) |
| **Service** | `vehicleService.lookup(plate, jurisdiction)` |
| **Returns** | `{ lookup, data, isLoading, error }` |

### `useVehicleDetail`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['vehicles', vehicleId]` |
| **Service** | `vehicleService.getVehicle(vehicleId)` |

---

## Verification Hooks

### `useVerifyPlate`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Standalone plate verification |
| **Service** | `verificationService.verify(payload)` |
| **Returns** | Mutation result with `VerificationResponse` |

### `useVerificationByScan`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['verification', 'by-scan', scanId]` |
| **Service** | `verificationService.getByScan(scanId)` |

---

## Alert Hooks

### `useAcknowledgeAlert`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Acknowledge open alert |
| **Service** | `alertService.acknowledge(alertId, notes)` |
| **On success** | Invalidate `['dashboard', 'alerts']` and `['alerts']` |

---

## Report Hooks

### `useGenerateReport`

| Attribute | Detail |
|-----------|--------|
| **Service** | `reportService.generate(payload)` |
| **On success** | Navigate to report detail or show download |

### `useDownloadReport`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Trigger PDF download via blob |
| **Service** | `reportService.download(reportId)` |

### `useReportList`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['reports', filters, page]` |
| **Service** | `reportService.list(params)` |

---

## Analytics Hooks

### `useAnalyticsQuery`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Generic hook parameterized by metric endpoint |
| **Params** | `metric: 'scan-volume' \| 'verification-failures' \| ...`, `dateRange`, `groupBy` |
| **Query key** | `['analytics', metric, params]` |
| **Enabled** | Only when `canAccess('analytics')` |

---

## History Hooks

### `useAuditLogs`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['history', 'audit', filters, page]` |
| **Service** | `historyService.getAuditLogs(params)` |

### `useScanHistory`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['history', 'scans', filters, page]` |
| **Service** | `historyService.getScanHistory(params)` |

### `useScanTimeline`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['history', 'scans', scanId, 'timeline']` |
| **Service** | `historyService.getScanTimeline(scanId)` |

### `usePlateSightings`

| Attribute | Detail |
|-----------|--------|
| **Query key** | `['history', 'plate', plate, params]` |
| **Service** | `historyService.getPlateSightings(plate, params)` |

---

## Common Hooks

### `useDebounce`

Debounce search inputs (plate lookup, filters). Default 300ms.

### `usePagination`

Sync page/pageSize with URL search params.

### `useMediaQuery`

Responsive breakpoints; toggle sidebar/mobile nav.

---

## Hook → Service → API Map

| Hook | Service Method | API Endpoint |
|------|----------------|--------------|
| `useCreateScan` | `scanService.createScan` | `POST /v1/scans` |
| `useScanDetail` | `scanService.getScan` | `GET /v1/scans/{id}` |
| `useDashboardSummary` | `dashboardService.getSummary` | `GET /v1/dashboard/summary` |
| `useVehicleLookup` | `vehicleService.lookup` | `GET /v1/vehicles/lookup` |
| `useVerifyPlate` | `verificationService.verify` | `POST /v1/verification` |
| `useGenerateReport` | `reportService.generate` | `POST /v1/reports` |
| `useAnalyticsQuery` | `analyticsService.query` | `GET /v1/analytics/*` |
| `useAuditLogs` | `historyService.getAuditLogs` | `GET /v1/history/audit` |

---

## Related

- [Services](services.md)
- [State Management](state-management.md)
