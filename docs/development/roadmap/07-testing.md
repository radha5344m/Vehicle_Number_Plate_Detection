# Phase 7 — Testing

**Path:** `tests/` + `frontend/**/*.test.*`  
**Rule:** Mirror source structure; domain tests use zero mocks.

Implement **in parallel with each layer** — files listed here are finalized/expanded in Phase 7.

---

## 7.1 Test Infrastructure

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/conftest.py` | Pytest fixtures (session, fakes) | fake ports | All backend tests |
| `tests/pytest.ini` or `pyproject.toml` [tool.pytest] | Pytest config | — | Test runner |
| `frontend/vitest.config.ts` | Vitest config | vite | Frontend tests |
| `frontend/src/test/setup.ts` | RTL setup | vitest | Component tests |
| `frontend/src/test/renderWithProviders.tsx` | Query + router wrapper | providers | Hook/component tests |

---

## 7.2 Fake Ports (`tests/fixtures/fakes/`)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `fake_clock.py` | Fixed time | ClockPort | Deterministic tests |
| `fake_config.py` | In-memory config | ConfigPort | All use case tests |
| `fake_logging.py` | Capture log entries | LoggingPort | Assertions |
| `fake_image_storage.py` | In-memory images | ImageStoragePort | Scan tests |
| `fake_plate_detector.py` | Canned bounding box | PlateDetectionPort | Pipeline tests |
| `fake_ocr.py` | Canned plate text | OcrPort | Pipeline tests |
| `fake_vehicle_registry.py` | Canned registry JSON | VehicleRegistryPort | Verification |
| `fake_scan_repository.py` | In-memory scans | ScanRepositoryPort | Most use cases |
| `fake_vehicle_repository.py` | In-memory vehicles | VehicleRepositoryPort | Lookup |
| `fake_verification_repository.py` | In-memory verifications | VerificationRepositoryPort | |
| `fake_risk_repository.py` | In-memory risk | RiskRepositoryPort | |
| `fake_alert_repository.py` | In-memory alerts | AlertRepositoryPort | |
| `fake_report_repository.py` | In-memory reports | ReportRepositoryPort | |
| `fake_officer_repository.py` | Test officers | OfficerRepositoryPort | Auth |
| `fake_history.py` | In-memory audit | History ports | |
| `fake_pdf_generator.py` | Returns dummy bytes | PdfGeneratorPort | Reports |
| `fake_token_provider.py` | Test JWTs | TokenProviderPort | Auth |

---

## 7.3 Test Data Fixtures

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/fixtures/data/images/valid_plate.jpg` | Happy-path scan | — | ML integration |
| `tests/fixtures/data/images/no_plate.jpg` | Detection failure | — | Error path |
| `tests/fixtures/data/images/blurry_plate.jpg` | Low OCR confidence | — | Edge case |
| `tests/fixtures/data/registry_responses/found.json` | Registry hit | — | Verification |
| `tests/fixtures/data/registry_responses/not_found.json` | Registry miss | — | Verification |
| `tests/fixtures/data/registry_responses/stolen.json` | Stolen vehicle | — | Escalate path |
| `tests/fixtures/data/pdf_templates/.gitkeep` | PDF expected output dir | — | Report tests |

---

