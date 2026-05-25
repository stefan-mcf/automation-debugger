# Sandbox Walkthrough

1. Create a Python 3.11 environment locally:
   `uv venv --python 3.11 .venv && source .venv/bin/activate && uv pip install -e ".[dev]"`
   (If your `uv` build does not accept `3.11`, pass an explicit interpreter path like `python3.11`.)
2. Inspect a failed synthetic event:
   `PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json`
   Output proof: `examples/output/diagnosis-malformed-date.json`
3. Replay a safe corrected event locally:
   `PYTHONPATH=src python -m automation_debugger.cli replay examples/input/malformed-date.json`
   Output proof: `examples/output/replay-success.json`
4. Verify an unsafe duplicate replay is refused:
   `PYTHONPATH=src python -m automation_debugger.cli replay examples/input/duplicate-event.json`
   Output proof: `examples/output/replay-refused.json`
5. Generate a client-readable report:
   `PYTHONPATH=src python -m automation_debugger.cli report examples/input/malformed-date.json --format html --output examples/output/fix-report.html`
   Output proof: `examples/output/fix-report.md`, `examples/output/fix-report.html`, `examples/output/fix-report.json`
6. Run tests and example verification:
   `PYTHONPATH=src python -m pytest -q && python -m ruff check . && python -m mypy src && python scripts/verify_examples.py`
7. Capture screenshot evidence with `PYTHONPATH=src python scripts/capture_screenshots.py`.
8. Use this repo as the failure-path companion to `api-webhook-bridge`: green-path webhook intake stays there; malformed, duplicate, invalid-signature, and destination-mismatch fixtures are explained here before any downstream Airtable/Sheets-style ops evidence is reviewed.

Everything is fixture-safe and synthetic. No live services are used.
