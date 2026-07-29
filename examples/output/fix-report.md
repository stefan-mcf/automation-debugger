# Fixture-Safe Automation Fix Report

## Executive summary

Synthetic generic_webhook fixture diagnosed as malformed_date; replay status: passed.

## What broke

- Trace ID: `trace-125f687e66`
- Workflow: Synthetic Automation Debug Session
- Platform fixture: generic_webhook
- Failure class: `malformed_date`
- Severity: medium
- Broken fields: created_at

## Business impact (synthetic counts only)

This report uses one synthetic failed event. No live services, customer records, or credentials were used.

## Root cause

Payload date format is malformed for the destination mapping.

## Evidence table

| Step | Evidence |
| --- | --- |
| formatter | Date field required normalization. |

## Corrected payload / field diff

```json
{
  "created_at": "2026-05-06",
  "email": "x@example.test",
  "event_id": "evt-report",
  "platform_hint": "generic_webhook",
  "synthetic_data_only": true,
  "type": "lead.created"
}
```

## Replay result

- Status: `passed`
- Reason: Local mock replay accepted corrected payload; no live services used.
- Destination: mock-crm

## Prevention notes

- Require an idempotency key before replaying failed events.
- Verify webhook signatures against the raw request body.
- Use retry/backoff and circuit-breaker rules for transient downstream failures.
- Store dead-letter records locally before transformation for auditability.
- Route unknown event types to manual review instead of guessing.

## Safety boundary

- fixture_safe: true
- live_services_used: false
- synthetic_data_only: true
- No live services were used.

## Next live-service steps requiring approval

- Approve credential scope before any live external-service test.
- Approve one sanitized customer sample before client-specific replay.
- Approve public sharing before linking this repo externally.
