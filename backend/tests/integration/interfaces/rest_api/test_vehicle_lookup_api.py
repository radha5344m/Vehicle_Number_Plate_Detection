"""Vehicle lookup API integration tests."""

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


def test_vehicle_lookup_requires_auth() -> None:
    with _client() as client:
        response = client.get("/v1/vehicles/lookup?plate=AP09AB1234")
        assert response.status_code == 401


def test_vehicle_lookup_found() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/vehicles/lookup?plate=AP09AB1234",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["lookup_status"] == "found"
        assert data["vehicle"]["make"] == "Toyota"


def test_vehicle_lookup_not_found() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/vehicles/lookup?plate=ZZ99ZZ9999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["lookup_status"] == "not_found"
        assert data["message"] == "Vehicle not found."
        assert data["vehicle"] is None
