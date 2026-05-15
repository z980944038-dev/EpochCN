# -*- coding: utf-8 -*-
import sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    header = next(f)
    rows = 0
    name_filled = 0
    rank_filled = 0
    desc_filled = 0
    tip_filled = 0
    desc_needed = 0
    tip_needed = 0
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip(): continue
        cols = line_nl.split("\t")
        while len(cols) < 12: cols.append("")
        rows += 1
        if cols[7].strip(): name_filled += 1
        if cols[8].strip(): rank_filled += 1
        if cols[5].strip() and cols[9].strip(): desc_filled += 1
        if cols[5].strip() and not cols[9].strip(): desc_needed += 1
        if cols[6].strip() and cols[10].strip(): tip_filled += 1
        if cols[6].strip() and not cols[10].strip(): tip_needed += 1

print(f"Total rows: {rows}")
print(f"name_zh filled: {name_filled}")
print(f"rank_zh filled: {rank_filled}")
print(f"description_zh filled: {desc_filled}, needed: {desc_needed}")
print(f"tooltip_zh filled: {tip_filled}, needed: {tip_needed}")
