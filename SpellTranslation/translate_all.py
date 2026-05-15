# -*- coding: utf-8 -*-
"""
Complete translation script for spell_english_spellbook_priority.tsv
Translates all remaining name_zh, rank_zh, description_zh, tooltip_zh fields.

Rules (from README_翻译说明.md):
- Do NOT translate WoW variables: $s1, $d, $o1, ${...}, $lxxx:yyy;, |cFFFFFFFF, |r
- \n = in-game newline, preserve as-is
- Rank translations: Rank N -> 等级 N, Passive -> 被动, etc.
- Empty English = keep Chinese empty
"""
import sys
import re
import os

TSV_PATH = sys.argv[1] if len(sys.argv) > 1 else r"spell_english_spellbook_priority.tsv"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else TSV_PATH

# ============================================================
# RANK MAP
# ============================================================
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

