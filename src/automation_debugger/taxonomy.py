"""Failure taxonomy and platform-normalization config loading."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = PACKAGE_ROOT / "configs" / "diagnosis-rules" / "failure-taxonomy.json"
PLATFORM_NORMALIZATION_PATH = PACKAGE_ROOT / "configs" / "diagnosis-rules" / "platform-normalization.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    return data


@lru_cache(maxsize=1)
def load_failure_taxonomy() -> dict[str, Any]:
    data = _load_json(TAXONOMY_PATH)
    classes = data.get("failure_classes", {})
    required = {
        "missing_required_field",
        "malformed_date",
        "duplicate_event",
        "destination_mismatch",
        "unknown_event_type",
        "invalid_webhook_signature",
        "downstream_500_loop",
        "rate_limit_backoff_needed",
    }
    missing = required.difference(classes)
    if missing:
        raise ValueError(f"taxonomy missing classes: {sorted(missing)}")
    return data


@lru_cache(maxsize=1)
def load_platform_normalization() -> dict[str, Any]:
    data = _load_json(PLATFORM_NORMALIZATION_PATH)
    for key in ("generic_webhook", "zapier", "make", "n8n", "api_webhook_bridge"):
        if key not in data.get("platforms", {}):
            raise ValueError(f"platform normalization missing {key}")
    return data
