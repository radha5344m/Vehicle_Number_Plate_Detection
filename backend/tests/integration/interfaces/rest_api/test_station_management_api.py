"""Police station management API integration tests."""

import uuid

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login(client: TestClient, badge_number: str, password: str) -> dict:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": badge_number, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_stations_require_super_admin() -> None:
    with _client() as client:
        officer = _login(client, "AP001", "Officer@123")
        response = client.get(
            "/v1/stations",
            headers={"Authorization": f"Bearer {officer['access_token']}"},
        )
        assert response.status_code == 403


def test_super_admin_can_create_edit_deactivate_search_filter_and_delete_stations() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        headers = {"Authorization": f"Bearer {admin['access_token']}"}
        token = uuid.uuid4().hex[:6].upper()
        station_name = f"Kanigiri Town {token}"
        station_code = f"KNG{token}"

        create = client.post(
            "/v1/stations",
            headers=headers,
            json={
                "station_name": station_name,
                "station_code": station_code,
                "district": "Prakasam",
                "state": "Andhra Pradesh",
                "address": "Main Road, Kanigiri",
                "pincode": "523230",
                "phone_number": "9000012345",
                "email": f"{station_code.lower()}@sentinelanpr.ai",
                "station_type": "town",
                "status": "active",
            },
        )
        assert create.status_code == 201
        station = create.json()["data"]["station"]
        station_id = station["station_id"]

        duplicate = client.post(
            "/v1/stations",
            headers=headers,
            json={
                "station_name": station_name,
                "station_code": station_code,
                "district": "Prakasam",
                "state": "Andhra Pradesh",
                "address": "Duplicate Address",
                "pincode": "523230",
                "phone_number": "9000012346",
                "email": f"dup.{station_code.lower()}@sentinelanpr.ai",
                "station_type": "town",
                "status": "active",
            },
        )
        assert duplicate.status_code == 400

        query = client.get(
            f"/v1/stations?search={station_code}&district=Prakasam&state=Andhra Pradesh&station_type=town",
            headers=headers,
        )
        assert query.status_code == 200
        items = query.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["station_code"] == station_code

        detail = client.get(f"/v1/stations/{station_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["data"]["station"]["station_name"] == station_name

        update = client.put(
            f"/v1/stations/{station_id}",
            headers=headers,
            json={
                "station_name": f"{station_name} Updated",
                "district": "Prakasam",
                "state": "Andhra Pradesh",
                "address": "Updated Address",
                "pincode": "523230",
                "phone_number": "9000099999",
                "email": f"updated.{station_code.lower()}@sentinelanpr.ai",
                "station_type": "rural",
                "status": "active",
            },
        )
        assert update.status_code == 200
        assert update.json()["data"]["station"]["station_type"] == "rural"

        deactivate = client.patch(
            f"/v1/stations/{station_id}/status",
            headers=headers,
            json={"status": "inactive"},
        )
        assert deactivate.status_code == 200
        assert deactivate.json()["data"]["station"]["status"] == "inactive"

        filtered = client.get(
            "/v1/stations?status=inactive&station_type=rural",
            headers=headers,
        )
        assert filtered.status_code == 200
        assert any(item["station_id"] == station_id for item in filtered.json()["data"]["items"])

        delete = client.delete(f"/v1/stations/{station_id}", headers=headers)
        assert delete.status_code == 200

        after_delete = client.get(f"/v1/stations?search={station_code}", headers=headers)
        assert after_delete.status_code == 200
        assert after_delete.json()["data"]["items"] == []
