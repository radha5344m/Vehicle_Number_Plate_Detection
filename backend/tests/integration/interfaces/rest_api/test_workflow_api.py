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
    image = Image.new("RGB", (1280, 960), color=(30, 41, 59))
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


def test_detect_vehicles_endpoint_returns_bounding_boxes() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/workflow/detect-vehicles",
            headers={"Authorization": f"Bearer {token}"},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        vehicles = response.json()["data"]["vehicles"]
        assert len(vehicles) >= 1
        assert response.json()["data"]["visible_plate_count"] >= 0
        first = vehicles[0]
        assert first["vehicle_id"]
        assert 0 <= first["x"] <= 1
        assert 0 <= first["y"] <= 1
        assert first["width"] > 0
        assert first["height"] > 0
        assert first["vehicle_type"]


def test_count_visible_vehicles_endpoint_returns_vehicle_count() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.post(
            "/v1/workflow/count-visible-vehicles",
            headers={"Authorization": f"Bearer {token}"},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["vehicle_count"] >= 1
        assert isinstance(data["vehicles"], list)
        if data["vehicles"]:
            assert "type" in data["vehicles"][0]


def test_vehicle_verification_with_selected_regions_returns_independent_investigations() -> None:
    with _client() as client:
        token = _login_token(client)
        selected_regions = (
            '[{"vehicle_id":"vehicle-1","x":0.1,"y":0.1,"width":0.35,"height":0.5},'
            '{"vehicle_id":"vehicle-2","x":0.55,"y":0.15,"width":0.3,"height":0.45}]'
        )
        response = client.post(
            "/v1/workflow/vehicle-verification",
            headers={"Authorization": f"Bearer {token}"},
            data={"selected_regions": selected_regions},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["investigations"] is not None
        assert len(data["investigations"]) == 2
        assert data["investigations"][0]["workflow_id"] != data["investigations"][1]["workflow_id"]
        assert data["investigations"][0]["scan_id"]
        assert data["investigations"][1]["scan_id"]
