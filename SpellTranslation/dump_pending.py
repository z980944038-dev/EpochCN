# -*- coding: utf-8 -*-
"""Dump rows that still need translation, grouped by name_en (unique names)."""
import sys
from collections import defaultdict

SRC = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "summary"

with open(SRC, "r", encoding="utf-8") as f:
    header = next(f).rstrip("\n").rstrip("\r").split("\t")
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        rows.append(cols)

name_groups = defaultdict(list)  # name_en -> [row indices]
for idx, r in enumerate(rows):
    if r[3].strip() and not r[7].strip():
        name_groups[r[3].strip()].append(idx)

# Sort by frequency desc
sorted_names = sorted(name_groups.items(), key=lambda x: -len(x[1]))

if MODE == "summary":
    print(f"Unique names needing translation: {len(sorted_names)}")
    print(f"Total rows still untranslated: {sum(len(v) for v in name_groups.values())}")
    # Show top 50 by occurrence
    print("\nTop 60 most frequent unique names pending:")
    for name, idxs in sorted_names[:60]:
        # Show associated skill_line_ids variety
        skill_lines = set()
        for i in idxs:
            if rows[i][2].strip():
                skill_lines.add(rows[i][2].strip())
        print(f"  [{len(idxs):4d}] {name} | skills={','.join(sorted(skill_lines))[:50]}")

elif MODE == "list":
    # Dump unique names (one per line) with a sample desc
    for name, idxs in sorted_names:
        sample_row = rows[idxs[0]]
        desc = sample_row[5].strip()[:100]
        tip = sample_row[6].strip()[:60]
        print(f"{name}\t{len(idxs)}\t{desc}\t{tip}")
