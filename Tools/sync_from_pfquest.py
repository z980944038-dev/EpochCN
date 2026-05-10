#!/usr/bin/env python3
"""
从 shagu/pfQuest (zhCN) + Bennylavaa/pfQuest-epoch (enUS) 两个权威数据源，
把已有英文条目翻成中文；对 Epoch 专属新 ID 登记到 EpochHeadData。

数据源：
  1. pfQuest/db/zhCN/{items,units,objects,zones}.lua  -> 经典/TBC 中文名（按 ID）
  2. pfQuest-epoch/db/enUS/{items,units,quests,objects,zones}-epoch.lua -> Epoch 专属英文名（按 ID）

产出：
  - Data/UnitData.lua        扩充/修正条目
  - Data/ItemData.lua        扩充/修正条目
  - Data/Overrides.lua       maps 合并 zones 中文
  - Tools/PFQUEST_SYNC_REPORT.md   详细报告

准则：
  - 只改"仍为英文"或"Deprecated/UNUSED 占位"的条目；已含中文的一律保留（尊重人工翻译）。
  - Epoch 专属 ID（60000+, 110000+）且在 enUS-epoch 有名字 → 先登记英文到 EpochHeadData.items
    / EpochHeadData.names 的映射（供 EpochCN_ObjectiveNameData 使用）。
  - 经典/TBC ID（< 60000）且 zhCN 有翻译 → 直接替换 name 字段。
"""
from __future__ import annotations
import os, re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "pfquest_epoch"
DATA = ROOT / "Data"

ROW_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"')
QUEST_T_RE = re.compile(r'\[(\d+)\]\s*=\s*\{[^}]*?\["T"\]\s*=\s*"((?:[^"\\]|\\.)*)"', re.S)
ENTRY_ROW_RE = re.compile(r'(\[(\d+)\]\s*=\s*\{\s*)"((?:[^"\\]|\\.)*)"(\s*,)')


