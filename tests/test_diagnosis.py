import pytest

from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.models import FailureClass


@pytest.mark.parametrize(
    ("path", "failure_class"),
    [
        ("examples/input/malformed-date.json", FailureClass.MALFORMED_DATE),
        ("examples/input/duplicate-event.json", FailureClass.DUPLICATE_EVENT),
        ("examples/input/missing-required-field.json", FailureClass.MISSING_REQUIRED_FIELD),
        ("examples/input/destination-mismatch.json", FailureClass.DESTINATION_MISMATCH),
        ("examples/input/unknown-event-type.json", FailureClass.UNKNOWN_EVENT_TYPE),
        ("examples/input/webhook-invalid-signature.json", FailureClass.INVALID_WEBHOOK_SIGNATURE),
        ("examples/input/downstream-500-loop.json", FailureClass.DOWNSTREAM_500_LOOP),
        ("examples/input/rate-limit-backoff.json", FailureClass.RATE_LIMIT_BACKOFF_NEEDED),
        ("examples/input/zapier-task_history-failed.json", FailureClass.MALFORMED_DATE),
        ("examples/input/make-incomplete-execution.json", FailureClass.DESTINATION_MISMATCH),
        ("examples/input/n8n-execution-failed.json", FailureClass.INVALID_WEBHOOK_SIGNATURE),
    ],
)
def test_fixture_failure_classes(path: str, failure_class: FailureClass) -> None:
    result = diagnose_payload(path)
    assert result.failure_class == failure_class
    assert result.trace_id.startswith("trace-")
    assert result.fixture_safe is True
    assert result.live_services_used is False
    assert result.synthetic_data_only is True
