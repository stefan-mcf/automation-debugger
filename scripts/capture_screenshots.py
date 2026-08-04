from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1400
HEIGHT = 800
BG = (11, 17, 32)
PANEL = (17, 24, 39)
PANEL_2 = (24, 34, 53)
TEXT = (229, 231, 235)
MUTED = (148, 163, 184)
BLUE = (96, 165, 250)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
BORDER = (51, 65, 85)

HEADER_BOX = (32, 28, 1368, 122)
FOOTER_BOX = (32, 730, 1368, 772)
TWO_COLUMN_BOXES = ((52, 154, 674, 670), (726, 154, 1348, 670))
THREE_COLUMN_BOXES = (
    (52, 154, 446, 670),
    (503, 154, 897, 670),
    (954, 154, 1348, 670),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
SUBTITLE_FONT = font(18)
PANEL_TITLE_FONT = font(18, bold=True)
BODY_FONT = font(16)
MONO_FONT = font(15)


def run(cmd: list[str], *, max_lines: int = 18) -> list[str]:
    env = {**os.environ, "PYTHONPATH": "src", "PYTHONWARNINGS": "ignore"}
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True, env=env)
    combined = (proc.stdout + proc.stderr).strip().splitlines()
    return combined[:max_lines] or ["command completed"]


def passed_count(lines: list[str]) -> int:
    summary = next((line for line in reversed(lines) if " passed" in line), "")
    match = re.search(r"(?P<passed>\d+) passed", summary)
    if not match:
        raise RuntimeError(f"unable to read pytest result from: {lines!r}")
    return int(match.group("passed"))


def validation_summary(core_lines: list[str], image_lines: list[str]) -> list[str]:
    core = passed_count(core_lines)
    image_checks = passed_count(image_lines)
    return [
        f"core checks: {core} passed",
        f"image checks: {image_checks} passed",
        f"full suite: {core + image_checks} passed",
    ]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def wrap_lines(lines: list[str], width: int) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(
            textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False)
            or [line]
        )
    return wrapped


def draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    accent: tuple[int, int, int] = BLUE,
    code: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 6, y2), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=PANEL_TITLE_FONT, fill=TEXT)
    y = y1 + 62
    selected_font = MONO_FONT if code else BODY_FONT
    max_chars = max(34, (x2 - x1 - 66) // (9 if code else 10))
    for line in wrap_lines(lines, max_chars)[:18]:
        fill = TEXT
        lowered = line.lower()
        if line.startswith(("PASS", "OK", "fixture_safe=true")) or "passed" in lowered:
            fill = GREEN
        elif line.startswith(("REFUSE", "BLOCK", "DENY")) or "failed" in lowered:
            fill = RED
        elif line.startswith(("$", "python", "PYTHONPATH")):
            fill = BLUE
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 28
        if y > y2 - 32:
            break


def render(
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    footer: str = "Local inputs | No provider writes | Synthetic records",
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    for x in range(0, WIDTH, 100):
        draw.line((x, 0, x, HEIGHT), fill=(15, 23, 42))
    for y in range(0, HEIGHT, 100):
        draw.line((0, y, WIDTH, y), fill=(15, 23, 42))

    draw.rounded_rectangle(HEADER_BOX, radius=24, fill=PANEL_2, outline=BORDER, width=2)
    draw.text((60, 50), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 94), subtitle, font=SUBTITLE_FONT, fill=MUTED)

    for panel in panels:
        draw_panel(
            draw,
            panel["box"],
            str(panel["title"]),
            list(panel["lines"]),
            accent=panel.get("accent", BLUE),
            code=bool(panel.get("code", False)),
        )

    draw.rounded_rectangle(FOOTER_BOX, radius=16, fill=PANEL_2, outline=BORDER, width=1)
    draw.text((56, 742), footer, font=BODY_FONT, fill=MUTED)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("SM-Systems-Validation", f"{title}\n{subtitle}\n{footer}")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 25_000 or max(stat.stddev) < 20:
        raise RuntimeError(
            f"image may be unreadable or blank: {path} "
            f"size={path.stat().st_size} stddev={stat.stddev}"
        )


def main() -> None:
    py = sys.executable
    malformed = load_json("examples/input/malformed-date.json")
    mismatch = load_json("examples/input/destination-mismatch.json")
    duplicate = load_json("examples/input/duplicate-event.json")

    cli_malformed = run(
        [py, "-m", "automation_debugger.cli", "inspect", "examples/input/malformed-date.json"]
    )
    cli_mismatch = run(
        [py, "-m", "automation_debugger.cli", "inspect", "examples/input/destination-mismatch.json"]
    )
    replay_ok = run(
        [py, "-m", "automation_debugger.cli", "replay", "examples/input/malformed-date.json"]
    )
    replay_duplicate = run(
        [py, "-m", "automation_debugger.cli", "replay", "examples/input/duplicate-event.json"]
    )
    core_test_lines = run(
        [py, "-m", "pytest", "-q", "-p", "no:warnings", "tests", "-k", "not screenshots"],
        max_lines=30,
    )
    image_test_lines = run(
        [py, "-m", "pytest", "-q", "-p", "no:warnings", "tests/test_screenshots.py"],
        max_lines=30,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = Path(temp_dir) / "operating-report.html"
        run(
            [
                py,
                "-m",
                "automation_debugger.cli",
                "report",
                "examples/input/malformed-date.json",
                "--format",
                "html",
                "--output",
                str(report_path),
            ]
        )
        report_size = report_path.stat().st_size

    render(
        OUT / "01-system-flow.png",
        "Automation Debugger System Flow",
        "Normalize failed events, decide replay safety, and return an operator-ready result.",
        [
            {
                "box": THREE_COLUMN_BOXES[0],
                "title": "Ingest",
                "lines": [
                    "Zapier task export",
                    "Make execution result",
                    "n8n failure record",
                    "Webhook payload",
                    "Dead-letter handoff",
                ],
            },
            {
                "box": THREE_COLUMN_BOXES[1],
                "title": "Diagnose",
                "lines": [
                    "normalize provider shape",
                    "assign stable trace ID",
                    "classify failure",
                    "evaluate correction",
                    "check replay risk",
                ],
            },
            {
                "box": THREE_COLUMN_BOXES[2],
                "title": "Control",
                "lines": [
                    "run local replay",
                    "refuse unsafe retry",
                    "write dead-letter record",
                    "return structured readback",
                    "prepare operating report",
                ],
            },
        ],
    )

    render(
        OUT / "02-interface-surface.png",
        "CLI and API Interfaces",
        "The same typed contracts are available to operators and integration callers.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Operator commands",
                "code": True,
                "lines": [
                    "$ automation-debugger inspect <fixture>",
                    "$ automation-debugger replay <fixture>",
                    "$ automation-debugger report <fixture>",
                    "",
                    "GET  /health",
                    "POST /diagnose",
                    "POST /replay",
                    "POST /report",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "CLI readback",
                "accent": GREEN,
                "code": True,
                "lines": cli_malformed,
            },
        ],
    )

    render(
        OUT / "03-core-processing.png",
        "Typed Failure Processing",
        "Destination mismatch is identified before any destination operation is prepared.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Controlled scenario",
                "code": True,
                "lines": [
                    f"event_id={mismatch.get('event_id')}",
                    f"source={mismatch.get('platform')}",
                    f"destination={mismatch.get('destination')}",
                    "expected_class=destination_mismatch",
                    "destination_operations=0",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Diagnosis readback",
                "accent": GREEN,
                "code": True,
                "lines": cli_mismatch,
            },
        ],
    )

    render(
        OUT / "04-replay-guardrail.png",
        "Replay Guardrails",
        "Duplicate and unsafe events stop before a repeated downstream operation can occur.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Duplicate scenario",
                "accent": RED,
                "code": True,
                "lines": [
                    f"event_id={duplicate.get('event_id')}",
                    "failure_class=duplicate_event",
                    "safe_action=refuse_replay",
                    "destination_operations=0",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Guardrail readback",
                "accent": RED,
                "code": True,
                "lines": replay_duplicate,
            },
        ],
    )

    render(
        OUT / "05-operating-readback.png",
        "Operating Readback",
        "Allowed corrections produce a local replay result and a client-readable operating report.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Corrected local replay",
                "accent": GREEN,
                "code": True,
                "lines": replay_ok,
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Generated report",
                "lines": [
                    "format: HTML, Markdown, or JSON",
                    f"generated bytes: {report_size}",
                    f"source event: {malformed.get('event_id')}",
                    "includes root cause and safe action",
                    "includes replay decision",
                    "includes live-service boundary",
                ],
            },
        ],
    )

    render(
        OUT / "06-validation-scope.png",
        "Validation and Scope",
        "Local checks cover typed contracts, failure paths, reports, examples, and image integrity.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Validation commands",
                "code": True,
                "lines": [
                    "$ python -m pytest -q",
                    "$ python -m ruff check .",
                    "$ python -m mypy src",
                    "$ python scripts/verify_examples.py",
                    "$ python scripts/capture_screenshots.py",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Current result",
                "accent": GREEN,
                "lines": [
                    *validation_summary(core_test_lines, image_test_lines),
                    "fixtures: synthetic",
                    "destination: local mock",
                    "provider credentials: none",
                    "customer records: none",
                    "live retry execution: excluded",
                ],
            },
        ],
    )

    print("six portfolio images rendered")


if __name__ == "__main__":
    main()
