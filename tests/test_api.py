from fastapi.testclient import TestClient

from automation_debugger.api import app

client = TestClient(app)


def test_health_endpoint_boundary() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["fixture_safe"] is True
    assert response.json()["live_services_used"] is False


def test_diagnose_endpoint() -> None:
    response = client.post("/diagnose", json={"payload": {"event_id": "evt", "type": "lead.created", "email": "x@example.test", "created_at": "05/06/2026"}})
    assert response.status_code == 200
    assert response.json()["failure_class"] == "malformed_date"


def test_replay_endpoint() -> None:
    response = client.post("/replay", json={"payload": {"event_id": "evt-r", "type": "lead.created", "email": "x@example.test", "created_at": "2026-05-06"}})
    assert response.status_code == 200
    assert response.json()["status"] == "passed"


def test_report_endpoint() -> None:
    response = client.post("/report", json={"payload": {"event_id": "evt-report", "type": "lead.created", "email": "x@example.test", "created_at": "05/06/2026"}})
    assert response.status_code == 200
    assert response.json()["fixture_safe"] is True
    assert "Executive summary" in response.json()["body"]
