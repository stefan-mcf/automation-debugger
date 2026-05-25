# Automation Debugger

A fixture-safe tool for diagnosing and repairing broken automation events — Zapier,
Make, n8n, webhook, and API-bridge failures — before any live retry is attempted.

Automation Debugger takes a failed workflow event, normalizes it regardless of the
source platform, classifies the failure, decides whether a safe correction exists,
and either replays the corrected event against local mock destinations or dead-letters
it with a clear reason. Every decision is traceable, every output is deterministic,
and no live service is ever contacted by default.

## What this is for

Use Automation Debugger when you need to:

- diagnose why a Zapier step, Make scenario, n8n execution, or webhook handler failed
- normalize failure exports from different platforms into one inspectable shape
- classify failures deterministically: malformed fields, missing data, duplicates,
  destination mismatches, invalid signatures, rate limits, and downstream error loops
- decide whether safe replay is possible or the event should be dead-lettered
- generate fix reports (JSON, Markdown, HTML) for review before touching live systems
- integrate a safe diagnosis/replay step into a broader automation pipeline via CLI or API

Automation Debugger does not connect to live Zapier, Make, n8n, Slack, CRM, Stripe,
or any cloud service. All shipped examples use synthetic fixtures.

## Failure classes handled

Each case below uses a short synthetic fixture. The debugger loads the fixture,
classifies the failure, decides whether a correction is safe, and writes the
diagnosis result to `examples/output/diagnosis-*.json`.

| Case | Input | Class | Result |
|---|---|---|---|
| Malformed date | `malformed-date` | `malformed_date` | Correct and replay locally. |
| Missing field | `missing-required-field` | `missing_required_field` | Dead-letter input. |
| Duplicate event | `duplicate-event` | `duplicate_event` | Refuse replay; keep trace. |
| Wrong destination | `destination-mismatch` | `destination_mismatch` | Block wrong target. |
| Unknown event | `unknown-event-type` | `unknown_event_type` | Require mapping review. |
| Bad signature | `webhook-invalid-signature` | `invalid_signature` | Refuse replay. |
| Retry storm | `downstream-500-loop` | `downstream_error_loop` | Stop retries locally. |
| Backoff needed | `rate-limit-backoff` | `rate_limit_backoff` | Return retry guidance. |
| Platform exports | Zapier / Make / n8n | normalized evidence | Parse source shape locally. |

All systems are synthetic and local. The project does not call Zapier, Make, n8n, Airtable, Slack, CRM, Google, Shopify, Stripe, cloud services, or any live webhook endpoint.

## Screenshots

These screenshots show failure intake, diagnosis, safe replay decisions, generated
fix reports, duplicate guards, and quality gates — all from synthetic local fixtures.

[![Automation Debugger flow proof](docs/screenshots/01-flow-overview.png)](docs/screenshots/01-flow-overview.png)

[![CLI diagnosis proof](docs/screenshots/02-cli-proof.png)](docs/screenshots/02-cli-proof.png)

[![Local API proof](docs/screenshots/03-openapi-endpoints.png)](docs/screenshots/03-openapi-endpoints.png)

[![Diagnosis JSON proof](docs/screenshots/04-diagnosis-output.png)](docs/screenshots/04-diagnosis-output.png)

[![Corrected replay proof](docs/screenshots/05-corrected-replay.png)](docs/screenshots/05-corrected-replay.png)

[![Generated fix report proof](docs/screenshots/06-fix-report.png)](docs/screenshots/06-fix-report.png)

[![Duplicate guard proof](docs/screenshots/07-duplicate-guard.png)](docs/screenshots/07-duplicate-guard.png)

[![Quality gate proof](docs/screenshots/08-quality-gates.png)](docs/screenshots/08-quality-gates.png)

Supporting docs:

- Command verification and local gates: `docs/evidence.md`
- Walkthrough narrative: `docs/sandbox-walkthrough.md`
- Case study: `docs/case-study.md`
- Screenshot guide: `docs/screenshots/README.md`

The screenshots are generated proof panels from synthetic local fixtures. They show no live account screens, credentials, browser tabs, private desktop context, or customer data.

See [`docs/case-study.md`](docs/case-study.md) for a worked example: diagnosing
and repairing a broken synthetic order-intake automation.

## Run the sandbox walkthrough

