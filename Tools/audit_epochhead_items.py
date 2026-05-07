from __future__ import annotations

from html import unescape
from pathlib import Path
import argparse
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(r"D:\1927\Ascension Launcher\resources\epoch-live")
ADDON = ROOT / "Interface" / "AddOns" / "EpochCN"
OBJECTIVE_NAMES = ADDON / "Data" / "ObjectiveNameData.lua"
OUT = ADDON / "Tools" / "EPOCHHEAD_ITEM_GAPS.md"


ITEM_RE = re.compile(
    r'data-item-id="(?P<id>\d+)".{0,500}?'
    r'<span class="font-medium [^"]+">(?P<name>.*?)</span>',
    re.S,
)
NEXT_RE = re.compile(r'href="(?P<href>\?page=\d+)">\s*Next', re.I)
LUA_NAME_RE = re.compile(r'\["((?:\\.|[^"\\])*)"\]\s*=\s*"((?:\\.|[^"\\])*)"')


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "EpochCN-localization-audit/0.1"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def load_known_names() -> set[str]:
    known: set[str] = set()
    if not OBJECTIVE_NAMES.exists():
        return known
    text = OBJECTIVE_NAMES.read_text(encoding="utf-8", errors="replace")
    for match in LUA_NAME_RE.finditer(text):
        known.add(match.group(1))
    return known


def parse_items(html: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for match in ITEM_RE.finditer(html):
        item_id = match.group("id")
        name = unescape(re.sub(r"<.*?>", "", match.group("name"))).strip()
        if name:
            items.append((item_id, name))
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit EpochHead item names missing from EpochCN name data.")
    parser.add_argument("--pages", type=int, default=5, help="Maximum EpochHead item pages to scan.")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    known = load_known_names()
    seen: dict[str, str] = {}
    missing: list[tuple[str, str]] = []
    url = "https://epochhead.com/items"

    for _ in range(max(1, args.pages)):
        html = fetch(url)
        for item_id, name in parse_items(html):
            if item_id in seen:
                continue
            seen[item_id] = name
            if name not in known:
                missing.append((item_id, name))

        next_match = NEXT_RE.search(html)
        if not next_match:
            break
        url = urljoin("https://epochhead.com/items", next_match.group("href"))

    lines = [
        "# EpochHead Item Gap Audit",
        "",
        f"Scanned EpochHead items: {len(seen)}",
        f"Missing exact English-name mappings: {len(missing)}",
        "",
        "| Item ID | English name |",
        "| ---: | --- |",
    ]
    for item_id, name in missing[:500]:
        lines.append(f"| {item_id} | `{name}` |")

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
