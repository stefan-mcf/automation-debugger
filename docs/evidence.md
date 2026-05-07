# Evidence Package

This repo provides deterministic local evidence for a broken automation repair/debug workflow.

## Final local gate results (2026-05-07)

Executed locally from the repository root before the human-gated external tranche:

```text
PYTHONPATH=src python -m pytest -q
44 passed, 1 warning in 0.40s

python -m ruff check .
All checks passed!

python -m mypy src
Success: no issues found in 15 source files

python scripts/verify_examples.py
verified 32 example json files

python scripts/capture_screenshots.py
screenshots rendered

JSON validity scan
json ok

secret pattern scan
no matches after replacing a false-positive hyphenated docs phrase
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
python scripts/capture_screenshots.py
```

## Screenshot list

See `docs/screenshots/README.md` for captions and proof purpose.

## Generated report outputs

- `examples/output/fix-report.json`
- `examples/output/fix-report.md`
- `examples/output/fix-report.html`

## Boundary

fixture_safe: true
live_services_used: false
synthetic_data_only: true

No live services, credentials, customer data, cloud deployment, public publishing, or client action are part of this local proof.
