"""Centralized API error handling integration tests."""

import io

from fastapi.testclient import TestClient
from PIL import Image

from sentinel_anpr.application.use_cases.health.get_health_use_case import GetHealthUseCase
from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


class _FailingDatabase:
    def ping(self) -> bool:
        return False


def _app_with_container(container):
    app = create_app()
    app.state.container = container
    return app


def _jpeg_bytes(width: int = 800, height: int = 600) -> bytes:
    image = Image.new("RGB", (width, height), color=(20, 120, 200))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _login_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def test_invalid_jwt_returns_auth_invalid_envelope() -> None:
    with TestClient(_app_with_container(build_container())) as client:
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer not-a-valid-jwt"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTH_INVALID"
        assert "sign in again" in body["error"]["message"].lower()


def test_health_returns_503_when_database_unavailable() -> None:
    container = build_container()
    container.get_health_use_case = GetHealthUseCase(
        config=container.config,
        database=_FailingDatabase(),
    )
    with TestClient(_app_with_container(container)) as client:
        response = client.get("/v1/health")
        assert response.status_code == 503
        body = response.json()
        assert body["success"] is True
        assert body["data"]["ready"] is False
        assert body["data"]["database"] == "unavailable"
        assert body["data"]["checks"][0]["status"] == "fail"


def test_workflow_invalid_image_returns_failed_status() -> None:
    with TestClient(_app_with_container(build_container())) as client:
        token = _login_token(client)
        response = client.post(
            "/v1/workflow/vehicle-verification",
            headers={"Authorization": f"Bearer {token}"},
            files={"vehicle_image": ("small.jpg", _jpeg_bytes(320, 240), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "failed"
        assert data["failed_stage"] == "upload"


def test_workflow_complete_end_to_end() -> None:
    with TestClient(_app_with_container(build_container())) as client:
        token = _login_token(client)
        response = client.post(
            "/v1/workflow/vehicle-verification",
            headers={"Authorization": f"Bearer {token}"},
            data={"location_label": "Error Handling Test Checkpoint"},
            files={"vehicle_image": ("vehicle.jpg", _jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["status"] == "completed"
        assert data["registration_number"] == "AP09AB1234"
        assert data["scan_id"]
        assert data["report_id"]
        assert body["meta"]["correlation_id"]
