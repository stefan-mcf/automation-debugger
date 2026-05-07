"""Typer CLI for the local fixture-safe proof."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from automation_debugger.diagnosis import diagnose_payload
from automation_debugger.replay import replay_payload
from automation_debugger.reports import report_to_html, report_to_markdown, write_report_files

app = typer.Typer(help="Fixture-safe automation diagnosis, replay, and report proof.")


@app.command()
def inspect(path: Annotated[Path, typer.Argument(help="Synthetic fixture JSON path")]) -> None:
    """Diagnose a synthetic failed automation event."""
    result = diagnose_payload(str(path))
    typer.echo(result.model_dump_json(indent=2))


@app.command()
def replay(path: Annotated[Path, typer.Argument(help="Synthetic fixture JSON path")]) -> None:
    """Replay a corrected synthetic event against a local mock destination only."""
    result = replay_payload(str(path))
    typer.echo(result.model_dump_json(indent=2))


@app.command(name="report")
def report_cmd(
    path: Annotated[Path, typer.Argument(help="Synthetic fixture JSON path")],
    output_format: Annotated[str, typer.Option("--format", help="md or html")] = "md",
    output: Annotated[Path | None, typer.Option("--output", help="Optional report path")] = None,
) -> None:
    """Generate a client-readable Markdown or HTML report."""
    if output:
        from automation_debugger.reports import build_report

        report = build_report(str(path))
        output.write_text(report_to_html(report) if output_format == "html" else report_to_markdown(report))
        typer.echo(str(output))
        return
    report = write_report_files(str(path), "examples/output/fix-report")
    typer.echo(report_to_html(report) if output_format == "html" else report_to_markdown(report))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
