# Architecture

Automation Debugger is the repair/debug spoke in the Workflow Automation Portfolio portfolio. It stays thin: shared runtime conventions belong in Automation Kit, working green-path integration proof belongs in api-webhook-bridge, and this repo focuses on failed events.

## Layers

1. Input fixtures and platform exports: generic webhooks plus synthetic Zapier task history, Make incomplete-execution, n8n execution, and api-webhook-bridge-style dead-letter handoff payloads.
2. Diagnosis/correction/replay engine: typed Pydantic models, taxonomy-driven failure classes, deterministic correction helpers, idempotency guard, webhook safety checks, and local dead-letter records.
3. Evidence/report/control surfaces: CLI, local FastAPI API, JSON examples, Markdown/HTML reports, screenshot evidence, and quality gates.

## Safety boundary

fixture_safe: true
live_services_used: false
synthetic_data_only: true

No live Zapier, Make, n8n, CRM, Google, Airtable, Slack, Discord, Stripe, cloud, webhook, LLM, OCR, or payment service is contacted by this proof.
