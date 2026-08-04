"""Typed models for fixture-safe automation debugging outputs."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FailureClass(str, Enum):
    MISSING_REQUIRED_FIELD = "missing_required_field"
    MALFORMED_DATE = "malformed_date"
    DUPLICATE_EVENT = "duplicate_event"
    DESTINATION_MISMATCH = "destination_mismatch"
    UNKNOWN_EVENT_TYPE = "unknown_event_type"
    INVALID_WEBHOOK_SIGNATURE = "invalid_webhook_signature"
    DOWNSTREAM_500_LOOP = "downstream_500_loop"
    RATE_LIMIT_BACKOFF_NEEDED = "rate_limit_backoff_needed"
    OK = "ok"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyBoundary(BaseModel):
    fixture_safe: Literal[True] = True
    live_services_used: Literal[False] = False
    synthetic_data_only: Literal[True] = True


class DiagnosticObservation(BaseModel):
    step: str
    message: str
    fields: list[str] = Field(default_factory=list)
    snippet: dict[str, Any] = Field(default_factory=dict)


class ReplayResult(SafetyBoundary):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    status: Literal["passed", "blocked", "duplicate", "dead_lettered", "refused"]
    destination: str = "local-mock-destination"
    reason: str = ""
    retry_count: int = 0
    dead_letter_path: str | None = None
    operation_count: int = 0


class DiagnosisResult(SafetyBoundary):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    workflow_name: str
    platform_hint: str = "generic_webhook"
    event_id: str = "unknown-event"
    failure_class: FailureClass
    severity: Severity
    likely_failure_step: str
    diagnosis_summary: str
    safe_to_retry: bool
    manual_review_required: bool
    broken_fields: list[str] = Field(default_factory=list)
    correction_suggestions: list[str] = Field(default_factory=list)
    corrected_payload: dict[str, Any] = Field(default_factory=dict)
    replay_result: ReplayResult | None = None
    handoff_notes: str = ""
    observations: list[DiagnosticObservation] = Field(default_factory=list)


class FixReport(SafetyBoundary):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    title: str
    executive_summary: str
    diagnosis: DiagnosisResult
    replay_result: ReplayResult | None = None
    prevention_notes: list[str] = Field(default_factory=list)
    next_live_service_steps_requiring_approval: list[str] = Field(default_factory=list)
