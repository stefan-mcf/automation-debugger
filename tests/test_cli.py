from typer.testing import CliRunner

from automation_debugger.cli import app

runner = CliRunner()


def test_cli_inspect_outputs_boundary_fields() -> None:
    result = runner.invoke(app, ["inspect", "examples/input/malformed-date.json"])
    assert result.exit_code == 0
    assert '"fixture_safe": true' in result.output
    assert "malformed_date" in result.output


def test_cli_replay_outputs_mock_result() -> None:
    result = runner.invoke(app, ["replay", "examples/input/malformed-date.json"])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_cli_report_writes_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    out = tmp_path / "report.html"
    result = runner.invoke(app, ["report", "examples/input/malformed-date.json", "--format", "html", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "fixture_safe=true" in out.read_text()
