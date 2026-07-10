# Pipeline Stages — Detailed Specifications

Each stage: purpose, layer, inputs, outputs, persistence, and failure behavior.

---

## Stage 0: Vehicle Image (Ingestion)

### Purpose

Accept a raw vehicle image and scan metadata into the system. Validate input quality, create a scan session, and prepare the image for downstream ML stages. **No AI inference occurs here.**

### Layer & Module

| Layer | Module |
|-------|--------|
| Application + Domain | Vehicle Scan |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_bytes` | binary | one of | Raw image data |
| `image_storage_key` | string | one of | Pre-uploaded object store reference |
| `officer_id` | UUID | yes | Scanning officer |
| `scanned_at` | timestamp | yes | Capture time |
| `latitude` | decimal | no | GPS latitude |
| `longitude` | decimal | no | GPS longitude |
| `location_label` | string | no | Checkpoint name |
| `camera_id` | string | no | Device identifier |
| `correlation_id` | UUID | no | Trace ID (generated if absent) |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Created scan session identifier |
| `image_storage_key` | string | Confirmed storage location |
| `processing_status` | enum | `received` |
| `correlation_id` | UUID | Pipeline trace ID |

### Persistence

| Table | Action |
|-------|--------|
| `scan_history` | INSERT — status `received` |
| `audit_logs` | APPEND — `scan.created` |

### Validation Rules (Domain)

- Image format must be supported (JPEG, PNG — _list TBD_)
- Image minimum resolution _TBD_
- Officer must be `active`
- `scanned_at` must not be in the future

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| Invalid image format | Reject; status `failed`, reason `invalid_image_format` |
| Officer inactive | Reject; no scan created |
| Storage unavailable | Reject; retry eligible |

### Interface to Next Stage

→ Passes `ImageCapture` to **Plate Detection**

---

## Stage 1: Plate Detection

### Purpose

Locate the license plate region within the full vehicle image using object detection (YOLO). Returns bounding box coordinates and confidence. **Does not read characters.**

### Layer & Module

| Layer | Module |
|-------|--------|
| Infrastructure | Plate Detection (`infrastructure/ai/yolo/`) |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan session reference |
| `image_storage_key` | string | yes | Full image location |
| `detection_config` | object | no | Confidence threshold override |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `boxes` | array | `[{ x, y, width, height, confidence }]` |
| `primary_box` | object | Highest-confidence box selected for OCR |
| `crop_storage_key` | string | Stored plate crop image |
| `model_version` | string | YOLO model version tag |
| `detection_confidence` | decimal | Primary box confidence (0.0–1.0) |
| `plates_found` | integer | Count of detected regions |

### Persistence

| Table | Action |
|-------|--------|
| `scan_history` | UPDATE — `detection_confidence`, `crop_storage_key`, `processing_status` → `detecting` → `recognizing`, `ml_model_version` |
| `audit_logs` | APPEND — `detection.completed` or `detection.failed` |

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| No plate detected | Halt pipeline; status `failed`, reason `no_plate_detected` |
| Multiple plates | Use highest-confidence box; log others in `metadata` |
| Model inference error | Halt; status `failed`, reason `detection_error` |
| Confidence below threshold | Halt; status `failed`, reason `low_detection_confidence` |

### Interface from Previous

← Receives `ImageCapture` from **Vehicle Image**

### Interface to Next Stage

→ Passes `PlateDetectionResult` to **OCR**

---

## Stage 2: OCR (Optical Character Recognition)

### Purpose

Extract alphanumeric plate text from the plate crop image using PaddleOCR. Returns raw text, normalized text, and per-character confidence.

### Layer & Module

| Layer | Module |
|-------|--------|
| Infrastructure | OCR (`infrastructure/ocr/paddleocr/`) |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan session reference |
| `crop_storage_key` | string | yes | Plate crop from detection stage |
| `jurisdiction` | string | no | Hint for character set / format rules |
| `ocr_config` | object | no | Language, threshold overrides |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `raw_text` | string | Unprocessed OCR output |
| `normalized_plate_text` | string | Domain-normalized plate string |
| `ocr_confidence` | decimal | Overall recognition confidence |
| `char_confidences` | array | Per-character confidence scores |
| `model_version` | string | OCR model version tag |

### Persistence

| Table | Action |
|-------|--------|
| `scan_history` | UPDATE — `detected_plate_text`, `normalized_plate_text`, `ocr_confidence`, `processing_status` → `completed` (ML stages done) |
| `audit_logs` | APPEND — `ocr.completed` or `ocr.failed` |

### Post-OCR Normalization (Application → Domain)

Infrastructure returns `raw_text`. Application invokes domain `PlateNumber` value object for normalization (strip spaces, uppercase, jurisdiction format rules). Normalized result stored separately from raw.

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| Empty OCR result | Halt; status `failed`, reason `ocr_empty` |
| Confidence below threshold | Halt; reason `low_ocr_confidence` |
| Invalid plate format after normalization | Continue with flag `format_warning` in metadata |
| PaddleOCR runtime error | Halt; reason `ocr_error` |

### Interface from Previous

← Receives `PlateDetectionResult` from **Plate Detection**

### Interface to Next Stage

→ Passes `OcrResult` to **Vehicle Lookup**

---

## Stage 3: Vehicle Lookup

### Purpose

Query the vehicle registry using the normalized plate text. Retrieve authoritative vehicle registration record for comparison. Returns match status and vehicle master data.

### Layer & Module

| Layer | Module |
|-------|--------|
| Application + Infrastructure | Vehicle, Vehicle Verification |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan session reference |
| `normalized_plate_text` | string | yes | Plate from OCR stage |
| `jurisdiction` | string | no | State/region code |
| `force_refresh` | boolean | no | Bypass local cache, hit external registry |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `lookup_status` | enum | `found`, `not_found`, `registry_unavailable` |
| `vehicle_id` | UUID | Local `vehicles` record ID (if found) |
| `vehicle_record` | object | `{ plate, make, model, color, year, type, registration_status, owner }` |
| `registry_external_id` | string | External RTO reference |
| `registry_synced_at` | timestamp | Cache freshness |

### Persistence

| Table | Action |
|-------|--------|
| `vehicles` | UPSERT — sync registry data to local cache |
| `scan_history` | UPDATE — `vehicle_id` if matched |
| `verification_results` | INSERT — preliminary `outcome_status` |
| `audit_logs` | APPEND — `lookup.completed` or `lookup.failed` |

### Lookup Strategy

```
1. Query local vehicles table by (plate, jurisdiction)
2. If stale or force_refresh → call VehicleRegistryPort (external RTO)
3. Upsert local cache
4. Return VehicleLookupResult
```

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| Plate not in registry | Continue pipeline; `lookup_status = not_found` |
| Registry API timeout | `lookup_status = registry_unavailable`; continue with degraded mode |
| Registry API error | Retry _N_ times; then degraded mode |
| Invalid jurisdiction | Halt; reason `invalid_jurisdiction` |

### Interface from Previous

← Receives `OcrResult` from **OCR**

### Interface to Next Stage

→ Passes `VehicleLookupResult` to **Vehicle Attribute Analysis**

---

## Stage 4: Vehicle Attribute Analysis

### Purpose

Compare **observed vehicle attributes** (from image analysis and scan context) against **registry attributes** (from lookup). Detect mismatches that may indicate cloned plates, wrong vehicles, or data errors. **Domain rules only — no ML required**, though optional visual attribute extraction from image may be added later.

### Layer & Module

| Layer | Module |
|-------|--------|
| Domain + Application | Vehicle Verification (extended) |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan reference |
| `normalized_plate_text` | string | yes | Recognized plate |
| `vehicle_record` | object | no | From lookup (null if not found) |
| `observed_attributes` | object | no | `{ color, type, make }` — from future CV or officer input |
| `ocr_confidence` | decimal | yes | Passed through for weighting |
| `detection_confidence` | decimal | yes | Passed through for weighting |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `verification_id` | UUID | Verification record ID |
| `outcome_status` | enum | `valid`, `invalid`, `unknown`, `expired`, `not_found` |
| `mismatch_reasons` | array | `[{ code, field, expected, observed, severity }]` |
| `attribute_match_score` | decimal | 0.0–1.0 composite match score |
| `verified_at` | timestamp | Verification completion time |

### Mismatch Reason Codes (Domain)

| Code | Condition |
|------|-----------|
| `PLATE_NOT_IN_REGISTRY` | Lookup returned not_found |
| `REGISTRATION_EXPIRED` | `registration_status = expired` |
| `REGISTRATION_STOLEN` | `registration_status = stolen` |
| `COLOR_MISMATCH` | Observed color ≠ registry color |
| `TYPE_MISMATCH` | Observed vehicle type ≠ registry type |
| `MAKE_MISMATCH` | Observed make ≠ registry make |
| `LOW_OCR_CONFIDENCE` | OCR confidence below verification threshold |

### Persistence

| Table | Action |
|-------|--------|
| `verification_results` | UPDATE — `outcome_status`, `mismatch_reasons`, `verified_at` |
| `audit_logs` | APPEND — `verification.completed` |

### Future Extension

Optional `infrastructure/ai/` visual attribute extractor (color, vehicle class) feeding `observed_attributes`. Interface unchanged — port `VisualAttributeExtractorPort` _TBD_.

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| No vehicle record | `outcome_status = not_found`; continue to Risk Engine |
| Stolen vehicle | `outcome_status = invalid`; flag high severity; continue |
| Attribute mismatch | `outcome_status = invalid`; continue with mismatch reasons |

### Interface from Previous

← Receives `VehicleLookupResult` + scan confidences from **Vehicle Lookup**

### Interface to Next Stage

→ Passes `AttributeAnalysisResult` to **Risk Engine**

---

## Stage 5: Risk Engine

### Purpose

Score fraud and cloned-plate risk by correlating the current scan with historical sightings, verification outcome, and attribute mismatches. Produce an explainable risk assessment.

### Layer & Module

| Layer | Module |
|-------|--------|
| Domain + Application | Risk Engine |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan reference |
| `normalized_plate_text` | string | yes | Plate for correlation |
| `verification_outcome` | object | yes | From attribute analysis |
| `vehicle_id` | UUID | no | Matched vehicle |
| `scan_metadata` | object | yes | `{ location, scanned_at, officer_id, confidences }` |
| `correlation_window_hours` | integer | no | Historical lookback (default from config) |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `assessment_id` | UUID | Risk assessment record ID |
| `risk_score` | decimal | 0.0–1.0 composite score |
| `clone_suspected` | boolean | `true` if score ≥ threshold |
| `signals` | array | `[{ name, weight, detail, contribution }]` |
| `policy_version` | string | Risk policy version used |
| `assessed_at` | timestamp | Assessment time |

### Risk Signals (Domain Policy)

| Signal | Trigger | Weight (_TBD_) |
|--------|---------|----------------|
| `DUPLICATE_PLATE_DIFFERENT_LOCATION` | Same plate sighted far away within window | High |
| `DUPLICATE_PLATE_DIFFERENT_VEHICLE_TYPE` | Correlated sighting with type mismatch | High |
| `ATTRIBUTE_MISMATCH` | From verification stage | Medium |
| `LOW_OCR_CONFIDENCE` | OCR below threshold but above halt | Medium |
| `REGISTRATION_STOLEN` | Stolen flag on vehicle | Critical |
| `PLATE_NOT_IN_REGISTRY` | No registry match | Medium |
| `RAPID_RESCAN` | Same plate scanned multiple times in short window | Low |

### Persistence

| Table | Action |
|-------|--------|
| `risk_assessments` | INSERT |
| `vehicle_alerts` | INSERT if `clone_suspected` or critical signal |
| `audit_logs` | APPEND — `risk.assessed` |

### Correlation Query

Risk Engine calls `HistoryQueryPort.find_sightings_by_plate(plate, window)` → queries `scan_history` indexed by `normalized_plate_text` + `scanned_at`.

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| History unavailable | Assess with available signals only; flag `degraded_assessment` |
| Policy error | Halt; reason `risk_policy_error` |

### Interface from Previous

← Receives `AttributeAnalysisResult` from **Attribute Analysis**

### Interface to Next Stage

→ Passes `RiskAssessmentResult` to **Decision**

---

## Stage 6: Decision

### Purpose

Apply domain decision policy to produce a final **actionable pipeline outcome**. Determines officer-facing recommendation: proceed, investigate, detain, or dismiss. Triggers alerts if not already raised.

### Layer & Module

| Layer | Module |
|-------|--------|
| Domain + Application | Orchestration + Domain Policy |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan reference |
| `verification_outcome` | object | yes | From attribute analysis |
| `risk_assessment` | object | yes | From risk engine |
| `existing_alerts` | array | no | Alerts already created in risk stage |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `decision` | enum | `clear`, `monitor`, `investigate`, `detain`, `escalate` |
| `decision_reasons` | array | Human-readable justification strings |
| `alert_ids` | array | Any alerts created or linked |
| `requires_report` | boolean | Whether investigation report is recommended |
| `decided_at` | timestamp | Decision time |

### Decision Matrix (Domain Policy)

| Verification | Risk Score | Clone Suspected | Decision |
|--------------|------------|-----------------|----------|
| valid | < 0.3 | no | `clear` |
| valid | 0.3–0.7 | no | `monitor` |
| valid | ≥ 0.7 | yes | `investigate` |
| invalid | any | no | `investigate` |
| invalid | ≥ 0.5 | yes | `detain` |
| not_found | ≥ 0.4 | no | `investigate` |
| any + stolen | any | — | `escalate` |

_Thresholds configurable via Configuration module — `policy_version` tracked._

### Persistence

| Table | Action |
|-------|--------|
| `scan_history` | UPDATE — `completed_at`, final `metadata` with decision |
| `vehicle_alerts` | INSERT if decision ≥ `investigate` and no alert exists |
| `audit_logs` | APPEND — `decision.made` |

### Notification Hook (Future)

If `decision` ∈ `{ detain, escalate }` → call `NotificationPort` (future module).

### Interface from Previous

← Receives `RiskAssessmentResult` + `AttributeAnalysisResult` from **Risk Engine**

### Interface to Next Stage

→ Passes `PipelineDecision` to **Investigation Report** (if `requires_report = true`)

---

## Stage 7: Investigation Report

### Purpose

Compose and export a formal PDF investigation document aggregating all pipeline stage outputs. **Triggered on demand** — not automatic for every scan (only when decision recommends or officer requests).

### Layer & Module

| Layer | Module |
|-------|--------|
| Application + Infrastructure | Reports |

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scan_id` | UUID | yes | Scan to document |
| `officer_id` | UUID | yes | Requesting/generating officer |
| `report_type` | enum | yes | `field_summary`, `full_investigation`, `incident` |
| `template_version` | string | no | Default from config |
| `pipeline_decision` | object | yes | From decision stage |
| `include_images` | boolean | no | Embed scan images in PDF |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | UUID | Report record ID |
| `scan_id` | UUID | Source scan |
| `storage_key` | string | PDF object store location |
| `checksum_sha256` | string | File integrity hash |
| `file_size_bytes` | integer | PDF size |
| `status` | enum | `generated` |
| `generated_at` | timestamp | Generation time |
| `download_url` | string | Signed URL _TBD_ |

