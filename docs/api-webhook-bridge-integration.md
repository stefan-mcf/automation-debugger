# api-webhook-bridge Integration

`api-webhook-bridge` is the sibling green-path spoke: it proves that a clean webhook/API event can be routed. `automation-debugger` is the repair/debug spoke: it consumes failed or dead-letter-style payloads and explains why they failed.

Current integration is fixture compatibility only. This repo does not import api-webhook-bridge internals unless a stable exported contract appears later.

Handoff example:

1. Bridge emits a local synthetic failed event with `event_id`, `workflow_name`, `failure_reason`, and raw payload.
2. Debugger normalizes it through `platform_parsers.py`.
3. Debugger diagnoses failure class, proposes deterministic correction if safe, refuses unsafe replay otherwise, and packages a report.

Safety boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
