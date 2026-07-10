"""RBAC authorization and scoping integration tests."""

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


def _create_user(
    client: TestClient,
    headers: dict[str, str],
    *,
    token: str,
    role: str,
    station: str,
) -> dict:
    response = client.post(
        "/v1/users",
        headers=headers,
        json={
            "employee_id": f"EMP-{token.upper()}",
            "first_name": role.title().replace("_", ""),
            "last_name": token[:4].upper(),
            "username": f"{role.lower()}_{token}",
            "email": f"{role.lower()}_{token}@sentinelanpr.ai",
            "phone_number": "9000012345",
            "badge_number": f"RB{token[:6].upper()}",
            "rank": "Inspector" if role == "STATION_ADMIN" else "Constable",
            "role": role,
            "police_station": station,
            "district": "Prakasam",
            "password": "TempPass@123",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["user"]


def _save_scan(client: TestClient, token: str, plate: str) -> None:
    response = client.post(
        "/v1/history/scans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "plate": plate,
            "risk_score": 0.42,
            "risk_level": "medium",
            "location_label": "RBAC Checkpoint",
        },
    )
    assert response.status_code == 200


def test_rbac_enforces_permissions_and_data_scoping() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        admin_headers = {"Authorization": f"Bearer {admin['access_token']}"}
        token = uuid.uuid4().hex[:8]

        station_admin = _create_user(
            client,
            admin_headers,
            token=f"sta{token}",
            role="STATION_ADMIN",
            station="Ongole Town",
        )
        same_station_officer = _create_user(
            client,
            admin_headers,
            token=f"ong{token}",
            role="POLICE_OFFICER",
            station="Ongole Town",
        )
        other_station_officer = _create_user(
            client,
            admin_headers,
            token=f"mrk{token}",
            role="POLICE_OFFICER",
            station="Markapur Town",
        )

        station_admin_session = _login(client, station_admin["username"], "TempPass@123")
        same_station_session = _login(client, same_station_officer["username"], "TempPass@123")
        other_station_session = _login(client, other_station_officer["username"], "TempPass@123")
        seeded_officer_session = _login(client, "AP001", "Officer@123")

        own_plate = f"AP{uuid.uuid4().hex[:6].upper()}11"
        same_station_plate = f"AP{uuid.uuid4().hex[:6].upper()}22"
        other_station_plate = f"AP{uuid.uuid4().hex[:6].upper()}33"

        _save_scan(client, seeded_officer_session["access_token"], own_plate)
        _save_scan(client, same_station_session["access_token"], same_station_plate)
        _save_scan(client, other_station_session["access_token"], other_station_plate)

        police_history = client.get(
            "/v1/history/scans",
            headers={"Authorization": f"Bearer {seeded_officer_session['access_token']}"},
        )
        assert police_history.status_code == 200
        police_plates = {item["plate_text"] for item in police_history.json()["data"]["items"]}
        assert own_plate in police_plates
        assert same_station_plate not in police_plates
        assert other_station_plate not in police_plates

        station_history = client.get(
            "/v1/history/scans",
            headers={"Authorization": f"Bearer {station_admin_session['access_token']}"},
        )
        assert station_history.status_code == 200
        station_plates = {item["plate_text"] for item in station_history.json()["data"]["items"]}
        assert own_plate in station_plates
        assert same_station_plate in station_plates
        assert other_station_plate not in station_plates

        police_reports = client.get(
            "/v1/investigation-reports",
            headers={"Authorization": f"Bearer {seeded_officer_session['access_token']}"},
        )
        assert police_reports.status_code == 200
        police_report_plates = {
            item["registration_number"] for item in police_reports.json()["data"]["items"]
        }
        assert own_plate in police_report_plates
        assert same_station_plate not in police_report_plates
        assert other_station_plate not in police_report_plates

        station_reports = client.get(
            "/v1/investigation-reports",
            headers={"Authorization": f"Bearer {station_admin_session['access_token']}"},
        )
        assert station_reports.status_code == 200
        station_report_plates = {
            item["registration_number"] for item in station_reports.json()["data"]["items"]
        }
        assert own_plate in station_report_plates
        assert same_station_plate in station_report_plates
        assert other_station_plate not in station_report_plates

        analytics_for_police = client.get(
            "/v1/analytics/overview",
            headers={"Authorization": f"Bearer {seeded_officer_session['access_token']}"},
        )
        assert analytics_for_police.status_code == 403

        analytics_for_station_admin = client.get(
            "/v1/analytics/overview",
            headers={"Authorization": f"Bearer {station_admin_session['access_token']}"},
        )
        assert analytics_for_station_admin.status_code == 200

        users_for_station_admin = client.get(
            "/v1/users",
            headers={"Authorization": f"Bearer {station_admin_session['access_token']}"},
        )
        assert users_for_station_admin.status_code == 403

        stations_for_station_admin = client.get(
            "/v1/stations",
            headers={"Authorization": f"Bearer {station_admin_session['access_token']}"},
        )
        assert stations_for_station_admin.status_code == 403
