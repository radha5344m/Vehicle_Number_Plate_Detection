"""Serve the built React SPA from the API process (single-origin deployment)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sentinel_anpr.infrastructure.config.settings import get_backend_dir


def _frontend_static_root() -> Path:
    return get_backend_dir() / "static" / "frontend"


def register_frontend_static_routes(app: FastAPI) -> bool:
    """Mount the Vite production bundle when ``static/frontend/index.html`` exists.

    Returns True when the SPA was registered.
    """
    static_root = _frontend_static_root()
    index_file = static_root / "index.html"
    if not index_file.is_file():
        return False

    assets_dir = static_root / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    async def spa_index() -> FileResponse:
        return FileResponse(index_file)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("v1/") or full_path == "v1":
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = static_root / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_file)

    return True


def register_api_root_route(app: FastAPI) -> None:
    """Expose a JSON root when the SPA bundle is not deployed (API-only service)."""
    static_root = _frontend_static_root()
    if (static_root / "index.html").is_file():
        return

    @app.get("/", include_in_schema=False)
    async def api_root() -> JSONResponse:
        return JSONResponse(
            {
                "service": "sentinel-anpr-ai",
                "status": "running",
                "health": "/v1/health",
                "docs": "/docs",
            }
        )
