"""Local JSON dead-letter evidence for refused/unsafe replay."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_dead_letter_record(*, trace_id: str, workflow_name: str, payload: dict[str, Any], reason: str, retry_count: int = 0) -> Path:
    out_dir = Path("examples/output/dead-letter")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{trace_id}.json"
    record = {
        "trace_id": trace_id,
        "workflow_name": workflow_name,
        "retry_count": retry_count,
        "error_reason": reason,
        "replay_status": "dead_lettered",
        "stored_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "raw_failed_payload": payload,
        "fixture_safe": True,
        "live_services_used": False,
        "synthetic_data_only": True,
    }
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return path
