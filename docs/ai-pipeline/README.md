# AI Pipeline Architecture — SentinelANPR AI

**Version:** 0.1.0 (Foundation)  
**Status:** Architecture only — no model code or inference implementation

---

## Purpose

Define the end-to-end **ANPR intelligence pipeline** from raw vehicle image to investigation report. Each stage has a single responsibility, explicit inputs/outputs, and port-based interfaces enabling independent testing and technology substitution.

---

## Pipeline Overview (current runtime)

The verification workflow uses a single **Vision AI** stage (Hugging Face Inference API by default) instead of separate YOLO + OCR adapters.

```
┌─────────────────┐
│  Vehicle Image  │  Ingestion / upload
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Vision AI     │  Hugging Face (or stub) — plate + attributes
└────────┬────────┘
         │ registration_number, confidence, attributes
         ▼
┌─────────────────┐
│ Vehicle Lookup  │  Registry verification
└────────┬────────┘
         ▼
┌─────────────────┐
│  Risk Engine    │  Clone / mismatch scoring
└────────┬────────┘
         ▼
┌─────────────────┐
│ Investigation   │  Persist + report
│     Report      │
└─────────────────┘
```

**Configuration:** `SENTINEL_VISION_PROVIDER=huggingface`, `HF_TOKEN`, `HF_MODEL`, `HF_API_URL`.  
See [configuration-strategy.md](../architecture/configuration-strategy.md). Historical stage specs below still describe the earlier YOLO/OCR design for reference.

---

## Design Principles

| Principle | Application |
|-----------|-------------|
| **Stage isolation** | Each stage communicates only via defined port contracts |
| **Fail-fast with context** | Failed stages set `processing_status` and `failure_reason`; pipeline halts or branches |
| **Immutable scan facts** | Each stage appends results; does not mutate prior stage outputs |
| **Domain purity** | Stages 4–6 apply business rules in domain/application — no ML frameworks |
| **Async-ready** | Stages may run synchronously (API) or via message queue between stages |
| **Audit everything** | Every stage transition writes to `audit_logs` and updates `scan_history` |

---

## Documents

| File | Description |
|------|-------------|
| [pipeline-stages.md](pipeline-stages.md) | Detailed stage specifications |
| [pipeline-interfaces.md](pipeline-interfaces.md) | Port contracts between stages |
| [pipeline-orchestration.md](pipeline-orchestration.md) | Orchestrator, state machine, error paths |

---

## Layer Placement (current runtime)

| Stage | Layer | Module |
|-------|-------|--------|
| Vehicle Image | Application + Domain | Vehicle Scan / upload |
| Vision AI | Infrastructure | `HuggingFaceVisionService` / stub (`VisionAiService` port) |
| Vehicle Lookup | Application + Infrastructure | Vehicle verification |
| Risk Engine | Domain + Application | Risk Engine |
| Investigation Report | Application + Infrastructure | Reports |

---

## Orchestrator

The **ProcessPlatePipelineUseCase** (`application/use_cases/orchestration/`) coordinates all stages sequentially. It:

1. Creates `scan_history` record (status: `received`)
2. Invokes each stage via outbound ports
3. Persists intermediate results to child tables
4. Emits domain events and audit log entries per transition
5. Produces final `PipelineDecision`

See [pipeline-orchestration.md](pipeline-orchestration.md).

---

## Related

- [Module Architecture](../architecture/modules.md)
- [Database Schema](../database/schema-design.md)
- [Hexagonal Ports](../architecture/hexagonal-ports-adapters.md)
