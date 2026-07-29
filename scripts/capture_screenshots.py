from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1280
HEIGHT = 760
BG = (10, 15, 28)
PANEL = (17, 24, 39)
PANEL_2 = (25, 35, 56)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
BLUE = (96, 165, 250)
YELLOW = (250, 204, 21)
PINK = (244, 114, 182)
RED = (248, 113, 113)
BORDER = (51, 65, 85)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
SUBTITLE_FONT = font(18)
BODY_FONT = font(20)
SMALL_FONT = font(16)
MONO_FONT = font(18)
MONO_SMALL = font(15)


def run(cmd: list[str], *, max_lines: int = 14) -> list[str]:
    env = {**os.environ, "PYTHONPATH": "src"}
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True, env=env)
    combined = (proc.stdout + proc.stderr).strip().splitlines()
    return combined[:max_lines] or ["command completed with no output"]


def load_json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text())


def wrap_lines(lines: list[str], width: int) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) or [line])
    return wrapped


def draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, lines: list[str], *, accent: tuple[int, int, int] = BLUE, code: bool = False) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=SUBTITLE_FONT, fill=accent)
    y = y1 + 58
    selected_font = MONO_SMALL if code else SMALL_FONT
    usable_width = max(220, x2 - x1 - 70)
    approx_char_px = 9 if code else 10
    max_chars = max(34, usable_width // approx_char_px)
    for line in wrap_lines(lines, max_chars)[:18]:
        fill = TEXT
        if line.startswith(("PASS", "✓", "fixture_safe=true", "live_services_used=false", "synthetic_data_only=true")):
            fill = GREEN
        elif line.startswith(("REFUSE", "unsafe", "blocked")) or "FAILED" in line:
            fill = RED
        elif line.startswith(("$", "python", "PYTHONPATH")):
            fill = YELLOW
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 26
        if y > y2 - 34:
            break


def render(path: Path, title: str, subtitle: str, panels: list[dict[str, object]], footer: str = "fixture_safe=true  live_services_used=false  synthetic_data_only=true") -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # subtle grid
    for x in range(0, WIDTH, 80):
        draw.line((x, 0, x, HEIGHT), fill=(15, 23, 42))
    for y in range(0, HEIGHT, 80):
        draw.line((0, y, WIDTH, y), fill=(15, 23, 42))

    draw.rounded_rectangle((30, 28, WIDTH - 30, 116), radius=24, fill=PANEL_2, outline=BORDER, width=2)
    draw.text((58, 48), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 90), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    for panel in panels:
        draw_panel(
            draw,
            panel["box"],  # type: ignore[arg-type]
            str(panel["title"]),
            list(panel["lines"]),  # type: ignore[arg-type]
            accent=panel.get("accent", BLUE),  # type: ignore[arg-type]
            code=bool(panel.get("code", False)),
        )

    draw.rounded_rectangle((30, HEIGHT - 54, WIDTH - 30, HEIGHT - 18), radius=16, fill=PANEL_2, outline=BORDER, width=1)
    draw.text((54, HEIGHT - 45), footer, font=SMALL_FONT, fill=GREEN)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Automation-Debugger", f"{title}\n{subtitle}\n{footer}")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 25_000 or max(stat.stddev) < 20:
        raise RuntimeError(f"screenshot may be unreadable/blank: {path} size={path.stat().st_size} stddev={stat.stddev}")


def main() -> None:
    py = sys.executable
    malformed = load_json("examples/input/malformed-date.json")
    mismatch = load_json("examples/input/destination-mismatch.json")
    duplicate = load_json("examples/input/duplicate-event.json")

    cli_malformed = run([py, "-m", "automation_debugger.cli", "inspect", "examples/input/malformed-date.json"], max_lines=18)
    cli_mismatch = run([py, "-m", "automation_debugger.cli", "inspect", "examples/input/destination-mismatch.json"], max_lines=18)
    replay_ok = run([py, "-m", "automation_debugger.cli", "replay", "examples/input/malformed-date.json"], max_lines=18)
    replay_dup = run([py, "-m", "automation_debugger.cli", "replay", "examples/input/duplicate-event.json"], max_lines=18)
    pytest_lines = run([py, "-m", "pytest", "-q", "tests", "-k", "not screenshots"], max_lines=10)
    run([py, "-m", "automation_debugger.cli", "report", "examples/input/malformed-date.json", "--format", "html", "--output", "examples/output/fix-report.html"], max_lines=5)
    report_size = (ROOT / "examples/output/fix-report.html").stat().st_size

    render(
        OUT / "01-flow-overview.png",
        "Automation Debugger Flow",
        "Failed workflow evidence becomes diagnosis, safe correction, replay decision, and client-readable report.",
        [
            {
                "box": (52, 148, 410, 628),
                "title": "Inputs",
                "accent": BLUE,
                "lines": ["Zapier task export", "Make incomplete execution", "n8n execution failure", "Generic webhook payload", "API bridge dead-letter handoff"],
            },
            {
                "box": (462, 148, 820, 628),
                "title": "Diagnosis",
                "accent": YELLOW,
                "lines": ["stable trace_id", "failure_class taxonomy", "severity + safe action", "correction eligibility", "dead-letter reason"],
            },
            {
                "box": (872, 148, 1230, 628),
                "title": "Evidence",
                "accent": GREEN,
                "lines": ["JSON diagnosis files", "local replay logs", "Markdown/HTML fix report", "API response examples", "quality gate results"],
            },
        ],
    )
    render(
        OUT / "02-cli-diagnosis.png",
        "CLI Diagnosis",
        "`automation-debugger inspect` classifies a malformed date fixture and returns safety fields.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Command",
                "accent": YELLOW,
                "code": True,
                "lines": [
                    "$ PYTHONPATH=src python -m automation_debugger.cli inspect examples/input/malformed-date.json",
                    "",
                    f"event_id={malformed.get('event_id')}",
                    "expected class: malformed_date",
                ],
            },
            {"box": (650, 148, 1230, 628), "title": "Output excerpt", "accent": GREEN, "code": True, "lines": cli_malformed},
        ],
    )
    render(
        OUT / "03-openapi-endpoints.png",
        "Local API Surface",
        "FastAPI endpoints expose fixture-safe diagnosis, replay, and report generation without live credentials.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Endpoints",
                "accent": BLUE,
                "lines": ["GET /health", "POST /diagnose", "POST /replay", "POST /report", "OpenAPI docs available when uvicorn runs locally"],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Health contract",
                "accent": GREEN,
                "code": True,
                "lines": ['{"status":"ok"}', '"fixture_safe": true', '"live_services_used": false', '"synthetic_data_only": true'],
            },
        ],
    )
    render(
        OUT / "04-diagnosis-output.png",
        "Diagnosis JSON",
        "Destination mismatch is detected before any unsafe replay is attempted.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Fixture",
                "accent": PINK,
                "code": True,
                "lines": [
                    f"event_id={mismatch.get('event_id')}",
                    f"source={mismatch.get('source_system')}",
                    f"destination={mismatch.get('destination_system')}",
                    "failure: destination_mismatch",
                ],
            },
            {"box": (650, 148, 1230, 628), "title": "Output excerpt", "accent": GREEN, "code": True, "lines": cli_mismatch},
        ],
    )
    render(
        OUT / "05-corrected-replay.png",
        "Corrected Replay",
        "A safe malformed-date correction replays only against the local mock destination.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Replay boundary",
                "accent": BLUE,
                "lines": ["deterministic date correction", "local mock destination", "no live webhook call", "traceable replay result"],
            },
            {"box": (650, 148, 1230, 628), "title": "Output excerpt", "accent": GREEN, "code": True, "lines": replay_ok},
        ],
    )
    render(
        OUT / "06-fix-report.png",
        "Generated Fix Report",
        "HTML report is generated locally from the same diagnosis/correction evidence used by CLI and API paths.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Report artifact",
                "accent": YELLOW,
                "code": True,
                "lines": ["examples/output/fix-report.html", f"bytes={report_size}", "source fixture=malformed-date.json", "format=html"],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Report includes",
                "accent": GREEN,
                "lines": ["failure summary", "root cause", "safe correction", "replay decision", "operator handoff notes"],
            },
        ],
    )
    render(
        OUT / "07-duplicate-guard.png",
        "Duplicate Replay Guard",
        "Duplicate/idempotency conflicts are refused and retained as local evidence instead of retried unsafely.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Fixture",
                "accent": RED,
                "code": True,
                "lines": [f"event_id={duplicate.get('event_id')}", "failure: duplicate_event", "safe action: refuse replay", "dead-letter evidence retained"],
            },
            {"box": (650, 148, 1230, 628), "title": "Output excerpt", "accent": GREEN, "code": True, "lines": replay_dup},
        ],
    )
    render(
        OUT / "08-quality-gates.png",
        "Quality Gate Results",
        "The evidence package is regenerated only after local tests and example verification pass.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Verified commands",
                "accent": BLUE,
                "code": True,
                "lines": [
                    "PYTHONPATH=src python -m pytest -q",
                    "python -m ruff check .",
                    "python -m mypy src",
                    "python scripts/verify_examples.py",
                    "python scripts/capture_screenshots.py",
                ],
            },
            {"box": (650, 148, 1230, 628), "title": "Pytest excerpt", "accent": GREEN, "code": True, "lines": pytest_lines},
        ],
    )
    print("screenshots rendered")


if __name__ == "__main__":
    main()
