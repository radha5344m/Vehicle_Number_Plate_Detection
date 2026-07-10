# Phase 4 — Infrastructure Layer

**Path:** `src/sentinel_anpr/infrastructure/`  
**Rule:** Implements outbound ports. No HTTP routing.

Implement sub-order: **config + logging → database → auth → ML/OCR → external → PDF → messaging**.

---

## 4.1 Config & Common

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/__init__.py` | Package marker | — | |
| `infrastructure/config/loaders/yaml_config_loader.py` | Implements `ConfigPort` | config YAML files | All adapters need config |
| `infrastructure/config/loaders/env_overlay.py` | Merge env vars over YAML | yaml loader | 12-factor |
| `infrastructure/common/system_clock.py` | Implements `ClockPort` | — | Testable time |
| `infrastructure/logging/formatters/json_formatter.py` | Structured JSON logs | — | Observability |
| `infrastructure/logging/handlers/stream_handler.py` | stdout handler | formatter | Default logging |
| `infrastructure/logging/adapters/logging_adapter.py` | Implements `LoggingPort` | handlers | Injected everywhere |

---

## 4.2 Database — Connection & Models

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/database/connection/engine.py` | SQLAlchemy engine factory | config_port | All repos need DB |
| `infrastructure/database/connection/session.py` | Session factory | engine | Per-request sessions |
| `infrastructure/database/unit_of_work/sqlalchemy_uow.py` | Implements `UnitOfWorkPort` | session | Transactions |
| `infrastructure/database/models/base.py` | Declarative base, mixins | — | ORM foundation |
| `infrastructure/database/models/stations/station_model.py` | `stations` table ORM | base | FK for officers |
| `infrastructure/database/models/officers/officer_model.py` | `officers` table | station_model | Auth + scans |
| `infrastructure/database/models/vehicles/vehicle_model.py` | `vehicles` table | base | Verification |
| `infrastructure/database/models/scan_history/scan_model.py` | `scan_history` table | officer, vehicle | Core fact table |
| `infrastructure/database/models/verification_results/verification_model.py` | 1:1 verification | scan_model | Normalized |
| `infrastructure/database/models/risk_assessments/risk_model.py` | Risk assessments | scan_model | Risk engine |
| `infrastructure/database/models/vehicle_alerts/alert_model.py` | Alerts | scan, vehicle, officer | Dashboard |
| `infrastructure/database/models/investigation_reports/report_model.py` | Reports | scan, officer | PDF metadata |
| `infrastructure/database/models/audit_logs/audit_model.py` | Append-only audit | officer | History |
| `infrastructure/database/migrations/env.py` | Alembic environment | engine | Schema management |
| `infrastructure/database/migrations/versions/001_initial_schema.py` | Initial migration | all models | First deploy |

---

## 4.3 Database — Mappers & Repositories

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/database/mappers/officer_mapper.py` | ORM ↔ domain officer | models, domain | Anti-corruption |
| `infrastructure/database/mappers/vehicle_mapper.py` | ORM ↔ vehicle_record | models, domain | |
| `infrastructure/database/mappers/scan_mapper.py` | ORM ↔ scan_session | models, domain | |
| `infrastructure/database/mappers/verification_mapper.py` | ORM ↔ outcome | models, domain | |
| `infrastructure/database/mappers/risk_mapper.py` | ORM ↔ assessment | models, domain | |
| `infrastructure/database/mappers/alert_mapper.py` | ORM ↔ alert | models, domain | |
| `infrastructure/database/mappers/report_mapper.py` | ORM ↔ report | models, domain | |
| `infrastructure/database/mappers/audit_mapper.py` | ORM ↔ audit_event | models, domain | |
| `infrastructure/database/repositories/officers/officer_repository.py` | `OfficerRepositoryPort` | mapper, session | Auth + attribution |
| `infrastructure/database/repositories/vehicles/vehicle_repository.py` | `VehicleRepositoryPort` | mapper, session | Lookup cache |
| `infrastructure/database/repositories/scan_history/scan_repository.py` | `ScanRepositoryPort` | mapper, session | Core persistence |
| `infrastructure/database/repositories/scan_history/image_storage.py` | `ImageStoragePort` (S3/local) | config | Scan images |
| `infrastructure/database/repositories/verification_results/verification_repository.py` | `VerificationRepositoryPort` | mapper | Verification |
| `infrastructure/database/repositories/risk_assessments/risk_repository.py` | `RiskRepositoryPort` | mapper | Risk |
| `infrastructure/database/repositories/vehicle_alerts/alert_repository.py` | `AlertRepositoryPort` | mapper | Alerts |
| `infrastructure/database/repositories/investigation_reports/report_repository.py` | `ReportRepositoryPort` | mapper | Reports |
| `infrastructure/database/repositories/audit_logs/audit_repository.py` | History command + query | mapper | Audit |
| `infrastructure/database/repositories/analytics/analytics_repository.py` | `AnalyticsRepositoryPort` | session, raw SQL | Read aggregations |

---

## 4.4 Authentication

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/authentication/jwt/token_provider.py` | Implements `TokenProviderPort` | config | Login/refresh |
| `infrastructure/authentication/jwt/jwt_validator.py` | Validate access tokens | config | Middleware |
| `infrastructure/authentication/providers/officer_credential_validator.py` | `CredentialValidatorPort` | officer_repo | Login |
| `infrastructure/authentication/api_key/api_key_validator.py` | System integrations | config | Admin API keys |
| `infrastructure/authentication/middleware/auth_context.py` | Resolve principal | jwt_validator, officer_repo | Request scope |

