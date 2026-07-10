"""Dashboard API integration tests."""

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
        json={"badge_number": "superadmin", "password": "Admin@123"},
    )
    return response.json()["data"]["access_token"]


def _officer_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def test_dashboard_summary() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total_scans"] >= 8
        assert body["data"]["verified_vehicles"] >= 0


def test_dashboard_recent_activity() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/dashboard/recent-activity?limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]["items"]) >= 1
        assert body["data"]["items"][0]["occurred_at"]


def test_executive_dashboard_returns_command_center_payload() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/dashboard/executive",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["kpis"]) >= 8
        assert len(data["daily_trend"]) >= 1
        assert len(data["risk_distribution"]) >= 1
        assert "connection_status" in data
        assert isinstance(data["insights"], list)


def test_executive_dashboard_scopes_to_police_officer() -> None:
    with _client() as client:
        token = _officer_token(client)
        response = client.get(
            "/v1/dashboard/executive",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["scope_label"]
        assert data["connection_status"]["status"] == "Connected"


def test_executive_dashboard_csv_export() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/dashboard/executive/export/csv",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert "Section,Label,Value" in response.text
