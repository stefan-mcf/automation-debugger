from pathlib import Path

from automation_debugger.idempotency import InMemoryIdempotencyStore
from automation_debugger.replay import replay_payload


def test_safe_replay_succeeds_against_mock_destination() -> None:
    result = replay_payload("examples/input/malformed-date.json")
    assert result.status == "passed"
    assert result.destination == "mock-crm"
    assert result.operation_count == 1


def test_missing_identifier_replay_is_refused() -> None:
    result = replay_payload({"type": "order.created", "email": "missing-id@example.test"})
    assert result.status == "refused"


def test_invalid_signature_replay_is_blocked() -> None:
    result = replay_payload("examples/input/webhook-invalid-signature.json")
    assert result.status == "blocked"


def test_downstream_loop_is_dead_lettered(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    fixture = Path("examples/input/downstream-500-loop.json").resolve()
    monkeypatch.chdir(tmp_path)
    result = replay_payload(str(fixture))
    assert result.status == "dead_lettered"
    assert result.dead_letter_path is not None


def test_duplicate_idempotency_blocks_second_operation() -> None:
    store = InMemoryIdempotencyStore()
    first = replay_payload("examples/input/malformed-date.json", store)
    second = replay_payload("examples/input/malformed-date.json", store)
    assert first.status == "passed"
    assert second.status == "duplicate"
    assert second.operation_count == 0
