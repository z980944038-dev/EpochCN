#!/usr/bin/env python3
"""Audit EpochHead coverage for EpochCN.

This is an offline build-time tool. It never runs in-game, so EpochCN keeps all
lookups table-based and avoids network or large scans during play.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import argparse
import re
import ssl
import time


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
OUT = ROOT / "Tools" / "EPOCHHEAD_COVERAGE.md"
BASE = "https://epochhead.com"

LUA_NAME_RE = re.compile(r'\["((?:\\.|[^"\\])*)"\]\s*=\s*"((?:\\.|[^"\\])*)"')
LUA_ROW_RE = re.compile(r"\[(\d+)\]\s*=\s*\{\s*\"((?:\\.|[^\"\\])*)\"")
ITEM_ROW_RE = re.compile(
    r'data-item-id="(?P<id>\d+)".{0,700}?alt="(?P<name>[^"]+)".{0,1400}?'
    r"<td>(?P<category>.*?)</td><td>(?P<slot>.*?)</td><td[^>]*>(?P<ilevel>.*?)</td>",
    re.S,
)
QUEST_ROW_RE = re.compile(
    r'href="/\?quest=(?P<id>\d+)".{0,120}?children\\?":\\?"(?P<flight_name>[^"\\]+)'
    r"|href=\"/\?quest=(?P<html_id>\d+)\">(?P<html_name>.*?)</a>",
    re.S,
)
NEXT_RE = re.compile(r'href="(?P<href>\?page=\d+[^"]*)".{0,80}?Next', re.I | re.S)


@dataclass(frozen=True)
class Row:
    id: int
    name: str


def fetch(url: str, pause: float) -> str:
    req = Request(url, headers={"User-Agent": "EpochCN-localization-audit/0.3"})
    try:
        resp = urlopen(req, timeout=30)
    except Exception as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        resp = urlopen(req, timeout=30, context=ssl._create_unverified_context())
    with resp:
        text = resp.read().decode("utf-8", "replace")
    if pause > 0:
        time.sleep(pause)
    return text


def clean_html(value: str) -> str:
    value = re.sub(r"<.*?>", "", value or "")
    value = value.replace("\\u0026", "&")
    return unescape(value).strip()


def load_known_names() -> set[str]:
    known: set[str] = set()
    for path in (DATA / "ObjectiveNameData.lua", DATA / "EpochHeadData.lua"):
      if not path.exists():
        continue
      for english, _ in LUA_NAME_RE.findall(path.read_text(encoding="utf-8", errors="replace")):
        known.add(english.replace('\\"', '"').replace("\\'", "'"))
    return known


def has_cn(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text or "")


def load_known_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return {int(row_id) for row_id, title in LUA_ROW_RE.findall(text) if has_cn(title)}


def parse_items(html: str) -> list[Row]:
    rows: list[Row] = []
    for match in ITEM_ROW_RE.finditer(html):
        rows.append(Row(int(match.group("id")), clean_html(match.group("name"))))
    return rows


def parse_quests(html: str) -> list[Row]:
    rows: list[Row] = []
    seen: set[int] = set()
    for match in QUEST_ROW_RE.finditer(html):
        raw_id = match.group("id") or match.group("html_id")
        raw_name = match.group("flight_name") or match.group("html_name")
        if not raw_id or not raw_name:
            continue
        row = Row(int(raw_id), clean_html(raw_name))
        if row.id not in seen:
            seen.add(row.id)
            rows.append(row)
    return rows


def crawl_listing(path: str, pages: int, pause: float, parser) -> list[Row]:
    rows: list[Row] = []
    seen: set[int] = set()
    url = urljoin(BASE, path)
    for _ in range(max(1, pages)):
        html = fetch(url, pause)
        for row in parser(html):
            if row.id not in seen:
                seen.add(row.id)
                rows.append(row)
        match = NEXT_RE.search(html)
        if not match:
            break
        url = urljoin(url, match.group("href"))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit EpochHead item/quest names missing from EpochCN.")
    parser.add_argument("--item-pages", type=int, default=50, help="EpochHead item pages to scan (full site: 333).")
    parser.add_argument("--quest-pages", type=int, default=30, help="EpochHead quest pages to scan (full site: 91).")
    parser.add_argument("--pause", type=float, default=0.25, help="Delay between requests.")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    known = load_known_names()
    known_item_ids = load_known_ids(DATA / "ItemData.lua") | load_known_ids(DATA / "EpochHeadData.lua")
    known_quest_ids = load_known_ids(DATA / "QuestCN_Data.lua") | load_known_ids(DATA / "EpochQuestData.lua") | load_known_ids(DATA / "EpochHeadData.lua")
    items = crawl_listing("/items", args.item_pages, args.pause, parse_items)
    quests = crawl_listing("/quests", args.quest_pages, args.pause, parse_quests)
    missing_items = [row for row in items if row.id not in known_item_ids and row.name not in known]
    missing_quests = [row for row in quests if row.id not in known_quest_ids and row.name not in known]

    lines = [
        "# EpochHead Coverage Audit",
        "",
        "Source: https://epochhead.com/",
        "",
        f"Scanned item rows: {len(items)}",
        f"Missing item name mappings: {len(missing_items)}",
        f"Scanned quest rows: {len(quests)}",
        f"Missing quest title mappings: {len(missing_quests)}",
        "",
        "## Missing Items",
        "",
        "| ID | English name |",
        "| ---: | --- |",
    ]
    lines.extend(f"| {row.id} | `{row.name}` |" for row in missing_items[:200])
    lines.extend(["", "## Missing Quests", "", "| ID | English title |", "| ---: | --- |"])
    lines.extend(f"| {row.id} | `{row.name}` |" for row in missing_quests[:200])

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
