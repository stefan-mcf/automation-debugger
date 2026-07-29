# Automation Debugger — Concept and Scope

Automation Debugger is a workflow diagnosis project for urgent automation repair and debugging work. It demonstrates that a broken event can be diagnosed, safely corrected when deterministic, replayed locally when safe, refused when unsafe, and packaged into a clean engineering report.

## Relationship to sibling repos

- Automation Kit: reusable local runtime, backbone, and conventions.
- api-webhook-bridge: green-path webhook/API integration spoke.
- automation-debugger: repair/debug spoke for failed webhook/workflow events.

## Systems represented by synthetic fixtures

Zapier, Make, n8n, webhooks, API bridge handoffs, CRM lead routing, field mapping, idempotency, webhook signatures, retry/backoff, and dead-letter handling.

## Core flows

- Broken lead event -> malformed date diagnosis -> corrected local replay.
- Missing required field -> manual review and replay refusal.
- Duplicate event -> idempotency guard refusal.
- Destination mismatch -> deterministic local reroute to mock CRM.
- Invalid signature -> webhook-auth refusal.
- Downstream 500 loop -> local dead-letter evidence.

## Applied use

Fixture-safe context for Zapier repair, Make scenario debugging, n8n execution failure, webhook/API debugging, Sheets/Airtable field mapping repair, CRM lead routing failures, and notification workflow repair.

## Safety and scope boundaries

fixture_safe: true
live_services_used: false
synthetic_data_only: true

No live external-service calls, credentials, real customer data, cloud deployment, public visibility change, production-readiness claim, client action, or off-platform delivery is allowed without explicit approval.
