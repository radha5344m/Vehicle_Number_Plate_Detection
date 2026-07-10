# API Conventions

Shared rules for all SentinelANPR AI REST endpoints.

**Version:** v1  
**Base URL:** `/v1`  
**Status:** Specification only — not implemented

---

## Transport

| Attribute | Value |
|-----------|-------|
| Protocol | HTTPS (TLS 1.2+) |
| Content-Type | `application/json` (except file upload) |
| Upload Content-Type | `multipart/form-data` |
| Character encoding | UTF-8 |
| Date/time format | ISO-8601 UTC (`2026-07-06T10:30:00Z`) |

---

## Authentication

### Mechanism

Bearer JWT in `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Types

| Token | Lifetime | Use |
|-------|----------|-----|
| Access token | 15 minutes (_configurable_) | API requests |
| Refresh token | 7 days (_configurable_) | Token renewal only |

### Public Endpoints (No Auth)

| Endpoint | Reason |
|----------|--------|
| `POST /v1/auth/login` | Credential exchange |
| `POST /v1/auth/refresh` | Token renewal |
| `GET /v1/health` | Liveness probe |

All other endpoints require a valid access token.

### Roles

| Role | Code | Capabilities |
|------|------|--------------|
| Officer | `officer` | Scan, view own station data |
| Supervisor | `supervisor` | Station dashboard, reports, analytics |
| Admin | `admin` | All stations, configuration, full history |
| System | `system` | Service-to-service (API key) |

### Authorization Header Errors

| Status | Code | When |
|--------|------|------|
| 401 | `AUTH_MISSING` | No `Authorization` header |
| 401 | `AUTH_INVALID` | Malformed or expired token |
| 403 | `AUTH_FORBIDDEN` | Valid token, insufficient role |

---

## Response Envelope

### Success

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `data` | object \| array | Response payload |
| `meta` | object | `{ correlation_id, timestamp, request_id }` |

### Error

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` |
| `error` | object | `{ code, message, details[] }` |
| `meta` | object | `{ correlation_id, timestamp, request_id }` |

### Pagination (List Endpoints)

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Result items |
| `meta.pagination` | object | `{ page, page_size, total_items, total_pages }` |

Query params: `page` (default 1), `page_size` (default 20, max 100).

---

## Standard Error Codes

| HTTP | Code | Description |
|------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request failed validation |
| 401 | `AUTH_MISSING` | No credentials |
| 401 | `AUTH_INVALID` | Invalid/expired token |
| 403 | `AUTH_FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | State conflict (e.g. duplicate) |
| 422 | `UNPROCESSABLE` | Semantic/business rule violation |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Dependency down (registry, ML) |

### Validation Error Detail Shape

| Field | Type | Description |
|-------|------|-------------|
| `field` | string | Dot-notation field path |
| `code` | string | Machine-readable rule code |
| `message` | string | Human-readable message |

---

## Correlation

| Header | Required | Description |
|--------|----------|-------------|
| `X-Correlation-ID` | No | Client-supplied trace ID; server generates if absent |
| `X-Request-ID` | Response only | Server-assigned request ID |

Returned in `meta.correlation_id` on all responses.

---

## Idempotency

`POST` endpoints that create resources accept optional:

```
Idempotency-Key: <uuid>
```

Duplicate key within 24h returns original response with `200` instead of `201`.

Applicable to: `POST /v1/scans`, `POST /v1/reports`.

---

## Related

- Per-resource specs in this directory
- [Interfaces layer schemas](../../src/sentinel_anpr/interfaces/schemas/)
