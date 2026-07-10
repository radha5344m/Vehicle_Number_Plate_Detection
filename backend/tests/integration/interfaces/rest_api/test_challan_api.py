"""e-Challan API integration tests."""

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login(client: TestClient, identifier: str, password: str) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_challan_routes_require_auth() -> None:
    with _client() as client:
        assert client.get("/v1/challans/violations").status_code == 401
        assert client.get("/v1/challans/search?registration_number=AP09AB1234").status_code == 401


def test_list_violation_master() -> None:
    with _client() as client:
        token = _login(client, "ap001", "Officer@123")
        response = client.get("/v1/challans/violations", headers=_auth_headers(token))
        assert response.status_code == 200
        items = response.json()["data"]
        assert len(items) >= 10
        codes = {item["violation_code"] for item in items}
        assert "NO_HELMET" in codes
        assert "OTHER" in codes


def test_issue_and_query_challan_as_officer() -> None:
    with _client() as client:
        token = _login(client, "ap001", "Officer@123")
        create_response = client.post(
            "/v1/challans",
            headers=_auth_headers(token),
            json={
                "registration_number": "AP09AB1234",
                "violation_type": "NO_HELMET",
                "fine_amount": 500,
                "remarks": "No helmet at checkpoint",
                "location_label": "Ongole Junction",
            },
        )
        assert create_response.status_code == 201, create_response.text
        created = create_response.json()["data"]["challan"]
        assert created["challan_number"].startswith("CH-")
        assert created["payment_status"] == "pending"
        assert created["fine_amount"] == 500

        search_response = client.get(
            "/v1/challans/search?registration_number=AP09AB1234",
            headers=_auth_headers(token),
        )
        assert search_response.status_code == 200
        search_data = search_response.json()["data"]
        assert search_data["pending_challans_count"] >= 1
        assert search_data["outstanding_fine_inr"] >= 500
        assert any(item["id"] == created["id"] for item in search_data["existing_challans"])

        pdf_response = client.get(
            f"/v1/challans/{created['id']}/download",
            headers=_auth_headers(token),
        )
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert len(pdf_response.content) > 100


def test_officer_cannot_delete_challan() -> None:
    with _client() as client:
        officer_token = _login(client, "ap001", "Officer@123")
        create_response = client.post(
            "/v1/challans",
            headers=_auth_headers(officer_token),
            json={
                "registration_number": "AP09ZZ9999",
                "violation_type": "SIGNAL_JUMP",
                "fine_amount": 1000,
            },
        )
        assert create_response.status_code == 201
        challan_id = create_response.json()["data"]["challan"]["id"]

        delete_response = client.delete(
            f"/v1/challans/{challan_id}",
            headers=_auth_headers(officer_token),
        )
        assert delete_response.status_code == 403


def test_super_admin_can_delete_challan() -> None:
    with _client() as client:
        officer_token = _login(client, "ap001", "Officer@123")
        create_response = client.post(
            "/v1/challans",
            headers=_auth_headers(officer_token),
            json={
                "registration_number": "AP09DEL001",
                "violation_type": "WRONG_PARKING",
                "fine_amount": 500,
            },
        )
        challan_id = create_response.json()["data"]["challan"]["id"]

        admin_token = _login(client, "superadmin", "Admin@123")
        delete_response = client.delete(
            f"/v1/challans/{challan_id}",
            headers=_auth_headers(admin_token),
        )
        assert delete_response.status_code == 204


def test_challan_analytics() -> None:
    with _client() as client:
        token = _login(client, "superadmin", "Admin@123")
        response = client.get("/v1/challans/analytics", headers=_auth_headers(token))
        assert response.status_code == 200
        data = response.json()["data"]
        assert "total_challans" in data
        assert "outstanding_fine_inr" in data
        assert "violation_distribution" in data
