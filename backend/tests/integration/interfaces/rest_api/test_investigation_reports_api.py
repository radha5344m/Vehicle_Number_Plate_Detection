"""Investigation reports API integration tests."""

from fastapi.testclient import TestClient

from sentinel_anpr.interfaces.dependency_injection.wiring.bootstrap import build_container
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app


def _client() -> TestClient:
    app = create_app()
    app.state.container = build_container()
    return TestClient(app)


def _login_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={"badge_number": "AP001", "password": "Officer@123"},
    )
    return response.json()["data"]["access_token"]


def test_investigation_reports_requires_auth() -> None:
    with _client() as client:
        response = client.get("/v1/investigation-reports")
        assert response.status_code == 401


def test_investigation_reports_returns_summary_and_rows() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/investigation-reports",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["summary"]["total_investigations"] >= 1
        assert "risk_distribution" in data
        assert "vehicle_type_distribution" in data
        assert "brand_distribution" in data
        assert "officer_performance" in data
        assert "station_performance" in data
        assert "verification_status_distribution" in data
        assert "daily_investigation_trend" in data
        assert "weekly_investigation_trend" in data
        assert "monthly_investigation_trend" in data
        assert "average_investigation_time_minutes" in data["summary"]
        assert "items" in data
        assert "pagination" in data


def test_investigation_reports_supports_enterprise_filters() -> None:
    with _client() as client:
        token = _login_token(client)
        response = client.get(
            "/v1/investigation-reports?search=AP09AB1234&registration_number=AP09AB1234&investigation_status=completed",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) >= 1
        assert all(item["registration_number"] == "AP09AB1234" for item in items)
        assert all(item["investigation_status"] == "completed" for item in items)


def test_investigation_reports_exports_pdf_csv_excel() -> None:
    with _client() as client:
        token = _login_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        pdf = client.get("/v1/investigation-reports/export/pdf", headers=headers)
        assert pdf.status_code == 200
        assert pdf.headers["content-type"] == "application/pdf"
        assert pdf.content.startswith(b"%PDF")

        csv = client.get("/v1/investigation-reports/export/csv", headers=headers)
        assert csv.status_code == 200
        assert "text/csv" in csv.headers["content-type"]
        assert b"Department Investigation Report" in csv.content
        assert b"Investigation Status" in csv.content
        assert b"District" in csv.content

        excel = client.get("/v1/investigation-reports/export/excel", headers=headers)
        assert excel.status_code == 200
        assert (
            excel.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert excel.content[:2] == b"PK"
