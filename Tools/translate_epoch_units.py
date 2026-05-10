#!/usr/bin/env python3
"""
针对 pfQuest-epoch enUS 列出的 Epoch 专属 NPC / 物品，
对其中可直接翻译的条目按命名规则给出中文翻译，并写入 EpochHeadData。

策略：
1. 加载 pfQuest-epoch enUS 的 items/units/objects/quests。
2. 对每条英文，先查 shagu/pfQuest zhCN（按 ID）；若无，且经典 pfQuest 的 enUS
   里也有同 ID（说明是翻版经典 NPC），直接继承 zhCN。
3. 对 Epoch 全新 ID（classic zhCN 里没有），用常用英文词根查表翻译：
   - 常见 NPC 后缀（Miner, Scout, Healer, Guard, Adept, Priest, Apprentice,
     Footman, Recruit, Bouncer, Trainer, Vendor, Quartermaster...）
   - 怪物职业/种族名（Gnoll, Murloc, Kobold, Defias, Bandit, Raider...）
   - 阵营名（Horde, Alliance, Stormwind, Orgrimmar...）
4. 所有派生结果追加到 EpochHeadData.lua 的 names 表（已存在的条目跳过）。
"""
from __future__ import annotations
import os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "pfquest_epoch"
DATA = ROOT / "Data"

ROW_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"')


def unesc(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def load_id_map(path):
    m = {}
    if not path.exists():
        return m
    with open(path, encoding="utf-8") as f:
        for line in f:
            hit = ROW_RE.search(line)
            if hit:
                m[int(hit.group(1))] = unesc(hit.group(2))
    return m


def has_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s or "")


# --------------- 翻译词典 ---------------
# 通用词根翻译（词/短语 → 中文）
# 注意：只收录"真正描述角色身份/种族"的词。颜色、形容词、数字等脱离语境会
# 产生错误翻译（Silver → "银色的" 当独立 NPC 名字时无意义），已刻意排除。
WORD_MAP = {
    # 称谓 / 职业
    "Apprentice": "学徒",
    "Journeyman": "熟练工",
    "Adept": "大师",
    "Trainer": "训练师",
    "Vendor": "商人",
    "Merchant": "商贩",
    "Quartermaster": "军需官",
    "Innkeeper": "旅店老板",
    "Barkeep": "酒保",
    "Flight Master": "飞行管理员",
    "Auctioneer": "拍卖师",
    "Banker": "银行家",
    "Bouncer": "保镖",
    "Recruit": "新兵",
    "Footman": "步兵",
    "Guard": "卫兵",
    "Guardian": "守护者",
    "Sentinel": "哨兵",
    "Scout": "侦察兵",
    "Warrior": "战士",
    "Priest": "牧师",
    "Mage": "法师",
    "Shaman": "萨满",
    "Rogue": "潜行者",
    "Hunter": "猎人",
    "Warlock": "术士",
    "Paladin": "圣骑士",
    "Druid": "德鲁伊",
    "Deathguard": "死亡卫士",
    "Lieutenant": "副队长",
    "Captain": "队长",
    "Marshal": "治安官",
    "Commander": "指挥官",
    "General": "将军",
    "Sergeant": "中士",
    "Corporal": "下士",
    "Champion": "勇士",
    "Chieftain": "酋长",
    "Warlord": "督军",
    "Overseer": "监工",
    "Foreman": "工头",
    "Peasant": "农夫",
    "Peon": "苦工",
    "Miner": "矿工",
    "Thug": "暴徒",
    "Bandit": "盗贼",
    "Cutthroat": "刺客",
    "Runt": "子嗣",
    "Brute": "野蛮人",
    "Spirit Healer": "灵魂医者",
    # 种族
    "Gnoll": "豺狼人",
    "Murloc": "鱼人",
    "Kobold": "狗头人",
    "Ogre": "食人魔",
    "Satyr": "萨特",
    "Harpy": "鹰身人",
    "Centaur": "半人马",
    "Naga": "纳迦",
    "Raptor": "迅猛龙",
    "Dragonkin": "龙人",
    "Dragonspawn": "龙人",
    "Whelp": "雏龙",
    "Whelpling": "雏龙",
    "Drake": "幼龙",
    "Dragon": "龙",
    "Demon": "恶魔",
    "Imp": "小鬼",
    "Felhunter": "魔犬",
    "Succubus": "魅魔",
    "Voidwalker": "虚空行者",
    "Infernal": "地狱火",
    "Skeleton": "骷髅",
    "Zombie": "僵尸",
    "Ghoul": "食尸鬼",
    "Abomination": "憎恶",
    "Banshee": "女妖",
    "Ghost": "幽灵",
    # 职业修饰
    "Spellcaster": "施法者",
    "Caster": "施法者",
    "Geomancer": "风水师",
    "Necromancer": "通灵师",
    "Summoner": "召唤师",
    "Healer": "治疗者",
    "Berserker": "狂战士",
    "Assassin": "刺客",
    "Archer": "射手",
    "Gunner": "枪手",
    "Raider": "袭击者",
    "Forager": "觅食者",
    "Reaver": "劫掠者",
    "Enforcer": "打手",
    "Thief": "盗贼",
    "Looter": "掠夺者",
    # 阵营专有词
    "Defias": "迪菲亚",
    "Scarlet": "血色",
    "Forsaken": "被遗忘者",
    "Bloodsail": "血帆",
    "Syndicate": "辛迪加",
    # 前缀修饰（必须和后续词结合才合理）
    "Greater": "强大的",
    "Lesser": "次级",
    "Young": "年幼的",
    "Ancient": "远古的",
    "Elder": "年长的",
    "Wounded": "受伤的",
    "Injured": "受伤的",
    "Dying": "垂死的",
    "Savage": "野蛮",
    "Fierce": "凶猛的",
    "Wild": "野性的",
    "Haunted": "闹鬼的",
    "Cursed": "被诅咒的",
}