---

## 4.5 AI / Plate Detection (YOLO)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/ai/yolo/config/yolo_config.py` | Model path, threshold | config_port | Detector setup |
| `infrastructure/ai/yolo/detector/plate_detector.py` | YOLO inference | yolo_config | `PlateDetectionPort` |
| `infrastructure/ai/yolo/models/model_loader.py` | Load weights | config | Startup |
| `infrastructure/ai/inference/inference_runtime.py` | GPU/CPU runtime wrapper | — | Shared ML runtime |
| `infrastructure/ai/pipelines/plate_processing/detection_adapter.py` | Implements `PlateDetectionPort` | plate_detector | Application boundary |
| `infrastructure/ai/pipelines/plate_processing/pipeline_config.py` | Stage wiring config | config | Orchestration support |
| `infrastructure/ai/visual_attributes/color_extractor.py` | Future observed color | cv2 (infra only) | Attribute analysis v2 |

---

## 4.6 OCR (PaddleOCR)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/ocr/paddleocr/paddleocr_engine.py` | PaddleOCR wrapper | config | OCR runtime |
| `infrastructure/ocr/preprocessor/image_preprocessor.py` | Crop normalization | cv2 (infra only) | OCR accuracy |
| `infrastructure/ocr/postprocessor/text_postprocessor.py` | Char cleanup | — | Before PlateNumber |
| `infrastructure/ocr/paddleocr/ocr_adapter.py` | Implements `OcrPort` | engine, pre/post | Application boundary |

---

## 4.7 External APIs

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/external/vehicle_registry/registry_client.py` | HTTP RTO client | config, logging | `VehicleRegistryPort` |
| `infrastructure/external/vehicle_registry/registry_response_mapper.py` | External JSON → domain | vehicle_mapper | Anti-corruption |

---

## 4.8 PDF Reports

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/pdf/templates/field_summary.html` | Report template | — | PDF content |
| `infrastructure/pdf/templates/full_investigation.html` | Full report template | — | |
| `infrastructure/pdf/generators/pdf_generator.py` | HTML → PDF | templates | `PdfGeneratorPort` |
| `infrastructure/pdf/exporters/storage_exporter.py` | Save PDF to object store | image_storage | Download URL |

---

## 4.9 Messaging (Future / Optional)

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `infrastructure/messaging/publishers/alert_publisher.py` | `NotificationPort` stub | logging | Future notifications |
| `infrastructure/notification/channels/webhook_channel.py` | Webhook delivery | config | Phase 2 feature |

---

## Phase 4 Exit Gate

- [ ] Integration tests: DB repos, OCR, YOLO (fixture images), registry (wiremock)
- [ ] Migrations apply cleanly on empty DB
- [ ] No imports from `interfaces/`

**Next:** [05-interfaces.md](05-interfaces.md)
