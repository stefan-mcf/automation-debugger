"""Backwards-compatible public diagnosis function."""

from __future__ import annotations

from typing import Any

from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.replay import replay_payload


def diagnose_workflow(payload: dict[str, Any]) -> dict[str, Any]:
    """Return diagnosis, corrected payload, replay result, and handoff notes as JSON dict."""
    diagnosis = diagnose_payload(payload)
    replay = replay_payload(payload)
    data = diagnosis.model_dump(mode="json")
    data["replay_result"] = replay.model_dump(mode="json")
    return data