# 这些词根只能作为"修饰符"出现，不能单独成名
MODIFIER_ONLY = {
    "Greater", "Lesser", "Young", "Ancient", "Elder", "Wounded", "Injured",
    "Dying", "Savage", "Fierce", "Wild", "Haunted", "Cursed",
}


def translate_by_words(name: str) -> str | None:
    """尝试用词根翻译一个名字。所有单词/短语都必须能翻译才成功。
    质量控制：
      - 至少包含一个非 modifier 词（否则单独一个"年幼的"没意义）。
      - 单词数 >= 2 才信任（单词直译可能是人名）。
    """
    parts = name.split()
    if not parts or len(parts) < 2:
        return None
    out = []
    used_words = []
    i = 0
    while i < len(parts):
        matched = False
        for length in (3, 2, 1):
            if i + length > len(parts):
                continue
            phrase = " ".join(parts[i:i + length])
            if phrase in WORD_MAP:
                out.append(WORD_MAP[phrase])
                used_words.append(phrase)
                i += length
                matched = True
                break
        if not matched:
            return None

    # 至少要有一个非 modifier 词（即实体词）
    non_modifier = [w for w in used_words if w not in MODIFIER_ONLY]
    if not non_modifier:
        return None
    return "".join(out)


# --------------- 主流程 ---------------

