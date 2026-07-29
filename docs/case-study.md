# Case Study: Repairing a Broken Synthetic Order-Intake Automation

A synthetic order-intake event arrives from a webhook/workflow-style export that represents the same buyer problem framed in Mock Job 01: a Shopify-like order, Stripe-like payment signal, or downstream ops handoff is almost valid, but the delivery contains malformed fields, missing routing data, duplicate idempotency state, or an unsafe destination mismatch.

Automation Debugger loads the fixture, assigns a stable trace ID, identifies the primary failure class, proposes deterministic corrections only when safe, and then replays the corrected event against a local mock destination. Unsafe cases, such as invalid webhook signatures, duplicate idempotency keys, unknown event types, and downstream 500 loops, are refused or dead-lettered with a clear reason.

## Buyer-readable outcome

The client gets a concise report showing what broke, why it broke, what changed, whether local replay passed or was refused, and which live-service next steps require explicit approval. In the broader order-intake project set, this complements the `api-webhook-bridge` green path and `sheets-airtable-sync` downstream reconciliation.

## Evidence

Strongest reproducible artifacts for the order-intake failure-path story:
- `examples/output/diagnosis-malformed-date.json`
- `examples/output/diagnosis-duplicate-event.json`
- `examples/output/replay-success.json`
- `examples/output/replay-refused.json`
- `examples/output/fix-report.md`
- `docs/screenshots/05-corrected-replay.png`
- `docs/screenshots/07-duplicate-guard.png`

Safety boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
