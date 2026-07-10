"""Vehicle image upload API integration tests."""

import io

from fastapi.testclient import TestClient
from PIL import Image

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


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


def test_upload_requires_auth() -> None:
    with _client() as client:
        response = client.post(
            "/v1/uploads/vehicle-image",
            files={"image": ("vehicle.jpg", _jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "AUTH_MISSING"


def test_upload_stores_image() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/uploads/vehicle-image",
            headers={"Authorization": f"Bearer {token}"},
            files={"image": ("vehicle.jpg", _jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["width"] == 800
        assert body["data"]["height"] == 600
        assert body["data"]["content_type"] == "image/jpeg"
        assert body["data"]["storage_key"].endswith(".jpg")


def test_upload_rejects_small_image() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/uploads/vehicle-image",
            headers={"Authorization": f"Bearer {token}"},
            files={"image": ("small.jpg", _jpeg_bytes(320, 240), "image/jpeg")},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
