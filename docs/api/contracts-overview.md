# REST API Specification — SentinelANPR AI

**Version:** v1  
**Status:** Specification only — not implemented

---

## Documents

| Resource | Specification |
|----------|---------------|
| Shared conventions | [conventions.md](conventions.md) |
| Authentication | [authentication.md](authentication.md) |
| Vehicle Scan | [vehicle-scan.md](vehicle-scan.md) |
| Vehicle Lookup | [vehicle-lookup.md](vehicle-lookup.md) |
| Verification | [verification.md](verification.md) |
| Dashboard | [dashboard.md](dashboard.md) |
| Reports | [reports.md](reports.md) |
| Analytics | [analytics.md](analytics.md) |
| History | [history.md](history.md) |
| Async events | [events-skeleton.md](events-skeleton.md) |

---

## Endpoint Index

### Authentication — `/v1/auth`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/v1/auth/login` | Public | Officer login |
| POST | `/v1/auth/refresh` | Public | Refresh access token |
| POST | `/v1/auth/logout` | Bearer | End session |
| GET | `/v1/auth/me` | Bearer | Current officer profile |
| POST | `/v1/auth/api-keys` | Admin | Create API key |

### Vehicle Scan — `/v1/scans`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/v1/scans` | Officer+ | Submit image, run pipeline |
| GET | `/v1/scans/{scan_id}` | Officer+ | Get scan result |
| GET | `/v1/scans` | Officer+ | List scans |
| POST | `/v1/scans/{scan_id}/retry` | Officer+ | Retry failed scan |

### Vehicle Lookup — `/v1/vehicles`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/v1/vehicles/lookup` | Officer+ | Lookup by plate |
| GET | `/v1/vehicles/{vehicle_id}` | Officer+ | Get vehicle by ID |
| GET | `/v1/vehicles` | Supervisor+ | Search vehicles |

### Verification — `/v1/verification`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/v1/verification` | Officer+ | Verify plate |
| GET | `/v1/verification/{verification_id}` | Officer+ | Get verification |
| GET | `/v1/verification/by-scan/{scan_id}` | Officer+ | Verification by scan |
| GET | `/v1/verification` | Supervisor+ | List verifications |

### Dashboard — `/v1/dashboard`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/v1/dashboard/summary` | Officer+ | Operational counters |
| GET | `/v1/dashboard/recent-flags` | Officer+ | Recent flagged scans |
| GET | `/v1/dashboard/alerts` | Officer+ | Open alert queue |
| PATCH | `/v1/dashboard/alerts/{alert_id}/acknowledge` | Officer+ | Acknowledge alert |

### Reports — `/v1/reports`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/v1/reports` | Officer+ | Generate report |
| GET | `/v1/reports/{report_id}` | Officer+ | Report metadata |
| GET | `/v1/reports/{report_id}/download` | Officer+ | Download PDF |
| GET | `/v1/reports` | Officer+ | List reports |
| PATCH | `/v1/reports/{report_id}/archive` | Supervisor+ | Archive report |

### Analytics — `/v1/analytics`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/v1/analytics/scan-volume` | Supervisor+ | Scan volume time series |
| GET | `/v1/analytics/verification-failures` | Supervisor+ | Failure rate time series |
| GET | `/v1/analytics/clone-detection-rate` | Supervisor+ | Clone rate time series |
| GET | `/v1/analytics/risk-distribution` | Supervisor+ | Risk score histogram |
| GET | `/v1/analytics/decision-breakdown` | Supervisor+ | Decision distribution |

### History — `/v1/history`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/v1/history/audit` | Supervisor+ | Query audit logs |
| GET | `/v1/history/audit/{audit_id}` | Supervisor+ | Single audit entry |
| GET | `/v1/history/scans` | Officer+ | Scan timeline |
| GET | `/v1/history/scans/{scan_id}/timeline` | Officer+ | Scan stage timeline |
| GET | `/v1/history/plate/{plate}/sightings` | Officer+ | Plate sighting history |

### Health

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/v1/health` | Public | Liveness/readiness |

---

## Role Legend

| Symbol | Roles |
|--------|-------|
| Public | No authentication |
| Bearer | Any authenticated user |
| Officer+ | `officer`, `supervisor`, `admin` |
| Supervisor+ | `supervisor`, `admin` |
| Admin | `admin` only |

---

## Schema Location

Request/response DTOs map to interface schemas:

```
interfaces/schemas/
├── requests/
│   ├── auth/
│   ├── ingestion/        ← scans
│   ├── recognition/
│   ├── verification/
│   ├── reporting/
│   └── dashboard/
└── responses/
    ├── auth/
    ├── common/
    ├── verification/
    ├── reporting/
    └── dashboard/
```

---

## Related

- [AI Pipeline](../ai-pipeline/README.md)
- [Database Schema](../database/schema-design.md)
- [Module Architecture](../architecture/modules.md)
