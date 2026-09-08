"""Render public contribution data into a self-hosted animated SVG."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "assets" / "contribution-heatmap.svg"
PALETTE = ["#161b22", "#251b3d", "#3b2470", "#5b21b6", "#7c3aed", "#a78bfa"]


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = {item["date"]: int(item["level"]) for item in payload["days"]}
    end = date.today()
    start = end - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # Sunday start

    cells: list[str] = []
    current = start
    for index in range(371):
        week, weekday = divmod(index, 7)
        x, y = 106 + week * 14, 84 + weekday * 18
        level = max(0, min(5, days.get(current.isoformat(), 0)))
        delay = min(2.8, (week + weekday) * 0.035)
        cells.append(
            f'<rect class="cell" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{PALETTE[level]}"><title>{current.isoformat()}: level {level}</title></rect>'
        )
        current += timedelta(days=1)

    active_days = sum(1 for level in days.values() if level > 0)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="248" viewBox="0 0 900 248" role="img" aria-label="GitHub contribution heatmap">
  <rect width="900" height="248" rx="14" fill="#0d1117" stroke="#30363d"/>
  <text x="28" y="32" fill="#e6edf3" font-family="ui-sans-serif, system-ui" font-size="17" font-weight="600">Contribution activity</text>
  <text x="28" y="58" fill="#8b949e" font-family="ui-monospace, monospace" font-size="13">{active_days} active contribution days in the last year</text>
  <g fill="#8b949e" font-family="ui-monospace, monospace" font-size="11"><text x="28" y="94">Sun</text><text x="28" y="130">Tue</text><text x="28" y="166">Thu</text><text x="28" y="202">Sat</text></g>
  <g>{''.join(cells)}</g>
  <g font-family="ui-monospace, monospace" font-size="11" fill="#8b949e"><text x="720" y="230">Less</text>{''.join(f'<rect x="{766 + i * 17}" y="220" width="11" height="11" rx="2" fill="{colour}"/>' for i, colour in enumerate(PALETTE))}<text x="871" y="230">More</text></g>
  <style>.cell {{ opacity: 0; transform: translateY(5px); animation: reveal .35s ease-out forwards; }} @keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}</style>
</svg>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