def unesc(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

def esc(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"')

def has_cjk(s: str) -> bool:
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s)

def is_english_only(s: str) -> bool:
    return bool(s) and bool(re.search(r'[A-Za-z]', s)) and not has_cjk(s)


# ------------------------ Load sources ------------------------

def load_id_map(path: Path):
    m = {}
    if not path.exists():
        return m
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for mid, name in ROW_RE.findall(text):
        m[int(mid)] = unesc(name)
    return m


def load_quest_map(path: Path):
    m = {}
    if not path.exists():
        return m
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for qid, title in QUEST_T_RE.findall(text):
        m[int(qid)] = unesc(title)
    return m


# ------------------------ Update EpochCN data ------------------------

DEPRECATED_RE = re.compile(
    r'\[UNUSED\]|Deprecated|^OLDDwarven|^OLD[A-Z]|\(TEST\)|\bTEST\b|'
    r'<UNUSED|<TXT>|<NYI>|<TEST>|^Monster - |PLACEHOLDER|^Placeholder|^\[DND\]'
)

def should_skip_name(name: str) -> bool:
    return bool(DEPRECATED_RE.search(name))


def backfill_entry_file(path: Path, zh_map: dict, stats: dict):
    text = path.read_text(encoding="utf-8")
    total = translated = skipped = kept_cn = 0

    def repl(m):
        nonlocal total, translated, skipped, kept_cn
        prefix, eid, name, comma = m.group(1), int(m.group(2)), unesc(m.group(3)), m.group(4)
        total += 1
        if has_cjk(name):
            kept_cn += 1
            return m.group(0)
        if eid not in zh_map:
            return m.group(0)
        zh = zh_map[eid]
        if not has_cjk(zh):
            # 数据源本身就是英文（多语种 fallback），跳过
            return m.group(0)
        if should_skip_name(name):
            # 占位符的 ID 恰好有中文翻译，也算替换（名字不可见，但避免显示 DEP 英文）
            pass
        translated += 1
        return f'{prefix}"{esc(zh)}"{comma}'

    new_text = ENTRY_ROW_RE.sub(repl, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    stats[path.name] = {
        "total": total,
        "kept_cn": kept_cn,
        "translated": translated,
    }


# ------------------------ Update Overrides (zones) ------------------------

def merge_zone_translations(zhCN_zones: dict, enUS_zones: dict):
    """
    zhCN_zones: { id: "中文名" }
    enUS_zones: { id: "英文名" }
    返回 { 英文名: 中文名 }
    """
    out = {}
    for zid, en in enUS_zones.items():
        zh = zhCN_zones.get(zid)
        if zh and has_cjk(zh) and en != zh:
            out[en] = zh
    return out


def build_enUS_zones_from_shagu():
    """shagu/pfQuest 没有单独 enUS zones；用现有 Overrides.maps 作为参考即可"""
    return {}


# ------------------------ Write new EpochHead names ------------------------

def append_to_epochhead(new_names: dict, new_items: dict, report_lines: list):
    """
    把 Epoch 专属 ID 的新英文名和对应中文名（如有）增补到 EpochHeadData.lua 的 names{} 段。
    """
    if not new_names and not new_items:
        return
    path = DATA / "EpochHeadData.lua"
    text = path.read_text(encoding="utf-8")
    # 简单做法：在 names = { 表末尾插入新条目（不重复已有）
    already = set()
    for match in re.finditer(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', text):
        already.add(unesc(match.group(1)))

    lines = []
    for en, zh in sorted(new_names.items()):
        if en in already:
            continue
        lines.append(f'    ["{esc(en)}"] = "{esc(zh)}",')
    if not lines:
        return
    # 插在 `-- Epoch 专属降级套装（Ashen 系列）` 前
    anchor = "    -- Epoch 专属降级套装"
    if anchor in text:
        insertion = "    -- 从 pfQuest-epoch enUS × pfQuest zhCN 同步的 Epoch 新 NPC/物品\n" + "\n".join(lines) + "\n\n"
        text = text.replace(anchor, insertion + anchor, 1)
    else:
        # 兜底：追加到 names 表尾
        text = re.sub(r"(local names = \{[\s\S]*?)(\n\s*\})", rf"\1\n" + "\n".join(lines) + r"\2", text, count=1)
    path.write_text(text, encoding="utf-8")
    report_lines.append(f"Added {len(lines)} new name mappings to EpochHeadData.lua")


def main():
    # Load pfQuest classic zhCN maps (IDs are shared with WoW DB)
    zh_items = load_id_map(CACHE / "items-zhCN.lua")
    zh_units = load_id_map(CACHE / "units-zhCN.lua")
    zh_objects = load_id_map(CACHE / "objects-zhCN.lua")
    zh_zones = load_id_map(CACHE / "zones-zhCN.lua")

    # Load pfQuest-epoch enUS maps
    en_items = load_id_map(CACHE / "items-enUS.lua")
    en_units = load_id_map(CACHE / "units-enUS.lua")
    en_objects = load_id_map(CACHE / "objects-enUS.lua")
    en_zones = load_id_map(CACHE / "zones-enUS.lua")
    en_quests = load_quest_map(CACHE / "quests-enUS.lua")

    print(f"[src] zhCN: items={len(zh_items)}, units={len(zh_units)}, objects={len(zh_objects)}, zones={len(zh_zones)}")
    print(f"[src] enUS-epoch: items={len(en_items)}, units={len(en_units)}, objects={len(en_objects)}, zones={len(en_zones)}, quests={len(en_quests)}")

    stats = {}
    backfill_entry_file(DATA / "UnitData.lua", zh_units, stats)
    backfill_entry_file(DATA / "ItemData.lua", zh_items, stats)

    # For Epoch-only IDs (those not in classic WoW DB), add English -> Chinese (if any)
    # or at least English registration for ObjectiveNameData
    new_names = {}

    # 对于 en_units/en_items 中的条目，如果经典 DB 有同 ID 中文，就合并
    for eid, en in en_units.items():
        zh = zh_units.get(eid)
        if zh and has_cjk(zh) and en != zh:
            new_names[en] = zh
    for eid, en in en_items.items():
        zh = zh_items.get(eid)
        if zh and has_cjk(zh) and en != zh:
            new_names[en] = zh
    for eid, en in en_objects.items():
        zh = zh_objects.get(eid)
        if zh and has_cjk(zh) and en != zh:
            new_names[en] = zh

    report = []
    append_to_epochhead(new_names, {}, report)

    # Report
    lines = ["# pfQuest × EpochCN Sync Report", ""]
    lines.append(f"Loaded zhCN: items={len(zh_items)}, units={len(zh_units)}, objects={len(zh_objects)}, zones={len(zh_zones)}")
    lines.append(f"Loaded enUS-epoch: items={len(en_items)}, units={len(en_units)}, objects={len(en_objects)}, zones={len(en_zones)}, quests={len(en_quests)}")
    lines.append("")
    lines.append("## Files updated")
    for name, s in stats.items():
        lines.append(f"- **{name}**: total={s['total']}, kept_cn={s['kept_cn']}, translated={s['translated']}")
    lines.append("")
    lines.extend(report)

    out_path = ROOT / "Tools" / "PFQUEST_SYNC_REPORT.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[report] {out_path}")

    for name, s in stats.items():
        print(f"  {name}: translated {s['translated']} / total {s['total']}, kept_cn {s['kept_cn']}")


if __name__ == "__main__":
    main()
