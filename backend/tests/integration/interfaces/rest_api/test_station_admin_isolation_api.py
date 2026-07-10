"""Station admin data isolation integration tests."""

import uuid

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login(client: TestClient, identifier: str, password: str) -> dict:
    response = client.post("/v1/auth/login", json={"identifier": identifier, "password": password})
    assert response.status_code == 200
    return response.json()["data"]


def _create_station_admin(client: TestClient, *, station: str) -> dict[str, str]:
    admin = _login(client, "superadmin", "Admin@123")
    headers = {"Authorization": f"Bearer {admin['access_token']}"}
    token = uuid.uuid4().hex[:6]
    username = f"stadmin{token}"
    badge = f"STA{token[:3].upper()}"
    create = client.post(
        "/v1/users",
        headers=headers,
        json={
            "employee_id": f"EMP-SA-{token.upper()}",
            "first_name": "Station",
            "last_name": "Admin",
            "username": username,
            "email": f"{username}@sentinelanpr.ai",
            "phone_number": "9000011111",
            "badge_number": badge,
            "rank": "Inspector",
            "role": "STATION_ADMIN",
            "police_station": station,
            "district": "Prakasam",
            "status": "active",
        },
    )
    assert create.status_code == 201
    temporary_password = create.json()["data"]["temporary_password"]
    assert temporary_password
    return {"username": username, "badge": badge, "password": temporary_password, "station": station}


def _auth_headers(client: TestClient, identifier: str, password: str) -> dict[str, str]:
    session = _login(client, identifier, password)
    return {"Authorization": f"Bearer {session['access_token']}"}


def test_station_admin_only_sees_own_station_officers() -> None:
    with _client() as client:
        ongole_admin = _create_station_admin(client, station="Ongole Town")
        markapur_admin = _create_station_admin(client, station="Markapur Town")
        ongole_headers = _auth_headers(client, ongole_admin["username"], ongole_admin["password"])
        markapur_headers = _auth_headers(client, markapur_admin["username"], markapur_admin["password"])
        token = uuid.uuid4().hex[:6]

        create_ongole_officer = client.post(
            "/v1/station-admin/officers",
            headers=ongole_headers,
            json={
                "employee_id": f"EMP-ONG-{token.upper()}",
                "first_name": "Ongole",
                "last_name": "Officer",
                "username": f"ongole{token}",
                "email": f"ongole{token}@sentinelanpr.ai",
                "phone_number": "9000022222",
                "badge_number": f"ONG{token[:3].upper()}",
                "rank": "Constable",
                "status": "active",
            },
        )
        assert create_ongole_officer.status_code == 201
        ongole_officer_id = create_ongole_officer.json()["data"]["officer"]["officer_id"]
        assert create_ongole_officer.json()["data"]["temporary_password"]

        ongole_officers = client.get("/v1/station-admin/officers", headers=ongole_headers)
        assert ongole_officers.status_code == 200
        ongole_ids = {item["officer_id"] for item in ongole_officers.json()["data"]["items"]}
        assert ongole_officer_id in ongole_ids
        assert all(item["rank"] != "Super Admin" for item in ongole_officers.json()["data"]["items"])

        markapur_officers = client.get("/v1/station-admin/officers", headers=markapur_headers)
        assert markapur_officers.status_code == 200
        markapur_ids = {item["officer_id"] for item in markapur_officers.json()["data"]["items"]}
        assert ongole_officer_id not in markapur_ids


def test_station_admin_cannot_manage_officers_from_other_stations() -> None:
    with _client() as client:
        ongole_admin = _create_station_admin(client, station="Ongole Town")
        markapur_admin = _create_station_admin(client, station="Markapur Town")
        ongole_headers = _auth_headers(client, ongole_admin["username"], ongole_admin["password"])
        markapur_headers = _auth_headers(client, markapur_admin["username"], markapur_admin["password"])
        token = uuid.uuid4().hex[:6]

        create_officer = client.post(
            "/v1/station-admin/officers",
            headers=ongole_headers,
            json={
                "employee_id": f"EMP-ISO-{token.upper()}",
                "first_name": "Isolated",
                "last_name": "Officer",
                "username": f"iso{token}",
                "email": f"iso{token}@sentinelanpr.ai",
                "badge_number": f"ISO{token[:3].upper()}",
                "rank": "Constable",
                "status": "active",
            },
        )
        assert create_officer.status_code == 201
        officer_id = create_officer.json()["data"]["officer"]["officer_id"]

        cross_update = client.put(
            f"/v1/station-admin/officers/{officer_id}",
            headers=markapur_headers,
            json={
                "first_name": "Blocked",
                "last_name": "Update",
                "email": f"blocked.{token}@sentinelanpr.ai",
                "rank": "Constable",
                "status": "active",
            },
        )
        assert cross_update.status_code == 404

        cross_delete = client.delete(f"/v1/station-admin/officers/{officer_id}", headers=markapur_headers)
        assert cross_delete.status_code == 404

        cross_reset = client.post(
            f"/v1/station-admin/officers/{officer_id}/reset-password",
            headers=markapur_headers,
            json={"new_password": "Blocked@1234"},
        )
        assert cross_reset.status_code == 404


def test_station_admin_cannot_access_global_management_or_users_api() -> None:
    with _client() as client:
        station_admin = _create_station_admin(client, station="Ongole Town")
        headers = _auth_headers(client, station_admin["username"], station_admin["password"])

        users = client.get("/v1/users", headers=headers)
        assert users.status_code == 403

        create_super_admin = client.post(
            "/v1/users",
            headers=headers,
            json={
                "employee_id": "EMP-BLOCKED",
                "first_name": "Blocked",
                "last_name": "Admin",
                "username": "blockedadmin",
                "email": "blocked@sentinelanpr.ai",
                "role": "SUPER_ADMIN",
                "police_station": "Headquarters",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert create_super_admin.status_code == 403

        stations = client.get("/v1/stations", headers=headers)
        assert stations.status_code == 403


def test_station_admin_profile_and_station_details_are_station_scoped() -> None:
    with _client() as client:
        ongole_admin = _create_station_admin(client, station="Ongole Town")
        markapur_admin = _create_station_admin(client, station="Markapur Town")
        ongole_headers = _auth_headers(client, ongole_admin["username"], ongole_admin["password"])
        markapur_headers = _auth_headers(client, markapur_admin["username"], markapur_admin["password"])

        ongole_profile = client.get("/v1/station-admin/profile", headers=ongole_headers)
        markapur_profile = client.get("/v1/station-admin/profile", headers=markapur_headers)
        assert ongole_profile.status_code == 200
        assert markapur_profile.status_code == 200
        assert ongole_profile.json()["data"]["station_name"] == "Ongole Town"
        assert markapur_profile.json()["data"]["station_name"] == "Markapur Town"

        update_station = client.patch(
            "/v1/station-admin/station",
            headers=ongole_headers,
            json={
                "address": "Updated Ongole Town Police Station",
                "phone_number": "9000099999",
                "email": "updated.ongole@sentinelanpr.ai",
            },
        )
        assert update_station.status_code == 200
        assert update_station.json()["data"]["station_name"] == "Ongole Town"
        assert update_station.json()["data"]["address"] == "Updated Ongole Town Police Station"

        markapur_after = client.get("/v1/station-admin/profile", headers=markapur_headers)
        assert markapur_after.json()["data"]["address"] != "Updated Ongole Town Police Station"
