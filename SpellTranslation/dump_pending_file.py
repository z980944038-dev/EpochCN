# -*- coding: utf-8 -*-
"""Dump pending unique names to a UTF-8 file, sorted by frequency desc."""
import sys
from collections import defaultdict

SRC = sys.argv[1]
DST = sys.argv[2]

with open(SRC, "r", encoding="utf-8") as f:
    header = next(f).rstrip("\n").rstrip("\r").split("\t")
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        rows.append(cols)

name_groups = defaultdict(list)
for idx, r in enumerate(rows):
    if r[3].strip() and not r[7].strip():
        name_groups[r[3].strip()].append(idx)

sorted_names = sorted(name_groups.items(), key=lambda x: -len(x[1]))

with open(DST, "w", encoding="utf-8", newline="\n") as f:
    f.write("name_en\tcount\tsample_desc\tsample_tip\tskill_ids\n")
    for name, idxs in sorted_names:
        sample_row = rows[idxs[0]]
        desc = sample_row[5].strip().replace("\t", " ")[:200]
        tip = sample_row[6].strip().replace("\t", " ")[:120]
        skills = set()
        for i in idxs:
            if rows[i][2].strip():
                skills.add(rows[i][2].strip())
        sk = ",".join(sorted(skills))[:60]
        f.write(f"{name}\t{len(idxs)}\t{desc}\t{tip}\t{sk}\n")

print(f"Wrote {len(sorted_names)} unique pending names to {DST}")