def main():
    zh_units = load_id_map(CACHE / "units-zhCN.lua")
    zh_items = load_id_map(CACHE / "items-zhCN.lua")
    zh_objects = load_id_map(CACHE / "objects-zhCN.lua")
    en_units = load_id_map(CACHE / "units-enUS.lua")
    en_items = load_id_map(CACHE / "items-enUS.lua")
    en_objects = load_id_map(CACHE / "objects-enUS.lua")

    # 经典 enUS 用来做"同 ID 同名"校验 —— 防止 Epoch 重用 ID 导致误翻
    classic_en_units = load_id_map(CACHE / "units-enUS-classic.lua")
    classic_en_items = load_id_map(CACHE / "items-enUS-classic.lua")

    # Load existing EpochHeadData existing keys (already-translated English names)
    ehd_path = DATA / "EpochHeadData.lua"
    ehd_text = ehd_path.read_text(encoding="utf-8") if ehd_path.exists() else ""
    already_keys = set()
    for hit in re.finditer(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', ehd_text):
        already_keys.add(unesc(hit.group(1)))

    new_mappings = {}
    inherited_count = 0
    derived_count = 0
    skipped_id_mismatch = 0

    def consider(english, candidate_zh, kind):
        nonlocal inherited_count, derived_count
        if not english or not candidate_zh:
            return False
        if english in already_keys or english in new_mappings:
            return False
        if not has_cjk(candidate_zh):
            return False
        if english == candidate_zh:
            return False
        new_mappings[english] = candidate_zh
        if kind == "inherited":
            inherited_count += 1
        else:
            derived_count += 1
        return True

    # 1) Epoch ID 继承经典 zhCN，但需 classic enUS 与 Epoch enUS 同名
    for eid, en in en_units.items():
        zh = zh_units.get(eid)
        if not (zh and has_cjk(zh)):
            continue
        classic_en = classic_en_units.get(eid)
        # 同 ID 同名才继承；若 classic 没有此 ID，或名字不同，跳过
        if classic_en == en:
            consider(en, zh, "inherited")
        elif classic_en is not None and classic_en != en:
            skipped_id_mismatch += 1

    for eid, en in en_items.items():
        zh = zh_items.get(eid)
        if not (zh and has_cjk(zh)):
            continue
        classic_en = classic_en_items.get(eid)
        if classic_en == en:
            consider(en, zh, "inherited")
        elif classic_en is not None and classic_en != en:
            skipped_id_mismatch += 1

    # objects 没有 classic enUS 映射，稳妥起见不做 ID 继承（objects 名字很通用）

    # 2) 对仍为英文的 units，尝试词根翻译
    for eid, en in en_units.items():
        if en in already_keys or en in new_mappings:
            continue
        zh = translate_by_words(en)
        if zh:
            consider(en, zh, "derived")

    # 3) items 也试，但更保守（避免装备误翻）
    for eid, en in en_items.items():
        if en in already_keys or en in new_mappings:
            continue
        # 只翻译单词数 <= 2 的简单物品名
        if len(en.split()) <= 2:
            zh = translate_by_words(en)
            if zh:
                consider(en, zh, "derived")

    print(f"Inherited from classic zhCN (same ID & same enUS name): {inherited_count}")
    print(f"Derived by word-root translation: {derived_count}")
    print(f"Skipped due to Epoch ID-name mismatch: {skipped_id_mismatch}")
    print(f"Total new mappings: {len(new_mappings)}")

    # 写入 EpochHeadData.lua：在 names = { ... } 末尾新增一段
    if new_mappings:
        lines = []
        for en, zh in sorted(new_mappings.items()):
            lines.append(f'    ["{esc(en)}"] = "{esc(zh)}",')

        anchor = "    -- Epoch 专属降级套装"
        block = "    -- pfQuest-epoch × classic zhCN 同步 + 词根派生翻译\n" + "\n".join(lines) + "\n\n"
        if anchor in ehd_text:
            ehd_text = ehd_text.replace(anchor, block + anchor, 1)
        else:
            # Fallback：末尾注入
            ehd_text = re.sub(r"(local names = \{)", r"\1\n" + block.rstrip() + r"\n", ehd_text, count=1)

        ehd_path.write_text(ehd_text, encoding="utf-8")
        print(f"[OK] wrote {len(new_mappings)} entries to {ehd_path}")

    # 报告
    report_lines = [
        "# pfQuest-epoch × classic zhCN translation sync",
        "",
        f"- Inherited from classic zhCN (same ID & same enUS name): **{inherited_count}**",
        f"- Derived by word-root translation: **{derived_count}**",
        f"- Skipped due to Epoch ID reused with different name: **{skipped_id_mismatch}**",
        f"- Total new mappings: **{len(new_mappings)}**",
        "",
        "## Sample (first 30)",
        "",
        "| English | Chinese |",
        "| --- | --- |",
    ]
    for en, zh in sorted(new_mappings.items())[:30]:
        report_lines.append(f"| `{en}` | {zh} |")
    (ROOT / "Tools" / "PFQUEST_TRANSLATE_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
