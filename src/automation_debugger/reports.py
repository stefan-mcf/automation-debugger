"""Client-readable Markdown/HTML report generation."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.models import FixReport
from automation_debugger.replay import replay_payload


def build_report(source: str | dict[str, Any]) -> FixReport:
    diagnosis = diagnose_payload(source)
    replay = replay_payload(source)
    return FixReport(
        trace_id=diagnosis.trace_id,
        title="Fixture-Safe Automation Fix Report",
        executive_summary=(f"Synthetic {diagnosis.platform_hint} fixture diagnosed as {diagnosis.failure_class.value}; replay status: {replay.status}."),
        diagnosis=diagnosis,
        replay_result=replay,
        prevention_notes=[
            "Require an idempotency key before replaying failed events.",
            "Verify webhook signatures against the raw request body.",
            "Use retry/backoff and circuit-breaker rules for transient downstream failures.",
            "Store dead-letter records locally before transformation for auditability.",
            "Route unknown event types to manual review instead of guessing.",
        ],
        next_live_service_steps_requiring_approval=[
            "Approve credential scope before any live external-service test.",
            "Approve one sanitized customer sample before client-specific replay.",
            "Approve public sharing before linking this repo externally.",
        ],
    )


def report_to_markdown(report: FixReport) -> str:
    diagnosis = report.diagnosis
    replay = report.replay_result
    corrected = json.dumps(diagnosis.corrected_payload, indent=2, sort_keys=True)
    return (
        f"""# {report.title}

## Executive summary

{report.executive_summary}

## What broke

- Trace ID: `{report.trace_id}`
- Workflow: {diagnosis.workflow_name}
- Platform fixture: {diagnosis.platform_hint}
- Failure class: `{diagnosis.failure_class.value}`
- Severity: {diagnosis.severity.value}
- Broken fields: {", ".join(diagnosis.broken_fields) or "none"}

## Business impact (synthetic counts only)

This report uses one synthetic failed event. No live services, customer records, or credentials were used.

## Root cause

{diagnosis.diagnosis_summary}

## Diagnostic observations

| Step | Observation |
| --- | --- |
"""
        + "\n".join(f"| {item.step} | {item.message} |" for item in diagnosis.observations)
        + f"""

## Corrected payload / field diff

```json
{corrected}
```

## Replay result

- Status: `{replay.status if replay else "not-run"}`
- Reason: {replay.reason if replay else "No replay result"}
- Destination: {replay.destination if replay else "n/a"}

## Prevention notes

"""
        + "\n".join(f"- {note}" for note in report.prevention_notes)
        + f"""

## Safety boundary

- fixture_safe: {str(report.fixture_safe).lower()}
- live_services_used: {str(report.live_services_used).lower()}
- synthetic_data_only: {str(report.synthetic_data_only).lower()}
- No live services were used.

## Next live-service steps requiring approval

"""
        + "\n".join(f"- {step}" for step in report.next_live_service_steps_requiring_approval)
        + "\n"
    )


def report_to_html(report: FixReport) -> str:
    md = html.escape(report_to_markdown(report))
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>{html.escape(report.title)}</title>
<style>
body {{ font-family: Inter, system-ui, sans-serif; background:#f8fafc; color:#102033; margin:0; padding:40px; }}
main {{ max-width: 980px; margin:auto; background:white; border:1px solid #d8e2ef; border-radius:20px; padding:34px; box-shadow:0 18px 45px rgba(15,23,42,.08); }}
pre {{ white-space: pre-wrap; background:#0f172a; color:#e2e8f0; padding:24px; border-radius:14px; overflow:auto; }}
.badge {{ display:inline-block; background:#dcfce7; color:#166534; border-radius:999px; padding:6px 12px; font-family:monospace; }}
</style>
</head>
<body><main><p class=\"badge\">fixture_safe=true | live_services_used=false | synthetic_data_only=true</p><pre>{md}</pre></main></body>
</html>"""


def write_report_files(source: str | dict[str, Any], output_base: str | Path = "examples/output/fix-report") -> FixReport:
    report = build_report(source)
    base = Path(output_base)
    base.parent.mkdir(parents=True, exist_ok=True)
    (base.with_suffix(".json")).write_text(report.model_dump_json(indent=2) + "\n")
    (base.with_suffix(".md")).write_text(report_to_markdown(report))
    (base.with_suffix(".html")).write_text(report_to_html(report))
    return report
