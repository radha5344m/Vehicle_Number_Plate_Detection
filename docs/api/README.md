# API Documentation

REST API contract specifications for SentinelANPR AI.

**Status:** Specification only — no server implementation.

---

## Start Here

1. [conventions.md](conventions.md) — Auth, envelopes, errors, pagination
2. [contracts-overview.md](contracts-overview.md) — Full endpoint index

---

## Resource Specifications

| Area | Document | Base Path |
|------|----------|-----------|
| Authentication | [authentication.md](authentication.md) | `/v1/auth` |
| Vehicle Scan | [vehicle-scan.md](vehicle-scan.md) | `/v1/scans` |
| Vehicle Lookup | [vehicle-lookup.md](vehicle-lookup.md) | `/v1/vehicles` |
| Verification | [verification.md](verification.md) | `/v1/verification` |
| Dashboard | [dashboard.md](dashboard.md) | `/v1/dashboard` |
| Reports | [reports.md](reports.md) | `/v1/reports` |
| Analytics | [analytics.md](analytics.md) | `/v1/analytics` |
| History | [history.md](history.md) | `/v1/history` |

---

## Interface Layer Mapping

| API Area | Route Handler Location |
|----------|------------------------|
| Auth | `interfaces/rest_api/v1/routes/auth/` |
| Scans | `interfaces/rest_api/v1/routes/plates/` |
| Vehicles | `interfaces/rest_api/v1/routes/verification/` |
| Verification | `interfaces/rest_api/v1/routes/verification/` |
| Dashboard | `interfaces/rest_api/v1/routes/dashboard/` |
| Reports | `interfaces/rest_api/v1/routes/reports/` |
| Analytics | `interfaces/rest_api/v1/routes/analytics/` |
| History | `interfaces/rest_api/v1/routes/sightings/` |

---

## Legacy

- [rest-api-skeleton.md](rest-api-skeleton.md) — Superseded by resource-specific specs above
