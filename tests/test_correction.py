from automation_debugger.correction import normalize_date, suggest_corrections


def test_malformed_date_is_corrected() -> None:
    assert normalize_date("05/06/2026") == ("2026-05-06", True)


def test_destination_mismatch_is_corrected() -> None:
    corrected, suggestions, fields = suggest_corrections({"destination": "legacy-crm"})
    assert corrected["destination"] == "mock-crm"
    assert "destination" in fields
    assert suggestions
