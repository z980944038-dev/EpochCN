#!/usr/bin/env python3
"""
双向同步 ObjectiveNameData.lua 与 UnitData/ItemData/pfQuest-epoch enUS：

场景：
  1. UnitData 已经有"[id] = {中文名, ...}"，而 pfQuest-epoch enUS 有"[id] = 英文名"，
     那么 "英文名 → 中文名" 应该存在于 ObjectiveNameData（供 Tooltip 翻译 NPC 对话框）。
  2. 对 UnitData/ItemData 中仍为英文的条目，若 ObjectiveNameData 里"英文→中文"存在
     且与其他来源一致，则回填为中文。

产出：在 ObjectiveNameData.lua 末尾追加一段"-- From UnitData/ItemData sync"。
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "pfquest_epoch"
DATA = ROOT / "Data"


def unesc(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def has_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s or "")

def is_english(s):
    return bool(s) and bool(re.search(r"[A-Za-z]", s)) and not has_cjk(s)


ID_ROW_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"')

def load_id_map(path: Path):
    if not path.exists():
        return {}
    m = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            hit = ID_ROW_RE.search(line)
            if hit:
                m[int(hit.group(1))] = unesc(hit.group(2))
    return m


def load_entry_map(path: Path):
    """Load our [id]={"name",...} data files -> { id: name }"""
    m = {}
    if not path.exists():
        return m
    entry_re = re.compile(r'\[(\d+)\]\s*=\s*\{\s*"((?:[^"\\]|\\.)*)"')
    with open(path, encoding="utf-8") as f:
        for line in f:
            hit = entry_re.search(line)
            if hit:
                m[int(hit.group(1))] = unesc(hit.group(2))
    return m


DEPRECATED_RE = re.compile(
    r'\[UNUSED\]|Deprecated|^OLDDwarven|^OLD[A-Z]|\(TEST\)|\bTEST\b|'
    r'<UNUSED|<TXT>|<NYI>|<TEST>|^Monster - |PLACEHOLDER|^Placeholder|^\[DND\]|^Blank$'
)


def main():
    # Load ObjectiveNameData (existing en → zh map)
    obj_path = DATA / "ObjectiveNameData.lua"
    obj_text = obj_path.read_text(encoding="utf-8")
    name_re = re.compile(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"')
    existing = {}
    for hit in name_re.finditer(obj_text):
        en = unesc(hit.group(1))
        zh = unesc(hit.group(2))
        if en and zh and en not in existing:
            existing[en] = zh
    print(f"ObjectiveNameData currently has {len(existing)} entries.")

    # Load enUS sources
    en_units = load_id_map(CACHE / "units-enUS.lua")
    en_items = load_id_map(CACHE / "items-enUS.lua")

    # Load our CN data (cn name by id)
    cn_units = load_entry_map(DATA / "UnitData.lua")
    cn_items = load_entry_map(DATA / "ItemData.lua")

    # 1) For each Epoch-reference id, if enUS and our CN are both non-empty
    #    and don't match, add "enUS -> CN" to ObjectiveNameData
    new_entries = {}

    def add(en, zh, source):
        if not en or not zh:
            return
        if DEPRECATED_RE.search(en):
            return
        if en in existing or en in new_entries:
            return
        if en == zh:
            return
        if not has_cjk(zh):
            return
        new_entries[en] = zh

    added_units = 0
    for eid, en in en_units.items():
        cn = cn_units.get(eid)
        if not cn or not has_cjk(cn):
            continue
        if DEPRECATED_RE.search(cn):
            continue
        if en not in existing and en not in new_entries and has_cjk(cn) and en != cn:
            new_entries[en] = cn
            added_units += 1

    added_items = 0
    for eid, en in en_items.items():
        cn = cn_items.get(eid)
        if not cn or not has_cjk(cn):
            continue
        if DEPRECATED_RE.search(cn):
            continue
        if en not in existing and en not in new_entries and has_cjk(cn) and en != cn:
            new_entries[en] = cn
            added_items += 1

    print(f"New NPC name mappings: {added_units}")
    print(f"New item name mappings: {added_items}")
    print(f"Total new entries to add: {len(new_entries)}")

    if not new_entries:
        return

    # Append to ObjectiveNameData before the final `}`
    # File ends with:   }\n\nfunction LoadEpochCNObjectiveNameData()\n...
    anchor = re.compile(r"\n\}\s*\n\s*function\s+LoadEpochCNObjectiveNameData", re.S)
    block_lines = ["", "  -- Auto-synced from UnitData/ItemData × pfQuest-epoch enUS"]
    for en, zh in sorted(new_entries.items()):
        block_lines.append(f'  ["{esc(en)}"] = "{esc(zh)}",')
    block = "\n".join(block_lines)

    new_obj_text, n = anchor.subn(block + "\n}\n\nfunction LoadEpochCNObjectiveNameData", obj_text, count=1)
    if n == 0:
        print("WARNING: can't find anchor, skipping.")
        return
    obj_path.write_text(new_obj_text, encoding="utf-8")
    print(f"[OK] appended {len(new_entries)} entries to ObjectiveNameData.lua")


if __name__ == "__main__":
    main()
