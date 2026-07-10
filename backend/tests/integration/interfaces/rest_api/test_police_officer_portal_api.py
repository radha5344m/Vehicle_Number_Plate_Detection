"""Police officer portal integration tests."""

import uuid

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login(client: TestClient, badge_number: str, password: str) -> dict:
    response = client.post("/v1/auth/login", json={"badge_number": badge_number, "password": password})
    assert response.status_code == 200
    return response.json()["data"]


def _create_police_officer(client: TestClient, station: str, token: str) -> dict[str, str]:
    admin = _login(client, "superadmin", "Admin@123")
    headers = {"Authorization": f"Bearer {admin['access_token']}"}
    username = f"field{token}"
    create = client.post(
        "/v1/users",
        headers=headers,
        json={
            "employee_id": f"EMP-PO-{token.upper()}",
            "first_name": "Field",
            "last_name": "Officer",
            "username": username,
            "email": f"{username}@sentinelanpr.ai",
            "phone_number": "9000012345",
            "badge_number": f"PO{token[:4].upper()}",
            "rank": "Constable",
            "role": "POLICE_OFFICER",
            "police_station": station,
            "district": "Prakasam",
            "password": "Officer@1234",
        },
    )
    assert create.status_code == 201
    return {"username": username, "password": "Officer@1234"}


def _save_scan(client: TestClient, access_token: str, plate: str) -> None:
    response = client.post(
        "/v1/history/scans",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "plate": plate,
            "risk_score": 0.88,
            "risk_level": "high",
            "location_label": "Officer Portal Checkpoint",
        },
    )
    assert response.status_code == 200


def test_police_officer_portal_requires_police_officer_role() -> None:
    with _client() as client:
        station_admin = _create_police_officer(client, "Ongole Town", uuid.uuid4().hex[:6])
        officer = _login(client, station_admin["username"], station_admin["password"])
        response = client.get(
            "/v1/station-admin/dashboard",
            headers={"Authorization": f"Bearer {officer['access_token']}"},
        )
        assert response.status_code == 403


def test_police_officer_portal_scopes_data_and_supports_profile_workflows() -> None:
    with _client() as client:
        first = _create_police_officer(client, "Ongole Town", uuid.uuid4().hex[:6])
        second = _create_police_officer(client, "Markapur Town", uuid.uuid4().hex[:6])

        first_login = _login(client, first["username"], first["password"])
        second_login = _login(client, second["username"], second["password"])

        own_plate = f"AP{uuid.uuid4().hex[:6].upper()}11"
        other_plate = f"AP{uuid.uuid4().hex[:6].upper()}22"
        _save_scan(client, first_login["access_token"], own_plate)
        _save_scan(client, second_login["access_token"], other_plate)

        headers = {"Authorization": f"Bearer {first_login['access_token']}"}

        dashboard = client.get("/v1/police-officer/dashboard", headers=headers)
        assert dashboard.status_code == 200
        assert dashboard.json()["data"]["summary"]["high_risk_vehicles_found"] >= 1

        investigations = client.get("/v1/police-officer/investigations", headers=headers)
        assert investigations.status_code == 200
        registrations = {
            item["registration_number"] for item in investigations.json()["data"]["items"]
        }
        assert own_plate in registrations
        assert other_plate not in registrations

        reports = client.get("/v1/police-officer/reports", headers=headers)
        assert reports.status_code == 200
        report_regs = {item["registration_number"] for item in reports.json()["data"]["items"]}
        assert own_plate in report_regs
        assert other_plate not in report_regs

        export_csv = client.get("/v1/police-officer/reports/export/csv", headers=headers)
        assert export_csv.status_code == 200
        assert "text/csv" in export_csv.headers["content-type"]

        notifications = client.get("/v1/police-officer/notifications", headers=headers)
        assert notifications.status_code == 200
        assert isinstance(notifications.json()["data"]["items"], list)

        profile = client.get("/v1/police-officer/profile", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["data"]["username"] == first["username"]

        change_password = client.post(
            "/v1/police-officer/profile/change-password",
            headers=headers,
            json={"current_password": "Officer@1234", "new_password": "Officer@5678"},
        )
        assert change_password.status_code == 200

        relogin = _login(client, first["username"], "Officer@5678")
        assert relogin["role"] == "POLICE_OFFICER"

        analytics = client.get("/v1/analytics/overview", headers=headers)
        assert analytics.status_code == 403

        users = client.get("/v1/users", headers=headers)
        assert users.status_code == 403

        stations = client.get("/v1/stations", headers=headers)
        assert stations.status_code == 403
