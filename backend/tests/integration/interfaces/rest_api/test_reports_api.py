"""Investigation report API integration tests."""

import io
import json

from fastapi.testclient import TestClient
from PIL import Image

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _vehicle_image_bytes() -> bytes:
    image = Image.new("RGB", (640, 360), color=(30, 41, 59))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _login_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def _report_payload() -> dict[str, object]:
    return {
        "detected_plate": "AP09AB1234",
        "ocr_registration_number": "AP09AB1234",
        "ocr_detected_text": "AP09AB1234",
        "ocr_confidence": 0.92,
        "risk_score": 0.15,
        "risk_level": "low",
        "recommendation": "Proceed with routine checks.",
        "vehicle_details": {
            "plate_number": "AP09AB1234",
            "make": "Toyota",
            "model": "Innova Crysta",
            "color": "White",
            "vehicle_type": "car",
            "registration_status": "active",
            "registered_owner": "Ravi Kumar",
        },
    }


def test_generate_investigation_report_requires_auth() -> None:
    with _client() as client:
        response = client.post(
            "/v1/reports/investigation",
            data={"payload": json.dumps(_report_payload())},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 401


def test_generate_and_download_investigation_report() -> None:
    with _client() as client:
        token = _login_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/v1/reports/investigation",
            headers=headers,
            data={"payload": json.dumps(_report_payload())},
            files={"vehicle_image": ("vehicle.jpg", _vehicle_image_bytes(), "image/jpeg")},
        )
        assert response.status_code == 201
        body = response.json()["data"]
        assert body["report_id"]
        assert body["download_url"].endswith("/download")

        download = client.get(body["download_url"], headers=headers)
        assert download.status_code == 200
        assert download.headers["content-type"] == "application/pdf"
        assert download.content.startswith(b"%PDF")
