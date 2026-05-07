from __future__ import annotations

from automation_debugger.debugger import diagnose_workflow


def test_malformed_payload_gets_corrected_and_replayed() -> None:
    result = diagnose_workflow(
        {
            "event_id": "evt-1",
            "type": "lead.created",
            "email": "ALICE@EXAMPLE.COM",
            "created_at": "05/06/2026",
        }
    )

    assert result["severity"] == "medium"
    assert result["likely_failure_step"] == "field_mapping"
    assert "created_at" in result["broken_fields"]
    assert result["corrected_payload"]["email"] == "alice@example.com"
    assert result["corrected_payload"]["created_at"] == "2026-05-06"
    assert result["replay_result"]["status"] == "passed"
    assert result["safe_to_retry"] is True
    assert result["live_services_used"] is False


def test_missing_required_email_routes_to_manual_review() -> None:
    result = diagnose_workflow({"event_id": "evt-2", "type": "lead.created"})

    assert result["severity"] == "high"
    assert result["replay_result"]["status"] == "blocked"
    assert result["safe_to_retry"] is False
    assert "email" in result["broken_fields"]


def test_duplicate_event_is_not_safe_to_retry() -> None:
    result = diagnose_workflow({"event_id": "duplicate-001", "type": "lead.created", "email": "a@b.com"})

    assert result["replay_result"]["status"] == "duplicate"
    assert result["safe_to_retry"] is False
