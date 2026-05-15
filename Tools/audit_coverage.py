#!/usr/bin/env python3
"""统计 EpochCN 数据文件中英文残留、Deprecated/UNUSED 占位、可疑脏数据数量。"""
import re, sys, os

# [id] = {"name", "desc", ...}  的第一个字符串
ENTRY_RE = re.compile(r'\[(\d+)\]\s*=\s*\{\s*"([^"\\]*(?:\\.[^"\\]*)*)"')
# Lua 字符串转义
def unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")

def contains_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s)

def classify(name):
    low = name.lower()
    if re.search(r'\[unused\]|deprecated|^old |^olddwarven|^test |placeholder|\bunused\b', low):
        return 'dep'
    if not name.strip():
        return 'empty'
    if contains_cjk(name):
        return 'cn'
    return 'en'

def audit(path):
    total = en = cn = dep = empty = 0
    en_samples = []
    dep_samples = []
    empty_ids = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = ENTRY_RE.search(line)
            if not m:
                continue
            total += 1
            qid = int(m.group(1))
            name = unescape(m.group(2))
            kind = classify(name)
            if kind == 'cn': cn += 1
            elif kind == 'dep':
                dep += 1
                if len(dep_samples) < 10:
                    dep_samples.append((qid, name))
            elif kind == 'en':
                en += 1
                if len(en_samples) < 10:
                    en_samples.append((qid, name))
            elif kind == 'empty':
                empty += 1
                if len(empty_ids) < 10:
                    empty_ids.append(qid)
    print(f"== {os.path.basename(path)} ==")
    print(f"  total={total}  cn={cn} ({cn*100/max(total,1):.1f}%)  en={en}  dep={dep}  empty={empty}")
    if en_samples:
        print(f"  EN samples: {en_samples[:5]}")
    if dep_samples:
        print(f"  DEP samples: {dep_samples[:5]}")
    if empty_ids:
        print(f"  EMPTY ids: {empty_ids[:5]}")

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in ['UnitData.lua', 'ItemData.lua', 'SpellData_Epoch.lua',
              'QuestCN_Data.lua', 'EpochQuestData.lua', 'CallBoardData.lua']:
        p = os.path.join(root, 'Data', f)
        if os.path.exists(p):
            audit(p)
