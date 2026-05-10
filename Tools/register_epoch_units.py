#!/usr/bin/env python3
"""
把 pfQuest-epoch enUS 中存在、但 UnitData.lua 中缺失的 Epoch 专属 NPC ID
作为新条目注册到 UnitData.lua，同时尝试用词根翻译给出中文名（能翻则翻）。

结构：[id] = {"中文名或英文名", "", "pfQuest-epoch"}
"""
from __future__ import annotations
import re, sys
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


ID_ROW_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"')
ENTRY_RE = re.compile(r'\[(\d+)\]\s*=\s*\{')


def load_id_map(path: Path):
    m = {}
    if not path.exists():
        return m
    with open(path, encoding="utf-8") as f:
        for line in f:
            hit = ID_ROW_RE.search(line)
            if hit:
                m[int(hit.group(1))] = unesc(hit.group(2))
    return m


def load_existing_ids(path: Path):
    ids = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            hit = ENTRY_RE.search(line)
            if hit:
                ids.add(int(hit.group(1)))
    return ids


# Import word translator from translate_epoch_units.py
sys.path.insert(0, str(ROOT / "Tools"))
from translate_epoch_units import translate_by_words  # noqa: E402


def main():
    en_units = load_id_map(CACHE / "units-enUS.lua")
    en_items = load_id_map(CACHE / "items-enUS.lua")

    # --- Units ---
    unit_path = DATA / "UnitData.lua"
    existing_unit_ids = load_existing_ids(unit_path)
    print(f"UnitData.lua existing IDs: {len(existing_unit_ids)}")

    missing = [(eid, en) for eid, en in en_units.items() if eid not in existing_unit_ids]
    print(f"pfQuest-epoch NPC IDs missing from UnitData.lua: {len(missing)}")

    if missing:
        # Build lines like [id] = {"name","","pfQuest-epoch"},
        translated = 0
        lines = []
        for eid, en in sorted(missing):
            zh = translate_by_words(en)
            if zh and has_cjk(zh):
                display = zh
                translated += 1
            else:
                display = en
            lines.append(f'[{eid}] = {{"{esc(display)}","","pfQuest-epoch"}},')

        print(f"  word-root translated: {translated}")

        # Insert before final closing: find last `}` followed by `end`
        text = unit_path.read_text(encoding="utf-8")
        # Structure:
        #   function LoadTPCNUnitData()
        #     TPCN_UnitData = {
        #       [...entries...]
        #     }
        #   end
        m = re.search(r"(\n\s*\}\s*\n\s*end\s*\Z)", text)
        if not m:
            print("Cannot find insertion anchor in UnitData.lua, aborting.")
            return
        insertion = "\n-- Auto-registered from pfQuest-epoch enUS (Epoch-only IDs)\n" + "\n".join(lines) + "\n"
        text_new = text[:m.start()] + insertion + text[m.start():]
        unit_path.write_text(text_new, encoding="utf-8")
        print(f"  [OK] appended {len(lines)} entries to UnitData.lua")

    # --- Items ---
    item_path = DATA / "ItemData.lua"
    existing_item_ids = load_existing_ids(item_path)
    print(f"ItemData.lua existing IDs: {len(existing_item_ids)}")

    missing_items = [(eid, en) for eid, en in en_items.items() if eid not in existing_item_ids]
    print(f"pfQuest-epoch Item IDs missing from ItemData.lua: {len(missing_items)}")

    if missing_items:
        translated = 0
        lines = []
        for eid, en in sorted(missing_items):
            zh = translate_by_words(en) if len(en.split()) <= 3 else None
            if zh and has_cjk(zh):
                display = zh
                translated += 1
            else:
                display = en
            lines.append(f'[{eid}] = {{"{esc(display)}","","pfQuest-epoch"}},')

        print(f"  word-root translated: {translated}")

        text = item_path.read_text(encoding="utf-8")
        m = re.search(r"(\n\s*\}\s*\n\s*end\s*\Z)", text)
        if not m:
            print("Cannot find insertion anchor in ItemData.lua, aborting.")
            return
        insertion = "\n-- Auto-registered from pfQuest-epoch enUS (Epoch-only IDs)\n" + "\n".join(lines) + "\n"
        text_new = text[:m.start()] + insertion + text[m.start():]
        item_path.write_text(text_new, encoding="utf-8")
        print(f"  [OK] appended {len(lines)} entries to ItemData.lua")


if __name__ == "__main__":
    main()
