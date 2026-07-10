# Phase 6 — Frontend

**Path:** `frontend/`  
**Rule:** Pages thin; hooks call services; no API in components.

Implement order: **tooling → types → services → stores → ui → shared → hooks → layouts → features → pages → router**.

---

## 6.0 Frontend Bootstrap

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `frontend/package.json` | Dependencies (React, Vite, Tailwind, Query, Zustand) | — | Install baseline |
| `frontend/tsconfig.json` | TypeScript config | — | Type checking |
| `frontend/vite.config.ts` | Vite + proxy to API | — | Dev server |
| `frontend/tailwind.config.ts` | Design tokens | — | Styling system |
| `frontend/postcss.config.js` | Tailwind pipeline | tailwind | CSS build |
| `frontend/index.html` | HTML shell | — | Vite entry |
| `frontend/src/main.tsx` | ReactDOM render | App | Entry point |
| `frontend/src/vite-env.d.ts` | Vite types | — | TS support |
| `frontend/src/styles/globals.css` | Base styles | tailwind | Global CSS |
| `frontend/src/styles/tailwind.css` | Tailwind directives | — | |
| `frontend/src/config/env.ts` | `VITE_API_BASE_URL` | — | Services need URL |
| `frontend/src/config/constants.ts` | App constants | — | Shared values |

---

## 6.1 Types (`types/api/`)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `types/api/common.ts` | Pagination, envelope, errors | `docs/api/conventions.md` | All services |
| `types/api/auth.ts` | Login, Me, OfficerSummary | API spec | authService |
| `types/api/scan.ts` | Scan request/response | API spec | scanService |
| `types/api/vehicle.ts` | VehicleLookup, VehicleRecord | API spec | vehicleService |
| `types/api/verification.ts` | Verification DTOs | API spec | verificationService |
| `types/api/dashboard.ts` | Summary, flags, alerts | API spec | dashboardService |
| `types/api/alert.ts` | Alert DTOs | API spec | alertService |
| `types/api/report.ts` | Report DTOs | API spec | reportService |
| `types/api/analytics.ts` | TimeSeries, distribution | API spec | analyticsService |
| `types/api/history.ts` | Audit, timeline, sightings | API spec | historyService |
| `types/enums.ts` | Decision, status enums | — | Shared UI |
| `types/index.ts` | Barrel export | all types | Imports |

---

