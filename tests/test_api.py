from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pmo.api import create_app


@pytest.fixture()
def api_client(tmp_path: Path):
    db_file = tmp_path / "api.db"
    app = create_app(f"sqlite:///{db_file}")
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()


def test_api_sample_seed(api_client: TestClient):
    response = api_client.post("/api/sample-data")
    assert response.status_code == 201
    payload = response.json()
    assert "business_unit_id" in payload

    list_response = api_client.get("/api/business-units")
    assert list_response.status_code == 200
    units = list_response.json()
    assert len(units) == 1
    assert units[0]["projects"]

    project_id = units[0]["projects"][0]["id"]
    detail = api_client.get(f"/api/projects/{project_id}")
    assert detail.status_code == 200
    project = detail.json()
    assert project["status_history"]
    assert project["resource_assignments"]


def test_business_unit_crud(api_client: TestClient):
    api_client.post("/api/sample-data")

    create_resp = api_client.post(
        "/api/business-units",
        json={"name": "New Unit", "type": "businessunit"},
    )
    assert create_resp.status_code == 201
    business_unit = create_resp.json()
    assert business_unit["name"] == "New Unit"

    bu_id = business_unit["id"]
    update_resp = api_client.put(
        f"/api/business-units/{bu_id}", json={"name": "Updated Unit"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Unit"

    delete_resp = api_client.delete(f"/api/business-units/{bu_id}")
    assert delete_resp.status_code == 204


def test_project_crud(api_client: TestClient):
    api_client.post("/api/sample-data")

    units_resp = api_client.get("/api/business-units")
    unit_id = units_resp.json()[0]["id"]

    create_payload = {
        "name": "Test Project",
        "businessunit_id": unit_id,
        "description": "Test description",
        "tender_no": "TEST-001",
        "scope_of_work": "Test scope",
        "budget": 100000.0,
        "bid_value": 95000.0,
    }
    create_resp = api_client.post("/api/projects", json=create_payload)
    assert create_resp.status_code == 201
    project = create_resp.json()
    assert project["name"] == "Test Project"

    project_id = project["id"]
    update_resp = api_client.put(
        f"/api/projects/{project_id}",
        json={"budget": 120000.0, "bid_value": 110000.0},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["budget"] == 120000.0
    assert updated["bid_value"] == 110000.0

    delete_resp = api_client.delete(f"/api/projects/{project_id}")
    assert delete_resp.status_code == 204


def test_issue_crud(api_client: TestClient):
    api_client.post("/api/sample-data")
    units_resp = api_client.get("/api/business-units")
    project_id = units_resp.json()[0]["projects"][0]["id"]

    create_resp = api_client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "name": "New Issue",
            "severity": "high",
            "status": "open",
            "opened_on": date.today().isoformat(),
        },
    )
    assert create_resp.status_code == 201
    issue = create_resp.json()
    assert issue["name"] == "New Issue"

    issue_id = issue["id"]
    update_resp = api_client.put(
        f"/api/issues/{issue_id}",
        json={"status": "resolved", "closed_on": date.today().isoformat()},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "resolved"

    delete_resp = api_client.delete(f"/api/issues/{issue_id}")
    assert delete_resp.status_code == 204


def test_change_request_crud(api_client: TestClient):
    api_client.post("/api/sample-data")
    units_resp = api_client.get("/api/business-units")
    project_id = units_resp.json()[0]["projects"][0]["id"]

    create_resp = api_client.post(
        f"/api/projects/{project_id}/change-requests",
        json={
            "name": "Scope Adjustment",
            "status": "submitted",
            "submitted_on": date.today().isoformat(),
        },
    )
    assert create_resp.status_code == 201
    change_request = create_resp.json()
    assert change_request["name"] == "Scope Adjustment"

    cr_id = change_request["id"]
    update_resp = api_client.put(
        f"/api/change-requests/{cr_id}",
        json={"status": "approved", "impact_summary": "Budget +5%"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "approved"

    delete_resp = api_client.delete(f"/api/change-requests/{cr_id}")
    assert delete_resp.status_code == 204
