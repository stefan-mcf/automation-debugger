"""Fixture-only webhook safety helpers."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any


def verify_hmac_signature(body: str, signature: str, secret: str = "fixture-secret") -> bool:
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def should_backoff(payload: dict[str, Any]) -> bool:
    reason = str(payload.get("failure_reason", "")).lower()
    status = str(payload.get("status_code", ""))
    return "rate limit" in reason or status == "429"


def should_open_circuit(payload: dict[str, Any]) -> bool:
    reason = str(payload.get("failure_reason", "")).lower()
    retry_count = int(payload.get("retry_count", 0) or 0)
    status = str(payload.get("status_code", ""))
    return retry_count >= 3 and ("timeout" in reason or status.startswith("5"))
