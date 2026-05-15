# -*- coding: utf-8 -*-
"""
Apply a translation TSV (en\tzh) to either the description_en or tooltip_en
column of the master TSV. Only fills empty zh cells; never overwrites.

Usage:
    python apply_translations.py <master.tsv> <field> <translations.tsv>
where <field> is one of: desc | tip | name
"""
import sys

MASTER = sys.argv[1]
FIELD  = sys.argv[2]   # desc | tip | name
TRANS  = sys.argv[3]

FIELD_INDEX = {
    "name": (3, 7),   # source col, target col
    "desc": (5, 9),
    "tip":  (6, 10),
}
SRC_IDX, DST_IDX = FIELD_INDEX[FIELD]

# Load translation dict
en_to_zh = {}
with open(TRANS, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        if i == 0 and ("en" in line_nl.lower() and "zh" in line_nl.lower()):
            continue  # header
        parts = line_nl.split("\t")
        if len(parts) >= 2:
            en = parts[0]
            zh = parts[1]
            if en and zh:
                en_to_zh[en] = zh

print(f"Loaded {len(en_to_zh)} translation entries")

# Load master TSV
with open(MASTER, "r", encoding="utf-8") as f:
    header = next(f).rstrip("\n").rstrip("\r").split("\t")
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        while len(cols) < 12:
            cols.append("")
        rows.append(cols[:12])

filled = 0
for r in rows:
    src = r[SRC_IDX].strip()
    dst = r[DST_IDX].strip()
    if src and not dst and src in en_to_zh:
        r[DST_IDX] = en_to_zh[src]
        filled += 1

# Write back
with open(MASTER, "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(header) + "\n")
    for r in rows:
        cleaned = [(c or "").replace("\t", " ") for c in r]
        f.write("\t".join(cleaned) + "\n")

print(f"Filled {filled} cells in field '{FIELD}'")

# Remaining
still = sum(
    1 for r in rows
    if r[SRC_IDX].strip() and not r[DST_IDX].strip()
)
print(f"Remaining {FIELD} cells pending: {still}")
