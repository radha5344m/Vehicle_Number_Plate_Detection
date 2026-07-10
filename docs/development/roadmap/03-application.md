# Phase 3 — Application Layer

**Path:** `src/sentinel_anpr/application/`  
**Rule:** Orchestrates domain + ports. No concrete infrastructure.

---

## 3.1 DTOs (Application Data Contracts)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/__init__.py` | Package marker | — | |
| `application/dto/__init__.py` | Subpackage | — | |
| `application/dto/common.py` | Pagination, envelope helpers | — | Shared list responses |
| `application/dto/auth_dto.py` | Login, token, officer summary | — | Before auth use cases |
| `application/dto/scan_dto.py` | CreateScan, ScanResult, ScanList | domain scan types | Scan use cases |
| `application/dto/vehicle_dto.py` | VehicleLookup, VehicleRecord | domain vehicle | Lookup use cases |
| `application/dto/verification_dto.py` | VerifyRequest, VerificationResponse | domain verification | Verification use cases |
| `application/dto/risk_dto.py` | RiskAssessment, signals | domain risk | Risk use cases |
| `application/dto/decision_dto.py` | PipelineDecision | domain decision | Orchestration output |
| `application/dto/alert_dto.py` | Alert summary, acknowledge | domain alert | Dashboard |
| `application/dto/report_dto.py` | GenerateReport, ReportReference | domain reporting | Reports |
| `application/dto/dashboard_dto.py` | Summary, flagged items | — | Dashboard queries |
| `application/dto/analytics_dto.py` | TimeSeries, distribution | — | Analytics queries |
| `application/dto/history_dto.py` | AuditEntry, timeline events | domain history | History queries |

---

## 3.2 Mappers

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/mappers/__init__.py` | Package marker | — | |
| `application/mappers/scan_mapper.py` | Domain scan ↔ DTO | `scan_dto`, `scan_session` | Keep domain out of interfaces |
| `application/mappers/verification_mapper.py` | Verification ↔ DTO | `verification_dto` | |
| `application/mappers/vehicle_mapper.py` | Vehicle ↔ DTO | `vehicle_dto` | |
| `application/mappers/risk_mapper.py` | Risk ↔ DTO | `risk_dto` | |
| `application/mappers/alert_mapper.py` | Alert ↔ DTO | `alert_dto` | |

---

## 3.3 Use Cases — Ingestion & Scan

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/use_cases/ingestion/ingest_image_use_case.py` | Validate capture; store image | ports: image_storage, officer_repo, history | Pipeline stage 0 |
| `application/use_cases/vehicle_scan/create_scan_use_case.py` | Create scan session | ingest, scan_repo | Before pipeline |
| `application/use_cases/vehicle_scan/get_scan_use_case.py` | Query scan by ID | scan_repo | GET /scans/{id} |
| `application/use_cases/vehicle_scan/list_scans_use_case.py` | Filtered scan list | scan_repo | GET /scans |
| `application/use_cases/vehicle_scan/retry_scan_use_case.py` | Retry failed pipeline | orchestration | POST retry |

---

## 3.4 Use Cases — Recognition (Application orchestration of ML ports)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/use_cases/plate_recognition/detect_plate_use_case.py` | Call detection port | plate_detection_port | Pipeline stage 1 |
| `application/use_cases/plate_recognition/recognize_plate_use_case.py` | Call OCR port; normalize | ocr_port, plate_number | Pipeline stage 2 |

---