### Report Content Sections

| Section | Source Stage |
|---------|-------------|
| Scan metadata | Vehicle Image |
| Detection overlay | Plate Detection |
| OCR result | OCR |
| Registry record | Vehicle Lookup |
| Verification outcome | Attribute Analysis |
| Risk assessment + signals | Risk Engine |
| Final decision | Decision |
| Officer attribution | Officer module |

### Persistence

| Table | Action |
|-------|--------|
| `investigation_reports` | INSERT |
| `audit_logs` | APPEND — `report.generated` |

### Failure Modes

| Condition | Behavior |
|-----------|----------|
| PDF generation failure | Status `draft`; retry eligible |
| Missing scan data | Reject; reason `incomplete_scan_data` |
| Storage failure | Retry; alert operations |

### Interface from Previous

← Receives `PipelineDecision` + all stage artifacts (loaded from DB by `scan_id`)

---

## Stage Summary Table

| # | Stage | AI/ML? | Layer | Persists To |
|---|-------|--------|-------|-------------|
| 0 | Vehicle Image | No | Application | `scan_history` |
| 1 | Plate Detection | **Yes** (YOLO) | Infrastructure | `scan_history` |
| 2 | OCR | **Yes** (PaddleOCR) | Infrastructure | `scan_history` |
| 3 | Vehicle Lookup | No | Infrastructure | `vehicles`, `verification_results` |
| 4 | Attribute Analysis | No (future CV optional) | Domain | `verification_results` |
| 5 | Risk Engine | No (rule-based) | Domain | `risk_assessments`, `vehicle_alerts` |
| 6 | Decision | No | Domain | `scan_history`, `vehicle_alerts` |
| 7 | Investigation Report | No | Infrastructure | `investigation_reports` |

---

## Related

- [Pipeline Interfaces](pipeline-interfaces.md)
- [Pipeline Orchestration](pipeline-orchestration.md)
