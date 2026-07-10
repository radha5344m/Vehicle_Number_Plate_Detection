# Error Handling Strategy

Skeleton for layered error handling in SentinelANPR AI.

---

## Error Taxonomy (Planned)

| Category | Layer | Example | HTTP Mapping (adapter) |
|----------|-------|---------|------------------------|
| Domain Error | Domain | `InvalidPlateFormatError` | 422 Unprocessable |
| Not Found | Domain/Application | `SightingNotFoundError` | 404 |
| Verification Failed | Domain | `RegistryMismatchError` | 200 with failure DTO |
| Infrastructure Error | Infrastructure | `RegistryUnavailableError` | 503 |
| Adapter Validation | Adapters | Malformed JSON | 400 |

---

## Principles

1. **Domain errors** express business rule violations — no HTTP status codes in domain
2. **Application layer** catches domain errors and maps to result DTOs or propagates
3. **Adapters** map application outcomes to transport-specific responses
4. **Never** leak stack traces or internal details to external clients in production

---

## Error Flow

```
Adapter → Use Case → Domain
                ↓ (DomainError)
         Application maps to Result DTO
                ↓
         Adapter maps to HTTP/gRPC/CLI exit code
```

---

## Planned Locations

| Artifact | Path |
|----------|------|
| Base domain error | `domain/common/errors/` |
| Context-specific errors | `domain/<context>/errors/` |
| Application error mapper | `application/services/` or per use case _TBD_ |
| Adapter exception handlers | `adapters/inbound/*/errors/` _TBD_ |

---

## Status

_TBD during implementation — record choices in ADR._
