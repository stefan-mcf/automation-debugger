"""Normalize synthetic platform-style exports into a shared webhook payload shape."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_payload(source: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(source, dict):
        return dict(source)
    path = Path(source)
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def normalize_platform_payload(payload: dict[str, Any]) -> dict[str, Any]:
    platform = str(payload.get("platform") or payload.get("platform_hint") or "generic_webhook")
    if platform == "zapier":
        task = payload.get("task_history", {})
        data = task.get("input_data", {})
        return {
            **data,
            "platform_hint": "zapier",
            "workflow_name": payload.get("workflow_name", "Synthetic Zapier Lead Router"),
            "event_id": task.get("task_id", data.get("event_id", "zapier_task_unknown")),
            "failure_reason": task.get("error", payload.get("failure_reason", "")),
            "failed_step": task.get("step", "zapier_action"),
            "synthetic_data_only": True,
        }
    if platform == "make":
        execution = payload.get("incomplete_execution", {})
        bundle = execution.get("bundle", {})
        return {
            **bundle,
            "platform_hint": "make",
            "workflow_name": payload.get("workflow_name", "Synthetic Make Scenario"),
            "event_id": execution.get("execution_id", bundle.get("event_id", "make-exec-unknown")),
            "failure_reason": execution.get("error", payload.get("failure_reason", "")),
            "failed_step": execution.get("module", "make_module"),
            "synthetic_data_only": True,
        }
    if platform == "n8n":
        execution = payload.get("execution", {})
        node = execution.get("failed_node", {})
        data = execution.get("data", {})
        return {
            **data,
            "platform_hint": "n8n",
            "workflow_name": payload.get("workflow_name", "Synthetic n8n Workflow"),
            "event_id": execution.get("id", data.get("event_id", "n8n-exec-unknown")),
            "failure_reason": node.get("error", payload.get("failure_reason", "")),
            "failed_step": node.get("name", "n8n_node"),
            "synthetic_data_only": True,
        }
    return {**payload, "platform_hint": platform, "synthetic_data_only": True}
