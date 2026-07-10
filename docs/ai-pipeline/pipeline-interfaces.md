# Pipeline Interfaces — Port Contracts

Interface definitions between pipeline stages. **Contracts only — no implementation.**

Each interface is an **outbound port** in `application/ports/outbound/` implemented by infrastructure, or an **application use case** boundary between orchestrated steps.

---

## Interface Map

```
Stage 0 ──ImageCapture─────────────────────────────▶ Stage 1
Stage 1 ──PlateDetectionResult─────────────────────▶ Stage 2
Stage 2 ──OcrResult────────────────────────────────▶ Stage 3
Stage 3 ──VehicleLookupResult──────────────────────▶ Stage 4
Stage 4 ──AttributeAnalysisResult──────────────────▶ Stage 5
Stage 5 ──RiskAssessmentResult─────────────────────▶ Stage 6
Stage 6 ──PipelineDecision─────────────────────────▶ Stage 7
```

---

## 0 → 1: ImageCapture

**Producer:** `IngestImageUseCase`  
**Consumer:** `PlateDetectionPort`  
**Direction:** Application → Infrastructure

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `image_storage_key` | string | Full image object store key |
| `correlation_id` | UUID | Pipeline trace ID |
| `metadata` | object | `{ scanned_at, officer_id, location, camera_id }` |

---

## 1 → 2: PlateDetectionResult

**Producer:** `PlateDetectionPort` (YOLO adapter)  
**Consumer:** `OcrPort`  
**Direction:** Infrastructure → Infrastructure (via orchestrator)

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `crop_storage_key` | string | Cropped plate image key |
| `primary_box` | object | `{ x, y, width, height, confidence }` |
| `boxes` | array | All detected regions |
| `detection_confidence` | decimal | Primary box confidence |
| `model_version` | string | YOLO model version |
| `plates_found` | integer | Detection count |

---

## 2 → 3: OcrResult

**Producer:** `OcrPort` (PaddleOCR adapter)  
**Consumer:** `VehicleLookupPort`  
**Direction:** Infrastructure → Application

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `raw_text` | string | Unprocessed OCR output |
| `normalized_plate_text` | string | Domain-normalized plate |
| `ocr_confidence` | decimal | Overall confidence |
| `char_confidences` | array | Per-character scores |
| `model_version` | string | OCR model version |

---

## 3 → 4: VehicleLookupResult

**Producer:** `VehicleRegistryPort` + `VehicleRepositoryPort`  
**Consumer:** `VerificationCommandPort` (attribute analysis)  
**Direction:** Infrastructure → Application

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `lookup_status` | enum | `found`, `not_found`, `registry_unavailable` |
| `vehicle_id` | UUID | Local vehicle record ID |
| `vehicle_record` | VehicleRecord | Registry attributes |
| `registry_external_id` | string | External RTO ID |
| `registry_synced_at` | timestamp | Cache timestamp |

### VehicleRecord (embedded)

| Field | Type |
|-------|------|
| `plate_number` | string |
| `make` | string |
| `model` | string |
| `color` | string |
| `year` | integer |
| `vehicle_type` | string |
| `registration_status` | enum |
| `registered_owner` | string |

---

## 4 → 5: AttributeAnalysisResult

**Producer:** `VerifyPlateUseCase`  
**Consumer:** `RiskAssessmentCommandPort`  
**Direction:** Application → Application

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `verification_id` | UUID | Verification record ID |
| `outcome_status` | enum | `valid`, `invalid`, `unknown`, `expired`, `not_found` |
| `mismatch_reasons` | array | `[{ code, field, expected, observed, severity }]` |
| `attribute_match_score` | decimal | 0.0–1.0 |
| `vehicle_id` | UUID | Matched vehicle (nullable) |
| `verified_at` | timestamp | Completion time |

---

## 5 → 6: RiskAssessmentResult

**Producer:** `DetectCloneUseCase` / `RiskAssessmentCommandPort`  
**Consumer:** `DecisionPolicyPort`  
**Direction:** Application → Domain

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `assessment_id` | UUID | Assessment record ID |
| `risk_score` | decimal | 0.0–1.0 |
| `clone_suspected` | boolean | Threshold breach |
| `signals` | array | `[{ name, weight, detail, contribution }]` |
| `policy_version` | string | Policy version |
| `assessed_at` | timestamp | Assessment time |
| `alert_id` | UUID | Alert created if flagged (nullable) |

---

## 6 → 7: PipelineDecision

**Producer:** `DecisionPolicyPort` / `ProcessPlatePipelineUseCase`  
**Consumer:** `ReportCommandPort`  
**Direction:** Domain → Application

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan session ID |
| `decision` | enum | `clear`, `monitor`, `investigate`, `detain`, `escalate` |
| `decision_reasons` | array | Justification strings |
| `alert_ids` | array | Linked alert UUIDs |
| `requires_report` | boolean | Report recommended |
| `decided_at` | timestamp | Decision time |

---

## Port Registry (Outbound)

All infrastructure-facing ports invoked by the orchestrator:

| Port | Stage | Implemented By |
|------|-------|----------------|
| `ImageStoragePort` | 0 | `infrastructure/database/` or object store |
| `PlateDetectionPort` | 1 | `infrastructure/ai/yolo/` |
| `OcrPort` | 2 | `infrastructure/ocr/paddleocr/` |
| `VehicleRegistryPort` | 3 | `infrastructure/external/vehicle_registry/` |
| `VehicleRepositoryPort` | 3 | `infrastructure/database/repositories/` |
| `HistoryQueryPort` | 5 | `infrastructure/database/repositories/` |
| `PdfGeneratorPort` | 7 | `infrastructure/pdf/` |
| `LoggingPort` | All | `infrastructure/logging/` |
| `ConfigurationPort` | All | `infrastructure/config/` |

### Port Registry (Application / Domain)

| Port | Stage | Owner |
|------|-------|-------|
| `VerificationCommandPort` | 4 | `application/verification/` |
| `RiskAssessmentCommandPort` | 5 | `application/risk/` |
| `DecisionPolicyPort` | 6 | `domain/` or `application/orchestration/` |
| `ReportCommandPort` | 7 | `application/reporting/` |
| `HistoryCommandPort` | All | `application/history/` |

---

## Optional Future Port

| Port | Stage | Purpose |
|------|-------|---------|
| `VisualAttributeExtractorPort` | 4 | CV-based color/type extraction from image |
| `NotificationPort` | 6 | Alert delivery on `detain`/`escalate` |

---

## Interface Versioning

| Field | Location | Purpose |
|-------|----------|---------|
| `contract_version` | Each result object | Breaking change detection |
| `model_version` | ML stage outputs | Reproducibility |
| `policy_version` | Risk + Decision outputs | Audit trail |

---

## Error Contract (All Stages)

Every stage failure returns a standardized envelope:

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan reference |
| `stage` | string | Failed stage name |
| `success` | boolean | `false` |
| `error_code` | string | Machine-readable code |
| `error_message` | string | Human-readable message |
| `retry_eligible` | boolean | Whether pipeline can be retried |
| `correlation_id` | UUID | Trace ID |

---

## Related

- [Pipeline Stages](pipeline-stages.md)
- [Pipeline Orchestration](pipeline-orchestration.md)
