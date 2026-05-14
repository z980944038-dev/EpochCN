#!/usr/bin/env python3
"""Audit mixed Chinese-English strings in EpochConsumableData.lua."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data" / "EpochConsumableData.lua"
STRING_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
IGNORED_ASCII_TOKENS = re.compile(r"\b(?:EpochHead|PvP|NPC|AH|ID|DBC|GM)\b", re.I)


def unescape_lua(text: str) -> str:
    return (
        text.replace(r"\\", "\\")
        .replace(r'\"', '"')
        .replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\t", "\t")
    )


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def has_ascii_letters(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text))


def has_meaningful_ascii(text: str) -> bool:
    cleaned = IGNORED_ASCII_TOKENS.sub("", text)
    return has_ascii_letters(cleaned)


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    counts: Counter[str] = Counter()

    for raw in STRING_RE.findall(text):
        value = unescape_lua(raw).strip()
        if not value:
            continue
        if has_cjk(value) and has_meaningful_ascii(value):
            counts[value] += 1

    total = sum(counts.values())
    unique = len(counts)
    print(f"file={DATA}")
    print(f"mixed_total={total}")
    print(f"mixed_unique={unique}")

    for value, count in counts.most_common(25):
        compact = value.replace("\n", r"\n")
        print(f"{count}\t{compact}")


if __name__ == "__main__":
    main()