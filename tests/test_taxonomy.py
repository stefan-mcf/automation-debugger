from automation_debugger.taxonomy import load_failure_taxonomy, load_platform_normalization


def test_taxonomy_loads_required_classes() -> None:
    classes = load_failure_taxonomy()["failure_classes"]
    assert "malformed_date" in classes
    assert "downstream_500_loop" in classes


def test_platform_normalization_loads_platforms() -> None:
    platforms = load_platform_normalization()["platforms"]
    assert {"zapier", "make", "n8n", "generic_webhook"}.issubset(platforms)
