# Pipeline Orchestration

How stages are coordinated, state transitions, error paths, and execution modes.

---

## Orchestrator

| Attribute | Value |
|-----------|-------|
| **Use case** | `ProcessPlatePipelineUseCase` |
| **Location** | `application/use_cases/orchestration/` |
| **Trigger** | REST API, CLI, or message consumer via `VehicleScanCommandPort` |

The orchestrator is the **only component** that sequences all eight stages. Individual stages do not call each other directly.

---

## State Machine

```
                    ┌───────────┐
                    │  received │
                    └─────┬─────┘
                          │ Stage 0 complete
                          ▼
                    ┌───────────┐
              ┌────▶│ detecting │◀── Stage 1 running
              │     └─────┬─────┘
              │           │ detection OK
              │           ▼
              │     ┌─────────────┐
              │     │ recognizing │◀── Stage 2 running
              │     └──────┬──────┘
              │            │ OCR OK
              │            ▼
              │     ┌─────────────┐
              │     │  verifying  │◀── Stages 3–4
              │     └──────┬──────┘
              │            │
              │            ▼
              │     ┌─────────────┐
              │     │  assessing  │◀── Stage 5
              │     └──────┬──────┘
              │            │
              │            ▼
              │     ┌─────────────┐
              │     │  deciding   │◀── Stage 6
              │     └──────┬──────┘
              │            │
              │            ▼
              │     ┌─────────────┐
              │     │  completed  │◀── Pipeline done
              │     └──────┬──────┘
              │            │ (optional)
              │            ▼
              │     ┌─────────────┐
              │     │  reporting  │◀── Stage 7 (on demand)
              │     └─────────────┘
              │
              │     ┌─────────────┐
              └─────│   failed    │◀── Any stage fatal error
                    └─────────────┘
```

### Status → Stage Mapping

| `processing_status` | Active Stage(s) |
|---------------------|-----------------|
| `received` | 0 — Vehicle Image |
| `detecting` | 1 — Plate Detection |
| `recognizing` | 2 — OCR |
| `verifying` | 3–4 — Lookup + Attribute Analysis |
| `assessing` | 5 — Risk Engine |
| `deciding` | 6 — Decision |
| `completed` | Pipeline finished |
| `reporting` | 7 — Investigation Report (optional) |
| `failed` | Halted — see `failure_reason` |

---

## Sequential Execution Flow

```
ProcessPlatePipelineUseCase.execute(command):

  1. STAGE 0  → ingest image, create scan_id
  2. STAGE 1  → plateDetectionPort.detect(ImageCapture)
  3. STAGE 2  → ocrPort.recognize(PlateDetectionResult)
  4. STAGE 3  → vehicleRegistryPort.lookup(OcrResult)
  5. STAGE 4  → verificationCommandPort.analyze(VehicleLookupResult)
  6. STAGE 5  → riskAssessmentPort.assess(AttributeAnalysisResult)
  7. STAGE 6  → decisionPolicyPort.decide(RiskAssessmentResult)
  8. STAGE 7  → reportCommandPort.generate(PipelineDecision)  [if requires_report]

  Each step:
    - Update scan_history.processing_status
    - Persist stage output to appropriate table
    - Append audit_logs entry
    - On fatal error → set status failed, halt
```

---

## Error Handling Strategy

### Fatal Errors (Pipeline Halts)

| Stage | Error Code | Retry? |
|-------|------------|--------|
| 0 | `invalid_image_format` | No |
| 0 | `storage_unavailable` | Yes |
| 1 | `no_plate_detected` | No |
| 1 | `detection_error` | Yes |
| 2 | `ocr_empty` | No |
| 2 | `ocr_error` | Yes |
| 3 | `invalid_jurisdiction` | No |
| 5 | `risk_policy_error` | Yes |
| 7 | `pdf_generation_error` | Yes |

### Non-Fatal Conditions (Pipeline Continues)

| Stage | Condition | Behavior |
|-------|-----------|----------|
| 3 | Plate not in registry | `lookup_status = not_found`; continue |
| 3 | Registry unavailable | Degraded mode; continue with warning |
| 4 | Attribute mismatch | `outcome_status = invalid`; continue |
| 4 | Stolen vehicle | Flag + continue to risk |
| 5 | History unavailable | Degraded assessment; continue |
| 6 | — | Decision always produced |

---

## Execution Modes

### Synchronous (Default for REST API)

All stages run in a single request thread. Officer receives final `PipelineDecision` in response.

| Attribute | Value |
|-----------|-------|
| Latency budget | _TBD_ (sum of all stage SLAs) |
| Timeout | Configurable per stage |
| Best for | Single image upload, field use |

### Asynchronous (Future — Message Queue)

Each stage completion publishes an event; next stage consumer picks up.

| Event | Triggers Stage |
|-------|---------------|
| `ScanReceived` | 1 — Detection |
| `PlateDetected` | 2 — OCR |
| `PlateRecognized` | 3–4 — Lookup + Verification |
| `PlateVerified` | 5 — Risk |
| `RiskAssessed` | 6 — Decision |
| `DecisionMade` | 7 — Report (if needed) |

Enables horizontal scaling of ML inference workers.

---

## Cross-Cutting Concerns

| Concern | Applied At | Mechanism |
|---------|------------|-----------|
| **Logging** | Every stage transition | `LoggingPort` with `correlation_id` |
| **Audit** | Every stage completion | `HistoryCommandPort.append()` |
| **Configuration** | Thresholds, timeouts | `ConfigurationPort` |
| **Auth** | Pipeline entry only | `AuthorizePort` — officer must be authenticated |
| **Metrics** | Every stage | Latency, success/failure counters _TBD_ |

---

## Composition Root Wiring

```
interfaces/dependency_injection/wiring/
  ├── binds PlateDetectionPort  → YoloPlateDetectorAdapter
  ├── binds OcrPort             → PaddleOcrAdapter
  ├── binds VehicleRegistryPort → VehicleRegistryClient
  ├── binds PdfGeneratorPort    → PdfGeneratorAdapter
  └── binds ProcessPlatePipelineUseCase → all ports injected
```

Only the composition root references concrete infrastructure classes.

---

## Testing Strategy

| Test Level | Approach |
|------------|----------|
| **Unit** | Each stage use case with fake ports |
| **Integration** | Real YOLO/OCR adapters against fixture images |
| **Pipeline E2E** | Full orchestrator with in-memory fakes → expected `PipelineDecision` |
| **Contract** | Verify each port input/output matches interface spec |

Fixture images: `tests/fixtures/data/images/`

---

## Performance Considerations (_TBD at implementation_)

| Stage | Expected Bottleneck | Mitigation |
|-------|---------------------|------------|
| 1 — Detection | GPU inference | Model quantization, batching |
| 2 — OCR | CPU/GPU inference | Crop-only input (small image) |
| 3 — Lookup | External API latency | Local cache (`vehicles` table) |
| 5 — Risk | DB correlation query | Index on `(normalized_plate_text, scanned_at)` |
| 7 — Report | PDF rendering | Async generation, background job |

---

## Related

- [Pipeline Stages](pipeline-stages.md)
- [Pipeline Interfaces](pipeline-interfaces.md)
- [Module Architecture](../architecture/modules.md)