## 3.5 Use Cases — Vehicle & Verification

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/use_cases/vehicle/lookup_vehicle_use_case.py` | Registry + cache lookup | registry_port, vehicle_repo | Stage 3 |
| `application/use_cases/vehicle/get_vehicle_use_case.py` | Get by ID | vehicle_repo | GET /vehicles/{id} |
| `application/use_cases/plate_verification/verify_plate_use_case.py` | Full verification | verification_policy, vehicle | Stage 4 |
| `application/use_cases/verification/analyze_attributes_use_case.py` | Attribute comparison | attribute_matcher | Split for SRP |

---

## 3.6 Use Cases — Risk & Decision

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/use_cases/clone_detection/assess_risk_use_case.py` | Risk scoring | clone_policy, history_query | Stage 5 |
| `application/use_cases/clone_detection/detect_clone_use_case.py` | Alias/wrapper for assess | assess_risk | API naming |
| `application/use_cases/orchestration/make_decision_use_case.py` | Apply decision policy | decision_policy, risk, verification | Stage 6 |
| `application/use_cases/orchestration/process_plate_pipeline_use_case.py` | **Full pipeline orchestrator** | all stage use cases | MVP critical path |

---

## 3.7 Use Cases — Auth, Officer, Alerts, Reports, Dashboard, Analytics, History

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/use_cases/authentication/login_use_case.py` | Authenticate officer | token_provider, credential_validator | Before protected API |
| `application/use_cases/authentication/refresh_token_use_case.py` | Refresh JWT | token_provider | Auth API |
| `application/use_cases/authentication/logout_use_case.py` | Revoke session | token_provider | Auth API |
| `application/use_cases/authentication/get_current_officer_use_case.py` | GET /auth/me | officer_repo | Profile |
| `application/use_cases/officer/get_officer_use_case.py` | Officer lookup | officer_repo | Internal |
| `application/use_cases/alerting/create_alert_use_case.py` | Raise alert from risk | alert_policy, alert_repo | Post-risk |
| `application/use_cases/alerting/acknowledge_alert_use_case.py` | Acknowledge alert | alert_repo, history | Dashboard PATCH |
| `application/use_cases/reporting/generate_report_use_case.py` | Aggregate + PDF | pdf_port, scan, verification, risk | Reports API |
| `application/use_cases/reporting/get_report_use_case.py` | Report metadata | report_repo | GET report |
| `application/use_cases/reporting/list_reports_use_case.py` | Report list | report_repo | GET /reports |
| `application/use_cases/reporting/archive_report_use_case.py` | Archive report | report_repo | Supervisor |
| `application/use_cases/dashboard/get_summary_use_case.py` | KPI aggregation | scan_repo, alert_repo | Dashboard |
| `application/use_cases/dashboard/get_recent_flags_use_case.py` | Flagged scans | scan_repo, risk_repo | Dashboard |
| `application/use_cases/dashboard/list_alerts_use_case.py` | Alert queue | alert_repo | Dashboard alerts |
| `application/use_cases/analytics/get_scan_volume_use_case.py` | Volume time series | analytics_repo | Analytics API |
| `application/use_cases/analytics/get_verification_failures_use_case.py` | Failure rates | analytics_repo | Analytics |
| `application/use_cases/analytics/get_clone_rate_use_case.py` | Clone rate | analytics_repo | Analytics |
| `application/use_cases/analytics/get_risk_distribution_use_case.py` | Histogram | analytics_repo | Analytics |
| `application/use_cases/analytics/get_decision_breakdown_use_case.py` | Decision counts | analytics_repo | Analytics |
| `application/use_cases/history/append_audit_use_case.py` | Write audit | history_command_port | Called by other use cases |
| `application/use_cases/history/query_audit_logs_use_case.py` | Query audit | history_query_port | History API |
| `application/use_cases/history/get_scan_timeline_use_case.py` | Scan stage timeline | history_query_port | Timeline API |
| `application/use_cases/history/get_plate_sightings_use_case.py` | Plate history | history_query_port | Clone investigation |

---

## 3.4 Application Services (Cross-cutting)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `application/services/error_mapper.py` | Domain error → result DTO | domain exceptions | Uniform use case errors |
| `application/services/authorization_service.py` | Role/scope checks | authorize_port | Reuse across use cases |

---

## Phase 3 Exit Gate

- [ ] All use cases unit-tested with **fake ports**
- [ ] `ProcessPlatePipelineUseCase` runs end-to-end with fakes
- [ ] No imports from `infrastructure/` or `interfaces/`

**Next:** [04-infrastructure.md](04-infrastructure.md)
