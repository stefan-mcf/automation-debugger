import json
from pathlib import Path

from automation_debugger.dead_letter import write_dead_letter_record


def test_dead_letter_record_is_local_and_safe(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    path = write_dead_letter_record(trace_id="trace-x", workflow_name="Synthetic", payload={"x": 1}, reason="timeout", retry_count=3)
    data = json.loads(path.read_text())
    assert data["replay_status"] == "dead_lettered"
    assert data["fixture_safe"] is True
    assert data["live_services_used"] is False
