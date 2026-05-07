"""Local idempotency guard for synthetic replay proof."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def seen(self, key: str) -> bool:
        return key in self._records

    def get(self, key: str) -> dict[str, Any] | None:
        return self._records.get(key)

    def put(self, key: str, value: dict[str, Any]) -> None:
        self._records[key] = dict(value)


class JsonIdempotencyStore(InMemoryIdempotencyStore):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__()
        if self.path.exists():
            data = json.loads(self.path.read_text())
            if isinstance(data, dict):
                self._records = {str(k): dict(v) for k, v in data.items() if isinstance(v, dict)}

    def put(self, key: str, value: dict[str, Any]) -> None:
        super().put(key, value)
        self.path.write_text(json.dumps(self._records, indent=2, sort_keys=True) + "\n")


def idempotency_key(payload: dict[str, Any]) -> str:
    key = payload.get("idempotency_key") or payload.get("event_id")
    return str(key or "missing-idempotency-key")
