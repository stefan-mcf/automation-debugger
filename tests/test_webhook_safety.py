import hashlib
import hmac

from automation_debugger.webhook_safety import (
    should_backoff,
    should_open_circuit,
    verify_hmac_signature,
)


def test_hmac_fixture_verification() -> None:
    body = '{"fixture":true}'
    sig = hmac.new(b"fixture-secret", body.encode(), hashlib.sha256).hexdigest()
    assert verify_hmac_signature(body, sig)


def test_backoff_and_circuit_breaker_decisions() -> None:
    assert should_backoff({"status_code": 429})
    assert should_open_circuit({"status_code": 500, "retry_count": 3})
