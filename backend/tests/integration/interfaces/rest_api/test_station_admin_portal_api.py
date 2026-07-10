"""Station admin portal integration tests."""

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


def _ensure_station_admin(client: TestClient) -> dict[str, str]:
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
            "police_station": "Ongole Town",
            "district": "Prakasam",
            "status": "active",
        },
    )
    assert create.status_code == 201
    return {"username": username, "badge": badge, "password": create.json()["data"]["temporary_password"]}


def test_station_admin_portal_requires_station_admin_role() -> None:
    with _client() as client:
        officer = _login(client, "AP001", "Officer@123")
        response = client.get(
            "/v1/station-admin/dashboard",
            headers={"Authorization": f"Bearer {officer['access_token']}"},
        )
        assert response.status_code == 403


def test_station_admin_can_manage_station_portal() -> None:
    with _client() as client:
        station_admin_account = _ensure_station_admin(client)
        station_admin = _login(client, station_admin_account["username"], station_admin_account["password"])
        headers = {"Authorization": f"Bearer {station_admin['access_token']}"}
        token = uuid.uuid4().hex[:6]
        officer_username = f"officer{token}"
        officer_badge = f"OP{token[:4].upper()}"

        dashboard = client.get("/v1/station-admin/dashboard", headers=headers)
        assert dashboard.status_code == 200
        assert "summary" in dashboard.json()["data"]

        create_officer = client.post(
            "/v1/station-admin/officers",
            headers=headers,
            json={
                "employee_id": f"EMP-PO-{token.upper()}",
                "first_name": "Field",
                "last_name": "Officer",
                "username": officer_username,
                "email": f"{officer_username}@sentinelanpr.ai",
                "phone_number": "9000022222",
                "badge_number": officer_badge,
                "rank": "Constable",
                "status": "active",
            },
        )
        assert create_officer.status_code == 201
        created_officer = create_officer.json()["data"]["officer"]
        assert create_officer.json()["data"]["temporary_password"]
        assert create_officer.json()["data"]["password_change_required"] is True
        officer_id = created_officer["officer_id"]

        officers = client.get("/v1/station-admin/officers?search=Field", headers=headers)
        assert officers.status_code == 200
        assert len(officers.json()["data"]["items"]) >= 1

        update_officer = client.put(
            f"/v1/station-admin/officers/{officer_id}",
            headers=headers,
            json={
                "first_name": "Field",
                "last_name": "Commander",
                "email": f"updated.{officer_username}@sentinelanpr.ai",
                "phone_number": "9000033333",
                "rank": "Head Constable",
                "status": "active",
            },
        )
        assert update_officer.status_code == 200
        assert update_officer.json()["data"]["officer"]["officer_name"] == "Field Commander"

        reset_password = client.post(
            f"/v1/station-admin/officers/{officer_id}/reset-password",
            headers=headers,
            json={"new_password": "Reset@1234"},
        )
        assert reset_password.status_code == 200

        deactivate_officer = client.post(
            f"/v1/station-admin/officers/{officer_id}/deactivate",
            headers=headers,
        )
        assert deactivate_officer.status_code == 200
        assert deactivate_officer.json()["data"]["officer"]["status"] == "inactive"

        investigations = client.get(
            "/v1/station-admin/investigations?officer=Ravi&verification_status=found",
            headers=headers,
        )
        assert investigations.status_code == 200
        assert "items" in investigations.json()["data"]

        reports = client.get("/v1/station-admin/reports", headers=headers)
        assert reports.status_code == 200
        assert "summary" in reports.json()["data"]

        analytics = client.get("/v1/station-admin/analytics", headers=headers)
        assert analytics.status_code == 200
        assert "weekly_labels" in analytics.json()["data"]

        notifications = client.get("/v1/station-admin/notifications", headers=headers)
        assert notifications.status_code == 200
        assert isinstance(notifications.json()["data"]["items"], list)

        profile = client.get("/v1/station-admin/profile", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["data"]["station_name"] == "Ongole Town"
