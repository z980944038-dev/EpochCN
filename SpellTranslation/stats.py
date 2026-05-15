# -*- coding: utf-8 -*-
import sys
path = sys.argv[1]
from collections import Counter
counts = Counter()
total = 0
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 0:
            continue
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        counts[len(cols)] += 1
        total += 1
print("Total data lines:", total)
for k in sorted(counts):
    print(f"  cols={k}: {counts[k]}")

# Now compute translation status assuming 12 columns
with open(path, "r", encoding="utf-8") as f:
    header = next(f)
    has_name = 0
    translated = 0
    untranslated = 0
    rows = 0
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        while len(cols) < 12:
            cols.append("")
        name_en = cols[3].strip()
        name_zh = cols[7].strip()
        rows += 1
        if name_en:
            has_name += 1
        if name_zh:
            translated += 1
        if name_en and not name_zh:
            untranslated += 1
print(f"Rows: {rows}, has_name_en: {has_name}, translated(name_zh): {translated}, need translate: {untranslated}")
