# Validation Record

Automation Debugger is validated through deterministic local scenarios and static quality checks.

## Commands

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

python -m pytest -q
python -m ruff check .
python -m mypy src
python scripts/verify_examples.py
python scripts/capture_screenshots.py
git diff --check
```

## Checked behaviour

- Typed diagnosis contracts and stable trace identifiers.
- Platform normalization for Zapier, Make, n8n, and generic webhooks.
- Deterministic field correction without source mutation.
- Duplicate, signature, routing, rate-limit, and downstream-error guardrails.
- Local replay, dead-letter, CLI, API, and report paths.
- JSON fixture integrity and six-image public sequence.
- Public copy, filenames, dimensions, metadata, and safety fields.

## Operating boundary

```text
fixture_safe=true
live_services_used=false
synthetic_data_only=true
```

No live services, credentials, customer records, cloud deployment, production retry, or client action is part of the default local workflow.
