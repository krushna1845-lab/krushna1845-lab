"""Fetch public GitHub contribution levels without requiring a token."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "krushna1845-lab"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"


def fallback_days() -> list[dict[str, object]]:
    start = date.today() - timedelta(days=370)
    return [
        {"date": (start + timedelta(days=offset)).isoformat(), "level": 0}
        for offset in range(371)
    ]


def main() -> None:
    url = f"https://github.com/users/{USERNAME}/contributions"
    request = Request(url, headers={"User-Agent": "github-profile-readme"})
    try:
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8")
        pattern = re.compile(r"<[^>]*data-date=\"(?P<date>\d{4}-\d{2}-\d{2})\"[^>]*data-level=\"(?P<level>\d+)\"[^>]*>")
        days = [
            {"date": match.group("date"), "level": int(match.group("level"))}
            for match in pattern.finditer(html)
        ]
        if not days:
            raise ValueError("GitHub returned no contribution cells")
    except Exception as error:  # Preserve a renderable profile when GitHub is unavailable.
        print(f"Warning: {error}. Writing an empty heatmap.", file=sys.stderr)
        days = fallback_days()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"username": USERNAME, "days": days}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
