from pathlib import Path

from fastapi.testclient import TestClient

from pmo.api import create_app


def test_api_sample_seed(tmp_path: Path):
    db_file = tmp_path / "api.db"
    app = create_app(f"sqlite:///{db_file}")
    client = TestClient(app)

    response = client.post("/api/sample-data")
    assert response.status_code == 201
    payload = response.json()
    assert "business_unit_id" in payload

    list_response = client.get("/api/business-units")
    assert list_response.status_code == 200
    units = list_response.json()
    assert len(units) == 1
    assert units[0]["projects"]

    project_id = units[0]["projects"][0]["id"]
    detail = client.get(f"/api/projects/{project_id}")
    assert detail.status_code == 200
    project = detail.json()
    assert project["status_history"]
    assert project["resource_assignments"]
