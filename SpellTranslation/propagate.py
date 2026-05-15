# -*- coding: utf-8 -*-
"""
Propagate existing translations to same-name/same-description variants.
Reads TSV where columns are:
  spell_id, priority, skill_line_ids, name_en, rank_en, description_en,
  tooltip_en, name_zh, rank_zh, description_zh, tooltip_zh, notes
Zero-hallucination: only fills zh fields when an English key already has
a known zh translation in the file.
"""
import csv, sys, io, os

IN = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else IN

COLS = ["spell_id","priority","skill_line_ids",
        "name_en","rank_en","description_en","tooltip_en",
        "name_zh","rank_zh","description_zh","tooltip_zh","notes"]

# Rank translation table (standard WLK/Classic Chinese)
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

def norm(s):
    return (s or "").strip()

def load(path):
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        header = next(reader)
        for r in reader:
            # pad to 12
            while len(r) < 12:
                r.append("")
            rows.append(r[:12])
    return header, rows

def save(path, header, rows):
    # Manual write to avoid csv module escaping/quoting the TSV.
    # Source cells may contain literal "\n" (two characters) meaning in-game
    # newline - we must preserve them. Guard only against real TAB / CR / LF.
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            cleaned = [ (c or "").replace("\t", " ").replace("\r", "").replace("\n", " ") for c in r ]
            f.write("\t".join(cleaned) + "\n")

def main():
    header, rows = load(IN)

    # Build translation dictionaries from already-translated rows
    name_dict = {}     # name_en -> name_zh (majority vote)
    desc_dict = {}     # description_en -> description_zh
    tip_dict  = {}     # tooltip_en -> tooltip_zh

    def add(d, k, v):
        k = norm(k); v = norm(v)
        if not k or not v:
            return
        if k not in d:
            d[k] = {}
        d[k][v] = d[k].get(v, 0) + 1

    for r in rows:
        name_en, rank_en, desc_en, tip_en = r[3], r[4], r[5], r[6]
        name_zh, rank_zh, desc_zh, tip_zh = r[7], r[8], r[9], r[10]
        if norm(name_en) and norm(name_zh):
            add(name_dict, name_en, name_zh)
        if norm(desc_en) and norm(desc_zh):
            add(desc_dict, desc_en, desc_zh)
        if norm(tip_en) and norm(tip_zh):
            add(tip_dict, tip_en, tip_zh)

    def winner(d, k):
        k = norm(k)
        if not k or k not in d:
            return None
        # highest frequency winner
        return max(d[k].items(), key=lambda x: x[1])[0]

    changed = 0
    rows_touched = 0

    for r in rows:
        name_en, rank_en, desc_en, tip_en = r[3], r[4], r[5], r[6]
        name_zh, rank_zh, desc_zh, tip_zh = r[7], r[8], r[9], r[10]
        touched = False

        # Name propagation
        if norm(name_en) and not norm(name_zh):
            w = winner(name_dict, name_en)
            if w:
                r[7] = w; changed += 1; touched = True

        # Rank propagation (from RANK_MAP)
        if norm(rank_en) and not norm(rank_zh):
            rn = norm(rank_en)
            if rn in RANK_MAP:
                r[8] = RANK_MAP[rn]; changed += 1; touched = True
            elif rn.startswith("Rank ") and rn[5:].strip().isdigit():
                r[8] = "等级 " + rn[5:].strip(); changed += 1; touched = True

        # Description propagation
        if norm(desc_en) and not norm(desc_zh):
            w = winner(desc_dict, desc_en)
            if w:
                r[9] = w; changed += 1; touched = True

        # Tooltip propagation
        if norm(tip_en) and not norm(tip_zh):
            w = winner(tip_dict, tip_en)
            if w:
                r[10] = w; changed += 1; touched = True

        if touched:
            rows_touched += 1

    save(OUT, header, rows)
    print(f"Cells filled: {changed}")
    print(f"Rows touched: {rows_touched}")

    # Report remaining work
    still = 0
    for r in rows:
        if norm(r[3]) and not norm(r[7]):
            still += 1
    print(f"Remaining rows with name_en but empty name_zh: {still}")

main()
