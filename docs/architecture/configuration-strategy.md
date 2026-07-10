# Configuration Strategy

How configuration is organized and loaded in SentinelANPR AI.

---

## Principles

1. **12-factor**: Config via environment; no secrets in repo
2. **Layered overrides**: `default` → `environment` → env vars
3. **Typed access**: Application uses `ConfigPort`, not raw `os.environ` in domain
4. **Validation at startup**: Fail fast on missing required settings

---

## Directory Layout

```
config/
├── default/          # Base YAML/JSON — committed
├── development/      # Dev overrides — committed
├── staging/          # Staging overrides — committed
├── production/       # Non-secret prod defaults — committed
└── local/            # Gitignored local overrides
```

---

## Configuration Categories (Planned)

| Category | Examples | Sensitivity |
|----------|----------|-------------|
| Server | Host, port, workers | Low |
| ML | Model paths, thresholds | Low |
| External APIs | Registry URL, timeouts | Medium |
| Secrets | API keys, DB passwords | High — env/vault only |
| Feature flags | Enable clone detection | Low |

---

## Loading Flow (Conceptual)

```
config/default/*.yaml
    + config/{env}/*.yaml
    + environment variables
    → ConfigLoader (infrastructure/config/)
    → ConfigPort implementation
    → Injected into use cases / adapters at composition root
```

---

## Runtime environment (backend)

Copy [`backend/.env.example`](../../backend/.env.example) to `backend/.env`. Secrets live only in `.env` (gitignored).

### Vision AI

| Variable | Required when | Description |
|----------|---------------|-------------|
| `SENTINEL_VISION_PROVIDER` | always | `gemini` (default) or `stub` (local/tests) |
| `GEMINI_API_KEY` | `provider=gemini` | Google AI Studio / Gemini API key |
| `SENTINEL_GEMINI_MODEL` | optional | Model id (default `gemini-2.5-flash`) |

When `SENTINEL_VISION_PROVIDER=gemini`, startup validates `GEMINI_API_KEY` only.  
`OPENAI_API_KEY` is **not** used and is **never** validated.

When `SENTINEL_VISION_PROVIDER=stub`, no cloud API key is required.

---

## Related

- [backend/config/README.md](../../backend/config/README.md)
- [Getting started](../development/getting-started.md)
