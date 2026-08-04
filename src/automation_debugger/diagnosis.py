"""Taxonomy-driven root-cause diagnosis for synthetic automation failures."""

from __future__ import annotations

import hashlib
from typing import Any

from automation_debugger.correction import suggest_corrections
from automation_debugger.models import DiagnosisResult, DiagnosticObservation, FailureClass, Severity
from automation_debugger.platform_parsers import load_payload, normalize_platform_payload
from automation_debugger.webhook_safety import should_backoff, should_open_circuit


def stable_trace_id(payload: dict[str, Any]) -> str:
    seed = "|".join(str(payload.get(k, "")) for k in ("workflow_name", "event_id", "type"))
    digest = hashlib.sha1(seed.encode()).hexdigest()[:10]
    return f"trace-{digest}"


def diagnose_payload(source: str | dict[str, Any]) -> DiagnosisResult:
    raw = load_payload(source) if not isinstance(source, dict) else source
    payload = normalize_platform_payload(raw)
    corrected, suggestions, correction_fields = suggest_corrections(payload)
    trace_id = str(payload.get("trace_id") or stable_trace_id(payload))
    workflow_name = str(payload.get("workflow_name") or "Synthetic Automation Debug Session")
    platform_hint = str(payload.get("platform_hint") or "generic_webhook")
    event_id = str(payload.get("event_id") or "unknown-event")
    failure_reason = str(payload.get("failure_reason") or "").lower()
    event_type = str(payload.get("type") or payload.get("event_type") or "")
    broken_fields: list[str] = list(dict.fromkeys(correction_fields))
    observations: list[DiagnosticObservation] = []

    def result(
        failure_class: FailureClass,
        severity: Severity,
        step: str,
        summary: str,
        safe_to_retry: bool,
        manual_review: bool,
        notes: str,
    ) -> DiagnosisResult:
        return DiagnosisResult(
            trace_id=trace_id,
            workflow_name=workflow_name,
            platform_hint=platform_hint,
            event_id=event_id,
            failure_class=failure_class,
            severity=severity,
            likely_failure_step=step,
            diagnosis_summary=summary,
            safe_to_retry=safe_to_retry,
            manual_review_required=manual_review,
            broken_fields=broken_fields,
            correction_suggestions=suggestions,
            corrected_payload=corrected,
            handoff_notes=notes,
            observations=observations,
        )

    if payload.get("signature_valid") is False or "signature" in failure_reason:
        broken_fields.append("signature")
        observations.append(DiagnosticObservation(step="webhook_auth", message="Invalid fixture HMAC signature."))
        return result(
            FailureClass.INVALID_WEBHOOK_SIGNATURE,
            Severity.HIGH,
            "webhook_auth",
            "Webhook signature validation failed; replay is refused.",
            False,
            True,
            "Verify HMAC secret and captured raw body before any live retry.",
        )
    if event_id.startswith("duplicate") or payload.get("duplicate") is True:
        broken_fields.append("event_id")
        observations.append(DiagnosticObservation(step="dedupe_guard", message="Duplicate idempotency key detected."))
        return result(
            FailureClass.DUPLICATE_EVENT,
            Severity.MEDIUM,
            "dedupe_guard",
            "Duplicate event/idempotency key detected before replay.",
            False,
            False,
            "Do not replay until idempotency state is checked.",
        )
    if not payload.get("email") and event_type in {"lead.created", "contact.created", ""}:
        broken_fields.append("email")
        observations.append(DiagnosticObservation(step="field_mapping", message="Required email field is missing."))
        return result(
            FailureClass.MISSING_REQUIRED_FIELD,
            Severity.HIGH,
            "field_mapping",
            "Required email is missing; downstream CRM mapping would fail.",
            False,
            True,
            "Request a corrected sample payload before retrying.",
        )
    if should_open_circuit(payload) or "500" in failure_reason or "timeout" in failure_reason:
        observations.append(DiagnosticObservation(step="downstream_call", message="Retry loop would keep hitting 5xx/timeout."))
        return result(
            FailureClass.DOWNSTREAM_500_LOOP,
            Severity.HIGH,
            "downstream_call",
            "Downstream 500/timeout loop detected; circuit breaker should stop replay.",
            False,
            True,
            "Store a local dead-letter record and wait for destination recovery.",
        )
    if should_backoff(payload):
        observations.append(DiagnosticObservation(step="retry_policy", message="Rate limit/backoff condition detected."))
        return result(
            FailureClass.RATE_LIMIT_BACKOFF_NEEDED,
            Severity.MEDIUM,
            "retry_policy",
            "Rate limit detected; retry only with exponential backoff and jitter.",
            False,
            False,
            "Apply backoff policy before approved replay.",
        )
    if "destination" in broken_fields:
        observations.append(DiagnosticObservation(step="routing", message="Destination mismatch corrected locally."))
        return result(
            FailureClass.DESTINATION_MISMATCH,
            Severity.MEDIUM,
            "routing",
            "Destination mismatch would route data to the wrong integration target.",
            True,
            False,
            "Update destination mapping and replay one approved synthetic sample.",
        )
    if "created_at" in broken_fields or "event_date" in broken_fields:
        observations.append(DiagnosticObservation(step="formatter", message="Date field required normalization."))
        return result(
            FailureClass.MALFORMED_DATE,
            Severity.MEDIUM,
            "field_mapping",
            "Payload date format is malformed for the destination mapping.",
            True,
            False,
            "Normalize date formatting before one local mock replay.",
        )
    if event_type and event_type not in {"lead.created", "contact.created", "order.created"}:
        observations.append(DiagnosticObservation(step="event_router", message=f"Unknown event type: {event_type}"))
        return result(
            FailureClass.UNKNOWN_EVENT_TYPE,
            Severity.MEDIUM,
            "event_router",
            "Unknown event type requires manual routing review.",
            False,
            True,
            "Add an approved routing branch before retrying.",
        )
    observations.append(DiagnosticObservation(step="local_replay", message="Payload is normalized and safe locally."))
    return result(
        FailureClass.OK,
        Severity.LOW,
        "local_replay",
        "Payload can be normalized and replayed locally.",
        True,
        False,
        "Replay against local mock adapter only; live replay requires approval.",
    )
