# Services Layer

HTTP communication with the SentinelANPR REST API. **Single entry point** for all backend calls.

---

## Architecture

```
Component → Hook → Service → httpClient → REST API
                      ↑
                 authInterceptor (JWT attach + refresh)
                 errorMapper (API error → app error)
```

---

## HTTP Client (`services/api/httpClient.ts`)

| Responsibility | Detail |
|----------------|--------|
| Base URL | From `config/env.ts` — `VITE_API_BASE_URL` |
| Headers | `Content-Type: application/json`; `Authorization` via interceptor |
| Timeout | 30s default; 120s for scan upload |
| Response | Unwrap `{ success, data, meta }` envelope |
| Errors | Throw typed `ApiError` via `errorMapper` |

---

## Auth Interceptor (`services/api/authInterceptor.ts`)

| Event | Behavior |
|-------|----------|
| Request | Attach `Bearer {access_token}` from `authStore` |
| 401 response | Attempt token refresh via `POST /v1/auth/refresh` |
| Refresh success | Retry original request with new token |
| Refresh failure | Clear auth store; redirect to `/login` |
| Correlation | Forward `X-Correlation-ID` header if present |

---

## Error Mapper (`services/api/errorMapper.ts`)

| API Error | Mapped Type |
|-----------|-------------|
| `VALIDATION_ERROR` | `ValidationError` with `details[]` |
| `AUTH_INVALID` | `AuthError` → trigger logout |
| `NOT_FOUND` | `NotFoundError` |
| `SERVICE_UNAVAILABLE` | `ServiceUnavailableError` |
| 5xx | `InternalError` |

---

## Service Catalog

### authService

| Method | API | Returns |
|--------|-----|---------|
| `login(credentials)` | `POST /v1/auth/login` | `LoginResponse` |
| `refresh(token)` | `POST /v1/auth/refresh` | `RefreshTokenResponse` |
| `logout(token)` | `POST /v1/auth/logout` | `void` |
| `getMe()` | `GET /v1/auth/me` | `MeResponse` |

### scanService

| Method | API | Returns |
|--------|-----|---------|
| `createScan(formData)` | `POST /v1/scans` | `ScanResponse` |
| `getScan(scanId)` | `GET /v1/scans/{id}` | `ScanDetailResponse` |
| `listScans(params)` | `GET /v1/scans` | `ScanListResponse` |
| `retryScan(scanId)` | `POST /v1/scans/{id}/retry` | `ScanResponse` |

**Note:** `createScan` uses `multipart/form-data` for image upload.

### vehicleService

| Method | API | Returns |
|--------|-----|---------|
| `lookup(plate, params)` | `GET /v1/vehicles/lookup` | `VehicleLookupResponse` |
| `getVehicle(vehicleId)` | `GET /v1/vehicles/{id}` | `VehicleDetailResponse` |
| `listVehicles(params)` | `GET /v1/vehicles` | `VehicleListResponse` |

### verificationService

| Method | API | Returns |
|--------|-----|---------|
| `verify(payload)` | `POST /v1/verification` | `VerificationResponse` |
| `getVerification(id)` | `GET /v1/verification/{id}` | `VerificationResponse` |
| `getByScan(scanId)` | `GET /v1/verification/by-scan/{id}` | `VerificationResponse` |
| `list(params)` | `GET /v1/verification` | `VerificationListResponse` |

### dashboardService

| Method | API | Returns |
|--------|-----|---------|
| `getSummary(params)` | `GET /v1/dashboard/summary` | `DashboardSummaryResponse` |
| `getRecentFlags(params)` | `GET /v1/dashboard/recent-flags` | `RecentFlagsResponse` |
| `getAlerts(params)` | `GET /v1/dashboard/alerts` | `DashboardAlertsResponse` |

### alertService

| Method | API | Returns |
|--------|-----|---------|
| `acknowledge(alertId, notes)` | `PATCH /v1/dashboard/alerts/{id}/acknowledge` | `AlertDetailResponse` |

### reportService

| Method | API | Returns |
|--------|-----|---------|
| `generate(payload)` | `POST /v1/reports` | `ReportResponse` |
| `getReport(reportId)` | `GET /v1/reports/{id}` | `ReportDetailResponse` |
| `download(reportId)` | `GET /v1/reports/{id}/download` | `Blob` |
| `list(params)` | `GET /v1/reports` | `ReportListResponse` |
| `archive(reportId)` | `PATCH /v1/reports/{id}/archive` | `ReportResponse` |

### analyticsService

| Method | API | Returns |
|--------|-----|---------|
| `getScanVolume(params)` | `GET /v1/analytics/scan-volume` | `AnalyticsTimeSeriesResponse` |
| `getVerificationFailures(params)` | `GET /v1/analytics/verification-failures` | `AnalyticsTimeSeriesResponse` |
| `getCloneDetectionRate(params)` | `GET /v1/analytics/clone-detection-rate` | `AnalyticsTimeSeriesResponse` |
| `getRiskDistribution(params)` | `GET /v1/analytics/risk-distribution` | `RiskDistributionResponse` |
| `getDecisionBreakdown(params)` | `GET /v1/analytics/decision-breakdown` | `DecisionBreakdownResponse` |

### historyService

| Method | API | Returns |
|--------|-----|---------|
| `getAuditLogs(params)` | `GET /v1/history/audit` | `AuditLogListResponse` |
| `getAuditLog(auditId)` | `GET /v1/history/audit/{id}` | `AuditLogDetailResponse` |
| `getScanHistory(params)` | `GET /v1/history/scans` | `ScanHistoryResponse` |
| `getScanTimeline(scanId)` | `GET /v1/history/scans/{id}/timeline` | `ScanTimelineResponse` |
| `getPlateSightings(plate, params)` | `GET /v1/history/plate/{plate}/sightings` | `PlateSightingsResponse` |

---

## Service Rules

| Rule | Detail |
|------|--------|
| **No React imports** | Services are framework-agnostic |
| **Typed returns** | All methods return typed promises from `types/api/` |
| **No caching** | Caching is TanStack Query's job in hooks |
| **Single responsibility** | One service per API resource area |
| **Testability** | Services mockable; inject `httpClient` in tests |

---

## Type Alignment

Types in `src/types/api/` mirror backend DTOs documented in `docs/api/`. When API changes, update types first.

---

## Related

- [REST API Spec](../api/contracts-overview.md)
- [Hooks](hooks.md)
