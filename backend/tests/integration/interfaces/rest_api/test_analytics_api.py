"""Analytics API integration tests."""

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def test_analytics_overview_requires_auth() -> None:
    with _client() as client:
        response = client.get("/v1/analytics/overview")
        assert response.status_code == 401


def test_analytics_overview_forbids_police_officer() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/analytics/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_analytics_overview_returns_chart_data_for_super_admin() -> None:
    with _client() as client:
        admin = client.post(
            "/v1/auth/login",
            json={"badge_number": "superadmin", "password": "Admin@123"},
        )
        token = admin.json()["data"]["access_token"]
        response = client.get(
            "/v1/analytics/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_scans"] >= 1
        assert len(data["daily_scans"]["labels"]) >= 1
        assert len(data["risk_distribution"]["labels"]) >= 1
        assert len(data["vehicle_types"]["labels"]) >= 1
        assert len(data["officer_activity"]["labels"]) >= 1
