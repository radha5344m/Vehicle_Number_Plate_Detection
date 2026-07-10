# Layouts

Structural wrappers that define page chrome, navigation, and authentication boundaries.

---

## Layout Hierarchy

```
RootLayout
├── AuthLayout          (login, public errors)
└── AppLayout           (authenticated app shell)
    ├── Header
    ├── Sidebar / MobileNav
    ├── <Outlet />      (page content)
    └── Footer
```

---

## Layout Components

### RootLayout

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Outermost wrapper; error boundary, global toast container |
| **Children** | Router outlet |
| **Responsibilities** | Global `ErrorBoundary`; toast/notification portal; no nav |
| **Used by** | All routes as ancestor |

### AuthLayout

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Centered, minimal chrome for unauthenticated pages |
| **Children** | Login form, error pages |
| **Responsibilities** | Brand logo, background, no sidebar |
| **Routes** | `/login`, `/forbidden` |

### AppLayout

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Primary authenticated shell with navigation |
| **Children** | All protected pages |
| **Responsibilities** | Render `Header`, `Sidebar`, `MobileNav`; station context badge; officer profile menu; `<Outlet />` for pages |
| **Responsive** | Sidebar collapses to `MobileNav` below `md` breakpoint |

### DashboardLayout _(optional variant)_

| Attribute | Detail |
|-----------|--------|
| **Purpose** | AppLayout with full-width content area for charts |
| **Extends** | AppLayout with `max-w-full` content zone |
| **Routes** | `/`, `/analytics` |

---

## Layout Sub-Components (`layouts/components/`)

### Header

| Responsibility | Detail |
|----------------|--------|
| Display | App title, station name, notification bell (alert count) |
| Actions | Profile dropdown (logout, settings) |
| Data | `useAuth` for officer name; alert count from dashboard query |

### Sidebar

| Responsibility | Detail |
|----------------|--------|
| Display | Primary navigation links |
| Role filtering | Hide Analytics/Audit for officer role |
| Active state | Highlight current route |
| Links | Dashboard, Scan, Scans, Lookup, Verification, Alerts, Reports, Analytics*, History* |

### MobileNav

| Responsibility | Detail |
|----------------|--------|
| Display | Bottom tab bar or hamburger drawer on mobile |
| Parity | Same links as Sidebar |

### Footer

| Responsibility | Detail |
|----------------|--------|
| Display | Version, environment badge (dev/staging), copyright |

---

## Layout vs Page Boundary

| Concern | Layout | Page |
|---------|--------|------|
| Navigation | ✓ | — |
| Auth shell | ✓ | — |
| Page title / breadcrumbs | Partial (header) | ✓ (`PageHeader`) |
| Feature content | — | ✓ |
| Data fetching | Alert count only | ✓ (via hooks) |

---

## Related

- [Routing](routing.md)
- [Pages](pages.md)
