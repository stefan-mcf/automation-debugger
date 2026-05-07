# Public Readiness Checklist

Status: public at <https://github.com/stefan-mcf/automation-debugger>.

## Local gates

- [x] `PYTHONPATH=src python -m pytest -q` — local verification command.
- [x] `python -m ruff check .` — local verification command.
- [x] `python -m mypy src` — local verification command.
- [x] `python scripts/verify_examples.py` — example fixture validation.
- [x] `python scripts/capture_screenshots.py` — screenshot renderer available.
- [x] JSON validity scan — covered by `scripts/verify_examples.py`.
- [x] Secret pattern scan — required before release tags or major public positioning changes.
- [x] CI workflow added at `.github/workflows/ci.yml` in the first-set reconciliation tranche.

## Public-claim audit

- [x] Synthetic fixtures only.
- [x] No production deployment claim.
- [x] No live external-service/customer data claim.
- [x] No credentials in `.env.example`.
- [x] Human approval gate remains for release/live/client actions.

Boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
