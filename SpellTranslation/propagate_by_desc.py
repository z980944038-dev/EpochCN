# -*- coding: utf-8 -*-
"""
Secondary propagation:
Sometimes name_en is unique in pending set, but another row in the file has
the SAME description_en (non-empty) WITH a known name_zh. In that case we can
safely copy the name_zh.
Also: if a spell ID is referenced via $NNNNNs1 pattern in descriptions, those
spells often share core name with the caller. Skip that heuristic for safety.
"""
import sys
from collections import defaultdict

IN = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else IN

with open(IN, "r", encoding="utf-8") as f:
    header = next(f).rstrip("\n").rstrip("\r").split("\t")
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        while len(cols) < 12: cols.append("")
        rows.append(cols[:12])

def norm(s): return (s or "").strip()

# Build desc_en -> {name_zh -> count} for rows that have both
desc_to_name = defaultdict(lambda: defaultdict(int))
for r in rows:
    de = norm(r[5])
    nz = norm(r[7])
    if de and nz and len(de) > 15:  # avoid tiny/ambiguous descriptions
        desc_to_name[de][nz] += 1

# Same for tooltip -> name
tip_to_name = defaultdict(lambda: defaultdict(int))
for r in rows:
    te = norm(r[6])
    nz = norm(r[7])
    if te and nz and len(te) > 15:
        tip_to_name[te][nz] += 1

filled = 0
for r in rows:
    if norm(r[3]) and not norm(r[7]):
        # Try description match first
        de = norm(r[5])
        if de and de in desc_to_name:
            counts = desc_to_name[de]
            # Require unanimous translation: only one name_zh for that desc
            if len(counts) == 1:
                r[7] = next(iter(counts.keys()))
                filled += 1
                continue
        # Try tooltip
        te = norm(r[6])
        if te and te in tip_to_name:
            counts = tip_to_name[te]
            if len(counts) == 1:
                r[7] = next(iter(counts.keys()))
                filled += 1
                continue

# Also propagate description_zh / tooltip_zh where name is now known but
# desc_zh/tip_zh empty and exact desc_en/tip_en pair exists with known zh.
desc_en_to_zh = defaultdict(lambda: defaultdict(int))
tip_en_to_zh  = defaultdict(lambda: defaultdict(int))
for r in rows:
    de, dz = norm(r[5]), norm(r[9])
    te, tz = norm(r[6]), norm(r[10])
    if de and dz: desc_en_to_zh[de][dz] += 1
    if te and tz: tip_en_to_zh[te][tz]  += 1

def winner(d, k):
    k = norm(k)
    if k and k in d:
        return max(d[k].items(), key=lambda x: x[1])[0]
    return None

desc_filled = 0
tip_filled = 0
for r in rows:
    if norm(r[5]) and not norm(r[9]):
        w = winner(desc_en_to_zh, r[5])
        if w:
            r[9] = w; desc_filled += 1
    if norm(r[6]) and not norm(r[10]):
        w = winner(tip_en_to_zh, r[6])
        if w:
            r[10] = w; tip_filled += 1

# Write out
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(header) + "\n")
    for r in rows:
        cleaned = [(c or "").replace("\t", " ") for c in r]
        f.write("\t".join(cleaned) + "\n")

print(f"Name filled via desc/tip match: {filled}")
print(f"Description cells filled: {desc_filled}")
print(f"Tooltip cells filled: {tip_filled}")

still = sum(1 for r in rows if norm(r[3]) and not norm(r[7]))
print(f"Rows still untranslated (name empty): {still}")
