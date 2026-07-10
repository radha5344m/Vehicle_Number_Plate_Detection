# Phase 5 — Interfaces Layer

**Path:** `src/sentinel_anpr/interfaces/` + `bootstrap/`  
**Rule:** Thin HTTP adapters + DI wiring. No business logic. No SQL.

---

## 5.1 Shared Schemas

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `interfaces/schemas/shared/pagination.py` | Page, page_size models | — | All list endpoints |
| `interfaces/schemas/shared/errors.py` | Error envelope models | — | API conventions |
| `interfaces/schemas/shared/envelope.py` | success/data/meta wrapper | — | All responses |
| `interfaces/schemas/requests/auth/login_request.py` | Login body | — | First endpoint |
| `interfaces/schemas/responses/auth/login_response.py` | Token response | auth_dto | |
| `interfaces/schemas/requests/auth/refresh_request.py` | Refresh body | — | |
| `interfaces/schemas/responses/auth/me_response.py` | Officer profile | auth_dto | |
| `interfaces/schemas/requests/ingestion/create_scan_request.py` | Multipart scan | scan_dto | Core API |
| `interfaces/schemas/responses/vehicle_scan/scan_response.py` | Scan result | scan_dto | |
| `interfaces/schemas/responses/vehicle_scan/scan_detail_response.py` | Full scan | scan_dto | |
| `interfaces/schemas/requests/vehicle_lookup/lookup_query.py` | Plate query params | — | |
| `interfaces/schemas/responses/vehicle_lookup/vehicle_response.py` | Vehicle record | vehicle_dto | |
| `interfaces/schemas/requests/verification/verify_plate_request.py` | Verify body | verification_dto | |
| `interfaces/schemas/responses/verification/verification_response.py` | Outcome | verification_dto | |
| `interfaces/schemas/responses/dashboard/summary_response.py` | Dashboard KPIs | dashboard_dto | |
| `interfaces/schemas/responses/dashboard/flags_response.py` | Flagged scans | dashboard_dto | |
| `interfaces/schemas/requests/reporting/generate_report_request.py` | Report body | report_dto | |
| `interfaces/schemas/responses/reporting/report_response.py` | Report metadata | report_dto | |
| `interfaces/schemas/requests/analytics/analytics_query.py` | Date range params | — | |
| `interfaces/schemas/responses/analytics/time_series_response.py` | Chart data | analytics_dto | |
| `interfaces/schemas/requests/history/audit_query.py` | Audit filters | — | |
| `interfaces/schemas/responses/history/audit_response.py` | Audit entries | history_dto | |
| `interfaces/schemas/responses/history/timeline_response.py` | Scan timeline | history_dto | |

---

## 5.2 Middleware & Dependencies

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `interfaces/rest_api/v1/middleware/correlation_id.py` | X-Correlation-ID | — | Tracing |
| `interfaces/rest_api/v1/middleware/auth_middleware.py` | JWT validation | jwt_validator | Protected routes |
| `interfaces/rest_api/v1/middleware/error_handler.py` | Map errors → HTTP | error_mapper | Global handler |
| `interfaces/rest_api/v1/middleware/logging_middleware.py` | Request logging | logging_port | Observability |
| `interfaces/rest_api/v1/dependencies/auth.py` | `get_current_officer` | auth middleware | Route DI |
| `interfaces/rest_api/v1/dependencies/pagination.py` | Page params | pagination schema | List routes |
| `interfaces/rest_api/v1/dependencies/use_cases.py` | Use case providers | DI container | All handlers |

---

## 5.3 Route Handlers

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `interfaces/rest_api/v1/routes/health/health_handler.py` | GET /v1/health | health use case | First live endpoint |
| `interfaces/rest_api/v1/routes/auth/auth_handler.py` | login, refresh, logout, me | auth use cases, schemas | Before protected routes |
| `interfaces/rest_api/v1/routes/plates/scan_handler.py` | POST/GET /v1/scans | scan use cases | **MVP critical** |
| `interfaces/rest_api/v1/routes/verification/vehicle_handler.py` | GET /v1/vehicles/* | vehicle use cases | Lookup API |
| `interfaces/rest_api/v1/routes/verification/verification_handler.py` | /v1/verification | verification use cases | Verify API |
| `interfaces/rest_api/v1/routes/dashboard/dashboard_handler.py` | /v1/dashboard/* | dashboard use cases | Officer UI |
| `interfaces/rest_api/v1/routes/dashboard/alert_handler.py` | acknowledge alert | acknowledge use case | Triage |
| `interfaces/rest_api/v1/routes/reports/report_handler.py` | /v1/reports/* | report use cases | PDF API |
| `interfaces/rest_api/v1/routes/analytics/analytics_handler.py` | /v1/analytics/* | analytics use cases | Supervisor UI |
| `interfaces/rest_api/v1/routes/history/history_handler.py` | /v1/history/* | history use cases | Audit API |
| `interfaces/rest_api/v1/routes/router.py` | Aggregate all v1 routes | handlers | App mounting |

---

## 5.4 Application Entry & DI

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `interfaces/rest_api/app/create_app.py` | FastAPI factory | router, middleware | App bootstrap |
| `interfaces/rest_api/app/lifespan.py` | Startup/shutdown (DB, ML) | config, engine, models | Load YOLO at start |
| `interfaces/dependency_injection/containers/app_container.py` | DI container definition | all adapters | Composition root |
| `interfaces/dependency_injection/providers/persistence_providers.py` | Wire repos | repositories | |
| `interfaces/dependency_injection/providers/ml_providers.py` | Wire YOLO, OCR | ai, ocr adapters | |
| `interfaces/dependency_injection/providers/auth_providers.py` | Wire JWT, validators | auth infra | |
| `interfaces/dependency_injection/providers/use_case_providers.py` | Wire use cases | application | |
| `interfaces/dependency_injection/wiring/bootstrap.py` | Bind all providers | providers | Single wiring point |
| `bootstrap/app_entry.py` | uvicorn entry `main` | create_app | Deployment entry |
| `bootstrap/container.py` | Re-export container | app_container | Legacy alias |

---

## Phase 5 Exit Gate

- [ ] OpenAPI spec auto-generated matches `docs/api/`
- [ ] Contract tests for all endpoints
- [ ] Postman/httpx e2e: login → scan → get result

**Next:** [06-frontend.md](06-frontend.md)
