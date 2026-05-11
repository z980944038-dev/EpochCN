#!/usr/bin/env python3
"""Scrape EpochHead all-item listing and item tooltip green lines."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
import argparse
import json
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "epochhead_items"
OUT = CACHE / "items.json"
LIST_CACHE = CACHE / "list.json"
SNAPSHOT = ROOT / "SourceData" / "EpochHead" / "items"
SNAPSHOT_OUT = SNAPSHOT / "items.json"
SNAPSHOT_LIST = SNAPSHOT / "list.json"
BASE = "https://epochhead.com"
LIST_URL = BASE + "/items"
USER_AGENT = "EpochCN-all-item-sync/0.1"

ITEM_ROW_RE = re.compile(
    r'data-item-id="(?P<id>\d+)".{0,700}?'
    r'alt="(?P<name>[^"]+)".{0,1400}?'
    r"<td>(?P<category>.*?)</td><td>(?P<slot>.*?)</td><td[^>]*>(?P<ilevel>.*?)</td>",
    re.S,
)
PAGE_RE = re.compile(r"Page\s+<!-- -->\d+<!-- -->\s+of\s+<!-- -->(\d+)")
GREEN_RE = re.compile(r'<li class="text-green-400">(.*?)</li>', re.S)
TOOLTIP_UL_RE = re.compile(r'<ul class="list-none space-y-1">(.*?)</ul>', re.S)
TOOLTIP_LI_RE = re.compile(r'<li class="([^"]*)">(.*?)</li>', re.S)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
META_DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.S | re.I)


def fetch(url: str, retries: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            proc = subprocess.run(
                ["curl", "-L", "-sS", "--max-time", "30", "-A", USER_AGENT, url],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return proc.stdout.decode("utf-8", "replace")
        except Exception as exc:
            last_error = exc
            time.sleep(0.75 + attempt)
    raise RuntimeError(f"fetch failed for {url}: {last_error}")


def clean_html(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", " ", value or "", flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<!--[\s\S]*?-->", " ", value)
    value = re.sub(r"<.*?>", " ", value)
    value = value.replace("\\u0026", "&")
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def parse_list_page(html: str) -> list[dict]:
    rows: list[dict] = []
    for match in ITEM_ROW_RE.finditer(html):
        item_id = int(match.group("id"))
        rows.append({
            "id": item_id,
            "name": clean_html(match.group("name")),
            "category": clean_html(match.group("category")),
            "slot": clean_html(match.group("slot")),
            "ilevel": clean_html(match.group("ilevel")),
            "url": f"{BASE}/?item={item_id}",
        })
    return rows


def parse_page_count(html: str) -> int:
    match = PAGE_RE.search(html)
    return int(match.group(1)) if match else 1


def parse_title(html: str, fallback: str) -> str:
    match = TITLE_RE.search(html)
    if not match:
        return fallback
    title = clean_html(match.group(1))
    return re.sub(r"\s+—\s+EpochHead.*$", "", title).strip() or fallback


def parse_meta_description(html: str) -> str:
    match = META_DESC_RE.search(html)
    return clean_html(match.group(1)) if match else ""


def parse_green_lines(html: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for match in GREEN_RE.finditer(html):
        line = clean_html(match.group(1))
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    return lines


def tooltip_color(class_name: str) -> str:
    if "text-green-400" in class_name:
        return "green"
    if "text-yellow" in class_name or "text-amber" in class_name:
        return "yellow"
    if "text-gray" in class_name or "text-neutral" in class_name or "muted" in class_name:
        return "gray"
    if "text-red" in class_name:
        return "red"
    return "normal"


def classify_tooltip_text(text: str) -> str:
    if re.match(r"^(Use|Equip|Chance on hit):", text):
        return "green"
    if re.match(r'^"[^"]+"$', text):
        return "yellow"
    return "normal"


def parse_tooltip_lines(html: str) -> list[dict]:
    match = TOOLTIP_UL_RE.search(html)
    if not match:
        return []
    rows: list[dict] = []
    for line_match in TOOLTIP_LI_RE.finditer(match.group(1)):
        class_name = line_match.group(1) or ""
        text = clean_html(line_match.group(2))
        if text:
            rows.append({"text": text, "color": tooltip_color(class_name), "className": class_name})
    if any(re.search(r"Retrieving item information", row["text"], re.I) for row in rows):
        return []
    return rows


def parse_meta_tooltip(title: str, description: str) -> list[dict]:
    text = clean_html(description or "")
    if title and text.startswith(title):
        text = clean_html(text[len(title):])
    if not text or re.search(r"Retrieving item information", text, re.I):
        return []

    marker = r'(?=\s+(?:"|Use:|Equip:|Chance on hit:|Binds|Requires|Unique|Races:|Classes:|Item Level|Speed|[0-9,.]+ - [0-9,.]+ Damage|\([0-9,.]+ damage per second\)|\+[0-9,.]+ )\b|$)'
    pattern = re.compile("|".join([
        r'"[^"]*"',
        r"Use:.*?" + marker,
        r"Equip:.*?" + marker,
        r"Chance on hit:.*?" + marker,
        r"Binds (?:to account|when picked up|when equipped|when used)",
        r"Unique(?:-Equipped)?(?: \(\d+\))?",
        r"One-Hand|Two-Hand|Main Hand|Off Hand|Held In Off-hand|Ranged|Thrown",
        r"Speed [0-9.]+",
        r"[0-9,.]+ - [0-9,.]+ Damage",
        r"\([0-9,.]+ damage per second\)",
        r"\+[0-9,.]+ [A-Za-z ]+",
        r"Requires Level \d+",
        r"Requires .*?" + marker,
        r"Item Level \d+",
        r"Races:.*?" + marker,
        r"Classes:.*?" + marker,
    ]), re.I)

    rows: list[dict] = []
    seen: set[str] = set()
    for match in pattern.finditer(text):
        line = clean_html(match.group(0))
        if line and line not in seen:
            seen.add(line)
            rows.append({"text": line, "color": classify_tooltip_text(line), "className": ""})
    return rows


def fetch_detail(item: dict) -> dict:
    html = fetch(item["url"])
    item = dict(item)
    item["name"] = parse_title(html, item.get("name") or "")
    item["description"] = parse_meta_description(html)
    tooltip = parse_tooltip_lines(html)
    if not tooltip:
        tooltip = parse_meta_tooltip(item["name"], item["description"])
    item["tooltip"] = tooltip
    green = [row["text"] for row in tooltip if row.get("color") == "green"]
    for line in parse_green_lines(html):
        if line not in green:
            green.append(line)
    item["green"] = green
    return item


def collect_list(total_pages_override: int | None = None) -> list[dict]:
    first = fetch(LIST_URL)
    total_pages = total_pages_override or parse_page_count(first)
    found: dict[int, dict] = {}
    for item in parse_list_page(first):
        found[item["id"]] = item
    print(f"list page 1/{total_pages}: items={len(found)}", flush=True)

    def fetch_list_page(page: int) -> tuple[int, str]:
        return page, fetch(f"{LIST_URL}?page={page}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_list_page, page) for page in range(2, total_pages + 1)]
        for index, future in enumerate(as_completed(futures), 2):
            _, html = future.result()
            for item in parse_list_page(html):
                found[item["id"]] = item
            if index % 25 == 0 or index == total_pages:
                print(f"list pages {index}/{total_pages}: items={len(found)}", flush=True)

    items = [found[item_id] for item_id in sorted(found)]
    LIST_CACHE.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return items


def load_existing_details() -> dict[int, dict]:
    details: dict[int, dict] = {}
    for path in (SNAPSHOT_OUT, OUT):
        if not path.exists():
            continue
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        details.update({int(row["id"]): row for row in rows if row.get("id") and not row.get("error")})
    return details


def write_details(rows: list[dict]) -> None:
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    OUT.write_text(text, encoding="utf-8")
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_OUT.write_text(text, encoding="utf-8")


def write_list(rows: list[dict]) -> None:
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    LIST_CACHE.write_text(text, encoding="utf-8")
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_LIST.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape all EpochHead item details.")
    parser.add_argument("--pages", type=int, default=None, help="Override list page count for testing.")
    parser.add_argument("--reuse-list", action="store_true", help="Reuse cached item list if present.")
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    if args.reuse_list and LIST_CACHE.exists():
        items = json.loads(LIST_CACHE.read_text(encoding="utf-8"))
    elif args.reuse_list and SNAPSHOT_LIST.exists():
        items = json.loads(SNAPSHOT_LIST.read_text(encoding="utf-8"))
    else:
        items = collect_list(args.pages)
    if items:
        write_list(items)

    details = load_existing_details()
    todo = [item for item in items if int(item["id"]) not in details or not details[int(item["id"])].get("tooltip")]
    print(f"detail queue: {len(todo)}/{len(items)}", flush=True)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(fetch_detail, item): item for item in todo}
        for index, future in enumerate(as_completed(futures), 1):
            item = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                row = dict(item)
                row["green"] = []
                row["error"] = str(exc)
            details[int(row["id"])] = row
            if index % 100 == 0 or index == len(todo):
                print(f"detail {index}/{len(todo)} complete={len(details)}/{len(items)}", flush=True)
                rows = [details[item_id] for item_id in sorted(details)]
                write_details(rows)

    rows = [details[item_id] for item_id in sorted(details)]
    write_details(rows)
    green_items = sum(1 for row in rows if row.get("green"))
    print(f"wrote {OUT}", flush=True)
    print(f"items={len(rows)} green_items={green_items}", flush=True)


if __name__ == "__main__":
    main()
