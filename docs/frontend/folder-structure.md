# Frontend Folder Structure

Root: `frontend/`

```
frontend/
├── public/
│   ├── favicon.ico
│   └── manifest.json
│
├── src/
│   ├── main.tsx                    # App entry (bootstrap only)
│   ├── vite-env.d.ts
│   │
│   ├── app/                        # Application shell
│   │   ├── App.tsx                 # Root component
│   │   ├── providers/              # Context/query/store providers
│   │   │   ├── AppProviders.tsx
│   │   │   ├── QueryProvider.tsx
│   │   │   └── ThemeProvider.tsx
│   │   └── router/
│   │       ├── AppRouter.tsx
│   │       └── routeConfig.ts
│   │
│   ├── pages/                      # Route-level pages (thin orchestrators)
│   │   ├── auth/
│   │   │   └── LoginPage.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── scan/
│   │   │   ├── ScanPage.tsx
│   │   │   ├── ScanDetailPage.tsx
│   │   │   └── ScanListPage.tsx
│   │   ├── vehicles/
│   │   │   ├── VehicleLookupPage.tsx
│   │   │   └── VehicleDetailPage.tsx
│   │   ├── verification/
│   │   │   └── VerificationPage.tsx
│   │   ├── alerts/
│   │   │   └── AlertsPage.tsx
│   │   ├── reports/
│   │   │   ├── ReportsPage.tsx
│   │   │   └── ReportDetailPage.tsx
│   │   ├── analytics/
│   │   │   └── AnalyticsPage.tsx
│   │   ├── history/
│   │   │   ├── ScanHistoryPage.tsx
│   │   │   ├── AuditLogPage.tsx
│   │   │   └── PlateSightingsPage.tsx
│   │   └── errors/
│   │       ├── NotFoundPage.tsx
│   │       └── ForbiddenPage.tsx
│   │
│   ├── layouts/                    # Structural wrappers
│   │   ├── RootLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   ├── AppLayout.tsx
│   │   ├── DashboardLayout.tsx
│   │   └── components/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── MobileNav.tsx
│   │       └── Footer.tsx
│   │
│   ├── components/
│   │   ├── ui/                     # Design system primitives
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Modal/
│   │   │   ├── Card/
│   │   │   ├── Badge/
│   │   │   ├── Table/
│   │   │   ├── Spinner/
│   │   │   ├── Alert/
│   │   │   └── Toast/
│   │   │
│   │   ├── shared/                 # Cross-feature components
│   │   │   ├── PageHeader/
│   │   │   ├── EmptyState/
│   │   │   ├── ErrorState/
│   │   │   ├── LoadingOverlay/
│   │   │   ├── Pagination/
│   │   │   ├── DateRangePicker/
│   │   │   ├── PlateDisplay/
│   │   │   ├── RiskScoreBadge/
│   │   │   ├── DecisionBadge/
│   │   │   ├── OfficerAvatar/
│   │   │   └── ProtectedRoute/
│   │   │
│   │   └── features/               # Feature-specific components
│   │       ├── auth/
│   │       │   └── LoginForm/
│   │       ├── scan/
│   │       │   ├── ImageCapture/
│   │       │   ├── ScanProgress/
│   │       │   ├── ScanResultCard/
│   │       │   └── ScanTimeline/
│   │       ├── dashboard/
│   │       │   ├── SummaryCards/
│   │       │   ├── RecentFlagsList/
│   │       │   └── AlertsQueue/
│   │       ├── vehicles/
│   │       │   ├── VehicleSearchForm/
│   │       │   └── VehicleInfoCard/
│   │       ├── verification/
│   │       │   ├── VerifyPlateForm/
│   │       │   └── MismatchReasonsList/
│   │       ├── alerts/
│   │       │   ├── AlertCard/
│   │       │   └── AcknowledgeAlertModal/
│   │       ├── reports/
│   │       │   ├── GenerateReportModal/
│   │       │   └── ReportListTable/
│   │       ├── analytics/
│   │       │   ├── ScanVolumeChart/
│   │       │   ├── FailureRateChart/
│   │       │   └── RiskDistributionChart/
│   │       └── history/
│   │           ├── AuditLogTable/
│   │           └── ScanHistoryTable/
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── auth/
│   │   │   ├── useAuth.ts
│   │   │   └── usePermissions.ts
│   │   ├── scan/
│   │   │   ├── useCreateScan.ts
│   │   │   ├── useScanDetail.ts
│   │   │   └── useScanPolling.ts
│   │   ├── dashboard/
│   │   │   ├── useDashboardSummary.ts
│   │   │   └── useRecentFlags.ts
│   │   ├── vehicles/
│   │   │   └── useVehicleLookup.ts
│   │   ├── verification/
│   │   │   └── useVerifyPlate.ts
│   │   ├── alerts/
│   │   │   └── useAcknowledgeAlert.ts
│   │   ├── reports/
│   │   │   ├── useGenerateReport.ts
│   │   │   └── useDownloadReport.ts
│   │   ├── analytics/
│   │   │   └── useAnalyticsQuery.ts
│   │   ├── history/
│   │   │   └── useAuditLogs.ts
│   │   └── common/
│   │       ├── useDebounce.ts
│   │       ├── usePagination.ts
│   │       └── useMediaQuery.ts
│   │
│   ├── services/                   # API communication layer
│   │   ├── api/
│   │   │   ├── httpClient.ts       # Axios/fetch + interceptors
│   │   │   ├── authInterceptor.ts
│   │   │   └── errorMapper.ts
│   │   ├── authService.ts
│   │   ├── scanService.ts
│   │   ├── vehicleService.ts
│   │   ├── verificationService.ts
│   │   ├── dashboardService.ts
│   │   ├── alertService.ts
│   │   ├── reportService.ts
│   │   ├── analyticsService.ts
│   │   └── historyService.ts
│   │
│   ├── stores/                     # Client-side global state
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── index.ts
│   │
│   ├── types/                      # TypeScript definitions
│   │   ├── api/                    # Mirror backend DTOs
│   │   │   ├── auth.ts
│   │   │   ├── scan.ts
│   │   │   ├── vehicle.ts
│   │   │   ├── verification.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── alert.ts
│   │   │   ├── report.ts
│   │   │   ├── analytics.ts
│   │   │   ├── history.ts
│   │   │   └── common.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   │
│   ├── routes/                     # Route path constants + guards
│   │   ├── paths.ts
│   │   ├── guards/
│   │   │   ├── AuthGuard.tsx
│   │   │   ├── RoleGuard.tsx
│   │   │   └── GuestGuard.tsx
│   │   └── index.ts
│   │
│   ├── config/
│   │   ├── env.ts
│   │   └── constants.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── plateUtils.ts
│   │
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   │
│   └── styles/
│       ├── globals.css
│       └── tailwind.css
│
├── index.html
├── package.json                    # (not created — no deps in foundation)
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
└── vite.config.ts
```

---

## Layer Responsibilities

| Layer | Responsibility | Must NOT |
|-------|----------------|----------|
| `pages/` | Route entry; compose layouts + features | Contain API calls or business logic |
| `layouts/` | Shell, navigation, outlet rendering | Fetch data |
| `components/features/` | Feature UI with props/callbacks | Import services directly |
| `components/ui/` | Stateless primitives | Know about API or routes |
| `hooks/` | Bind services to components; loading/error state | Render JSX |
| `services/` | HTTP calls; map API responses to types | Hold React state |
| `stores/` | Client-global state (auth, UI) | Duplicate server cache |
| `types/` | Type definitions | Contain runtime logic |

---

## Naming Conventions

| Artifact | Convention | Example |
|----------|------------|---------|
| Page | `*Page.tsx` | `DashboardPage.tsx` |
| Layout | `*Layout.tsx` | `AppLayout.tsx` |
| Feature component | PascalCase folder | `ScanResultCard/` |
| Hook | `use*` | `useScanDetail.ts` |
| Service | `*Service.ts` | `scanService.ts` |
| Store | `*Store.ts` | `authStore.ts` |
| Type file | Domain name | `scan.ts` |

---

## Related

- [Pages](pages.md)
- [Components](components.md)
