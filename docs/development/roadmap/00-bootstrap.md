# Phase 0 — Project Bootstrap

Prerequisites before Domain. Tooling only — no business logic.

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `pyproject.toml` | Python project metadata, dependencies, tool config (ruff, mypy, pytest) | — | Defines runtime before any module |
| `requirements.txt` or lockfile | Pinned dependencies for reproducible builds | `pyproject.toml` | Team install baseline |
| `src/sentinel_anpr/__init__.py` | Package root; version export | — | Makes `sentinel_anpr` importable |
| `src/sentinel_anpr/py.typed` | PEP 561 typed package marker | `__init__.py` | Enables mypy across layers |
| `.env.example` | Document `SENTINEL_*` variables | `docs/api/conventions.md` | Config contract before loaders |
| `config/default/app.yaml` | Complete default app settings | — | Config loader needs files |
| `config/default/database.yaml` | DB connection defaults (no secrets) | — | Repository phase prep |
| `config/default/ml.yaml` | Model paths, thresholds | — | ML adapter phase prep |
| `config/default/auth.yaml` | JWT issuer, TTL settings | — | Auth adapter phase prep |
| `Makefile` or `scripts/setup/dev.sh` | `install`, `lint`, `test` commands | `pyproject.toml` | Developer ergonomics |
| `README.md` (update) | Local run instructions | Bootstrap files | Onboarding |

**Exit gate:** `python -c "import sentinel_anpr"` succeeds; `ruff check src` runs (empty).
