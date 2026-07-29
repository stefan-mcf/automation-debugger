# Evidence Package

This repo provides deterministic local evidence for a broken automation repair/debug workflow.

## Final local gate results (2026-05-09)

Executed locally from the repository root for the Mock Job 01 failure/replay tranche:

```text
# Use any Python 3.11 interpreter available on your system.
# If your `uv` build does not accept `3.11`, pass an explicit interpreter path (e.g. `python3.11`).
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

PYTHONPATH=src python -m pytest -q
44 passed, 1 warning in 0.73s

python -m ruff check .
All checks passed!

python -m mypy src
Success: no issues found in 15 source files

python scripts/verify_examples.py
verified 32 example json files

PYTHONPATH=src python scripts/capture_screenshots.py
screenshots rendered
```

## Reproducible commands

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check .
python -m mypy src
python scripts/verify_examples.py
PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json
PYTHONPATH=src python -m automation_debugger.cli replay examples/input/malformed-date.json
PYTHONPATH=src python -m automation_debugger.cli report examples/input/malformed-date.json --format html --output examples/output/fix-report.html
PYTHONPATH=src python scripts/capture_screenshots.py
```

## Screenshot list

See `docs/screenshots/README.md` for captions and intended use.

## Generated report outputs

- `examples/output/fix-report.json`
- `examples/output/fix-report.md`
- `examples/output/fix-report.html`

## Boundary

fixture_safe: true
live_services_used: false
synthetic_data_only: true

No live services, credentials, customer data, cloud deployment, public publishing, or client action are part of the default local workflow.
