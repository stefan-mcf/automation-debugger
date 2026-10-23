# Image Index

The six images in this directory are generated from controlled local scenarios:

```bash
PYTHONPATH=src python scripts/capture_screenshots.py
```

They use a shared SM Systems technical-project layout with no browser chrome, account screens, credentials, customer records, absolute desktop paths, or private identifiers.

| File | Function |
| --- | --- |
| [System flow](01-system-flow.png) | Intake, diagnosis, and replay-control architecture. |
| [Interface surface](02-interface-surface.png) | CLI commands, API routes, and local CLI readback. |
| [Core processing](03-core-processing.png) | Typed destination-mismatch processing. |
| [Replay guardrail](04-replay-guardrail.png) | Duplicate-event refusal and zero-operation result. |
| [Operating readback](05-operating-readback.png) | Corrected local replay and generated operating report. |
| [Validation and scope](06-validation-scope.png) | Recorded checks and explicit local-only boundary. |

Each PNG is 1400x800 and includes machine-readable project metadata.

These are generated local panels. Use current CI rather than historical panel
totals for the latest validation result.
