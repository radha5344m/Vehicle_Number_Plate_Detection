"""Scan history API integration tests."""

import uuid

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


def test_list_scan_history_requires_auth() -> None:
    with _client() as client:
        response = client.get("/v1/history/scans")
        assert response.status_code == 401


def test_list_scan_history_returns_seeded_scans() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/history/scans",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) >= 1
        assert data["pagination"]["total_items"] >= 1


def test_list_scan_history_filters_by_plate() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/history/scans?plate=AP09AB1234",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) >= 1
        assert all(item["plate_text"] == "AP09AB1234" for item in items)


def test_list_scan_history_filters_by_risk_level() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/history/scans?risk_level=critical",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) >= 1
        assert all(item["risk_level"] == "critical" for item in items)


def test_save_completed_scan() -> None:
    plate = f"AP{uuid.uuid4().hex[:6].upper()}01"
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/history/scans",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "plate": plate,
                "risk_score": 0.15,
                "risk_level": "low",
                "location_label": "Test Checkpoint",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["plate_text"] == plate
        assert data["scan_id"]

        list_response = client.get(
            f"/v1/history/scans?plate={plate}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        items = list_response.json()["data"]["items"]
        assert len(items) >= 1
        assert any(item["plate_text"] == plate for item in items)
