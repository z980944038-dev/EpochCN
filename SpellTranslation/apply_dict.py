# -*- coding: utf-8 -*-
"""Apply a name_en -> name_zh dictionary to the TSV. Only fills empty name_zh.
Also apply rank translation rules (Rank N / Passive / etc.)."""
import sys

DICT = sys.argv[1]
TSV  = sys.argv[2]
OUT  = sys.argv[3] if len(sys.argv) > 3 else TSV

RANK_MAP = {
    "": "",
    "Passive": "被动",
    "Racial Passive": "种族被动",
    "Racial": "种族",
    "Summon": "召唤",
    "Shapeshift": "变形",
    "Apprentice": "学徒",
    "Journeyman": "熟练",
    "Expert": "专家",
    "Artisan": "工匠",
    "Master": "大师",
    "Grand Master": "宗师",
    "Illustrious Grand Master": "卓越宗师",
}

# Load dictionary
name_dict = {}
with open(DICT, "r", encoding="utf-8") as f:
    header = next(f)  # skip header
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        parts = line_nl.split("\t")
        if len(parts) >= 2:
            en = parts[0].strip()
            zh = parts[1].strip()
            if en and zh:
                name_dict[en] = zh
print(f"Dictionary entries loaded: {len(name_dict)}")

# Load TSV
with open(TSV, "r", encoding="utf-8") as f:
    header = next(f).rstrip("\n").rstrip("\r").split("\t")
    rows = []
    for line in f:
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        while len(cols) < 12: cols.append("")
        rows.append(cols[:12])

filled_name = 0
filled_rank = 0
for r in rows:
    name_en = r[3].strip()
    rank_en = r[4].strip()
    if name_en and not r[7].strip() and name_en in name_dict:
        r[7] = name_dict[name_en]
        filled_name += 1
    if rank_en and not r[8].strip():
        if rank_en in RANK_MAP:
            r[8] = RANK_MAP[rank_en]
            filled_rank += 1
        elif rank_en.startswith("Rank ") and rank_en[5:].strip().isdigit():
            r[8] = "等级 " + rank_en[5:].strip()
            filled_rank += 1

# Write
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(header) + "\n")
    for r in rows:
        cleaned = [(c or "").replace("\t", " ") for c in r]
        f.write("\t".join(cleaned) + "\n")

print(f"Names filled from dict: {filled_name}")
print(f"Ranks filled: {filled_rank}")

still = sum(1 for r in rows if r[3].strip() and not r[7].strip())
print(f"Remaining rows with name_en but empty name_zh: {still}")
