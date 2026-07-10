# Phase 1 — Domain Layer

**Path:** `src/sentinel_anpr/domain/`  
**Rule:** Zero imports from application, infrastructure, interfaces, or frameworks.

Implement in sub-phase order: **common → contexts → cross-context policies**.

---

## 1.1 Common Kernel

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/__init__.py` | Package marker | — | Root of innermost layer |
| `domain/common/__init__.py` | Subpackage marker | — | |
| `domain/common/exceptions/domain_error.py` | Base domain exception | — | All context errors extend this |
| `domain/common/exceptions/invalid_plate_format_error.py` | Plate format violation | `domain_error` | Used by PlateNumber VO |
| `domain/common/exceptions/officer_not_active_error.py` | Officer duty rule violation | `domain_error` | Scan attribution rules |
| `domain/common/value_objects/plate_number.py` | Normalized plate; format invariants | `invalid_plate_format_error` | Core ubiquitous language |
| `domain/common/value_objects/confidence_score.py` | 0.0–1.0 validated score | — | OCR/detection/risk |
| `domain/common/value_objects/jurisdiction.py` | Region code (AP, TS, …) | — | Lookup + verification |
| `domain/common/value_objects/entity_id.py` | Typed UUID wrapper base | — | Strong IDs |
| `domain/common/events/domain_event.py` | Base event with `occurred_at` | — | Event sourcing prep |
| `domain/common/enums/processing_status.py` | Scan lifecycle states | — | Shared by vehicle_scan |
| `domain/common/enums/decision.py` | clear, monitor, investigate, detain, escalate | — | Decision policy |
| `domain/common/enums/severity.py` | low → critical | — | Alerts, mismatches |

---

## 1.2 Officer Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/officer/__init__.py` | Package marker | — | |
| `domain/officer/entities/officer.py` | Officer identity, rank, status | `entity_id`, enums | Scan attribution |
| `domain/officer/value_objects/badge_number.py` | Badge validation | — | Officer identity |
| `domain/officer/value_objects/station_assignment.py` | Station binding | `jurisdiction` | Scope rules |
| `domain/officer/services/officer_policy.py` | Active-duty check | `officer` entity | Domain rule before scan |

---

## 1.3 Vehicle Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/vehicle/__init__.py` | Package marker | — | |
| `domain/vehicle/entities/vehicle_record.py` | Registry vehicle attributes | `plate_number`, `jurisdiction` | Verification comparison |
| `domain/vehicle/enums/registration_status.py` | active, stolen, expired, … | — | Verification outcomes |
| `domain/vehicle/enums/vehicle_type.py` | car, motorcycle, truck | — | Attribute analysis |
| `domain/vehicle/services/vehicle_invariants.py` | Plate–vehicle binding rules | `vehicle_record` | Domain integrity |

---

## 1.4 Ingestion Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/ingestion/__init__.py` | Package marker | — | |
| `domain/ingestion/entities/capture.py` | Image intake metadata | `processing_status` | Pipeline stage 0 |
| `domain/ingestion/value_objects/geo_location.py` | Lat/long + label | — | Scan metadata |
| `domain/ingestion/value_objects/camera_source.py` | Device identifier | — | Audit trail |
| `domain/ingestion/events/capture_received.py` | Domain event | `domain_event` | History integration |
| `domain/ingestion/services/capture_validator.py` | Image metadata rules | `capture` | Pre-ML validation |

---

## 1.5 Vehicle Scan Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/vehicle_scan/__init__.py` | Package marker | — | |
| `domain/vehicle_scan/entities/scan_session.py` | Scan aggregate root | `capture`, `plate_number`, `processing_status` | Central pipeline entity |
| `domain/vehicle_scan/value_objects/scan_metadata.py` | Correlation, timestamps | — | Tracing |
| `domain/vehicle_scan/events/scan_started.py` | Event | `domain_event` | Audit |
| `domain/vehicle_scan/events/scan_completed.py` | Event | `domain_event` | Audit |
| `domain/vehicle_scan/events/scan_failed.py` | Event | `domain_event` | Error path |
| `domain/vehicle_scan/services/scan_state_machine.py` | Valid status transitions | `processing_status` | Orchestration rules |

