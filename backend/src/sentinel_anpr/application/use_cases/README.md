# Application — Use Cases

One class per user/system intent (Single Responsibility).

---

## By Context

| Directory | Use Cases |
|-----------|-----------|
| `ingestion/` | `IngestImageUseCase` |
| `plate_recognition/` | `RecognizePlateUseCase` |
| `plate_verification/` | `VerifyPlateUseCase` |
| `clone_detection/` | `DetectCloneUseCase` |
| `orchestration/` | `ProcessPlatePipelineUseCase` |

---

## Pattern

Each use case:

1. Accepts input DTO or command
2. Invokes domain logic
3. Calls outbound ports as needed
4. Returns output DTO or result type

---

## Placeholders

See `*.placeholder` files in each subdirectory.