## 6.2 Services

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `services/api/httpClient.ts` | Axios/fetch wrapper | env | All services |
| `services/api/authInterceptor.ts` | JWT attach + refresh | authStore | Authenticated calls |
| `services/api/errorMapper.ts` | API error → app error | common types | Hooks |
| `services/authService.ts` | /v1/auth/* | httpClient, types | Auth flow |
| `services/scanService.ts` | /v1/scans/* | httpClient, types | Core feature |
| `services/vehicleService.ts` | /v1/vehicles/* | httpClient, types | Lookup |
| `services/verificationService.ts` | /v1/verification/* | httpClient, types | Verify |
| `services/dashboardService.ts` | /v1/dashboard/* | httpClient, types | Dashboard |
| `services/alertService.ts` | Alert acknowledge | httpClient, types | Alerts |
| `services/reportService.ts` | /v1/reports/* | httpClient, types | Reports |
| `services/analyticsService.ts` | /v1/analytics/* | httpClient, types | Analytics |
| `services/historyService.ts` | /v1/history/* | httpClient, types | History |

---

## 6.3 Stores

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `stores/authStore.ts` | Tokens, officer, session | types/auth | Interceptor + guards |
| `stores/uiStore.ts` | Sidebar, station, theme | — | Layout state |
| `stores/index.ts` | Barrel export | stores | |

---

## 6.4 UI Primitives (`components/ui/`)

Each folder: `Component.tsx`, `Component.types.ts`, `index.ts`

| Component | Purpose | Depends On | Why This Stage |
|-----------|---------|------------|----------------|
| `Button/` | Actions, variants | tailwind | Every page |
| `Input/` | Text fields | tailwind | Forms |
| `Select/` | Dropdowns | tailwind | Filters |
| `Modal/` | Dialogs | tailwind | Acknowledge, generate report |
| `Card/` | Content panels | tailwind | Dashboard, results |
| `Badge/` | Status chips | tailwind | Decision, severity |
| `Table/` | Data tables | tailwind | Lists |
| `Spinner/` | Loading | tailwind | Async states |
| `Alert/` | Inline alerts | tailwind | Errors |
| `Toast/` | Notifications | tailwind | Login errors, success |

---

## 6.5 Shared Components

| Component | Purpose | Depends On | Why This Stage |
|-----------|---------|------------|----------------|
| `PageHeader/` | Title, breadcrumbs, actions | ui/Button | All pages |
| `EmptyState/` | No data UX | ui/Button | Lists |
| `ErrorState/` | Error + retry | ui/Button | Failed queries |
| `LoadingOverlay/` | Full-page load | ui/Spinner | Scan processing |
| `Pagination/` | Page controls | ui/Button | Lists |
| `DateRangePicker/` | Analytics filters | ui/Input | Analytics, history |
| `PlateDisplay/` | Formatted plate | types | Scan, vehicle |
| `RiskScoreBadge/` | Color-coded score | ui/Badge, enums | Scan, alerts |
| `DecisionBadge/` | Decision colors | ui/Badge, enums | Scan, dashboard |
| `OfficerAvatar/` | Officer display | types/auth | Header, detail |
| `ProtectedRoute/` | Auth wrapper | authStore, routes | Router |

---

## 6.6 Feature Components

| Component | Purpose | Depends On | Why This Stage |
|-----------|---------|------------|----------------|
| `auth/LoginForm/` | Login UI | ui/Input, Button | LoginPage |
| `scan/ImageCapture/` | Camera + upload | ui/Button | ScanPage |
| `scan/ScanProgress/` | Pipeline stepper | ui/Spinner | ScanPage |
| `scan/ScanResultCard/` | Full result display | PlateDisplay, badges | ScanPage, detail |
| `scan/ScanTimeline/` | Stage timeline | types/history | ScanDetailPage |
| `dashboard/SummaryCards/` | KPI grid | ui/Card | DashboardPage |
| `dashboard/RecentFlagsList/` | Flagged list | ui/Table | DashboardPage |
| `dashboard/AlertsQueue/` | Open alerts | AlertCard | DashboardPage |
| `vehicles/VehicleSearchForm/` | Plate search | ui/Input | LookupPage |
| `vehicles/VehicleInfoCard/` | Vehicle details | ui/Card | Lookup, detail |
| `verification/VerifyPlateForm/` | Verify form | ui/Input | VerificationPage |
| `verification/MismatchReasonsList/` | Mismatch table | ui/Table | VerificationPage |
| `alerts/AlertCard/` | Alert row/card | DecisionBadge | AlertsPage |
| `alerts/AcknowledgeAlertModal/` | Ack modal | ui/Modal | AlertsPage |
| `reports/GenerateReportModal/` | Generate dialog | ui/Modal | ReportsPage |
| `reports/ReportListTable/` | Report list | ui/Table | ReportsPage |
| `analytics/ScanVolumeChart/` | Volume chart | recharts | AnalyticsPage |
| `analytics/FailureRateChart/` | Failure chart | recharts | AnalyticsPage |
| `analytics/RiskDistributionChart/` | Histogram | recharts | AnalyticsPage |
| `history/AuditLogTable/` | Audit table | ui/Table | AuditLogPage |
| `history/ScanHistoryTable/` | Scan history | ui/Table | ScanHistoryPage |

---

## 6.7 Hooks

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `hooks/auth/useAuth.ts` | Login, logout | authService, authStore | Auth flow |
| `hooks/auth/usePermissions.ts` | Role checks | authStore | RoleGuard, nav |
| `hooks/scan/useCreateScan.ts` | Submit scan | scanService, Query | ScanPage |
| `hooks/scan/useScanDetail.ts` | Get scan | scanService, Query | Detail page |
| `hooks/scan/useScanPolling.ts` | Poll async scan | scanService, Query | Async mode |
| `hooks/scan/useScanList.ts` | List scans | scanService, Query | ScanListPage |
| `hooks/dashboard/useDashboardSummary.ts` | Summary | dashboardService | Dashboard |
| `hooks/dashboard/useRecentFlags.ts` | Flags | dashboardService | Dashboard |
| `hooks/vehicles/useVehicleLookup.ts` | Lookup | vehicleService | Lookup page |
| `hooks/vehicles/useVehicleDetail.ts` | Detail | vehicleService | Vehicle detail |
| `hooks/verification/useVerifyPlate.ts` | Verify | verificationService | Verify page |
| `hooks/alerts/useAcknowledgeAlert.ts` | Acknowledge | alertService | Alerts |
| `hooks/reports/useGenerateReport.ts` | Generate | reportService | Reports |
| `hooks/reports/useDownloadReport.ts` | PDF download | reportService | Report detail |
| `hooks/reports/useReportList.ts` | List reports | reportService | Reports |
| `hooks/analytics/useAnalyticsQuery.ts` | Chart data | analyticsService | Analytics |
| `hooks/history/useAuditLogs.ts` | Audit query | historyService | Audit page |
| `hooks/history/useScanHistory.ts` | Scan history | historyService | History page |
| `hooks/history/useScanTimeline.ts` | Timeline | historyService | Scan detail |
| `hooks/history/usePlateSightings.ts` | Plate sightings | historyService | Sightings page |
| `hooks/common/useDebounce.ts` | Debounce | — | Search inputs |
| `hooks/common/usePagination.ts` | URL pagination | react-router | Lists |
| `hooks/common/useMediaQuery.ts` | Responsive | — | Layout |

---

## 6.8 Layouts

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `layouts/RootLayout.tsx` | Error boundary, toast | ui/Toast | App root |
| `layouts/AuthLayout.tsx` | Login shell | — | LoginPage |
| `layouts/AppLayout.tsx` | Main shell + outlet | Header, Sidebar | Protected pages |
| `layouts/components/Header.tsx` | Top bar | OfficerAvatar, useAuth | Navigation |
| `layouts/components/Sidebar.tsx` | Nav links | usePermissions | Role-filtered nav |
| `layouts/components/MobileNav.tsx` | Mobile nav | useMediaQuery | Responsive |
| `layouts/components/Footer.tsx` | Footer | env | Version display |

---

## 6.9 Pages

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `pages/auth/LoginPage.tsx` | Login route | LoginForm, useAuth | First UI screen |
| `pages/dashboard/DashboardPage.tsx` | Home | SummaryCards, hooks | Landing after login |
| `pages/scan/ScanPage.tsx` | New scan | ImageCapture, ScanProgress | **MVP critical** |
| `pages/scan/ScanDetailPage.tsx` | Scan detail | ScanResultCard, Timeline | Result review |
| `pages/scan/ScanListPage.tsx` | Scan list | ScanHistoryTable | History browse |
| `pages/vehicles/VehicleLookupPage.tsx` | Lookup | VehicleSearchForm | Manual lookup |
| `pages/vehicles/VehicleDetailPage.tsx` | Vehicle detail | VehicleInfoCard | |
| `pages/verification/VerificationPage.tsx` | Verify plate | VerifyPlateForm | |
| `pages/alerts/AlertsPage.tsx` | Alert queue | AlertCard, modal | Triage |
| `pages/reports/ReportsPage.tsx` | Reports list | ReportListTable | |
| `pages/reports/ReportDetailPage.tsx` | Report detail | useDownloadReport | PDF |
| `pages/analytics/AnalyticsPage.tsx` | Charts | charts, RoleGuard | Supervisor |
| `pages/history/ScanHistoryPage.tsx` | Scan history | ScanHistoryTable | |
| `pages/history/AuditLogPage.tsx` | Audit log | AuditLogTable | Supervisor |
| `pages/history/PlateSightingsPage.tsx` | Plate timeline | usePlateSightings | Clone investigation |
| `pages/errors/NotFoundPage.tsx` | 404 | — | Router fallback |
| `pages/errors/ForbiddenPage.tsx` | 403 | — | Role guard |

---

## 6.10 Router & App

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `routes/paths.ts` | Path constants | — | Router, links |
| `routes/guards/AuthGuard.tsx` | Require auth | authStore | Protected routes |
| `routes/guards/GuestGuard.tsx` | Login only | authStore | Login route |
| `routes/guards/RoleGuard.tsx` | Role check | usePermissions | Analytics, audit |
| `app/providers/QueryProvider.tsx` | TanStack Query | — | Data fetching |
| `app/providers/ThemeProvider.tsx` | Theme context | uiStore | Optional dark mode |
| `app/providers/AppProviders.tsx` | Compose providers | Query, Theme | main.tsx |
| `app/router/routeConfig.ts` | Route definitions | pages, guards, layouts | |
| `app/router/AppRouter.tsx` | BrowserRouter | routeConfig | |
| `app/App.tsx` | Root component | AppRouter, providers | |

---

## Phase 6 Exit Gate

- [ ] Login → scan → view result works against staging API
- [ ] Supervisor can access analytics; officer cannot
- [ ] Lighthouse accessibility baseline met

**Next:** [07-testing.md](07-testing.md)
