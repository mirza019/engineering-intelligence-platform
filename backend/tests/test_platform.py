from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.synthetic import generate_data

client = TestClient(app)


def test_synthetic_data_minimums():
    data = generate_data()
    assert len(data["projects"]) >= 20
    assert len(data["milestones"]) >= 100
    assert len(data["quality_issues"]) >= 50
    assert len(data["lessons_learned"]) >= 50
    assert len({d["document_id"] for d in data["engineering_documents"]}) >= 30


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model"].startswith("qwen")


def test_latest_document_is_r03():
    response = client.get("/api/documents/SPEC-001/latest")
    assert response.status_code == 200
    assert response.json()["revision"] == "R03"
    assert response.json()["revision_status"] == "Released"


def test_supplier_cannot_read_internal_quality_issues():
    response = client.get("/api/quality-issues", headers={"x-role": "supplier", "x-user": "supplier.demo"})
    assert response.status_code == 403


def test_supplier_only_sees_external_current_documents():
    response = client.get("/api/documents", headers={"x-role": "supplier"})
    assert response.status_code == 200
    assert response.json()
    assert all(d["classification"] == "external" and d["is_current"] for d in response.json())


def test_quality_rules_pass():
    response = client.get("/api/quality-results")
    assert response.status_code == 200
    assert all(r["passed"] for r in response.json())


def test_project_detail_composes_domain_data():
    response = client.get("/api/projects/P1007")
    assert response.status_code == 200
    body = response.json()
    assert body["milestones"] and body["equipment"] and body["documents"]
