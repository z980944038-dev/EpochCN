#!/usr/bin/env python3
"""
用 ObjectiveNameData.lua 中的英→中映射，回填 UnitData.lua / ItemData.lua /
QuestCN_Data.lua / EpochQuestData.lua / CallBoardData.lua 中仍为英文的条目。

规则：
- 只替换"整条名字是英文"的条目。
- 跳过 Deprecated / [UNUSED] / TEST / <TXT> / <NYI> / Monster / Blank 等占位。
- 如果 ObjectiveNameData 中没有精确匹配，尝试去掉前缀（如 "Deprecated "）。
- 每处改动都打印到日志，方便人工审阅。

运行：python3 Tools/backfill_from_objectives.py
"""
import re, sys, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ_PATH = os.path.join(ROOT, 'Data', 'ObjectiveNameData.lua')

# 加载英→中映射
OBJ_RE = re.compile(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"')
def unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")
def escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def contains_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s)

def load_objective_map():
    m = {}
    with open(OBJ_PATH, encoding='utf-8') as f:
        for line in f:
            hit = OBJ_RE.search(line)
            if not hit: continue
            en = unescape(hit.group(1))
            cn = unescape(hit.group(2))
            if not en or not cn: continue
            if en == cn: continue
            if not contains_cjk(cn): continue
            # 同一 en 只保留第一次出现
            m.setdefault(en, cn)
    return m

# [id] = {"name", ...}  第一个字符串
ENTRY_RE = re.compile(r'(\[\d+\]\s*=\s*\{\s*)"((?:[^"\\]|\\.)*)"')

SKIP_PATTERNS = [
    r'\[UNUSED\]',
    r'Deprecated',
    r'^OLDDwarven',
    r'^OLD[A-Z]',
    r'\(TEST\)',
    r' TEST\b',
    r'<UNUSED',
    r'<TXT>',
    r'<NYI>',
    r'<TEST>',
    r'^Monster - ',
    r'^Blank$',
    r'PLACEHOLDER',
]
SKIP_RE = re.compile('|'.join(SKIP_PATTERNS))

def should_skip(name):
    return bool(SKIP_RE.search(name))

def is_english_only(s):
    return bool(s) and not contains_cjk(s) and re.search(r'[A-Za-z]', s)

def backfill_file(path, obj_map, stats):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    out = []
    changed = 0
    file_stats = {'total': 0, 'english': 0, 'skipped': 0, 'translated': 0}
    def replace(m):
        prefix, name = m.group(1), unescape(m.group(2))
        file_stats['total'] += 1
        if not is_english_only(name):
            return m.group(0)
        file_stats['english'] += 1
        if should_skip(name):
            file_stats['skipped'] += 1
            return m.group(0)
        cn = obj_map.get(name)
        if not cn:
            # 去掉末尾数字/后缀再试一次
            trimmed = re.sub(r'\s+\d+$', '', name)
            if trimmed != name:
                cn = obj_map.get(trimmed)
        if cn and cn != name and contains_cjk(cn):
            file_stats['translated'] += 1
            return f'{prefix}"{escape(cn)}"'
        return m.group(0)
    new_text = ENTRY_RE.sub(replace, text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
    print(f"  {os.path.basename(path)}: total={file_stats['total']} english_left={file_stats['english']} translated={file_stats['translated']} skipped={file_stats['skipped']}")
    stats[path] = file_stats
    return file_stats['translated']

def main():
    print("Loading ObjectiveNameData…")
    obj_map = load_objective_map()
    print(f"  loaded {len(obj_map)} en->cn mappings")

    stats = {}
    total_changed = 0
    for fname in ['UnitData.lua', 'ItemData.lua', 'QuestCN_Data.lua',
                  'EpochQuestData.lua', 'CallBoardData.lua']:
        p = os.path.join(ROOT, 'Data', fname)
        if not os.path.exists(p): continue
        total_changed += backfill_file(p, obj_map, stats)

    print(f"\nTotal translations applied: {total_changed}")

if __name__ == '__main__':
    main()
