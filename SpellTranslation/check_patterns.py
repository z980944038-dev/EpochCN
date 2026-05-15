# -*- coding: utf-8 -*-
"""Identify common patterns among pending names to enable template translation."""
import sys, re
from collections import Counter

SRC = sys.argv[1]

with open(SRC, "r", encoding="utf-8") as f:
    header = next(f)
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip(): continue
        cols = line_nl.split("\t")
        while len(cols) < 12: cols.append("")
        rows.append(cols[:12])

pending = [r for r in rows if r[3].strip() and not r[7].strip()]

# Categorize by name/desc patterns
patterns = Counter()
examples = {}

def categorize(name, desc, tip):
    name = name.strip()
    desc = desc.strip()
    tip = tip.strip()
    # Empty desc and tip - likely gear/consumable
    if not desc and not tip:
        return "gear-or-item-no-desc"
    # Mount descriptions
    if "Summons and dismisses a rideable" in desc or "Rides and parks" in desc:
        return "mount-rideable"
    if desc.startswith("Calls forth the") and "mammoth" in desc.lower():
        return "mount-mammoth-caravan"
    if "Right Click to summon and dismiss" in desc:
        return "companion-pet"
    # Enchant patterns
    if name.startswith("Enchant ") and " - " in name:
        return "enchant-pattern"
    # Glyph patterns
    if name.startswith("Glyph of "):
        return "glyph-pattern"
    # Create oil/elixir
    if desc.startswith("Creates ") and name.endswith(" Oil"):
        return "oil-pattern"
    if desc.startswith("Creates "):
        return "create-pattern"
    # Teleport/Portal
    if name.startswith("Teleport:"):
        return "teleport-pattern"
    if name.startswith("Portal:"):
        return "portal-pattern"
    # Cooking recipes
    if name.startswith("Recipe:") or name.startswith("Pattern:") or name.startswith("Plans:") or name.startswith("Schematic:") or name.startswith("Formula:") or name.startswith("Design:") or name.startswith("Manual:"):
        return "recipe-pattern"
    # Smelt
    if name.startswith("Smelt "):
        return "smelt-pattern"
    # Transmute
    if name.startswith("Transmute:"):
        return "transmute-pattern"
    # Summon xxx
    if name.startswith("Summon "):
        return "summon-pattern"
    return "other"

for r in pending:
    cat = categorize(r[3], r[5], r[6])
    patterns[cat] += 1
    if cat not in examples:
        examples[cat] = (r[3], r[5][:100] if r[5] else "", r[6][:60] if r[6] else "")

for cat, cnt in patterns.most_common():
    print(f"  [{cnt:5d}] {cat}  -- e.g. {examples[cat][0]!r}")
