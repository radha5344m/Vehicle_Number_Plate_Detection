"""Health endpoint integration test."""

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def test_health_returns_ok() -> None:
    app = create_app()
    app.state.container = build_container()
    with TestClient(app) as client:
        response = client.get("/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] in ("ok", "degraded")
        assert body["data"]["ready"] is True
        assert body["data"]["database"] == "connected"
        assert body["data"]["checks"]
        assert "version" in body["data"]
        assert "checked_at" in body["data"]
        assert "X-Correlation-ID" in response.headers
