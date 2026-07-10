# Phase 8 — Deployment

**Path:** `deploy/`, `docker/`, `docs/deployment/`, CI configs  
**Rule:** Infrastructure as code; secrets via env — never in images.

---

## 8.1 Containerization

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `Dockerfile` | Backend API image | bootstrap/app_entry, requirements | Runnable API |
| `Dockerfile.ml` | Optional ML worker image (GPU) | YOLO, PaddleOCR deps | Heavy ML separate from API |
| `frontend/Dockerfile` | Nginx static SPA | frontend build | UI hosting |
| `docker-compose.yml` | Local full stack | Dockerfiles, postgres | Dev/staging parity |
| `docker-compose.prod.yml` | Production overrides | docker-compose | Prod deploy |
| `.dockerignore` | Exclude dev files | — | Smaller images |

---

## 8.2 Database Operations

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `scripts/ops/migrate.sh` | Run Alembic migrations | migrations | Pre-deploy step |
| `scripts/ops/seed_stations.py` | Seed station reference data | officer models | First deploy |
| `scripts/ops/seed_dev_officer.py` | Dev officer account | migrations | Local/staging only |

---

## 8.3 Configuration per Environment

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `config/staging/app.yaml` | Staging overrides | default | Staging deploy |
| `config/staging/database.yaml` | Staging DB settings | — | |
| `config/production/app.yaml` | Production defaults | default | Prod deploy |
| `config/production/ml.yaml` | Prod model paths | — | ML serving |
| `docs/deployment/environment-matrix.md` | Env comparison table | all configs | Ops reference |
| `docs/deployment/secrets-management.md` | Vault/env var guide | .env.example | Security |

---

## 8.4 CI/CD

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `.github/workflows/ci.yml` | Lint + test on PR | tests/, pyproject | Quality gate |
| `.github/workflows/build.yml` | Build Docker images | Dockerfiles | Artifact pipeline |
| `.github/workflows/deploy-staging.yml` | Deploy to staging | build workflow | Auto-deploy |
| `scripts/ci/run_tests.sh` | Local CI simulation | pytest, vitest | Developer parity |
| `scripts/ci/lint.sh` | ruff + mypy + eslint | config files | Code quality |

---

## 8.5 Runtime & Orchestration

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `deploy/kubernetes/api-deployment.yaml` | API pods | Docker image | K8s option |
| `deploy/kubernetes/ml-deployment.yaml` | ML worker pods | Dockerfile.ml | GPU scheduling |
| `deploy/kubernetes/ingress.yaml` | HTTPS ingress | API service | External access |
| `deploy/kubernetes/configmap.yaml` | Non-secret config | config YAML | K8s config |
| `deploy/kubernetes/secrets.yaml.example` | Secret template | — | Never commit real secrets |
| `docs/deployment/runbook.md` | Deploy procedure | all deploy files | Ops |
| `docs/deployment/rollback.md` | Rollback steps | migrations | Incident response |
| `docs/deployment/monitoring.md` | Metrics, alerts | logging setup | Production ops |

---

## 8.6 Health & Observability

| File | Purpose | Depends On | Why This Stage |
|------|---------|------------|----------------|
| `interfaces/rest_api/v1/routes/health/health_handler.py` | Already in Phase 5 | DB, ML readiness | Load balancer checks |
| `docs/operations/monitoring.md` | SLIs, dashboards | health endpoints | SRE |
| `docs/operations/incident-response.md` | Playbooks | runbook | On-call |

---

## Deployment Order

```
1. Provision database (PostgreSQL)
2. Run migrations (scripts/ops/migrate.sh)
3. Seed reference data (stations)
4. Deploy ML models to volume / object store
5. Deploy API container (config via env)
6. Deploy frontend static assets
7. Smoke test: health → login → scan
8. Enable monitoring alerts
```

---

## Phase 8 Exit Gate

- [ ] Staging URL accessible; HTTPS enabled
- [ ] Migrations automated in CI/CD
- [ ] Secrets in vault/env — not in git
- [ ] Rollback tested once

---

## Project Complete

All phases delivered → production-ready SentinelANPR AI.

Return to [README.md](README.md) for phase index.
