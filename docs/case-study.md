# Case study: making failed automation retries safe

Automation failures are rarely difficult because an error message is missing. They are difficult because the operator cannot tell how far the event travelled before it failed.

A workflow may have created a CRM record but missed the notification, accepted a webhook before returning an error, or entered a retry loop after a provider timeout. Pressing “run again” can repair the workflow, create a duplicate, or make the incident harder to reconstruct.

Automation Debugger is a working Python toolkit for that decision. It turns a failed event into a repeatable diagnosis, keeps the original payload intact, and allows replay only when the event passes explicit safety checks.

## The operating problem

The input may come from Zapier task history, a Make incomplete execution, an n8n execution export, or a generic webhook record. Those platforms describe similar failures with different field names and levels of detail.

The tool needed to answer five questions consistently:

1. What type of failure occurred?
2. Is the payload itself repairable?
3. Has the event already been applied?
4. Would a replay target the intended destination?
5. What should the next engineer or operator do?

## What I built

```text
provider export or webhook record
                │
                ▼
       platform normalisation
                │
                ▼
       deterministic diagnosis
                │
                ▼
       correction candidate
                │
                ▼
   signature, destination and
       idempotency safeguards
          ┌─────┴─────┐
          ▼           ▼
     local replay   refusal
          └─────┬─────┘
                ▼
      engineering handover
```

The implementation is split into small modules for platform parsing, classification, correction, idempotency, webhook safety, replay, dead-letter handling, and report generation. The same engine is exposed through a Typer CLI and a FastAPI service.

The failure taxonomy covers malformed dates, missing fields, duplicate events, destination mismatches, unknown event types, invalid signatures, downstream error loops, rate limits, and provider-specific export shapes.

## The important design decisions

### Diagnosis and replay are separate actions

Inspection never implies permission to replay. The tool produces a diagnosis first, then evaluates a separate replay request against the safety rules.

### Corrections never overwrite the source event

When a field can be repaired deterministically, the corrected payload is stored as a candidate beside the original. That leaves a reviewable record of exactly what changed.

### Refusal is an intentional result

Duplicate events, invalid signatures, destination mismatches, and already-applied operations exit with a structured refusal. A refused replay records zero destination operations.

### The handover is part of the product

The output is not only a machine response. JSON, Markdown, and HTML reports explain the classification, affected fields, proposed correction, replay decision, and remaining action in a form another engineer can use.

## Worked example

The `malformed-date` scenario follows the full repair path:

1. The event is normalised and assigned a stable trace ID.
2. The date error is classified without changing the source record.
3. A deterministic correction is prepared.
4. Destination and idempotency checks run again.
5. The corrected event is replayed against the local adapter.
6. The tool writes the diagnosis, replay record, and handover report.

The `duplicate-event` scenario enters through the same intake path but exits with a refusal. This is the distinction the project is built around: valid data can still be unsafe to repeat.

## Result

The repository provides:

- one diagnosis model across Zapier, Make, n8n, and generic webhook records;
- a clear allowed/refused replay decision;
- stable trace and idempotency identifiers;
- dead-letter output for events that must stop;
- CLI and API access to the same rules;
- 32 committed JSON examples and a recorded quality run of 44 passing tests;
- reproducible screenshots and handover reports generated from the committed scenarios.

The result is a diagnostic workflow that can be reviewed, tested, and extended without relying on a live customer account to understand its behaviour.

## Scope and production path

The repository runs against controlled local scenarios and local destination adapters. It does not sign in to Zapier, Make, n8n, Airtable, or a CRM, and it does not replay customer events.

A production implementation would add an approved provider adapter, scoped credentials, durable idempotency storage, a sanitised incident payload, monitoring, and a separate change review. Those concerns are isolated from the diagnosis engine so the core decision rules remain testable.

## Explore the implementation

- [Architecture](architecture.md)
- [API surface](api.md)
- [Worked local walkthrough](sandbox-walkthrough.md)
- [Validation record](evidence.md)
- [Generated screenshots](screenshots/README.md)
- [Back to the repository overview](../README.md)
