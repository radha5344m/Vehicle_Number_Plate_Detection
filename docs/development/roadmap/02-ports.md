# Phase 2 — Ports (Application Interfaces)

**Path:** `src/sentinel_anpr/application/ports/`  
**Rule:** Protocol/ABC classes only — no implementations, no framework imports.

Ports depend on **domain types** and **application DTOs** (DTOs may be stubbed minimally here).

---

## 2.1 Outbound Ports (Driven)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/ports/__init__.py` | Package marker | — | |
| `application/ports/outbound/__init__.py` | Subpackage marker | — | |
| `application/ports/outbound/clock_port.py` | Testable time abstraction | — | Used by all time-sensitive use cases |
| `application/ports/outbound/config_port.py` | Typed configuration access | — | Before infra config loader |
| `application/ports/outbound/logging_port.py` | Structured logging interface | — | Cross-cutting; no concrete logger |
| `application/ports/outbound/image_storage_port.py` | Store/retrieve scan images | — | Scan pipeline stage 0 |
| `application/ports/outbound/plate_detection_port.py` | YOLO detection contract | `bounding_box` VO | Stage 1 interface |
| `application/ports/outbound/ocr_port.py` | PaddleOCR contract | `recognition_result` | Stage 2 interface |
| `application/ports/outbound/vehicle_registry_port.py` | External RTO lookup | `vehicle_record`, `plate_number` | Stage 3 interface |
| `application/ports/outbound/vehicle_repository_port.py` | Local vehicle cache CRUD | `vehicle_record` | After registry port |
| `application/ports/outbound/scan_repository_port.py` | Persist scan sessions | `scan_session` | Core persistence |
| `application/ports/outbound/verification_repository_port.py` | Persist verification outcomes | `verification_outcome` | Normalized table |
| `application/ports/outbound/risk_repository_port.py` | Persist risk assessments | `clone_risk_assessment` | Risk engine output |
| `application/ports/outbound/alert_repository_port.py` | Persist/query alerts | `alert` | Dashboard + triage |
| `application/ports/outbound/report_repository_port.py` | Persist report metadata | `report_spec` | Reports module |
| `application/ports/outbound/officer_repository_port.py` | Officer lookup | `officer` | Auth + attribution |
| `application/ports/outbound/history_command_port.py` | Append audit events | `audit_event` | Cross-cutting writes |
| `application/ports/outbound/history_query_port.py` | Query sightings, audit | `plate_number` | Risk correlation |
| `application/ports/outbound/pdf_generator_port.py` | Render PDF bytes | `report_spec` | Reports infrastructure |
| `application/ports/outbound/notification_port.py` | Future alert delivery | — | Stub for phase 4+ |
| `application/ports/outbound/token_provider_port.py` | JWT issue/validate | — | Auth infrastructure |
| `application/ports/outbound/credential_validator_port.py` | Validate officer credentials | — | Login flow |
| `application/ports/outbound/analytics_repository_port.py` | Aggregation queries | — | Analytics use cases |
| `application/ports/outbound/unit_of_work_port.py` | Transaction boundary | repo ports | Multi-table writes |

---

## 2.2 Inbound Ports (Driving)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/ports/inbound/__init__.py` | Subpackage marker | — | |
| `application/ports/inbound/health_check_port.py` | Liveness/readiness | — | First interface to wire |
| `application/ports/inbound/authenticate_port.py` | Login use case entry | — | Auth before protected routes |
| `application/ports/inbound/authorize_port.py` | Permission check | `officer` | Role gating |
| `application/ports/inbound/vehicle_scan_command_port.py` | Start/query scan | `scan_session` | Core ANPR entry |
| `application/ports/inbound/vehicle_lookup_query_port.py` | Plate lookup | `vehicle_record` | Lookup API |
| `application/ports/inbound/verification_command_port.py` | Verify plate | `verification_outcome` | Verification API |
| `application/ports/inbound/risk_assessment_command_port.py` | Assess risk | `clone_risk_assessment` | Risk engine entry |
| `application/ports/inbound/report_command_port.py` | Generate report | — | Reports API |
| `application/ports/inbound/dashboard_query_port.py` | Dashboard summaries | — | Dashboard API |
| `application/ports/inbound/analytics_query_port.py` | Analytics time series | — | Analytics API |
| `application/ports/inbound/history_query_port_inbound.py` | History API surface | — | May delegate to outbound query |

---

## Phase 2 Exit Gate

- [ ] Every port has a corresponding fake in `tests/fixtures/fakes/` (stubs)
- [ ] Use cases can be sketched against port signatures
- [ ] No SQL, FastAPI, or ML imports in port files

**Next:** [03-application.md](03-application.md)
