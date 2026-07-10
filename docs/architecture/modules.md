# SentinelANPR AI — Module Architecture

**Version:** 0.2.0 (Foundation)  
**Status:** Architecture only — no implementation

---

## Design Principles

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | Each module owns exactly one reason to change |
| **Clean Architecture** | Domain modules never depend on frameworks or infrastructure |
| **Hexagonal** | Cross-module interaction via **public ports** only |
| **Dependency Inversion** | Application depends on abstractions; infrastructure implements them |

---

## Module Catalog

| # | Module | Primary Layer | SRP Summary |
|---|--------|---------------|-------------|
| 1 | [Authentication](#1-authentication) | Infrastructure + Application | Prove identity and authorize access |
| 2 | [Officer](#2-officer) | Domain + Application | Manage officer identity and assignment context |
| 3 | [Vehicle](#3-vehicle) | Domain + Application | Represent registered vehicle master data |
| 4 | [Vehicle Scan](#4-vehicle-scan) | Domain + Application | Orchestrate a single scan event lifecycle |
| 5 | [OCR](#5-ocr) | Infrastructure | Extract plate text from a plate image crop |
| 6 | [Plate Detection](#6-plate-detection) | Infrastructure | Locate plate region within a full image |
| 7 | [Vehicle Verification](#7-vehicle-verification) | Domain + Application | Validate scan against registry records |
| 8 | [Risk Engine](#8-risk-engine) | Domain + Application | Score clone/fraud risk from signals |
| 9 | [Reports](#9-reports) | Domain + Application + Infrastructure | Compose and export formal documents |
| 10 | [Dashboard](#10-dashboard) | Application + Interfaces | Serve real-time operational summaries |
| 11 | [Analytics](#11-analytics) | Application | Compute trends and statistical insights |
| 12 | [History](#12-history) | Domain + Application | Store and retrieve immutable audit records |
| 13 | [Configuration](#13-configuration) | Infrastructure + Application | Provide typed runtime settings |
| 14 | [Logging](#14-logging) | Infrastructure | Emit structured observability events |
| 15 | [Notification](#15-notification-future) | Infrastructure (future) | Deliver outbound alerts to external channels |

---

## System Context — Module Interactions

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Authentication│────▶│   Officer    │     │  Configuration  │
└──────┬───────┘     └──────┬───────┘     └────────┬────────┘
       │                    │                       │
       ▼                    ▼                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      Vehicle Scan                             │
│  (orchestrates scan lifecycle)                                │
└──────┬───────────────────┬──────────────────┬──────────────┘
       │                   │                  │
       ▼                   ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│   Plate     │───▶│     OCR     │    │    Vehicle       │
│  Detection  │    │             │    │  Verification    │
└─────────────┘    └─────────────┘    └────────┬─────────┘
                                               │
       ┌───────────────────────────────────────┤
       ▼                                       ▼
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│    Risk     │───▶│   History   │◀───│     Vehicle      │
│   Engine    │    │             │    │                  │
└──────┬──────┘    └──────┬──────┘    └──────────────────┘
       │                  │
       ▼                  ├──────────────────┐
┌─────────────┐           ▼                  ▼
│Notification │    ┌─────────────┐   ┌─────────────┐
│  (future)   │    │  Dashboard  │   │  Analytics  │
└─────────────┘    └─────────────┘   └──────┬──────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   Reports   │
                                    └─────────────┘

        ═══════════ Cross-cutting: Logging, Configuration ═══════════
```

---

## Layer Placement Map

```
domain/
├── officer/              ← Officer
├── vehicle/              ← Vehicle
├── vehicle_scan/         ← Vehicle Scan
├── verification/         ← Vehicle Verification
├── risk/                 ← Risk Engine
├── reporting/            ← Reports (content rules)
└── history/              ← History

application/
├── authentication/       ← Authentication (use cases)
├── officer/
├── vehicle/
├── vehicle_scan/
├── verification/
├── risk/
├── reporting/
├── dashboard/            ← Dashboard
├── analytics/            ← Analytics
├── history/
└── ports/                ← All public port interfaces

infrastructure/
├── authentication/       ← Authentication (implementations)
├── ocr/                  ← OCR
├── ai/yolo/              ← Plate Detection
├── pdf/                  ← Reports (rendering)
├── database/             ← Persistence for all modules
├── logging/              ← Logging
├── config/               ← Configuration
└── messaging/            ← Notification (future)

interfaces/
├── rest_api/v1/routes/   ← HTTP exposure per module
├── schemas/              ← Request/response contracts
└── dependency_injection/ ← Module wiring
```

---

## Module Specifications

---

### 1. Authentication

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Establish **who** is calling the system and **what** they are permitted to do. Does not manage officer profiles. |
| **Primary layer** | Infrastructure (implementations) + Application (policies) |

#### Responsibilities

- Validate credentials (JWT, API key, session token)
- Resolve authenticated principal identity
- Enforce role/permission checks before use case execution
- Reject unauthenticated or unauthorized requests at the interface boundary
- Propagate principal context to downstream modules

#### Must NOT Do

- Store officer biographical data (→ Officer module)
- Perform vehicle or scan business logic
- Issue business alerts

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | Interfaces (REST middleware) | Receives raw tokens/credentials |
| Outbound | `OfficerQueryPort` | Resolve officer ID from principal |
| Outbound | `ConfigurationPort` | Auth secrets, token TTL, issuer settings |
| Outbound | `LoggingPort` | Auth success/failure audit events |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `AuthenticatePort` | Inbound | Validate credentials → `AuthPrincipal` |
| `AuthorizePort` | Inbound | Check permission for action/resource |
| `TokenProviderPort` | Outbound | Issue and refresh tokens |
| `CredentialValidatorPort` | Outbound | Validate against identity store |
| `AuthPrincipal` | DTO | `{ principal_id, roles[], session_id }` |

#### Folder Mapping

`infrastructure/authentication/` · `application/authentication/` · `interfaces/rest_api/v1/routes/auth/`

---

### 2. Officer

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Manage **officer domain identity** — badge, name, rank, station, duty status — separate from authentication mechanics. |
| **Primary layer** | Domain + Application |

#### Responsibilities

- Define officer entity and value objects (badge number, rank, station)
- Track duty assignment context relevant to scans
- Provide officer lookup for scan attribution
- Enforce officer-related business rules (e.g., active duty required to scan)

#### Must NOT Do

- Validate passwords or JWTs (→ Authentication)
- Process images or plates
- Compute risk scores

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `OfficerQueryPort`, `OfficerCommandPort` | CRUD and lookup |
| Outbound | `OfficerRepositoryPort` | Persist officer records |
| Outbound | `HistoryPort` | Record officer action audit entries |
| Cross-cutting | `LoggingPort` | Officer lifecycle events |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `OfficerQueryPort` | Inbound | `get_officer(id)`, `find_by_badge(badge)` |
| `OfficerCommandPort` | Inbound | `register_officer()`, `update_assignment()` |
| `OfficerRepositoryPort` | Outbound | Persistence abstraction |
| `OfficerSummary` | DTO | `{ id, badge, name, rank, station_id, status }` |

#### Folder Mapping

`domain/officer/` · `application/officer/` · `infrastructure/database/repositories/` (officer repo)

---

### 3. Vehicle

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Represent **registered vehicle master data** as a domain concept — the authoritative record of a vehicle and its plate binding. |
| **Primary layer** | Domain + Application |

#### Responsibilities

- Model vehicle attributes (plate, make, model, color, registration status)
- Express vehicle–plate binding rules
- Provide vehicle lookup semantics for other modules
- Hold domain invariants (e.g., one active plate per vehicle)

#### Must NOT Do

- Call external registry APIs directly (→ Infrastructure via ports)
- Run OCR or detection
- Generate reports or dashboards

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `VehicleQueryPort` | Lookup by plate or vehicle ID |
| Outbound | `VehicleRegistryPort` | Fetch/sync with external RTO registry |
| Outbound | `VehicleRepositoryPort` | Local cache of registry snapshots |
| Outbound | `HistoryPort` | Record vehicle record changes |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `VehicleQueryPort` | Inbound | `get_by_plate(plate)`, `get_by_id(id)` |
| `VehicleRegistryPort` | Outbound | External authority lookup |
| `VehicleRepositoryPort` | Outbound | Local persistence |
| `VehicleRecord` | DTO | `{ id, plate, make, model, color, status, registered_at }` |

#### Folder Mapping

`domain/vehicle/` · `application/vehicle/` · `infrastructure/external/vehicle_registry/`

---

### 4. Vehicle Scan

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Own the **end-to-end lifecycle of a single scan event** — from image intake through recognition to handoff for verification and risk assessment. |
| **Primary layer** | Domain + Application (orchestrator) |

#### Responsibilities

- Create and track scan session state machine (`received → detecting → recognizing → completed | failed`)
- Attach scan metadata (timestamp, location, camera, officer)
- Coordinate Plate Detection → OCR pipeline via ports
- Emit domain events (`ScanStarted`, `ScanCompleted`, `ScanFailed`)
- Persist scan results for downstream modules

#### Must NOT Do

- Implement YOLO or PaddleOCR (→ Plate Detection, OCR modules)
- Verify against registry (→ Vehicle Verification)
- Score risk (→ Risk Engine)

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `VehicleScanCommandPort` | Start/process scan |
| Outbound | `PlateDetectionPort` | Localize plate region |
| Outbound | `OcrPort` | Extract plate text |
| Outbound | `ImageStoragePort` | Store raw/crop images |
| Outbound | `ScanRepositoryPort` | Persist scan records |
| Outbound | `OfficerQueryPort` | Attribute scan to officer |
| Outbound | `HistoryPort` | Immutable scan audit |
| Outbound | `LoggingPort` | Scan pipeline telemetry |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `VehicleScanCommandPort` | Inbound | `start_scan(image, metadata)`, `get_scan_status(id)` |
| `ScanQueryPort` | Inbound | `get_scan_result(id)` |
| `PlateDetectionPort` | Outbound | `detect(image) → bounding_box` |
| `OcrPort` | Outbound | `recognize(crop) → plate_text, confidence` |
| `ScanResult` | DTO | `{ scan_id, plate_text, confidence, bbox, status, officer_id }` |

#### Folder Mapping

`domain/vehicle_scan/` · `application/vehicle_scan/` · `application/use_cases/orchestration/`

---

### 5. OCR

| Attribute | Detail |
|-----------|--------|
| **Purpose** | **Extract alphanumeric plate text** from a pre-cropped plate image. Single concern: character recognition only. |
| **Primary layer** | Infrastructure (PaddleOCR adapter) |

#### Responsibilities

- Preprocess plate crop for OCR input
- Run PaddleOCR inference
- Post-process raw OCR output (character cleanup)
- Return normalized text and per-character confidence
- Report inference latency and model version

#### Must NOT Do

- Detect plate location in full image (→ Plate Detection)
- Verify plate against registry
- Store scan records
- Apply business normalization rules (→ Domain value objects via Application)

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `OcrPort` (implemented) | Called by Vehicle Scan |
| Outbound | `ConfigurationPort` | Model path, language, thresholds |
| Outbound | `LoggingPort` | Inference metrics and errors |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `OcrPort` | Outbound (implemented) | `recognize(image_crop) → OcrResult` |
| `OcrResult` | DTO | `{ text, confidence, char_confidences[], model_version }` |

#### Folder Mapping

`infrastructure/ocr/paddleocr/` · `infrastructure/ocr/preprocessor/` · `infrastructure/ocr/postprocessor/`

---

### 6. Plate Detection

| Attribute | Detail |
|-----------|--------|
| **Purpose** | **Locate the license plate region** within a full vehicle image using object detection (YOLO). Does not read characters. |
| **Primary layer** | Infrastructure (YOLO adapter) |

#### Responsibilities

- Load and manage YOLO model artifacts
- Run plate detection inference on input image
- Return bounding box(es) with confidence scores
- Handle multi-plate and no-plate scenarios
- Report detection latency and model version

#### Must NOT Do

- Perform OCR (→ OCR module)
- Verify or score risk
- Manage scan lifecycle

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `PlateDetectionPort` (implemented) | Called by Vehicle Scan |
| Outbound | `ConfigurationPort` | Model weights path, confidence threshold |
| Outbound | `LoggingPort` | Detection metrics |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `PlateDetectionPort` | Outbound (implemented) | `detect(image) → DetectionResult` |
| `DetectionResult` | DTO | `{ boxes[{x,y,w,h,confidence}], model_version }` |

#### Folder Mapping

`infrastructure/ai/yolo/` · `infrastructure/ai/inference/` · `infrastructure/ai/pipelines/`

---

### 7. Vehicle Verification

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Determine whether a **recognized plate matches authoritative registry data** and whether vehicle attributes are consistent. |
| **Primary layer** | Domain + Application |

#### Responsibilities

- Apply verification policies (plate format, jurisdiction rules)
- Compare scan result against Vehicle module records
- Produce verification outcome (`valid`, `invalid`, `unknown`, `expired`)
- Record mismatch reasons for audit and risk input
- Emit `PlateVerified` / `PlateVerificationFailed` domain events

#### Must NOT Do

- Run OCR or detection
- Compute clone risk score (→ Risk Engine)
- Generate PDF reports

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `VerificationCommandPort` | `verify(scan_result)` |
| Outbound | `VehicleQueryPort` | Fetch vehicle registry data |
| Outbound | `VerificationRepositoryPort` | Store verification outcomes |
| Outbound | `HistoryPort` | Audit trail |
| Outbound | `LoggingPort` | Verification events |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `VerificationCommandPort` | Inbound | `verify(scan_id | plate_text) → VerificationOutcome` |
| `VerificationQueryPort` | Inbound | `get_verification(scan_id)` |
| `VerificationOutcome` | DTO | `{ status, plate, vehicle_id, mismatch_reasons[], verified_at }` |

#### Folder Mapping

`domain/plate_verification/` · `application/use_cases/plate_verification/`

---

### 8. Risk Engine

| Attribute | Detail |
|-----------|--------|
| **Purpose** | **Score fraud and cloned-plate risk** by correlating verification results, historical sightings, and anomaly signals. |
| **Primary layer** | Domain + Application |

#### Responsibilities

- Define risk scoring policies and thresholds
- Correlate current scan with historical sightings (same plate, different vehicle context)
- Produce risk score (0.0–1.0) and explainable signal list
- Flag `clone_suspected` when threshold exceeded
- Emit `RiskAssessed` / `CloneSuspected` domain events

#### Must NOT Do

- Deliver notifications (→ Notification, future)
- Verify plates against registry (consumes verification outcome)
- Render dashboards (→ Dashboard consumes risk data)

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `RiskAssessmentCommandPort` | `assess(scan_id, verification_outcome)` |
| Outbound | `HistoryQueryPort` | Past sightings for correlation |
| Outbound | `RiskRepositoryPort` | Persist assessments |
| Outbound | `NotificationPort` (future) | Trigger alert on high risk |
| Outbound | `HistoryPort` | Audit risk decisions |
| Outbound | `LoggingPort` | Scoring telemetry |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `RiskAssessmentCommandPort` | Inbound | `assess(context) → RiskAssessment` |
| `RiskQueryPort` | Inbound | `get_assessment(scan_id)` |
| `HistoryQueryPort` | Outbound | `find_sightings_by_plate(plate, window)` |
| `RiskAssessment` | DTO | `{ score, clone_suspected, signals[], assessed_at }` |

#### Folder Mapping

`domain/clone_detection/` · `domain/risk/` · `application/use_cases/clone_detection/`

---

### 9. Reports

| Attribute | Detail |
|-----------|--------|
| **Purpose** | **Compose and export formal documents** (PDF) from scan, verification, and risk data for legal and operational use. |
| **Primary layer** | Domain (content rules) + Application + Infrastructure (PDF rendering) |

#### Responsibilities

- Define report content structure and mandatory fields (domain rules)
- Aggregate data from Scan, Verification, Risk, Officer modules
- Apply report templates and formatting policies
- Generate PDF via infrastructure adapter
- Track report generation in history

#### Must NOT Do

- Perform scans or verification
- Serve real-time dashboard widgets (→ Dashboard)
- Compute analytics aggregates (→ Analytics)

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `ReportCommandPort` | `generate_report(scan_id, template)` |
| Outbound | `ScanQueryPort` | Scan data |
| Outbound | `VerificationQueryPort` | Verification data |
| Outbound | `RiskQueryPort` | Risk data |
| Outbound | `OfficerQueryPort` | Officer attribution |
| Outbound | `PdfGeneratorPort` | Render PDF bytes |
| Outbound | `ReportRepositoryPort` | Store generated reports |
| Outbound | `HistoryPort` | Report issuance audit |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `ReportCommandPort` | Inbound | `generate(request) → ReportReference` |
| `ReportQueryPort` | Inbound | `get_report(id)`, `download(id)` |
| `PdfGeneratorPort` | Outbound | `render(template, data) → bytes` |
| `ReportReference` | DTO | `{ report_id, scan_id, template, generated_at, download_url }` |

#### Folder Mapping

`domain/reporting/` · `application/use_cases/reporting/` · `infrastructure/pdf/`

---

### 10. Dashboard

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Provide **real-time operational summaries** for officers and supervisors on active duty — today's scans, flags, station activity. |
| **Primary layer** | Application + Interfaces |

#### Responsibilities

- Aggregate live counters (scans today, verifications failed, clones flagged)
- Serve station-level and officer-level summary views
- Expose recent high-priority events (last N flagged scans)
- Apply authorization scoping (officer sees own station only)

#### Must NOT Do

- Run ML inference
- Perform long-range statistical analysis (→ Analytics)
- Generate PDF exports (→ Reports)
- Store raw scan data (reads via query ports)

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `DashboardQueryPort` | REST handlers call this |
| Outbound | `ScanQueryPort` | Recent scan counts |
| Outbound | `VerificationQueryPort` | Failure counts |
| Outbound | `RiskQueryPort` | Flagged clone counts |
| Outbound | `AuthorizePort` | Scope by role/station |
| Outbound | `ConfigurationPort` | Refresh intervals, limits |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `DashboardQueryPort` | Inbound | `get_summary(station_id)`, `get_recent_flags(limit)` |
| `DashboardSummary` | DTO | `{ scans_today, verifications_failed, clones_flagged, last_updated }` |
| `FlaggedScanItem` | DTO | `{ scan_id, plate, risk_score, officer, timestamp }` |

#### Folder Mapping

`application/dashboard/` · `interfaces/rest_api/v1/routes/` (dashboard endpoints) · `interfaces/schemas/responses/`

---

### 11. Analytics

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Compute **historical trends, patterns, and statistical insights** across time ranges for planning and command review. |
| **Primary layer** | Application |

#### Responsibilities

- Aggregate scan volumes by hour/day/station/officer
- Compute verification failure rates and clone detection rates over time
- Support date-range queries and grouping dimensions
- Provide data series for charts (no rendering — data only)

#### Must NOT Do

- Serve real-time operational counters (→ Dashboard)
- Generate PDF reports (→ Reports, though may share queries)
- Modify source data

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `AnalyticsQueryPort` | Range and dimension parameters |
| Outbound | `AnalyticsRepositoryPort` | Optimized read models / aggregations |
| Outbound | `HistoryQueryPort` | Raw event source for aggregation |
| Outbound | `AuthorizePort` | Role-based data access |
| Outbound | `ConfigurationPort` | Query limits, retention windows |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `AnalyticsQueryPort` | Inbound | `get_scan_volume(range, group_by)`, `get_failure_rate(range)` |
| `AnalyticsTimeSeries` | DTO | `{ labels[], values[], metric, period }` |
| `AnalyticsRepositoryPort` | Outbound | Pre-computed or on-demand aggregation |

#### Folder Mapping

`application/analytics/` · `interfaces/rest_api/v1/routes/` (analytics endpoints)

---

### 12. History

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Maintain an **immutable audit trail** of all significant system events — scans, verifications, risk decisions, officer actions, report generation. |
| **Primary layer** | Domain + Application |

#### Responsibilities

- Define audit event types and mandatory fields
- Append-only write semantics (no update/delete of audit records)
- Support filtered retrieval by entity, officer, plate, time range
- Provide correlation ID tracing across event chains

#### Must NOT Do

- Compute analytics aggregates (→ Analytics reads from history)
- Authenticate users
- Run business pipelines

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `HistoryCommandPort` | `append(event)` — called by other modules |
| Inbound | `HistoryQueryPort` | `query(filters)` — called by Analytics, Risk, Dashboard |
| Outbound | `HistoryRepositoryPort` | Append-only persistence |
| Outbound | `ConfigurationPort` | Retention policy |
| Outbound | `LoggingPort` | Meta-audit of history writes |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `HistoryCommandPort` | Outbound (consumed) | `append(AuditEvent)` |
| `HistoryQueryPort` | Outbound (consumed) | `query(filter) → AuditEvent[]` |
| `AuditEvent` | DTO | `{ event_id, type, entity_id, actor_id, payload, timestamp, correlation_id }` |

#### Folder Mapping

`domain/history/` · `application/history/` · `infrastructure/database/repositories/`

---

### 13. Configuration

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Provide **typed, environment-aware runtime settings** to all modules without coupling them to files or environment variables. |
| **Primary layer** | Infrastructure + Application (port) |

#### Responsibilities

- Load layered config (`default` → `environment` → env vars)
- Validate required settings at startup
- Expose typed getters per config section (ML, auth, DB, logging)
- Support hot-reload for non-secret settings _TBD_

#### Must NOT Do

- Enforce business rules
- Store officer or vehicle data
- Handle HTTP requests directly

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Implements | `ConfigurationPort` | Single outbound port for all modules |
| Reads | Filesystem / env vars | `config/` directory |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `ConfigurationPort` | Outbound (implemented) | `get(section)`, `get_string(key)`, `get_int(key)`, `require(key)` |
| Config sections | — | `app`, `database`, `ml`, `ocr`, `auth`, `logging` |

#### Folder Mapping

`infrastructure/config/loaders/` · `config/` (repo root) · `application/ports/outbound/`

---

### 14. Logging

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Provide **structured observability** — application logs, error traces, performance metrics — as a cross-cutting infrastructure concern. |
| **Primary layer** | Infrastructure |

#### Responsibilities

- Configure log formatters (JSON structured logs)
- Route logs to handlers (stdout, file, external aggregator _TBD_)
- Provide `LoggingPort` for modules to emit leveled, contextual messages
- Inject correlation ID and principal ID into log context
- Never log secrets or full plate images

#### Must NOT Do

- Store business audit events (→ History module)
- Make authorization decisions
- Expose logs via public REST API without auth _TBD_

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Implements | `LoggingPort` | Used by all modules |
| Reads | `ConfigurationPort` | Log level, output targets |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `LoggingPort` | Outbound (implemented) | `debug(msg, ctx)`, `info()`, `warning()`, `error()`, `with_context(correlation_id)` |

#### Folder Mapping

`infrastructure/logging/formatters/` · `infrastructure/logging/handlers/` · `infrastructure/logging/config/`

---

### 15. Notification (future)

| Attribute | Detail |
|-----------|--------|
| **Purpose** | **Deliver outbound alerts** to external channels (SMS, email, push, webhook) when risk or operational events require human attention. |
| **Primary layer** | Infrastructure (future) |
| **Status** | Planned — interfaces defined, implementation deferred |

#### Responsibilities

- Accept notification requests from Risk Engine and Alerting domain
- Route to appropriate channel adapter
- Track delivery status (sent, failed, retry)
- Apply rate limiting and escalation policies _TBD_

#### Must NOT Do

- Decide whether to alert (→ Risk Engine / Alerting domain)
- Store scan or verification data
- Authenticate officers

#### Dependencies

| Direction | Module / Port | Why |
|-----------|---------------|-----|
| Inbound | `NotificationPort` | Called by Risk Engine |
| Outbound | Channel adapters | SMS, email, push, webhook _TBD_ |
| Outbound | `HistoryPort` | Delivery audit |
| Outbound | `ConfigurationPort` | Channel credentials, templates |
| Outbound | `LoggingPort` | Delivery telemetry |

#### Public Interfaces (Ports)

| Port | Type | Contract Summary |
|------|------|------------------|
| `NotificationPort` | Outbound (future) | `send(NotificationRequest) → DeliveryStatus` |
| `NotificationRequest` | DTO | `{ channel, recipient, template, payload, priority }` |
| `DeliveryStatus` | DTO | `{ notification_id, status, sent_at, error? }` |

#### Folder Mapping

`infrastructure/messaging/publishers/` · `domain/alerting/` (policy) · _future:_ `infrastructure/notification/`

---

## Cross-Module Dependency Matrix

Rows depend on columns.

|  | Auth | Officer | Vehicle | Scan | OCR | Detect | Verify | Risk | Reports | Dash | Analytics | History | Config | Log | Notify |
|--|:----:|:-------:|:-------:|:----:|:---:|:------:|:------:|:----:|:-------:|:----:|:---------:|:-------:|:------:|:---:|:------:|
| **Auth** | — | ✓ | | | | | | | | | | ✓ | ✓ | ✓ | |
| **Officer** | | — | | | | | | | | | | ✓ | | ✓ | |
| **Vehicle** | | | — | | | | | | | | | ✓ | | ✓ | |
| **Scan** | | ✓ | | — | ✓ | ✓ | | | | | | ✓ | ✓ | ✓ | |
| **OCR** | | | | | — | | | | | | | | ✓ | ✓ | |
| **Detection** | | | | | | — | | | | | | | ✓ | ✓ | |
| **Verify** | | | ✓ | ✓ | | | — | | | | | ✓ | | ✓ | |
| **Risk** | | | | ✓ | | | ✓ | — | | | ✓ | ✓ | | ✓ | ✓ |
| **Reports** | | ✓ | | ✓ | | | ✓ | ✓ | — | | | ✓ | | ✓ | |
| **Dashboard** | ✓ | | | ✓ | | | ✓ | ✓ | | — | | | ✓ | | |
| **Analytics** | ✓ | | | | | | | | | | — | ✓ | ✓ | ✓ | |
| **History** | | | | | | | | | | | | — | ✓ | ✓ | |
| **Config** | | | | | | | | | | | | | — | | |
| **Logging** | | | | | | | | | | | | | ✓ | — | |

---

## Domain Isolation Guarantee

The following modules have **domain components** that must remain free of:

`FastAPI` · `SQLAlchemy` · `OpenCV` · `PaddleOCR` · `YOLO` · database drivers · any framework

| Module | Domain Package |
|--------|----------------|
| Officer | `domain/officer/` |
| Vehicle | `domain/vehicle/` |
| Vehicle Scan | `domain/vehicle_scan/` |
| Vehicle Verification | `domain/plate_verification/` |
| Risk Engine | `domain/clone_detection/`, `domain/risk/` |
| Reports | `domain/reporting/` |
| History | `domain/history/` |
| Notification (policy only) | `domain/alerting/` |

Infrastructure-only modules (no domain layer): **OCR**, **Plate Detection**, **Authentication**, **Configuration**, **Logging**, **Notification (delivery)**.

---

## Implementation Order (Recommended)

```
Phase 1 — Core pipeline
  Configuration → Logging → History
  → Plate Detection → OCR → Vehicle Scan
  → Vehicle → Vehicle Verification → Risk Engine

Phase 2 — Identity
  → Officer → Authentication

Phase 3 — Presentation
  → Dashboard → Analytics → Reports

Phase 4 — Future
  → Notification
```

---

## Related Documents

- [Architecture Overview](overview.md)
- [Bounded Contexts](bounded-contexts.md)
- [Hexagonal Ports & Adapters](hexagonal-ports-adapters.md)
- [Dependency Direction](dependency-direction.md)
- [Module Map (folders)](module-map.md)
