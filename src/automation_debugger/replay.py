"""Local mock replay engine with duplicate and dead-letter protection."""

from __future__ import annotations

from typing import Any

from automation_debugger.dead_letter import write_dead_letter_record
from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.idempotency import InMemoryIdempotencyStore, idempotency_key
from automation_debugger.models import FailureClass, ReplayResult


def replay_payload(source: str | dict[str, Any], store: InMemoryIdempotencyStore | None = None) -> ReplayResult:
    store = store or InMemoryIdempotencyStore()
    diagnosis = diagnose_payload(source)
    payload = diagnosis.corrected_payload
    key = idempotency_key(payload)
    if key == "missing-idempotency-key":
        return ReplayResult(
            trace_id=diagnosis.trace_id,
            status="refused",
            reason="Missing event_id/idempotency_key; replay could duplicate destination operations.",
        )
    if store.seen(key):
        return ReplayResult(
            trace_id=diagnosis.trace_id,
            status="duplicate",
            reason="Idempotency guard refused duplicate local replay.",
            operation_count=0,
        )
    if diagnosis.failure_class is FailureClass.DUPLICATE_EVENT:
        return ReplayResult(
            trace_id=diagnosis.trace_id,
            status="duplicate",
            reason=diagnosis.diagnosis_summary,
            operation_count=0,
        )
    if diagnosis.failure_class in {
        FailureClass.INVALID_WEBHOOK_SIGNATURE,
        FailureClass.MISSING_REQUIRED_FIELD,
        FailureClass.UNKNOWN_EVENT_TYPE,
        FailureClass.RATE_LIMIT_BACKOFF_NEEDED,
    }:
        return ReplayResult(
            trace_id=diagnosis.trace_id,
            status="blocked",
            reason=diagnosis.diagnosis_summary,
        )
    if diagnosis.failure_class is FailureClass.DOWNSTREAM_500_LOOP:
        path = write_dead_letter_record(
            trace_id=diagnosis.trace_id,
            workflow_name=diagnosis.workflow_name,
            payload=payload,
            reason=diagnosis.diagnosis_summary,
            retry_count=int(payload.get("retry_count", 0) or 0),
        )
        return ReplayResult(
            trace_id=diagnosis.trace_id,
            status="dead_lettered",
            reason=diagnosis.diagnosis_summary,
            retry_count=int(payload.get("retry_count", 0) or 0),
            dead_letter_path=str(path),
        )
    result = ReplayResult(
        trace_id=diagnosis.trace_id,
        status="passed",
        destination="mock-crm",
        reason="Local mock replay accepted corrected payload; no live services used.",
        operation_count=1,
    )
    store.put(key, result.model_dump(mode="json"))
    return result
