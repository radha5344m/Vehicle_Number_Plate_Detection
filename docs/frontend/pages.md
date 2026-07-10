# Pages

Route-level page components. Each page is a **thin orchestrator** — composes layout sections and feature components; delegates logic to hooks.

---

## Page Catalog

| Page | Route | Layout | Roles | API Services |
|------|-------|--------|-------|--------------|
| LoginPage | `/login` | AuthLayout | Public | authService |
| DashboardPage | `/` | AppLayout | Officer+ | dashboardService |
| ScanPage | `/scan` | AppLayout | Officer+ | scanService |
| ScanDetailPage | `/scans/:scanId` | AppLayout | Officer+ | scanService, historyService |
| ScanListPage | `/scans` | AppLayout | Officer+ | scanService |
| VehicleLookupPage | `/vehicles/lookup` | AppLayout | Officer+ | vehicleService |
| VehicleDetailPage | `/vehicles/:vehicleId` | AppLayout | Officer+ | vehicleService |
| VerificationPage | `/verification` | AppLayout | Officer+ | verificationService |
| AlertsPage | `/alerts` | AppLayout | Officer+ | dashboardService, alertService |
| ReportsPage | `/reports` | AppLayout | Officer+ | reportService |
| ReportDetailPage | `/reports/:reportId` | AppLayout | Officer+ | reportService |
| AnalyticsPage | `/analytics` | AppLayout | Supervisor+ | analyticsService |
| ScanHistoryPage | `/history/scans` | AppLayout | Officer+ | historyService |
| AuditLogPage | `/history/audit` | AppLayout | Supervisor+ | historyService |
| PlateSightingsPage | `/history/plate/:plate` | AppLayout | Officer+ | historyService |
| NotFoundPage | `*` | RootLayout | Public | — |
| ForbiddenPage | `/forbidden` | RootLayout | Public | — |

---

## Page Responsibilities

### LoginPage

| Responsibility | Detail |
|----------------|--------|
| Render | `LoginForm` centered in `AuthLayout` |
| On success | Redirect to `/` (dashboard) |
| On failure | Display API error via toast |
| State | Delegates to `useAuth` hook |

### DashboardPage

| Responsibility | Detail |
|----------------|--------|
| Render | `SummaryCards`, `RecentFlagsList`, `AlertsQueue` |
| Data | `useDashboardSummary`, `useRecentFlags` |
| Scope | Officer sees own station; supervisor selects station |
| Refresh | Auto-refresh every 30s (_configurable_) |

### ScanPage

| Responsibility | Detail |
|----------------|--------|
| Render | `ImageCapture`, `ScanProgress`, `ScanResultCard` |
| Flow | Upload image → POST `/v1/scans` → show result or poll async |
| State | `useCreateScan`, `useScanPolling` (async mode) |
| UX | Camera capture + file upload; location auto-fill if available |

### ScanDetailPage

| Responsibility | Detail |
|----------------|--------|
| Render | Full scan result, `ScanTimeline`, linked alerts/reports |
| Data | `useScanDetail`, scan timeline from history API |
| Actions | Retry (if failed), generate report, acknowledge alert |

### ScanListPage

| Responsibility | Detail |
|----------------|--------|
| Render | Filterable scan table with `Pagination` |
| Filters | Plate, decision, date range, status |
| Data | TanStack Query list with `usePagination` |

### VehicleLookupPage

| Responsibility | Detail |
|----------------|--------|
| Render | `VehicleSearchForm`, `VehicleInfoCard` |
| Data | `useVehicleLookup` → GET `/v1/vehicles/lookup` |
| UX | Plate input with format hint; force refresh toggle |

### VehicleDetailPage

| Responsibility | Detail |
|----------------|--------|
| Render | Vehicle record, scan history link, active alerts |
| Data | GET `/v1/vehicles/{id}` |

### VerificationPage

| Responsibility | Detail |
|----------------|--------|
| Render | `VerifyPlateForm`, `MismatchReasonsList` |
| Modes | Standalone verify OR linked to scan_id query param |
| Data | `useVerifyPlate` → POST `/v1/verification` |

### AlertsPage

| Responsibility | Detail |
|----------------|--------|
| Render | Alert queue table, `AcknowledgeAlertModal` |
| Filters | Status, severity, station |
| Actions | Acknowledge, navigate to scan detail |

### ReportsPage

| Responsibility | Detail |
|----------------|--------|
| Render | `ReportListTable`, `GenerateReportModal` trigger |
| Data | GET `/v1/reports` with filters |
| Actions | Download PDF, view detail |

### ReportDetailPage

| Responsibility | Detail |
|----------------|--------|
| Render | Report metadata, download button, linked scan summary |
| Actions | Download, archive (supervisor+) |

### AnalyticsPage

| Responsibility | Detail |
|----------------|--------|
| Render | Date range picker, chart grid |
| Charts | `ScanVolumeChart`, `FailureRateChart`, `RiskDistributionChart`, decision breakdown |
| Data | `useAnalyticsQuery` per chart |
| Access | Supervisor+ only — `RoleGuard` |

### ScanHistoryPage

| Responsibility | Detail |
|----------------|--------|
| Render | `ScanHistoryTable` with filters |
| Data | GET `/v1/history/scans` |

### AuditLogPage

| Responsibility | Detail |
|----------------|--------|
| Render | `AuditLogTable` with entity/event filters |
| Data | GET `/v1/history/audit` |
| Access | Supervisor+ only |

### PlateSightingsPage

| Responsibility | Detail |
|----------------|--------|
| Render | Sighting timeline for a plate (clone investigation) |
| Data | GET `/v1/history/plate/{plate}/sightings` |
| Entry | Linked from scan detail or manual plate search |

---

## Page Anti-Patterns

- Pages must **not** import `services/` directly — use hooks
- Pages must **not** contain Tailwind-heavy markup — extract to components
- Pages must **not** manage auth tokens — `authStore` + interceptors handle this

---

## Related

- [Routing](routing.md)
- [Layouts](layouts.md)
