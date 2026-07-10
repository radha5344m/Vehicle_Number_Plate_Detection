"""Vehicle verification workflow API integration tests."""

import io

from fastapi.testclient import TestClient
from PIL import Image

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _vehicle_image_bytes() -> bytes:
    image = Image.new("RGB", (960, 540), color=(30, 41, 59))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _login_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"identifier": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def test_vehicle_verification_workflow_requires_auth() -> None:
    with _client() as client:
        response = client.post(
            "/v1/workflow/vehicle-verification",
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 401


def test_vehicle_verification_workflow_completes_synchronously() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/workflow/vehicle-verification",
            headers={"Authorization": f"Bearer {token}"},
            data={"location_label": "Workflow Test Checkpoint"},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "completed"
        assert data["registration_number"] == "AP09AB1234"
        assert data["scan_id"]
        assert data["report_id"]
        assert data["report_download_url"]
        assert data["risk_level"] in {"low", "medium", "high", "critical"}
        assert len(data["steps"]) >= 6
