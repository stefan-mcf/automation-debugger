# Architecture

Automation Debugger is the repair/diagnosis companion case study to Automation Kit and api-webhook-bridge. It stays thin: shared runtime conventions belong in Automation Kit, green-path integration belongs in api-webhook-bridge, and this repo focuses on failed events.

## Layers

1. Input fixtures and platform exports: generic webhooks plus synthetic Zapier task history, Make incomplete-execution, n8n execution, and api-webhook-bridge-style dead-letter handoff payloads.
2. Diagnosis/correction/replay engine: typed Pydantic models, taxonomy-driven failure classes, deterministic correction helpers, idempotency guard, webhook safety checks, and local dead-letter records.
3. Report and control surfaces: CLI, local FastAPI API, JSON examples, Markdown and HTML reports, generated images, and quality gates.

## Safety boundary

fixture_safe: true
live_services_used: false
synthetic_data_only: true

No live Zapier, Make, n8n, CRM, Google, Airtable, Slack, Discord, Stripe, cloud, webhook, LLM, OCR, or payment service is contacted by the default local workflow.
