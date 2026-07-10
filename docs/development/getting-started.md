# SentinelANPR AI — Quick start

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Edit `backend/.env` and set vision configuration:

```env
SENTINEL_VISION_PROVIDER=gemini
GEMINI_API_KEY=
SENTINEL_GEMINI_MODEL=gemini-2.5-flash
```

- Set `GEMINI_API_KEY` to your Google AI Studio / Gemini API key when using Gemini.
- For local runs without a cloud key: `SENTINEL_VISION_PROVIDER=stub`.
- `OPENAI_API_KEY` is not used.

Start the API (port **8080**):

```bash
python main.py
```

Health: http://127.0.0.1:8080/v1/health

### Demo login accounts

| Role | Identifier | Password |
|------|------------|----------|
| Super Admin | `superadmin` or `ADMIN001` | `Admin@123` |
| Police Officer | `AP001` or `ap001` | `Officer@123` |

Passwords are reset to these values whenever the API starts and re-seeds demo users.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173

Optional: `frontend/.env.local` with `VITE_API_BASE_URL=http://127.0.0.1:8080` for direct API calls (avoids large-upload proxy issues on Windows).

## Environment

| File | Purpose |
|------|---------|
| `backend/.env.example` | Template — copy to `backend/.env` |
| `backend/.env` | Local secrets (never commit) |

See [Configuration strategy](../architecture/configuration-strategy.md).
