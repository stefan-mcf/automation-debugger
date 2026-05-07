# Local API

Run locally only:

```bash
PYTHONPATH=src uvicorn automation_debugger.api:app --host 127.0.0.1 --port 8011
```

Endpoints:

- `GET /health`
- `POST /diagnose`
- `POST /replay`
- `POST /report`

All responses include or preserve the proof boundary: fixture_safe=true, live_services_used=false, synthetic_data_only=true.

OpenAPI docs are available at `http://127.0.0.1:8011/docs` when the local server is running. Do not expose this server publicly for the proof workflow.
