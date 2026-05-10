#!/usr/bin/env python3
"""分析 UnitData 和 ItemData 中剩余的英文条目分布，找出共性以便批量翻译。"""
import re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENTRY_RE = re.compile(r'\[(\d+)\]\s*=\s*\{\s*"((?:[^"\\]|\\.)*)"')

def unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")

def contains_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s)

def iter_entries(path):
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = ENTRY_RE.search(line)
            if m:
                yield int(m.group(1)), unescape(m.group(2))

def has_prefix(name, *prefixes):
    return any(name.startswith(p) for p in prefixes)

def analyze(path):
    entries = [(i, n) for i, n in iter_entries(path) if n and not contains_cjk(n) and re.search(r'[A-Za-z]', n)]
    print(f"\n== {os.path.basename(path)} has {len(entries)} English entries ==")

    # Bucketize
    buckets = collections.Counter()
    for _, n in entries:
        if has_prefix(n, '[UNUSED]', '<UNUSED>', 'Deprecated', 'OLDDwarven',
                     'OLD ', '(Deprecated)', '<TXT>', '<TEST>', '<NYI>',
                     'Monster -', 'TEST ', 'test '):
            buckets['PLACEHOLDER'] += 1
        elif re.search(r'\(.*DEPRECATED.*\)', n, re.IGNORECASE):
            buckets['PLACEHOLDER'] += 1
        elif re.search(r'\bTEST\b', n, re.IGNORECASE):
            buckets['PLACEHOLDER'] += 1
        elif 'Dummy' in n:
            buckets['DUMMY'] += 1
        elif 'trigger' in n.lower() or 'bunny' in n.lower():
            buckets['TRIGGER'] += 1
        else:
            buckets['REAL'] += 1

    for k, v in buckets.most_common():
        print(f"  {k:15s} {v:6d}")

    real = [(i, n) for i, n in entries
            if not has_prefix(n, '[UNUSED]', '<UNUSED>', 'Deprecated',
                            'OLDDwarven', 'OLD ', '<TXT>', '<TEST>',
                            '<NYI>', 'Monster -', 'TEST ', 'test ')
            and 'Dummy' not in n
            and 'trigger' not in n.lower()
            and 'bunny' not in n.lower()
            and not re.search(r'\bTEST\b', n, re.IGNORECASE)]

    print(f"\n  REAL samples (first 30):")
    for i, n in real[:30]:
        print(f"    [{i:6d}] {n}")

analyze(os.path.join(ROOT, 'Data', 'UnitData.lua'))
analyze(os.path.join(ROOT, 'Data', 'ItemData.lua'))
analyze(os.path.join(ROOT, 'Data', 'QuestCN_Data.lua'))
