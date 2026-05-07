"""Deterministic, fixture-safe payload correction helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_date(value: object) -> tuple[str | None, bool]:
    if value in (None, ""):
        return None, False
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            normalized = datetime.strptime(text, fmt).strftime("%Y-%m-%d")
            return normalized, normalized != text
        except ValueError:
            continue
    return text, False


def suggest_corrections(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    corrected = dict(payload)
    suggestions: list[str] = []
    broken_fields: list[str] = []
    email = corrected.get("email")
    if isinstance(email, str):
        clean_email = email.strip().lower()
        if clean_email != email:
            suggestions.append("Trim and lowercase email before destination upsert.")
            corrected["email"] = clean_email
    date_value = corrected.get("created_at") or corrected.get("event_date")
    normalized_date, changed = normalize_date(date_value)
    if normalized_date is not None:
        key = "created_at" if "created_at" in corrected else "event_date"
        corrected[key] = normalized_date
    if changed:
        broken_fields.append("created_at" if "created_at" in corrected else "event_date")
        suggestions.append("Normalize date to ISO-8601 YYYY-MM-DD before replay.")
    if corrected.get("destination") == "legacy-crm":
        corrected["destination"] = "mock-crm"
        broken_fields.append("destination")
        suggestions.append("Map legacy destination to approved local mock CRM route.")
    return corrected, suggestions, broken_fields
