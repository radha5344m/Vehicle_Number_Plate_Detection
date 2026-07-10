# Deployment Documentation

Deployment notes for SentinelANPR AI.

## Root cause of `/v1/auth/login` 404 after deploy

Locally, Vite proxies `/v1` to `http://127.0.0.1:8080`. In production, if `VITE_API_BASE_URL` is empty, the browser calls `/v1/...` on the **frontend host**, which has no API — hence **404**.

## Root cause of `Cannot GET /v1/health`

That message is **not** from FastAPI. It means the request hit a **static site** or **Node server**, not the Python API.

| Response | What you hit |
|----------|----------------|
| `Cannot GET /v1/health` | Frontend static site, or wrong server type |
| `{"detail":"Not Found"}` | FastAPI running, but wrong path |
| `{"data":{"status":"ok",...}}` | Backend working correctly |

**Fix:** Open the **Python Web Service** URL (not a Static Site). The API must run:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

with **Root directory** = `backend`.

## Option A — Single Render web service (recommended)

One service serves both the API and the built React app on the same origin.

1. Use the repo [`render.yaml`](../render.yaml) blueprint, or configure manually:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt && python scripts/build_frontend_bundle.py`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Health check:** `/v1/health`
2. Set env vars: `GEMINI_API_KEY`, `SENTINEL_VISION_PROVIDER=gemini`, `SENTINEL_AUTH_JWT_SECRET`
3. Leave `VITE_API_BASE_URL` empty — the build script sets same-origin mode automatically.

## Option B — Split frontend + backend

1. **Backend** (Render Web Service): deploy `backend/` with start command above.
2. **Frontend** (Render Static Site or similar):
   - **Build command:** `npm ci && npm run build`
   - **Env at build time:** `VITE_API_BASE_URL=https://<your-backend>.onrender.com`
3. **Backend env:** `SENTINEL_CORS_ORIGINS=https://<your-frontend>.onrender.com`

## Verify

- `GET https://<backend>/v1/health` → 200
- Login from the deployed UI → no 404 on `/v1/auth/login`

## Related

- [Operations](../operations/README.md)
- [Frontend env](../frontend/README.md)
