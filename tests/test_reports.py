from pathlib import Path

from automation_debugger.reports import (
    build_report,
    report_to_html,
    report_to_markdown,
    write_report_files,
)


def test_markdown_report_contains_client_readable_sections() -> None:
    report = build_report("examples/input/malformed-date.json")
    md = report_to_markdown(report)
    assert "Executive summary" in md
    assert "What broke" in md
    assert "Prevention notes" in md
    assert "live_services_used: false" in md


def test_html_report_is_self_contained() -> None:
    html = report_to_html(build_report("examples/input/malformed-date.json"))
    assert "<!doctype html>" in html.lower()
    assert "fixture_safe=true" in html


def test_write_report_files(tmp_path: Path) -> None:
    report = write_report_files("examples/input/malformed-date.json", tmp_path / "fix-report")
    assert report.trace_id.startswith("trace-")
    assert (tmp_path / "fix-report.md").exists()
    assert (tmp_path / "fix-report.html").exists()
