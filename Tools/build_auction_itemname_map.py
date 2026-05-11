#!/usr/bin/env python3
"""
生成 Data/ItemNameMap.lua —— 拍卖行中英双向映射专用数据表。

数据来源（按 ID 对齐以保证精确）：
  1. pfQuest classic enUS + zhCN (items-enUS-classic.lua, items-zhCN.lua)
  2. pfQuest-epoch enUS (items-enUS.lua) × 我们的 ItemData.lua 的中文
  3. EpochHeadData 的 ["英文"] = "中文" 对
  4. Overrides.englishItems

输出：EpochCN_ItemNameMap = { [英文] = "中文", ... }
只保留英文键非空、中文值非空、且两者都不同的条目。
"""
from __future__ import annotations
import re
import json
from pathlib import Path
from html import unescape
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "pfquest_epoch"
DATA = ROOT / "Data"


def unesc(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def has_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s or "")

def is_english_only(s):
    return bool(s) and bool(re.search(r"[A-Za-z]", s)) and not has_cjk(s)


ID_ROW_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"')
# Questie 格式: [id] = {'name',...} 用单引号
QUESTIE_ROW_RE = re.compile(r"\[(\d+)\]\s*=\s*\{'((?:[^'\\]|\\.)*)'")
ENTRY_RE = re.compile(r'\[(\d+)\]\s*=\s*\{\s*"((?:[^"\\]|\\.)*)"')
NAME_PAIR_RE = re.compile(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"')


def load_id_map(path):
    m = {}
    if not path.exists(): return m
    for line in path.open(encoding="utf-8"):
        hit = ID_ROW_RE.search(line)
        if hit: m[int(hit.group(1))] = unesc(hit.group(2))
    return m


def load_questie_item_map(path):
    """Load Questie format [id] = {'name',...}."""
    m = {}
    if not path.exists(): return m
    for line in path.open(encoding="utf-8"):
        hit = QUESTIE_ROW_RE.search(line)
        if hit:
            name = hit.group(2).replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
            m[int(hit.group(1))] = name
    return m


def load_entry_map(path):
    m = {}
    if not path.exists(): return m
    for line in path.open(encoding="utf-8"):
        hit = ENTRY_RE.search(line)
        if hit: m[int(hit.group(1))] = unesc(hit.group(2))
    return m


def load_name_pairs(path):
    m = {}
    if not path.exists(): return m
    text = path.read_text(encoding="utf-8")
    for hit in NAME_PAIR_RE.finditer(text):
        m[unesc(hit.group(1))] = unesc(hit.group(2))
    return m


def load_json_item_id_map(path):
    m = {}
    if not path.exists(): return m
    rows = json.loads(path.read_text(encoding="utf-8"))
    for row in rows:
        try:
            item_id = int(row.get("id"))
        except (TypeError, ValueError):
            continue
        name = row.get("name")
        if name:
            m[item_id] = name
    return m


EPOCHHEAD_ITEM_RE = re.compile(
    r'data-item-id="(?P<id>\d+)".{0,500}?'
    r'<span class="font-medium [^"]+">(?P<name>.*?)</span>',
    re.S,
)
EPOCHHEAD_NEXT_RE = re.compile(r'href="(?P<href>\?page=\d+)">\s*Next', re.I)


def load_epochhead_item_id_map(path, pages=25):
    cached = load_json_item_id_map(path)
    if cached:
        return cached

    seen = {}
    url = "https://epochhead.com/items"
    for _ in range(pages):
        req = Request(url, headers={"User-Agent": "EpochCN-localization-sync/0.1"})
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", "replace")
        for match in EPOCHHEAD_ITEM_RE.finditer(html):
            item_id = int(match.group("id"))
            name = unescape(re.sub(r"<.*?>", "", match.group("name"))).strip()
            if name and item_id not in seen:
                seen[item_id] = name
        next_match = EPOCHHEAD_NEXT_RE.search(html)
        if not next_match:
            break
        url = urljoin("https://epochhead.com/items", next_match.group("href"))

    if seen:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            rows = [{"id": iid, "name": name} for iid, name in sorted(seen.items())]
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass
    return seen


# 排除不该进搜索映射的占位/废弃/测试条目
SKIP_NAME_RE = re.compile(
    r'\[UNUSED\]|Deprecated|^OLD[A-Z]|\(TEST\)|\bTEST\b|<UNUSED|<TXT>|<NYI>|'
    r'<TEST>|^Monster - |PLACEHOLDER|^Placeholder|^\[DND\]|^Blank$|'
    r'\(DEPRECATED\)|\(deprecated\)|^Unused\b|\(old\)|\(Old\)|DEBUG'
)

def is_skippable(english, chinese):
    if not english or not chinese: return True
    if not has_cjk(chinese): return True
    if english == chinese: return True
    if SKIP_NAME_RE.search(english): return True
    if SKIP_NAME_RE.search(chinese): return True
    return False


def main():
    pairs_en_to_zh = {}
    search_aliases = {}

    def add_pair(en, zh):
        if is_skippable(en, zh):
            return False
        if en not in pairs_en_to_zh:
            pairs_en_to_zh[en] = zh
            return True
        return False

    def add_alias(en, zh):
        if is_skippable(en, zh):
            return False
        if pairs_en_to_zh.get(en) != zh and zh not in search_aliases:
            search_aliases[zh] = en
            return True
        return False

    # 1) pfQuest classic: 同 ID 英文 + 中文
    classic_en = load_id_map(CACHE / "items-enUS-classic.lua")
    classic_zh = load_id_map(CACHE / "items-zhCN.lua")
    cnt1 = 0
    for iid, en in classic_en.items():
        zh = classic_zh.get(iid)
        if not zh: continue
        if add_pair(en, zh):
            cnt1 += 1
    print(f"[1] classic pfQuest: +{cnt1}")

    # 1b) pfQuest TBC (covers TBC + WotLK through tbc dataset)
    tbc_en = load_id_map(CACHE / "items-enUS-tbc.lua")
    tbc_zh = load_id_map(CACHE / "items-zhCN-tbc.lua")
    cnt1b = 0
    for iid, en in tbc_en.items():
        zh = tbc_zh.get(iid)
        if not zh: continue
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt1b += 1
    print(f"[1b] TBC/WotLK pfQuest: +{cnt1b}")

    # 2) pfQuest-epoch enUS × our ItemData.lua CN (按 ID)
    epoch_en = load_id_map(CACHE / "items-enUS.lua")
    our_items = load_entry_map(DATA / "ItemData.lua")
    cnt2 = 0
    for iid, en in epoch_en.items():
        zh = our_items.get(iid)
        if not zh: continue
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt2 += 1
    print(f"[2] pfQuest-epoch × our ItemData: +{cnt2}")

    # 2b) Questie-Epoch WotLK itemDB enUS × our ItemData.lua CN (按 ID)
    #     覆盖 WotLK 专属物品（Saronite, Frostweave, Titansteel 等）
    questie_en = load_questie_item_map(CACHE / "questie-wotlk-itemdb.lua")
    cnt2b = 0
    for iid, en in questie_en.items():
        zh = our_items.get(iid)
        if not zh: continue
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt2b += 1
    print(f"[2b] Questie WotLK × our ItemData: +{cnt2b}")

    # 3) 经典 pfQuest enUS × 我们的 ItemData (如果 ID 重叠也能补)
    # 2c) EpochHead scraped item IDs x our ItemData CN.
    #     This catches Project Epoch items whose Chinese wording in ItemData
    #     differs slightly from the curated EpochHead name pair.
    epochhead_item_en = load_epochhead_item_id_map(CACHE / "epochhead-items.json")
    cnt2c = 0
    for iid, en in epochhead_item_en.items():
        zh = our_items.get(iid)
        if not zh: continue
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt2c += 1
    print(f"[2c] EpochHead items x our ItemData: +{cnt2c}")

    cnt3 = 0
    for iid, en in classic_en.items():
        zh = our_items.get(iid)
        if not zh: continue
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt3 += 1
    print(f"[3] classic enUS × our ItemData: +{cnt3}")

    # 4) EpochHeadData 名字对
    ehd_pairs = load_name_pairs(DATA / "EpochHeadData.lua")
    cnt4 = 0
    for en, zh in ehd_pairs.items():
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt4 += 1
    print(f"[4] EpochHeadData name pairs: +{cnt4}")

    # 5) Overrides.englishItems
    override_en = load_name_pairs(DATA / "Overrides.lua")
    cnt5 = 0
    for en, zh in override_en.items():
        add_alias(en, zh)
        if add_pair(en, zh):
            cnt5 += 1
    print(f"[5] Overrides.englishItems: +{cnt5}")

    print(f"\nTotal entries: {len(pairs_en_to_zh)}")
    print(f"Search aliases: {len(search_aliases)}")

    # ObjectiveNameData 已经作为 runtime 兜底在 AuctionHouse.lua 里使用，不重复写入
    # 避免 ItemNameMap 文件过大。

    # 写出
    out = DATA / "ItemNameMap.lua"
    with out.open("w", encoding="utf-8") as f:
        f.write("-- Generated by Tools/build_auction_itemname_map.py (do not edit).\n")
        f.write("-- Sources: pfQuest classic (enUS × zhCN), pfQuest-epoch enUS, ItemData, EpochHeadData, Overrides.\n\n")
        f.write("function LoadEpochCNItemNameMap()\n")
        f.write("  EpochCN_ItemNameMap = {\n")
        for en, zh in sorted(pairs_en_to_zh.items()):
            f.write(f'    ["{esc(en)}"] = "{esc(zh)}",\n')
        f.write("  }\n")
        f.write("  EpochCN_ItemSearchAliases = {\n")
        for zh, en in sorted(search_aliases.items()):
            f.write(f'    ["{esc(zh)}"] = "{esc(en)}",\n')
        f.write("  }\n")
        f.write("  local function IsSkippedSearchAlias(english)\n")
        f.write("    return string.find(english, \"DEPRECATED\", 1, true)\n")
        f.write("      or string.find(english, \"deprecated\", 1, true)\n")
        f.write("      or string.find(english, \"[UNUSED]\", 1, true)\n")
        f.write("      or string.find(english, \"(TEST)\", 1, true)\n")
        f.write("      or string.find(english, \"<TEST>\", 1, true)\n")
        f.write("      or string.find(english, \"<NYI>\", 1, true)\n")
        f.write("      or string.find(english, \"<TXT>\", 1, true)\n")
        f.write("      or string.find(english, \"OLDDwarven\", 1, true)\n")
        f.write("      or string.sub(english, 1, 4) == \"OLD \"\n")
        f.write("      or string.find(english, \"PLACEHOLDER\", 1, true)\n")
        f.write("      or string.find(english, \"Placeholder\", 1, true)\n")
        f.write("      or string.find(english, \"(old)\", 1, true)\n")
        f.write("      or string.find(english, \"(DEPRECATED)\", 1, true)\n")
        f.write("  end\n")
        f.write("  for english, chinese in pairs(EpochCN_ItemNameMap) do\n")
        f.write("    local current = EpochCN_ItemSearchAliases[chinese]\n")
        f.write("    if not IsSkippedSearchAlias(english) and (current == nil or IsSkippedSearchAlias(current)) then\n")
        f.write("      EpochCN_ItemSearchAliases[chinese] = english\n")
        f.write("    end\n")
        f.write("  end\n")
        f.write("end\n")
    print(f"[OK] wrote {out}")


if __name__ == "__main__":
    main()
