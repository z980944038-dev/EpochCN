# -*- coding: utf-8 -*-
"""Dump pending names separated by category. Outputs several files."""
import sys
from collections import defaultdict

SRC = sys.argv[1]
OUT_PREFIX = sys.argv[2]

with open(SRC, "r", encoding="utf-8") as f:
    header = next(f)
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip(): continue
        cols = line_nl.split("\t")
        while len(cols) < 12: cols.append("")
        rows.append(cols[:12])

def categorize(name, desc, tip):
    name = name.strip()
    desc = desc.strip()
    tip = tip.strip()
    if not desc and not tip:
        return "items_no_desc"
    if "Summons and dismisses a rideable" in desc or "Rides and parks" in desc:
        return "mount"
    if desc.startswith("Calls forth") and "mammoth" in desc.lower():
        return "mount"
    if desc.startswith("Summons and dismisses") and "mount" in desc.lower():
        return "mount"
    if "Right Click to summon and dismiss" in desc:
        return "pet_companion"
    if name.startswith("Enchant ") and " - " in name:
        return "enchant"
    if name.startswith("Glyph of "):
        return "glyph"
    if desc.startswith("Creates ") and (name.endswith(" Oil") or "Oil" in name):
        return "oil"
    if name.startswith("Teleport:") or name.startswith("Portal:"):
        return "teleport_portal"
    if name.startswith("Smelt "):
        return "smelt"
    if name.startswith("Transmute:"):
        return "transmute"
    if name.startswith("Summon "):
        return "summon"
    if name.startswith("Recipe:") or name.startswith("Pattern:") or name.startswith("Plans:") or name.startswith("Schematic:") or name.startswith("Formula:") or name.startswith("Design:") or name.startswith("Manual:"):
        return "recipe"
    return "other"

groups = defaultdict(list)
for r in rows:
    if r[3].strip() and not r[7].strip():
        cat = categorize(r[3], r[5], r[6])
        groups[cat].append(r)

# Dedupe by name_en within each group
for cat, group_rows in groups.items():
    seen = {}
    for r in group_rows:
        n = r[3].strip()
        if n not in seen:
            seen[n] = r
    # Write
    path = f"{OUT_PREFIX}_{cat}.tsv"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("name_en\tdesc_en\ttip_en\trank_en\tskill_ids\n")
        for n, r in sorted(seen.items()):
            desc = r[5].strip().replace("\t", " ")
            tip  = r[6].strip().replace("\t", " ")
            rank = r[4].strip()
            sk = r[2].strip()
            f.write(f"{n}\t{desc}\t{tip}\t{rank}\t{sk}\n")
    print(f"  [{cat}] unique: {len(seen)}, total rows: {len(group_rows)} -> {path}")

print(f"Total pending rows: {sum(len(v) for v in groups.values())}")
