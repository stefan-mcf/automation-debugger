from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    paths = sorted((ROOT / "examples").rglob("*.json"))
    assert paths, "no example JSON files found"
    for path in paths:
        data = json.loads(path.read_text())
        assert isinstance(data, dict), path
        if "output" in path.parts or path.parent.name in {"input", "api-responses"}:
            text = path.read_text().lower()
            assert "fixture_safe" in text, path
            assert "live_services_used" in text, path
            assert "synthetic_data_only" in text, path
    print(f"verified {len(paths)} example json files")


if __name__ == "__main__":
    main()
