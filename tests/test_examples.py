import json
from pathlib import Path


def test_all_example_json_parses_and_declares_boundary() -> None:
    paths = sorted(Path("examples").rglob("*.json"))
    assert paths
    for path in paths:
        data = json.loads(path.read_text())
        assert isinstance(data, dict)
        text = path.read_text().lower()
        assert "fixture_safe" in text
        assert "live_services_used" in text
        assert "synthetic_data_only" in text
