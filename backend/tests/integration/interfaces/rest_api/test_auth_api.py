"""Authentication API integration tests."""

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def test_login_success() -> None:
    with _client() as client:
        response = client.post(
            "/v1/auth/login",
            json={"identifier": "AP001", "password": "Officer@123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["token_type"] == "Bearer"
        assert body["data"]["officer"]["badge_number"] == "AP001"
        assert body["data"]["user"]["username"] == "ap001"
        assert body["data"]["role"] == "POLICE_OFFICER"
        assert "vehicle_verification" in body["data"]["permissions"]
        assert body["data"]["station"]["station_id"]
        assert body["data"]["station"]["station_code"] == "ONG01"
        assert body["data"]["token"]["access_token"]


def test_login_invalid_credentials() -> None:
    with _client() as client:
        response = client.post(
            "/v1/auth/login",
            json={"identifier": "AP001", "password": "wrong-password"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTH_LOGIN_INVALID"


def test_me_requires_token() -> None:
    with _client() as client:
        response = client.get("/v1/auth/me")
        assert response.status_code == 401
        body = response.json()
        assert body["error"]["code"] == "AUTH_MISSING"
        assert "sign in" in body["error"]["message"].lower()


def test_me_rejects_invalid_jwt() -> None:
    with _client() as client:
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["error"]["code"] == "AUTH_INVALID"


def test_me_with_token() -> None:
    with _client() as client:
        login = client.post(
            "/v1/auth/login",
            json={"identifier": "AP001", "password": "Officer@123"},
        )
        token = login.json()["data"]["access_token"]
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["officer"]["badge_number"] == "AP001"
        assert body["data"]["user"]["username"] == "ap001"
        assert body["data"]["role"] == "POLICE_OFFICER"
        assert "vehicle_verification" in body["data"]["permissions"]


def test_logout_revokes_session() -> None:
    with _client() as client:
        login = client.post(
            "/v1/auth/login",
            json={"identifier": "AP001", "password": "Officer@123"},
        )
        data = login.json()["data"]
        response = client.post(
            "/v1/auth/logout",
            headers={"Authorization": f"Bearer {data['access_token']}"},
            json={"refresh_token": data["refresh_token"]},
        )
        assert response.status_code == 200
        assert response.json()["data"]["message"] == "Logged out successfully"


def test_super_admin_login_success() -> None:
    with _client() as client:
        response = client.post(
            "/v1/auth/login",
            json={"identifier": "superadmin", "password": "Admin@123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["officer"]["username"] == "superadmin"
        assert body["data"]["role"] == "SUPER_ADMIN"
        assert body["data"]["station"]["station_name"] == "Headquarters"
        assert "dashboard" in body["data"]["permissions"]
        assert "users" in body["data"]["permissions"]


def test_login_success_with_employee_id() -> None:
    with _client() as client:
        response = client.post(
            "/v1/auth/login",
            json={"identifier": "EMP-0001", "password": "Officer@123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["officer"]["employee_id"] == "EMP-0001"
        assert body["data"]["role"] == "POLICE_OFFICER"
