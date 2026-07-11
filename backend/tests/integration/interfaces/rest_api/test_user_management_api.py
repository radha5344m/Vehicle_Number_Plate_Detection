"""User management API integration tests."""

import re
import uuid

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login(client: TestClient, identifier: str, password: str) -> dict:
    response = client.post(
        "/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_users_requires_super_admin() -> None:
    with _client() as client:
        officer = _login(client, "ap001", "Officer@123")
        response = client.get(
            "/v1/users",
            headers={"Authorization": f"Bearer {officer['access_token']}"},
        )
        assert response.status_code == 403


def test_super_admin_can_create_edit_deactivate_reset_and_filter_users() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        headers = {"Authorization": f"Bearer {admin['access_token']}"}
        token = uuid.uuid4().hex[:8]
        email = f"priya{token}@sentinelanpr.ai"
        first_name = f"Priya{token[:4]}"

        create = client.post(
            "/v1/users",
            headers=headers,
            json={
                "first_name": first_name,
                "last_name": "Reddy",
                "email": email,
                "phone_number": "9000001001",
                "rank": "Inspector",
                "role": "STATION_ADMIN",
                "police_station": "Markapur Town",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert create.status_code == 201
        create_data = create.json()["data"]
        created = create_data["user"]
        officer_id = created["officer_id"]
        employee_id = created["employee_id"]
        user_id = created["user_id"]
        username = created["username"]
        assert re.fullmatch(r"AP-\d{2}-\d{2,}", user_id)
        assert employee_id.startswith("STA")
        assert username == employee_id.lower()
        assert create_data["temporary_password"] == f"{employee_id}@2026"
        assert create_data["password_change_required"] is True
        temporary_password = create_data["temporary_password"]

        query = client.get(
            f"/v1/users?search={first_name}&role=STATION_ADMIN&station=Markapur",
            headers=headers,
        )
        assert query.status_code == 200
        items = query.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["employee_id"] == employee_id
        assert items[0]["user_id"] == user_id

        update = client.patch(
            f"/v1/users/{officer_id}",
            headers=headers,
            json={
                "employee_id": employee_id,
                "first_name": first_name,
                "last_name": "Rao",
                "email": f"updated.{email}",
                "phone_number": "9000002002",
                "rank": "DSP",
                "role": "POLICE_OFFICER",
                "police_station": "Ongole Rural",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert update.status_code == 200
        assert update.json()["data"]["user"]["full_name"] == f"{first_name} Rao"
        assert update.json()["data"]["user"]["role"] == "POLICE_OFFICER"

        deactivate = client.post(f"/v1/users/{officer_id}/deactivate", headers=headers)
        assert deactivate.status_code == 200
        assert deactivate.json()["data"]["user"]["status"] == "inactive"

        reset_password = client.post(
            f"/v1/users/{officer_id}/reset-password",
            headers=headers,
            json={"new_password": "ResetPass@456"},
        )
        assert reset_password.status_code == 200
        assert reset_password.json()["data"]["temporary_password"] is None

        reset_generated = client.post(
            f"/v1/users/{officer_id}/reset-password",
            headers=headers,
            json={},
        )
        assert reset_generated.status_code == 200
        generated_password = reset_generated.json()["data"]["temporary_password"]
        assert generated_password == f"{employee_id}@2026"

        login_after_reset = client.post(
            "/v1/auth/login",
            json={"identifier": username, "password": generated_password},
        )
        assert login_after_reset.status_code == 403

        activate = client.post(f"/v1/users/{officer_id}/activate", headers=headers)
        assert activate.status_code == 200
        relogin = client.post(
            "/v1/auth/login",
            json={"identifier": username, "password": generated_password},
        )
        assert relogin.status_code == 200
        assert relogin.json()["data"]["role"] == "POLICE_OFFICER"

        delete = client.delete(f"/v1/users/{officer_id}", headers=headers)
        assert delete.status_code == 200

        after_delete = client.get(f"/v1/users?search={employee_id}", headers=headers)
        assert after_delete.status_code == 200
        assert after_delete.json()["data"]["items"] == []


def test_super_admin_can_create_another_super_admin_without_station() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        headers = {"Authorization": f"Bearer {admin['access_token']}"}
        token = uuid.uuid4().hex[:8]
        response = client.post(
            "/v1/users",
            headers=headers,
            json={
                "first_name": "Deputy",
                "last_name": "Admin",
                "email": f"deputy{token}@sentinelanpr.ai",
                "phone_number": "9000003003",
                "role": "SUPER_ADMIN",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["user"]["role"] == "SUPER_ADMIN"
        assert data["user"]["police_station"] == "Headquarters"
        assert data["user"]["employee_id"].startswith("ADMIN")
        assert data["user"]["username"] == data["user"]["employee_id"].lower()
        assert data["temporary_password"] == f"{data['user']['employee_id']}@2026"
        assert data["password_change_required"] is True


def test_user_ids_are_unique_across_multiple_creates() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        headers = {"Authorization": f"Bearer {admin['access_token']}"}
        user_ids: list[str] = []
        for index in range(2):
            token = uuid.uuid4().hex[:6]
            response = client.post(
                "/v1/users",
                headers=headers,
                json={
                    "first_name": f"User{index}",
                    "last_name": "Test",
                    "email": f"user{index}-{token}@sentinelanpr.ai",
                    "rank": "Inspector",
                    "role": "POLICE_OFFICER",
                    "police_station": "Markapur Town",
                    "status": "active",
                },
            )
            assert response.status_code == 201
            user_ids.append(response.json()["data"]["user"]["user_id"])
        assert len(set(user_ids)) == 2


def test_super_admin_can_reset_station_admin_password_with_audit_fields() -> None:
    with _client() as client:
        admin = _login(client, "superadmin", "Admin@123")
        headers = {"Authorization": f"Bearer {admin['access_token']}"}
        token = uuid.uuid4().hex[:8]
        email = f"stationadmin{token}@sentinelanpr.ai"

        create = client.post(
            "/v1/users",
            headers=headers,
            json={
                "first_name": "Reset",
                "last_name": "Target",
                "email": email,
                "rank": "Inspector",
                "role": "STATION_ADMIN",
                "police_station": "Markapur Town",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert create.status_code == 201
        officer_id = create.json()["data"]["user"]["officer_id"]
        username = create.json()["data"]["user"]["username"]

        reset = client.post(
            f"/v1/users/station-admins/{officer_id}/reset-password",
            headers=headers,
            json={"new_password": "ResetPass@456", "confirm_password": "ResetPass@456"},
        )
        assert reset.status_code == 200
        data = reset.json()["data"]
        assert data["temporary_password"] is None
        assert data["password_change_required"] is True

        login = client.post(
            "/v1/auth/login",
            json={"identifier": username, "password": "ResetPass@456"},
        )
        assert login.status_code == 200


def test_station_admin_cannot_reset_another_station_admin_password() -> None:
    with _client() as client:
        super_admin = _login(client, "superadmin", "Admin@123")
        super_headers = {"Authorization": f"Bearer {super_admin['access_token']}"}
        token = uuid.uuid4().hex[:8]
        email = f"peeradmin{token}@sentinelanpr.ai"

        create_target = client.post(
            "/v1/users",
            headers=super_headers,
            json={
                "first_name": "Peer",
                "last_name": "Admin",
                "email": email,
                "rank": "Inspector",
                "role": "STATION_ADMIN",
                "police_station": "Markapur Town",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert create_target.status_code == 201
        target_officer_id = create_target.json()["data"]["user"]["officer_id"]

        actor_email = f"actoradmin{token}@sentinelanpr.ai"
        create_actor = client.post(
            "/v1/users",
            headers=super_headers,
            json={
                "first_name": "Actor",
                "last_name": "Admin",
                "email": actor_email,
                "rank": "Inspector",
                "role": "STATION_ADMIN",
                "police_station": "Ongole Rural",
                "district": "Prakasam",
                "status": "active",
            },
        )
        assert create_actor.status_code == 201
        actor_data = create_actor.json()["data"]
        actor_username = actor_data["user"]["username"]
        actor_password = actor_data["temporary_password"]
        activate = client.post(
            f"/v1/users/{actor_data['user']['officer_id']}/activate",
            headers=super_headers,
        )
        assert activate.status_code == 200

        station_admin = _login(client, actor_username, actor_password)
        station_headers = {"Authorization": f"Bearer {station_admin['access_token']}"}
        response = client.post(
            f"/v1/users/station-admins/{target_officer_id}/reset-password",
            headers=station_headers,
            json={"new_password": "Blocked@1234", "confirm_password": "Blocked@1234"},
        )
        assert response.status_code == 403
