from automation_debugger.models import DiagnosisResult, FailureClass, Severity


def test_model_defaults_keep_fixture_safe_boundary() -> None:
    result = DiagnosisResult(
        trace_id="trace-test",
        workflow_name="Synthetic Test",
        failure_class=FailureClass.MALFORMED_DATE,
        severity=Severity.MEDIUM,
        likely_failure_step="field_mapping",
        diagnosis_summary="date fix",
        safe_to_retry=True,
        manual_review_required=False,
    )
    data = result.model_dump()
    assert data["fixture_safe"] is True
    assert data["live_services_used"] is False
    assert data["synthetic_data_only"] is True
