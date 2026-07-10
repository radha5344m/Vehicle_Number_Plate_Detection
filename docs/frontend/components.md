# Components

Three-tier component architecture: **UI primitives**, **shared**, and **feature** components.

---

## Tier Model

```
pages/
  └── layouts/
        └── components/features/     ← domain UI, uses hooks via props/callbacks
              └── components/shared/  ← reusable composites
                    └── components/ui/ ← stateless primitives
```

---

## UI Primitives (`components/ui/`)

Stateless, style-only building blocks. No API awareness. Styled with Tailwind + variant props.

| Component | Responsibility | Props (conceptual) |
|-----------|----------------|-------------------|
| `Button` | Clickable action | `variant`, `size`, `loading`, `disabled` |
| `Input` | Text input | `label`, `error`, `type` |
| `Select` | Dropdown | `options`, `value`, `onChange` |
| `Modal` | Overlay dialog | `open`, `onClose`, `title` |
| `Card` | Content container | `title`, `padding` |
| `Badge` | Status chip | `variant`, `children` |
| `Table` | Data table shell | `columns`, `data`, `loading` |
| `Spinner` | Loading indicator | `size` |
| `Alert` | Inline message | `variant`, `message` |
| `Toast` | Transient notification | Via toast provider |

**Rule:** UI components accept data via props only. No hooks except `useId`, `useRef` for a11y.

---

## Shared Components (`components/shared/`)

Cross-feature composites used on multiple pages.

| Component | Responsibility | Used On |
|-----------|----------------|---------|
| `PageHeader` | Title, breadcrumbs, action slot | All pages |
| `EmptyState` | No data illustration + CTA | Lists, search |
| `ErrorState` | Error message + retry button | Failed queries |
| `LoadingOverlay` | Full-section spinner | Scan processing |
| `Pagination` | Page controls | All list pages |
| `DateRangePicker` | From/to date selection | Analytics, history |
| `PlateDisplay` | Formatted plate with jurisdiction | Scan, vehicle, alerts |
| `RiskScoreBadge` | Color-coded risk score 0–1 | Scan result, alerts |
| `DecisionBadge` | Decision enum with color | Scan result, dashboard |
| `OfficerAvatar` | Officer initials + rank | Scan detail, reports |
| `ProtectedRoute` | Auth + role guard wrapper | Router |

### PlateDisplay

| Responsibility | Format plate string; show jurisdiction badge; monospace font |
|----------------|--------------------------------------------------------------|

### RiskScoreBadge

| Responsibility | Map score to color: green < 0.3, yellow 0.3–0.7, red > 0.7 |
|----------------|---------------------------------------------------------------|

### DecisionBadge

| Responsibility | `clear`=green, `monitor`=blue, `investigate`=orange, `detain`/`escalate`=red |
|----------------|-------------------------------------------------------------------------------|

---

## Feature Components (`components/features/`)

Domain-specific UI. Receive data and callbacks from page/hook layer.

### auth/

| Component | Responsibility |
|-----------|----------------|
| `LoginForm` | Badge + password fields; submit handler; validation errors |

### scan/

| Component | Responsibility |
|-----------|----------------|
| `ImageCapture` | Camera access, file drop zone, image preview |
| `ScanProgress` | Pipeline stage stepper (detecting → OCR → verify → risk → decision) |
| `ScanResultCard` | Plate, confidence, verification, risk, decision summary |
| `ScanTimeline` | Stage-by-stage timeline from history API |

**ScanProgress stages:** Maps to backend `processing_status` + timeline events.

### dashboard/

| Component | Responsibility |
|-----------|----------------|
| `SummaryCards` | Grid of KPI cards (scans, failures, clones, alerts) |
| `RecentFlagsList` | Scrollable flagged scan list |
| `AlertsQueue` | Compact open alerts with acknowledge action |

### vehicles/

| Component | Responsibility |
|-----------|----------------|
| `VehicleSearchForm` | Plate input, jurisdiction, force refresh |
| `VehicleInfoCard` | Make, model, color, status, owner (masked) |

### verification/

| Component | Responsibility |
|-----------|----------------|
| `VerifyPlateForm` | Plate + optional observed attributes |
| `MismatchReasonsList` | Table of mismatch codes with severity |

### alerts/

| Component | Responsibility |
|-----------|----------------|
| `AlertCard` | Alert summary, severity, status, actions |
| `AcknowledgeAlertModal` | Notes input, confirm acknowledge |

### reports/

| Component | Responsibility |
|-----------|----------------|
| `GenerateReportModal` | Scan ID, report type, include images |
| `ReportListTable` | Sortable report list with download action |

### analytics/

| Component | Responsibility |
|-----------|----------------|
| `ScanVolumeChart` | Line/bar chart — scan volume time series |
| `FailureRateChart` | Line chart with rate overlay |
| `RiskDistributionChart` | Histogram of risk scores |

### history/

| Component | Responsibility |
|-----------|----------------|
| `AuditLogTable` | Filterable audit log with entity links |
| `ScanHistoryTable` | Scan list with plate, decision, date |

---

## Component Responsibility Rules

| Rule | Detail |
|------|--------|
| **Single responsibility** | One visual concern per component |
| **Props down, events up** | No direct service imports in feature components |
| **Composition over inheritance** | Build pages from small components |
| **Colocation** | Feature component folder contains sub-components if private |
| **No business logic** | Validation in hooks/utils; display logic only in components |

### Folder Pattern

```
components/features/scan/ScanResultCard/
├── ScanResultCard.tsx      # Main component
├── ScanResultCard.types.ts # Props interface
└── index.ts                # Barrel export
```

---

## Tailwind Strategy

| Concern | Approach |
|---------|----------|
| Design tokens | `tailwind.config.ts` — colors, spacing, fonts |
| Component variants | `class-variance-authority` (_TBD_) or manual `cn()` utility |
| Dark mode | `class` strategy on `html`; police field use may prefer light-only |
| Responsive | Mobile-first; scan page optimized for tablet/field use |

---

## Related

- [Hooks](hooks.md)
- [Pages](pages.md)
