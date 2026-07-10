# Application — DTOs

Data Transfer Objects for crossing application boundaries.

---

## Planned DTOs

| File | Purpose |
|------|---------|
| `recognition_dto.placeholder` | Recognition pipeline I/O |
| `verification_dto.placeholder` | Verification I/O |
| `clone_detection_dto.placeholder` | Clone detection I/O |

---

## Rules

- DTOs are **not** domain entities
- Adapters map HTTP/CLI/gRPC payloads to/from DTOs
- Domain objects stay inside use cases
