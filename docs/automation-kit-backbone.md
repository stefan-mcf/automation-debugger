# Automation Kit Backbone Boundary

Automation Debugger is built using Automation Kit conventions but does not duplicate Automation Kit's reusable runtime.

The only code boundary is `src/automation_debugger/backbone.py`, which optionally imports Automation Kit mock clients:

```python
try:
    from auto_kit.mock_clients import MockCRMClient, MockSlackClient
except ImportError:
    MockCRMClient = None
    MockSlackClient = None
```

If Automation Kit is not installed, all tests and fixture-safe proof commands still run with local fallback status. This keeps the public proof inspectable as a standalone spoke while documenting the intended backbone relationship.

Safety boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.
