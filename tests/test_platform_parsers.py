from automation_debugger.platform_parsers import load_payload, normalize_platform_payload


def test_zapier_fixture_normalizes_to_shared_shape() -> None:
    payload = normalize_platform_payload(load_payload("examples/input/zapier-task_history-failed.json"))
    assert payload["platform_hint"] == "zapier"
    assert payload["event_id"] == "zap_task_001"
    assert payload["email"] == "zapier@example.test"


def test_make_fixture_normalizes_to_shared_shape() -> None:
    payload = normalize_platform_payload(load_payload("examples/input/make-incomplete-execution.json"))
    assert payload["platform_hint"] == "make"
    assert payload["destination"] == "legacy-crm"