## 7.4 Unit Tests — Domain

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/unit/domain/common/test_plate_number.py` | Plate normalization | plate_number | First domain test |
| `tests/unit/domain/common/test_confidence_score.py` | Score bounds | confidence_score | |
| `tests/unit/domain/officer/test_officer_policy.py` | Active duty rules | officer_policy | |
| `tests/unit/domain/vehicle/test_vehicle_invariants.py` | Vehicle rules | vehicle_invariants | |
| `tests/unit/domain/ingestion/test_capture_validator.py` | Capture validation | capture_validator | |
| `tests/unit/domain/vehicle_scan/test_scan_state_machine.py` | Status transitions | scan_state_machine | |
| `tests/unit/domain/plate_verification/test_verification_policy.py` | Verification rules | verification_policy | |
| `tests/unit/domain/plate_verification/test_attribute_matcher.py` | Mismatch detection | attribute_matcher | |
| `tests/unit/domain/clone_detection/test_clone_detection_policy.py` | Risk signals | clone_policy | |
| `tests/unit/domain/decision/test_decision_policy.py` | Decision matrix | decision_policy | |
| `tests/unit/domain/alerting/test_alert_policy.py` | Alert rules | alert_policy | |
| `tests/unit/domain/reporting/test_report_content_policy.py` | Report sections | report_content_policy | |

---

## 7.5 Unit Tests — Application

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/unit/application/use_cases/test_ingest_image.py` | Ingest use case | fakes | |
| `tests/unit/application/use_cases/test_detect_plate.py` | Detection use case | fake detector | |
| `tests/unit/application/use_cases/test_recognize_plate.py` | OCR use case | fake ocr | |
| `tests/unit/application/use_cases/test_lookup_vehicle.py` | Lookup use case | fake registry | |
| `tests/unit/application/use_cases/test_verify_plate.py` | Verify use case | fakes | |
| `tests/unit/application/use_cases/test_assess_risk.py` | Risk use case | fake history | |
| `tests/unit/application/use_cases/test_make_decision.py` | Decision use case | domain policies | |
| `tests/unit/application/use_cases/test_process_pipeline.py` | **Full pipeline** | all fakes | MVP gate |
| `tests/unit/application/use_cases/test_login.py` | Auth | fake token | |
| `tests/unit/application/use_cases/test_generate_report.py` | Reports | fake pdf | |
| `tests/unit/application/use_cases/test_dashboard_summary.py` | Dashboard | fake repos | |

---

## 7.6 Integration Tests — Infrastructure

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/integration/infrastructure/database/test_scan_repository.py` | Real DB CRUD | test DB, migrations | Persistence |
| `tests/integration/infrastructure/database/test_audit_append_only.py` | No update/delete | test DB | Audit integrity |
| `tests/integration/infrastructure/ai/test_yolo_detector.py` | Real YOLO inference | fixture image, GPU optional | ML |
| `tests/integration/infrastructure/ocr/test_paddleocr.py` | Real OCR | fixture image | ML |
| `tests/integration/infrastructure/external/test_registry_client.py` | HTTP client | wiremock | External |
| `tests/integration/infrastructure/authentication/test_jwt_flow.py` | Token round-trip | jwt provider | Auth |
| `tests/integration/infrastructure/pdf/test_pdf_generator.py` | PDF output | templates | Reports |

---

## 7.7 Integration Tests — Interfaces

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/integration/interfaces/rest_api/test_health.py` | GET /health | test client | First API test |
| `tests/integration/interfaces/rest_api/test_auth.py` | Login flow | test client, DB | |
| `tests/integration/interfaces/rest_api/test_scans.py` | Scan endpoints | test client, fakes/real ML | **MVP** |
| `tests/integration/interfaces/rest_api/test_verification.py` | Verify API | test client | |
| `tests/integration/interfaces/rest_api/test_dashboard.py` | Dashboard API | test client | |
| `tests/integration/interfaces/rest_api/test_reports.py` | Reports API | test client | |
| `tests/integration/interfaces/rest_api/test_analytics.py` | Analytics API | test client | |
| `tests/integration/interfaces/rest_api/test_history.py` | History API | test client | |
| `tests/integration/interfaces/dependency_injection/test_container.py` | DI wiring | container | All routes |

---

## 7.8 E2E Tests

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `tests/e2e/scenarios/test_login_to_scan_pipeline.py` | Full backend flow | running API, fixtures | Release gate |
| `tests/e2e/scenarios/test_clone_detection_scenario.py` | Multi-sighting risk | DB seed data | Risk validation |
| `tests/e2e/scenarios/test_report_generation.py` | Scan → report PDF | full stack | Reports gate |

---

## 7.9 Frontend Tests

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `frontend/src/services/scanService.test.ts` | Service unit tests | mocked http | |
| `frontend/src/hooks/scan/useCreateScan.test.ts` | Hook tests | mocked service | |
| `frontend/src/components/features/scan/ScanResultCard.test.tsx` | Component RTL | render helper | |
| `frontend/src/pages/scan/ScanPage.test.tsx` | Page integration | MSW mock API | |
| `frontend/e2e/login-scan.spec.ts` | Playwright E2E | staging URL | Pre-deploy |

---

## Phase 7 Exit Gate

- [ ] CI pipeline: lint → unit → integration → e2e
- [ ] Domain coverage ≥ 95%; application ≥ 85%
- [ ] No merge without tests for new use cases

**Next:** [08-deployment.md](08-deployment.md)
