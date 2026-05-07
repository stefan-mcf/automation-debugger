# Sandbox Walkthrough

1. Install locally with `pip install -e .[dev]` or run commands with `PYTHONPATH=src`.
2. Inspect a failed synthetic event:
   `PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json`
3. Replay a safe corrected event locally:
   `PYTHONPATH=src python -m automation_debugger.cli replay examples/input/malformed-date.json`
4. Generate a client-readable report:
   `PYTHONPATH=src python -m automation_debugger.cli report examples/input/malformed-date.json --format html --output examples/output/fix-report.html`
5. Run tests and example verification.
6. Capture screenshot evidence with `python scripts/capture_screenshots.py`.

Everything is fixture-safe and synthetic. No live services are used.
