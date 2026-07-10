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
