# api-webhook-bridge Integration

`api-webhook-bridge` is the sibling green-path companion: it handles clean webhook/API event routing. `automation-debugger` is the repair/diagnosis companion: it consumes failed or dead-letter-style payloads and explains why they failed.

Current integration is fixture compatibility only. This repo does not import api-webhook-bridge internals unless a stable exported contract appears later.

Handoff example:

1. Bridge emits a local synthetic failed event with `event_id`, `workflow_name`, `failure_reason`, and raw payload.
2. Debugger normalizes it through `platform_parsers.py`.
3. Debugger diagnoses failure class, proposes deterministic correction if safe, refuses unsafe replay otherwise, and packages a report.

For Mock Job 01 (`order-intake-ops-sync`), this is the failure-path companion to the Shopify-like order and Stripe-like payment flow: `api-webhook-bridge` shows that a clean approved event can be accepted and mapped, while `automation-debugger` shows what happens when signature checks fail, duplicates arrive, routing targets mismatch, or malformed fields would make downstream Airtable and Sheets-style reconciliation unsafe.

Representative artifacts for that buyer story:
- `examples/output/diagnosis-malformed-date.json`
- `examples/output/diagnosis-duplicate-event.json`
- `examples/output/replay-success.json`
- `examples/output/replay-refused.json`
- `examples/output/fix-report.md`
- `docs/screenshots/07-duplicate-guard.png`

Safety boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
