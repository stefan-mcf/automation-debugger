# Local Operation

## Install

Create the reference Python 3.11 environment from the repository root:

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Inspect and replay

Inspect a failed synthetic event:

```bash
PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json
```

Run the allowed correction against the local mock destination:

```bash
PYTHONPATH=src python -m automation_debugger.cli replay examples/input/malformed-date.json
```

Confirm that a duplicate replay is refused:

```bash
PYTHONPATH=src python -m automation_debugger.cli replay examples/input/duplicate-event.json
```

## Generate an operating report

```bash
PYTHONPATH=src python -m automation_debugger.cli report \
  examples/input/malformed-date.json \
  --format html \
  --output /tmp/automation-debugger-report.html
```

## Validate the repository

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src
python scripts/verify_examples.py
python scripts/capture_screenshots.py
```

Automation Debugger owns the failure path. `api-webhook-bridge` owns accepted webhook intake and mapping. No live services or customer records are used by either repository's local scenarios.
