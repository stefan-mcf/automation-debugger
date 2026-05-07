from automation_debugger.idempotency import InMemoryIdempotencyStore, idempotency_key


def test_idempotency_key_prefers_explicit_key() -> None:
    assert idempotency_key({"event_id": "evt", "idempotency_key": "key"}) == "key"


def test_store_tracks_cached_result() -> None:
    store = InMemoryIdempotencyStore()
    store.put("k", {"status": "passed"})
    assert store.seen("k") is True
    assert store.get("k") == {"status": "passed"}