```bash
# Use any Python 3.11 interpreter available on your system.
# If your `uv` build does not accept `3.11`, pass an explicit interpreter path (e.g. `python3.11`).
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json
PYTHONPATH=src python -m automation_debugger.cli replay examples/input/malformed-date.json
PYTHONPATH=src python -m automation_debugger.cli report examples/input/malformed-date.json --format html --output examples/output/fix-report.html
python scripts/verify_examples.py
```

Useful local checks:

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check .
python -m mypy src
PYTHONPATH=src python scripts/capture_screenshots.py
```

## Local API

```bash
PYTHONPATH=src uvicorn automation_debugger.api:app --host 127.0.0.1 --port 8011
curl -fsS http://127.0.0.1:8011/health
```

Endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Fixture-safety and service health flags. |
| `POST /diagnose` | Classify a broken event payload and return traceable diagnosis results. |
| `POST /replay` | Apply safe correction/replay logic against local mock destinations only. |
| `POST /report` | Generate JSON/Markdown/HTML fix-report content from diagnosis results. |

See `docs/api.md` and `examples/api-responses/` for request/response examples.

## Companion to Automation Kit

Automation Kit is the reusable pattern layer. Automation Debugger is the thin
repair/diagnosis companion case study.

Shared pattern conventions:

- deterministic synthetic fixtures under `examples/input/`;
- typed workflow/event models under `src/automation_debugger/models.py`;
- local mock replay and dead-letter records instead of live external-service calls;
- repeatable CLI/API/report outputs under `examples/output/`;
- screenshot and gate verification under `docs/screenshots/` and `docs/evidence.md`.

See `docs/automation-kit-backbone.md` for the explicit backbone relationship.

## Green path + repair path

Automation Debugger and [api-webhook-bridge](https://github.com/stefan-mcf/api-webhook-bridge)
cover the two most common integration milestones:

| Milestone | Repo | What it handles |
|---|---|---|
| Build a safe first webhook/API bridge | `api-webhook-bridge` | Valid event → mapped destination → audit trail |
| Diagnose and repair a broken automation | `automation-debugger` | Failed event → diagnosis → correction/refusal → fix report |

## Project docs

| Doc | Path |
|---|---|
| Architecture | `docs/architecture.md` |
| Automation Kit relationship | `docs/automation-kit-backbone.md` |
| API Webhook Bridge relationship | `docs/api-webhook-bridge-integration.md` |
| FastAPI notes | `docs/api.md` |
| Sandbox walkthrough | `docs/sandbox-walkthrough.md` |
| Case study | `docs/case-study.md` |
| Command verification and gates | `docs/evidence.md` |
| Screenshot guide | `docs/screenshots/README.md` |
| Readiness checklist | `docs/public-readiness-checklist.md` |

## Safety boundary

- Fixture-safe synthetic examples only.
- Empty credential placeholders only.
- `fixture_safe: true`, `live_services_used: false`, and `synthetic_data_only: true` are carried through all outputs.
- Replay uses local mock destinations only.
- Dead-letter records are written locally for unsafe events.
- No live external-service calls, customer data, cloud resources, public visibility changes, releases, or external delivery actions are part of the default local workflow.
- Public release, live external-service testing, credentials, real webhook delivery logs, and cloud deployment remain human-gated.

## Quality gates

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check .
python -m mypy src
python scripts/verify_examples.py
PYTHONPATH=src python scripts/capture_screenshots.py
git diff --check
```

Current verification status is summarized in `docs/evidence.md` and `docs/public-readiness-checklist.md`.

## Environment

See `.env.example`:

| Variable | Default | Description |
|---|---|---|
| `AUTOMATION_DEBUGGER_USE_LIVE_SERVICES` | `false` | Reserved opt-in gate; live services are disabled by default. |
| `AUTOMATION_DEBUGGER_MOCK_SEED` | `42` | Deterministic mock data seed. |
| `AUTOMATION_KIT_PATH` | empty | Optional sibling checkout path for relationship docs and local experimentation. |

## Repository layout

```text
src/automation_debugger/
  api.py
  cli.py
  correction.py
  dead_letter.py
  diagnosis.py
  platform_parsers.py
  replay.py
  reports.py
  webhook_safety.py
configs/diagnosis-rules/
  failure-taxonomy.json
  platform-normalization.json
examples/
  input/
  output/
  api-responses/
docs/
  architecture.md
  api.md
  case-study.md
  evidence.md
  screenshots/
scripts/
  capture_screenshots.py
  verify_examples.py
tests/
```

## License

MIT License. See `LICENSE`.
