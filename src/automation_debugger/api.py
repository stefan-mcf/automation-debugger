"""Local FastAPI control surface for fixture-safe automation debugging."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from automation_debugger.backbone import as_dict, get_backbone_status
from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.replay import replay_payload
from automation_debugger.reports import report_to_html, report_to_markdown, write_report_files

app = FastAPI(
    title="Automation Debugger Local Fixture API",
    version="0.1.0",
    description="Synthetic/local-only automation failure diagnosis, replay, and report proof.",
)


class PayloadRequest(BaseModel):
    payload: dict[str, Any]


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "fixture_safe": True,
        "live_services_used": False,
        "synthetic_data_only": True,
        "backbone": as_dict(get_backbone_status()),
    }


@app.post("/diagnose")
def diagnose(request: PayloadRequest) -> dict[str, Any]:
    return diagnose_payload(request.payload).model_dump(mode="json")


@app.post("/replay")
def replay(request: PayloadRequest) -> dict[str, Any]:
    return replay_payload(request.payload).model_dump(mode="json")


@app.post("/report")
def report(request: PayloadRequest, format: str = "md") -> dict[str, Any]:
    proof = write_report_files(request.payload)
    body = report_to_html(proof) if format == "html" else report_to_markdown(proof)
    return {
        "trace_id": proof.trace_id,
        "format": format,
        "body": body,
        "fixture_safe": True,
        "live_services_used": False,
        "synthetic_data_only": True,
    }
