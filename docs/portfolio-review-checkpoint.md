# Portfolio Review Checkpoint

Automation Debugger is public at <https://github.com/stefan-mcf/automation-debugger>.

## Current public state

- Visibility: public.
- Role: broken automation diagnosis, replay, and structured fix-report proof spoke.
- CI workflow: `.github/workflows/ci.yml` added in the first-set reconciliation tranche.
- Boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.

## Remaining approval gates

Stop before:

- release/tag creation;
- live Zapier/Make/n8n/CRM/Google/Airtable/Slack/Discord/Stripe/webhook/cloud/LLM/OCR/payment services;
- real customer or client data;
- publishing release assets;
- sending or sharing generated client-facing reports externally without approval.

## Verification bundle

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check .
python -m mypy src
python scripts/verify_examples.py
git diff --check
```
