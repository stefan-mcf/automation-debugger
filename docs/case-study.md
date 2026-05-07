# Case Study: Repairing a Broken Synthetic Lead Automation

A synthetic lead event arrives from a workflow-platform-style export. The destination expects normalized email and ISO-8601 dates, but the failed event contains inconsistent field formatting or missing routing data.

Automation Debugger loads the fixture, assigns a stable trace ID, identifies the primary failure class, proposes deterministic corrections only when safe, and then replays the corrected event against a local mock destination. Unsafe cases, such as invalid webhook signatures, duplicate idempotency keys, unknown event types, and downstream 500 loops, are refused or dead-lettered with a clear reason.

## Buyer-readable outcome

The client gets a concise report showing what broke, why it broke, what changed, whether local replay passed or was refused, and which live-service next steps require explicit approval.

## Evidence

See `docs/screenshots/` and `examples/output/fix-report.md` for the reproducible proof package.

Safety boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
