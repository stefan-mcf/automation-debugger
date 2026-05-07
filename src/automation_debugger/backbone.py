"""Optional Automation Kit backbone imports isolated behind a safe boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - depends on sibling checkout/install state
    from auto_kit.mock_clients import MockCRMClient, MockSlackClient
except ImportError:  # pragma: no cover - fallback for standalone public proof
    MockCRMClient = None
    MockSlackClient = None


@dataclass(frozen=True)
class BackboneStatus:
    automation_kit_available: bool
    mock_crm_available: bool
    mock_slack_available: bool
    fixture_safe: bool = True
    live_services_used: bool = False
    synthetic_data_only: bool = True


def get_backbone_status() -> BackboneStatus:
    return BackboneStatus(
        automation_kit_available=MockCRMClient is not None or MockSlackClient is not None,
        mock_crm_available=MockCRMClient is not None,
        mock_slack_available=MockSlackClient is not None,
    )


def as_dict(status: BackboneStatus) -> dict[str, Any]:
    return {
        "automation_kit_available": status.automation_kit_available,
        "mock_crm_available": status.mock_crm_available,
        "mock_slack_available": status.mock_slack_available,
        "fixture_safe": status.fixture_safe,
        "live_services_used": status.live_services_used,
        "synthetic_data_only": status.synthetic_data_only,
    }
