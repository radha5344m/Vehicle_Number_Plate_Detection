# Configuration

Environment-specific configuration for SentinelANPR AI.

---

## Structure

| Directory | Purpose | Committed |
|-----------|---------|-----------|
| `default/` | Base settings shared by all environments | Yes |
| `development/` | Local development overrides | Yes |
| `staging/` | Staging environment overrides | Yes |
| `production/` | Production non-secret defaults | Yes |
| `local/` | Developer machine overrides | **No** (gitignored) |

---

## Rules

1. **Never commit secrets** — use environment variables or secret manager
2. **Override order:** `default` → `{environment}` → env vars → `local/`
3. Application code reads config via `ConfigPort` only

---

## Planned Files (Implementation)

| File | Description |
|------|-------------|
| `default/app.yaml` | App name, log level |
| `default/ml.yaml` | Model paths, thresholds |
| `development/app.yaml` | Dev-specific overrides |
| `../.env.example` | Required env vars (Hugging Face vision: `HF_TOKEN`, etc.) |

---

## Related

- [Configuration Strategy](../docs/architecture/configuration-strategy.md)
