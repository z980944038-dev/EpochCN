#!/usr/bin/env python3
# fix_glyph_tokens.py — 用 WoW 3.3.5 已知数值替换 SpellData_52 中的 m1/1000 DBC token 雕文描述

import os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', 'Data')
target = os.path.join(data_dir, 'SpellData_52.lua')

# Standard WoW 3.3.5 glyph values (only those with m1/1000 tokens currently broken)
# Format: spell_id -> (name, corrected_description)
glyph_fixes = {
    54818: ("割裂雕文",        "你的割裂持续时间延长4秒。"),
    54826: ("生命绽放雕文",    "生命绽放的持续时间延长2秒。"),
    54928: ("奉献雕文",        "奉献的持续时间和冷却时间延长2秒。"),
    55443: ("冰霜震击雕文",    "使你的冰霜震击持续时间延长2秒。"),
    55676: ("心灵尖啸雕文",    "你的心灵尖啸持续时间延长3秒，但不再降低目标的移动速度。"),
    55685: ("救赎之魂雕文",    "救赎之魂的持续时间延长2秒。"),
    56232: ("死亡缠绕雕文",    "使你的凋零缠绕的持续时间延长2秒。"),
    56241: ("痛苦诅咒雕文",    "使你的痛苦诅咒的持续时间延长4秒。"),
    56381: ("奥术能量雕文",    "奥术强化持续时间延长8秒。"),
    56798: ("闷棍雕文",        "闷棍的持续时间延长3秒。"),
    56799: ("闪避雕文",        "闪避的持续时间延长3秒。"),
    56801: ("割裂雕文",        "割裂的持续时间延长4秒。"),
    56803: ("破甲雕文",        "破甲的持续时间延长12秒。"),
    56808: ("冲动雕文",        "使你的冲动持续时间延长3秒。"),
    56810: ("切割雕文",        "切割的持续时间延长3秒。"),
    56814: ("鬼魅攻击雕文",    "鬼魅攻击伤害提高20%，效果持续时间延长10秒，但冷却时间增加30秒。"),
    56832: ("毒蛇刺钉雕文",    "你的毒蛇钉刺持续时间延长6秒。"),
    58385: ("撕裂雕文",        "你的撕裂不再消耗怒气，且持续时间延长6秒。"),
    62969: ("狂暴雕文",        "狂暴的持续时间延长4秒。"),
    63218: ("圣光道标雕文",    "圣光道标持续时间延长30秒。"),
    63246: ("希望圣歌雕文",    "使你的希望圣歌的持续时间额外延长6秒。"),
    63256: ("嫁祸诀窍雕文",    "使你的嫁祸诀窍提供的额外伤害和仇恨转移效果持续时间延长10秒。"),
    63273: ("激流雕文",        "激流持续时间延长3秒。"),
    63303: ("恶魔变形雕文",    "使你的恶魔变形的持续时间延长6秒。"),
}

with open(target, encoding='utf-8') as f:
    lines = f.readlines()

fixed = 0
for i, line in enumerate(lines):
    for spell_id, (name, new_desc) in glyph_fixes.items():
        bracket = f'[{spell_id}]'
        if bracket in line and '/1000' in line:
            lines[i] = f'[{spell_id}] = {{"{name}","{new_desc}","汉化"}},\n'
            print(f"  Fixed [{spell_id}] {name}")
            fixed += 1
            break

print(f"\nTotal fixed: {fixed}")
with open(target, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Saved to", target)