---

## 1.6 Plate Recognition Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/plate_recognition/__init__.py` | Package marker | — | |
| `domain/plate_recognition/entities/recognition_result.py` | OCR outcome entity | `plate_number`, `confidence_score` | Post-OCR domain object |
| `domain/plate_recognition/value_objects/bounding_box.py` | Detection region | — | YOLO result mapping |
| `domain/plate_recognition/services/plate_text_policy.py` | Post-OCR cleanup rules | `plate_number` | Between OCR and lookup |

---

## 1.7 Plate Verification Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/plate_verification/__init__.py` | Package marker | — | |
| `domain/plate_verification/entities/verification_outcome.py` | Verification result | `vehicle_record`, enums | Stage 4 output |
| `domain/plate_verification/value_objects/mismatch_reason.py` | Structured mismatch | `severity` | Explainability |
| `domain/plate_verification/enums/outcome_status.py` | valid, invalid, not_found, … | — | API + DB |
| `domain/plate_verification/services/verification_policy.py` | Compare observed vs registry | `verification_outcome` | Attribute analysis |
| `domain/plate_verification/services/attribute_matcher.py` | Color/type/make comparison | `mismatch_reason` | Clone signal input |

---

## 1.8 Risk / Clone Detection Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/clone_detection/__init__.py` | Package marker | — | |
| `domain/clone_detection/entities/clone_risk_assessment.py` | Risk aggregate | `confidence_score` | Risk engine output |
| `domain/clone_detection/value_objects/risk_signal.py` | Named signal + weight | `severity` | Explainability |
| `domain/clone_detection/services/clone_detection_policy.py` | Correlation scoring rules | `risk_signal` | Pure risk logic |
| `domain/clone_detection/services/risk_threshold_policy.py` | clone_suspected threshold | — | Configurable via app layer |

---

## 1.9 Decision Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/decision/__init__.py` | Package marker | — | |
| `domain/decision/entities/pipeline_decision.py` | Final actionable outcome | `decision` enum | Stage 6 output |
| `domain/decision/services/decision_policy.py` | Decision matrix | `verification_outcome`, `clone_risk_assessment` | Business rules for officer action |
| `domain/decision/value_objects/decision_reason.py` | Human justification | — | UI + reports |

---

## 1.10 Alerting Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/alerting/__init__.py` | Package marker | — | |
| `domain/alerting/entities/alert.py` | Alert entity | `severity`, status enums | Dashboard triage |
| `domain/alerting/enums/alert_type.py` | clone_suspected, stolen, … | — | DB + API |
| `domain/alerting/enums/alert_status.py` | open, acknowledged, resolved | — | Workflow |
| `domain/alerting/services/alert_policy.py` | When to raise alert | `pipeline_decision` | Separates alert rules from risk |

---

## 1.11 Reporting Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/reporting/__init__.py` | Package marker | — | |
| `domain/reporting/entities/report_spec.py` | Required report sections | — | PDF content rules |
| `domain/reporting/enums/report_type.py` | field_summary, full_investigation | — | API |
| `domain/reporting/services/report_content_policy.py` | Mandatory fields per type | `report_spec` | Before PDF generator |

---

## 1.12 History Context

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `domain/history/__init__.py` | Package marker | — | |
| `domain/history/entities/audit_event.py` | Immutable audit record | `domain_event` | Append-only log |
| `domain/history/enums/audit_action.py` | create, verify, assess, … | — | DB + API |
| `domain/history/enums/entity_type.py` | scan, vehicle, alert, … | — | Polymorphic audit |

---

## Phase 1 Exit Gate

- [ ] All domain unit tests pass with **zero mocks**
- [ ] `import-linter` / custom script confirms no forbidden imports
- [ ] Every enum/value object used by ports is defined

**Next:** [02-ports.md](02-ports.md)
