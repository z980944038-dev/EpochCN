#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DIR = ROOT / "SpellTranslation"
SOURCE = TRANSLATION_DIR / "spell_english_spellbook_priority.tsv"
DICT_NAMES = TRANSLATION_DIR / "dict_names.tsv"
DESC_DICT = TRANSLATION_DIR / "desc_dict.tsv"
TIP_DICT = TRANSLATION_DIR / "trans_tip_all.tsv"
ITEM_NAME_MAP = ROOT / "Data" / "ItemNameMap.lua"
OBJECTIVE_NAME_DATA = ROOT / "Data" / "ObjectiveNameData.lua"
OUT_SPELL = ROOT / "Data" / "SpellData_Epoch.lua"
OUT_RAW = ROOT / "Data" / "SpellRaw_Epoch.lua"
OUT_SEASON = ROOT / "Data" / "SpellData_Season.lua"


TOKEN_REPLACEMENTS = [
    (re.compile(r"\$l([^:;]*):([^;]*);"), lambda m: m.group(1) or m.group(2) or ""),
    (re.compile(r"\$\{[^{}]*\}"), ""),
    (re.compile(r"\$\([^)]*\}"), ""),
    (re.compile(r"\$\([^)]*\)"), ""),
    (re.compile(r"\$/[\d.]+;[A-Za-z]\d*"), ""),
    (re.compile(r"\$\*[\d.]+;[A-Za-z]\d*"), ""),
    (re.compile(r"\$\d+[A-Za-z]\d*"), ""),
    (re.compile(r"\$[A-Za-z_]+\d*"), ""),
    (re.compile(r"\$"), ""),
    (re.compile(r"\d{4,}m\d+/[-\d.]*"), ""),
    (re.compile(r"\bm\d+/[-\d.]+"), ""),
    (re.compile(r"/\d*\.?\d*;s\d+"), ""),
    (re.compile(r"0-m\d+/[\d.]+"), ""),
    (re.compile(r"\d{5,}s\d+"), ""),
    (re.compile(r"\d{5,}d\b"), ""),
    (re.compile(r"\d{4,}a\d+"), ""),
    (re.compile(r"@req:[^@]+@\s*"), ""),
]

SLASH_TOKEN = r"(?:/\d+;\d+[A-Za-z]\d*|/\d+;[A-Za-z]\d*|/\d+;)"
FORMULA_TOKEN = (
    r"(?:\$\{[^{}]*\}|\$\([^)]*\}|\$\([^)]*\)|"
    r"\$/[\d.]+;[A-Za-z]\d*|\$\*[\d.]+;[A-Za-z]\d*|"
    r"\$\d+[A-Za-z]\d*|\$[A-Za-z_]+\d*|"
    r"<[^>]+>|" + SLASH_TOKEN + r"|\$)"
)

CONTEXT_REPLACEMENTS = [
    (re.compile(rf"在\s*{FORMULA_TOKEN}\s*内"), "在一段时间内"),
    (re.compile(rf"持续\s*{FORMULA_TOKEN}"), "持续一段时间"),
    (re.compile(rf"每\s*{FORMULA_TOKEN}\s*秒"), "每隔一段时间"),
    (re.compile(rf"{FORMULA_TOKEN}\s*秒"), "数秒"),
    (re.compile(rf"{FORMULA_TOKEN}\s*码"), "一定范围"),
    (re.compile(rf"{FORMULA_TOKEN}\s*%"), "一定比例"),
    (re.compile(rf"{FORMULA_TOKEN}\s*点"), "一定量"),
    (re.compile(rf"{FORMULA_TOKEN}\s*个"), "若干个"),
    (re.compile(rf"{FORMULA_TOKEN}\s*层"), "若干层"),
    (re.compile(rf"{FORMULA_TOKEN}\s*次"), "若干次"),
]

CONDITIONAL_TEXT_RE = re.compile(r"\?[A-Za-z]\d+\[([^\]]*)\]\[([^\]]*)\]")
PLURAL_FORM_RE = re.compile(r"\$l([^:;]*):([^;]*);")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'/-]*")


MANUAL_NAME_OVERRIDES = {
    "Aspect of the Hawk": "雄鹰守护",
    "Aspect of the Monkey": "灵猴守护",
    "Aspect of the Cheetah": "猎豹守护",
    "Aspect of the Beast": "野兽守护",
    "Aspect of the Pack": "豹群守护",
    "Aspect of the Viper": "蝰蛇守护",
    "Aspect of the Dragonhawk": "龙鹰守护",
    "Immolation Trap": "献祭陷阱",
    "Immolation Trap Effect": "献祭陷阱效果",
    "Explosive Trap": "爆炸陷阱",
    "Explosive Trap Effect": "爆炸陷阱效果",
    "Freezing Trap": "冰冻陷阱",
    "Frost Trap": "冰霜陷阱",
    "Snake Trap": "毒蛇陷阱",
    "Scare Beast": "恐吓野兽",
    "Feed Pet": "喂养宠物",
    "Dismiss Pet": "解散宠物",
    "Revive Pet": "复活宠物",
    "Mend Pet": "治疗宠物",
    "Call Pet": "召唤宠物",
    "Tame Beast": "驯服野兽",
    "Track Beasts": "追踪野兽",
    "Track Humanoids": "追踪人型生物",
    "Track Hidden": "追踪隐藏生物",
    "Track Undead": "追踪亡灵",
    "Track Dragonkin": "追踪龙类",
    "Track Elementals": "追踪元素生物",
    "Track Demons": "追踪恶魔",
    "Track Giants": "追踪巨人",
    "Leatherworking": "制皮",
    "Dragonscale Leatherworking": "龙鳞制皮",
    "Elemental Leatherworking": "元素制皮",
    "Tribal Leatherworking": "部族制皮",
    "Skinning": "剥皮",
    "Mining": "采矿",
    "Alchemy": "炼金术",
    "First Aid": "急救",
    "Cooking": "烹饪",
    "Fishing": "钓鱼",
    "Blacksmithing": "锻造",
    "Tailoring": "裁缝",
    "Engineering": "工程学",
    "Enchanting": "附魔",
    "Inscription": "铭文",
    "Jewelcrafting": "珠宝加工",
    "Herbalism": "草药学",
    "Light Armor Kit": "轻型护甲片",
    "Medium Armor Kit": "中型护甲片",
    "Heavy Armor Kit": "重型护甲片",
    "Thick Armor Kit": "厚护甲片",
    "Heavy Warrior's Kit": "重型战士护甲片",
    "Thick Sorcerer's Kit": "厚重巫师护甲片",
    "Thick Protector's Kit": "厚重防护护甲片",
    "Mail": "锁甲",
    "Leather": "皮甲",
    "Cloth": "布甲",
    "Shield": "盾牌",
    "Hex of Weakness": "虚弱妖术",
    "Starshards": "星辰碎片",
    "Improved Fireball": "强化火球术",
    "Burning Soul": "燃烧之魂",
    "Molten Shields": "熔岩护盾",
    "Flame Throwing": "烈焰投掷",
    "Impact": "冲击",
    "Critical Mass": "火焰重击",
    "Ignite": "点燃",
    "Fire Power": "火焰强化",
    "Combustion": "燃烧",
    "Piercing Ice": "刺骨寒冰",
    "Frost Channeling": "冰霜导能",
    "Shatter": "碎冰",
    "Permafrost": "永冻",
    "Winter's Chill": "寒冬之寒",
    "Ice Shards": "寒冰碎片",
    "Arcane Subtlety": "奥术精妙",
    "Arcane Concentration": "奥术专注",
    "Arcane Focus": "奥术集中",
    "Arcane Mind": "奥术心智",
    "Arcane Impact": "奥术冲击",
    "Magic Attunement": "魔法协调",
    "Presence of Mind": "气定神闲",
    "Arcane Power": "奥术强化",
    "Evocation": "唤醒",
    "Improved Counterspell": "强化法术反制",
    "Sword Specialization": "剑类武器专精",
    "Mace Specialization": "锤类武器专精",
    "Death Wish": "死亡之愿",
    "Mortal Strike": "致死打击",
    "Tactical Mastery": "战术掌握",
    "Anger Management": "愤怒掌控",
    "Iron Will": "钢铁意志",
    "Defiance": "挑衅",
    "Commanding Presence": "统御之力",
    "Flurry": "乱舞",
    "Cruelty": "残忍",
    "Booming Voice": "震耳嗓音",
    "Unbridled Wrath": "怒不可遏",
    "Piercing Howl": "刺耳怒吼",
    "Sweeping Strikes": "横扫攻击",
    "Deadly Poison III": "致命药膏 III",
    "Deadly Poison IV": "致命药膏 IV",
    "Curse of Tongues": "语言诅咒",
    "Poleaxe Specialization": "长柄斧专精",
    "Revenge Stun": "复仇昏迷",
    "Concussion Blow": "震荡猛击",
    "Deep Wounds": "重伤",
    "Last Stand": "破釜沉舟",
    "Wound Poison II": "致伤药膏 II",
    "Wound Poison III": "致伤药膏 III",
    "Wound Poison IV": "致伤药膏 IV",
    "Disenchant": "分解",
    "Chilled": "冰冻",
}

MANUAL_ID_DESCRIPTIONS = {
    8613: "剥取动物的毛皮和皮革，用于制皮。使剥皮技能上限达到75点。需要剥皮小刀。",
    8617: "进一步学习剥取野兽皮革的技巧，用于制皮。使剥皮技能上限达到150点。需要剥皮小刀。",
    8618: "熟练掌握剥取野兽皮革的技巧，用于制皮。使剥皮技能上限达到225点。需要剥皮小刀。",
    10768: "精通剥取野兽皮革的技巧，用于制皮。使剥皮技能上限达到300点。需要剥皮小刀。",
}

MANUAL_DESC_BY_NAME = {
    "Aspect of the Hawk": "猎人获得雄鹰守护，远程攻击强度提高一定量。同一时间只能激活一种守护。\n\n效果：远程攻击强度提高一定量。",
    "Aspect of the Monkey": "猎人获得灵猴守护，躲闪几率提高一定比例。同一时间只能激活一种守护。\n\n效果：躲闪几率提高一定比例。",
    "Immolation Trap": "放置一个火焰陷阱，使第一个靠近的敌人在一段时间内受到一定量火焰伤害。陷阱持续一段时间。同一时间只能激活一个陷阱。",
    "Immolation Trap Effect": "每隔一段时间造成一定量火焰伤害。",
    "Dragonscale Leatherworking": "允许制皮师制作普通制皮师无法制作的特殊龙鳞护甲。龙鳞护甲均为锁甲。",
    "Elemental Leatherworking": "允许制皮师制作普通制皮师无法制作的特殊元素护甲。",
    "Tribal Leatherworking": "允许制皮师制作普通制皮师无法制作的特殊部族护甲。",
    "Heavy Warrior's Kit": "此物品在制作后会与你绑定。",
    "Thick Sorcerer's Kit": "此物品在制作后会与你绑定。",
    "Thick Protector's Kit": "此物品在制作后会与你绑定。",
}

LEATHERWORKING_RANK_DESCRIPTIONS = {
    "Apprentice": "允许制皮师制造皮甲，最高技能上限为75点。需要通过剥皮技能收集的皮革碎片和兽皮。",
    "Journeyman": "允许制皮师制造工艺精良的皮甲，最高技能上限为150点。",
    "Expert": "允许制皮师制造高品质的皮甲，最高技能上限为225点。",
    "Artisan": "允许制皮师制造大师级皮甲，最高技能上限为300点。",
    "Master": "允许制皮师制造大师级皮甲，最高技能上限为375点。",
    "Grand Master": "允许制皮师制造宗师级皮甲，最高技能上限为450点。",
}

TERM_REPLACEMENTS = {
    "Fire damage": "火焰伤害",
    "Frost damage": "冰霜伤害",
    "Nature damage": "自然伤害",
    "Shadow damage": "暗影伤害",
    "Arcane damage": "奥术伤害",
    "Holy damage": "神圣伤害",
    "attack power": "攻击强度",
    "ranged attack power": "远程攻击强度",
    "spell power": "法术强度",
    "Stamina": "耐力",
    "Spirit": "精神",
    "Agility": "敏捷",
    "Strength": "力量",
    "Intellect": "智力",
    "armor": "护甲",
    "Leatherworking": "制皮",
    "Skinning Knife": "剥皮小刀",
    "Skinning": "剥皮",
    "Iron": "铁锭",
    "Gold": "金锭",
    "Mithril": "秘银",
    "Truesilver": "真银",
}

ENCHANT_TARGETS = {
    "2H Weapon": "双手武器",
    "Weapon": "武器",
    "Shield": "盾牌",
    "Cloak": "披风",
    "Bracer": "护腕",
    "Chest": "胸甲",
    "Gloves": "手套",
    "Boots": "靴子",
    "Ring": "戒指",
}

ENCHANT_WORDS = {
    "Minor": "初级",
    "Lesser": "次级",
    "Greater": "强效",
    "Superior": "超强",
    "Major": "特效",
    "Mighty": "强力",
    "Stamina": "耐力",
    "Spirit": "精神",
    "Agility": "敏捷",
    "Strength": "力量",
    "Intellect": "智力",
    "Health": "生命值",
    "Mana": "法力值",
    "Protection": "防护",
    "Resistance": "抗性",
    "Shadow": "暗影",
    "Fire": "火焰",
    "Frost": "冰霜",
    "Nature": "自然",
    "Arcane": "奥术",
    "Striking": "打击",
    "Impact": "冲击",
    "Defense": "防御",
}


def normalize_text(value: str | None) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    return value.replace("\\n", "\n")


def has_cjk(value: str | None) -> bool:
    return bool(CJK_RE.search(value or ""))


def english_word_count(value: str | None) -> int:
    return len(ASCII_WORD_RE.findall(value or ""))


def looks_untranslated(value: str | None, source: str | None = None) -> bool:
    text = normalize_text(value)
    src = normalize_text(source)
    if not text:
        return True
    if src and text.lower() == src.lower():
        return True
    if not has_cjk(text) and re.search(r"[A-Za-z]", text):
        return True
    return english_word_count(text) >= 4


def is_good_translation(value: str | None, source: str | None = None) -> bool:
    text = normalize_text(value)
    if not text or not has_cjk(text):
        return False
    if source and text.lower() == normalize_text(source).lower():
        return False
    return english_word_count(text) < 4


def is_good_name_translation(value: str | None, source: str | None = None) -> bool:
    text = normalize_text(value)
    if not text or not has_cjk(text):
        return False
    if source and text.lower() == normalize_text(source).lower():
        return False
    return english_word_count(text) == 0


def load_pair_file(path: Path) -> dict[str, str]:
    pairs: dict[str, str] = {}
    if not path.exists():
        return pairs
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if len(row) < 2:
                continue
            key = normalize_text(row[0])
            value = normalize_text(row[1])
            if key and is_good_translation(value, key):
                pairs[key] = value
    return pairs


def lua_unescape(value: str) -> str:
    return (
        value
        .replace(r"\\", "\\")
        .replace(r"\"", '"')
        .replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\t", "\t")
    )


def load_lua_string_map(path: Path) -> dict[str, str]:
    pairs: dict[str, str] = {}
    if not path.exists():
        return pairs
    pattern = re.compile(r'\["((?:\\.|[^"\\])*)"\]\s*=\s*"((?:\\.|[^"\\])*)"')
    for match in pattern.finditer(path.read_text(encoding="utf-8", errors="ignore")):
        key = lua_unescape(match.group(1)).strip()
        value = lua_unescape(match.group(2)).strip()
        if key and is_good_translation(value, key):
            pairs[key] = value
    return pairs


def canonical_english(value: str | None) -> str:
    text = normalize_text(value).lower()
    if not text:
        return ""
    text = PLURAL_FORM_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = CONDITIONAL_TEXT_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = re.sub(r"\$\{[^{}]*\}", "<token>", text)
    text = re.sub(r"\$\([^)]*\}", "<token>", text)
    text = re.sub(r"\$\([^)]*\)", "<token>", text)
    text = re.sub(r"\$/[\d.]+;[a-z]\d*", "<token>", text)
    text = re.sub(r"\$\*[\d.]+;[a-z]\d*", "<token>", text)
    text = re.sub(r"\$\d+[a-z]\d*", "<token>", text)
    text = re.sub(r"\$[a-z_]+\d*", "<token>", text)
    text = re.sub(r"\d{4,}", "<id>", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sanitize_display_text(value: str | None) -> str:
    text = normalize_text(value)
    if not text:
        return ""

    text = PLURAL_FORM_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = CONDITIONAL_TEXT_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)

    for pattern, replacement in CONTEXT_REPLACEMENTS:
        text = pattern.sub(replacement, text)

    previous = None
    while previous != text:
        previous = text
        for pattern, replacement in TOKEN_REPLACEMENTS:
            text = pattern.sub(replacement, text)

    text = re.sub(r"([^\d])%([，。、；：,.!?;:]|$)", r"\1\2", text)
    text = re.sub(r"\s+([，。、；：,.!?;:])", r"\1", text)
    text = re.sub(r"@+\s*%", "一定比例", text)
    text = re.sub(r"<[^>]+>\s*%", "一定比例", text)
    text = re.sub(r"<[^>]+>\s*点", "一定量", text)
    text = re.sub(r"<[^>]+>\s*个", "若干个", text)
    text = re.sub(r"<[^>]+>\s*秒", "数秒", text)
    text = re.sub(r"<[^>]+>", "相应数值", text)
    text = re.sub(r"\.1%", "一定比例", text)
    text = re.sub(r"/\d+;\d+[A-Za-z]\d*", "一定量", text)
    text = re.sub(r"/\d+;[A-Za-z]\d*", "一定量", text)
    text = re.sub(r"/\d+;", "", text)
    text = re.sub(r"\?[A-Za-z]\d+", "", text)
    text = re.sub(r"\[[^\]]*\]\[[^\]]*\]", "", text)
    text = text.replace("一定范围范围", "一定范围")
    text = text.replace("在数秒", "在数秒")
    text = text.replace("一定比例每次", "一定比例。每次")
    text = text.replace("by.", "一定量。")
    text = text.replace("by .", "一定量。")
    text = text.replace("for.", "一段时间。")
    text = text.replace("for .", "一段时间。")
    text = text.replace("over.", "在一段时间内。")
    text = text.replace("over .", "在一段时间内。")
    text = re.sub(r"([。！？])[ \t]+", r"\1", text)
    text = re.sub(r"[ \t]+([。！？])", r"\1", text)
    text = re.sub(r"(?<=[\u3400-\u9fff])[ \t]+(?=[\u3400-\u9fff])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^[ \t]+|[ \t]+$", "", text)
    return text.strip()


def lua_quote(value: str) -> str:
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\n", "\\n")
    return f'"{value}"'


def read_source_rows() -> list[dict[str, str]]:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for row in reader:
            spell_id = row.get("spell_id", "").strip()
            if spell_id.isdigit() and normalize_text(row.get("name_en")):
                rows.append(row)
        return rows


def build_translation_maps(rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    name_votes: dict[str, Counter[str]] = {}
    desc_votes: dict[str, Counter[str]] = {}
    desc_canonical_votes: dict[str, Counter[str]] = {}
    tip_votes: dict[str, Counter[str]] = {}

    for row in rows:
        name_en = normalize_text(row.get("name_en"))
        name_zh = normalize_text(row.get("name_zh"))
        desc_en = normalize_text(row.get("description_en"))
        desc_zh = normalize_text(row.get("description_zh"))
        tip_en = normalize_text(row.get("tooltip_en"))
        tip_zh = normalize_text(row.get("tooltip_zh"))

        if name_en and is_good_translation(name_zh, name_en):
            name_votes.setdefault(name_en, Counter())[name_zh] += 1
        if name_en and not is_good_translation(name_zh, name_en):
            tip_as_name = normalize_text(row.get("tooltip_zh"))
            if not desc_en and 0 < len(tip_as_name) <= 40 and is_good_translation(tip_as_name, name_en):
                name_votes.setdefault(name_en, Counter())[tip_as_name] += 1
        if desc_en and is_good_translation(desc_zh, desc_en):
            desc_votes.setdefault(desc_en, Counter())[desc_zh] += 1
            key = canonical_english(desc_en)
            if key:
                desc_canonical_votes.setdefault(key, Counter())[desc_zh] += 1
        if tip_en and is_good_translation(tip_zh, tip_en):
            tip_votes.setdefault(tip_en, Counter())[tip_zh] += 1

    name_map = {key: votes.most_common(1)[0][0] for key, votes in name_votes.items()}
    desc_map = {key: votes.most_common(1)[0][0] for key, votes in desc_votes.items()}
    desc_canonical_map = {key: votes.most_common(1)[0][0] for key, votes in desc_canonical_votes.items()}
    tip_map = {key: votes.most_common(1)[0][0] for key, votes in tip_votes.items()}

    name_map.update(load_pair_file(DICT_NAMES))
    item_name_maps = load_lua_string_map(OBJECTIVE_NAME_DATA)
    item_name_maps.update(load_lua_string_map(ITEM_NAME_MAP))
    for english, chinese in list(item_name_maps.items()):
        if english.startswith("Glyph of ") and chinese.endswith("雕文"):
            inner_english = english[len("Glyph of "):]
            inner_chinese = chinese[:-2]
            if inner_english and inner_chinese:
                item_name_maps.setdefault(inner_english, inner_chinese)
        for en_prefix, zh_prefix in (
            ("Formula: ", "公式："),
            ("Pattern: ", "图样："),
            ("Plans: ", "设计图："),
            ("Recipe: ", "食谱："),
            ("Design: ", "图鉴："),
            ("Schematic: ", "结构图："),
            ("Manual: ", "手册："),
            ("Book: ", "书籍："),
        ):
            if english.startswith(en_prefix) and chinese.startswith(zh_prefix):
                inner_english = english[len(en_prefix):]
                inner_chinese = chinese[len(zh_prefix):]
                if inner_english and inner_chinese:
                    item_name_maps.setdefault(inner_english, inner_chinese)
    name_map.update(item_name_maps)
    name_map.update(MANUAL_NAME_OVERRIDES)
    desc_map.update(load_pair_file(DESC_DICT))
    tip_map.update(load_pair_file(TIP_DICT))
    return name_map, desc_map | desc_canonical_map, tip_map


def repair_mixed_name(value: str, name_map: dict[str, str]) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    if text.startswith("Enchant ") and " - " in text:
        target, effect = text[len("Enchant "):].split(" - ", 1)
        target_zh = ENCHANT_TARGETS.get(target, repair_mixed_name(target, name_map))
        effect_zh = effect
        for english, chinese in sorted(ENCHANT_WORDS.items(), key=lambda item: len(item[0]), reverse=True):
            effect_zh = re.sub(rf"\b{re.escape(english)}\b", chinese, effect_zh)
        if has_cjk(target_zh) and has_cjk(effect_zh):
            return f"附魔{target_zh} - {effect_zh}".strip()
    if text.startswith("Transmute: ") and " to " in text:
        source, target = text[len("Transmute: "):].split(" to ", 1)
        source_zh = TERM_REPLACEMENTS.get(source, repair_mixed_name(source, name_map))
        target_zh = TERM_REPLACEMENTS.get(target, repair_mixed_name(target, name_map))
        if has_cjk(source_zh) and has_cjk(target_zh):
            return f"转化：{source_zh}到{target_zh}".strip()
    if text.startswith("Improved "):
        inner = repair_mixed_name(text[len("Improved "):], name_map)
        return ("强化" + inner).strip()
    if text.startswith("Greater "):
        inner = repair_mixed_name(text[len("Greater "):], name_map)
        return ("强效" + inner).strip()
    if text.startswith("Lesser "):
        inner = repair_mixed_name(text[len("Lesser "):], name_map)
        return ("次级" + inner).strip()
    if text.startswith("Glyph of "):
        inner = repair_mixed_name(text[len("Glyph of "):], name_map)
        return (inner + "雕文").strip()

    for english, chinese in sorted(MANUAL_NAME_OVERRIDES.items(), key=lambda item: len(item[0]), reverse=True):
        if english and chinese:
            text = re.sub(re.escape(english), chinese, text, flags=re.IGNORECASE)

    def replace_segment(match: re.Match[str]) -> str:
        segment = match.group(0).strip()
        return MANUAL_NAME_OVERRIDES.get(segment) or name_map.get(segment) or segment

    text = re.sub(r"[A-Za-z][A-Za-z' -]*[A-Za-z]", replace_segment, text)
    return text.strip()


def localize_name(row: dict[str, str], name_map: dict[str, str]) -> str:
    name_en = normalize_text(row.get("name_en"))
    name_zh = sanitize_display_text(row.get("name_zh"))

    if name_en in MANUAL_NAME_OVERRIDES:
        return MANUAL_NAME_OVERRIDES[name_en]
    if name_en in name_map:
        mapped = sanitize_display_text(name_map[name_en])
        repaired_mapped = sanitize_display_text(repair_mixed_name(mapped, name_map))
        if is_good_name_translation(repaired_mapped, name_en):
            return repaired_mapped
        if is_good_name_translation(mapped, name_en):
            return mapped

    repaired = sanitize_display_text(repair_mixed_name(name_zh, name_map))
    if is_good_name_translation(repaired, name_en):
        return repaired

    repaired_en = sanitize_display_text(repair_mixed_name(name_en, name_map))
    if is_good_name_translation(repaired_en, name_en):
        return repaired_en

    return name_zh or name_en


def localize_description(
    row: dict[str, str],
    desc_map: dict[str, str],
    tip_map: dict[str, str],
) -> str:
    spell_id = int(row["spell_id"])
    name_en = normalize_text(row.get("name_en"))
    rank_en = normalize_text(row.get("rank_en"))
    desc_en = normalize_text(row.get("description_en"))
    tip_en = normalize_text(row.get("tooltip_en"))
    desc_zh = normalize_text(row.get("description_zh"))
    tip_zh = normalize_text(row.get("tooltip_zh"))
    skill_line_ids = set((row.get("skill_line_ids") or "").split(","))

    if skill_line_ids & {"38", "39", "253"}:
        desc = sanitize_display_text(desc_zh)
        tip = sanitize_display_text(tip_zh)
        if not desc:
            return tip
        if not tip or tip == desc or tip in desc:
            return desc
        return desc + "\n\n效果：" + tip

    if spell_id in MANUAL_ID_DESCRIPTIONS:
        desc = MANUAL_ID_DESCRIPTIONS[spell_id]
        tip = ""
    elif name_en == "Leatherworking" and rank_en in LEATHERWORKING_RANK_DESCRIPTIONS:
        desc = LEATHERWORKING_RANK_DESCRIPTIONS[rank_en]
        tip = ""
    elif name_en in MANUAL_DESC_BY_NAME:
        desc = MANUAL_DESC_BY_NAME[name_en]
        tip = ""
    else:
        canonical_key = canonical_english(desc_en)
        desc = ""
        if desc_en in desc_map:
            desc = desc_map[desc_en]
        elif canonical_key in desc_map:
            desc = desc_map[canonical_key]
        elif is_good_translation(desc_zh, desc_en):
            desc = desc_zh
        elif desc_zh and not looks_untranslated(desc_zh, desc_en):
            desc = desc_zh

        tip = ""
        if tip_en in tip_map:
            tip = tip_map[tip_en]
        elif is_good_translation(tip_zh, tip_en):
            tip = tip_zh
        elif tip_zh and not looks_untranslated(tip_zh, tip_en):
            tip = tip_zh

    desc = sanitize_display_text(desc)
    tip = sanitize_display_text(tip)

    if not desc:
        return tip
    if not tip or tip == desc or tip in desc:
        return desc
    return desc + "\n\n效果：" + tip


def write_spell_data(rows: list[dict[str, str]], name_map: dict[str, str], desc_map: dict[str, str], tip_map: dict[str, str]) -> None:
    lines = [
        "-- Auto-generated by Tools/generate_spell_data_from_translation.py.",
        "-- Source: SpellTranslation/spell_english_spellbook_priority.tsv.",
        "function LoadTPCNSpellDataEpoch()",
        "    TPCN_SpellData_Epoch = {",
    ]

    for row in rows:
        spell_id = int(row["spell_id"])
        name = localize_name(row, name_map)
        rank = sanitize_display_text(row.get("rank_zh"))
        desc = localize_description(row, desc_map, tip_map)
        fields = [lua_quote(name), lua_quote(desc), lua_quote("SpellTranslation")]
        if rank:
            fields.append(lua_quote(rank))
        lines.append(f"        [{spell_id}] = {{{', '.join(fields)}}},")

    lines.extend([
        "    }",
        "end",
        "",
    ])
    OUT_SPELL.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_raw_data(rows: list[dict[str, str]]) -> None:
    lines = [
        "-- Auto-generated by Tools/generate_spell_data_from_translation.py.",
        "-- English raw names let EpochCN map client spell text back to Chinese translations.",
        "function LoadEpochCNSpellRawData()",
        "    EpochCN_SpellRawData = {",
    ]

    for row in rows:
        spell_id = int(row["spell_id"])
        name = normalize_text(row.get("name_en"))
        rank = normalize_text(row.get("rank_en"))
        if not name:
            continue
        fields = [lua_quote(name)]
        if rank:
            fields.append(lua_quote(rank))
        lines.append(f"        [{spell_id}] = {{{', '.join(fields)}}},")

    lines.extend([
        "    }",
        "end",
        "",
    ])
    OUT_RAW.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_compat_loaders() -> None:
    OUT_SEASON.write_text(
        "\n".join([
            "-- Season spell overrides. Kept as an explicit empty layer.",
            "function LoadTPCNSpellDataSeason()",
            "    TPCN_SpellData_Season = {}",
            "end",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    rows = read_source_rows()
    rows.sort(key=lambda row: int(row["spell_id"]))
    name_map, desc_map, tip_map = build_translation_maps(rows)
    write_spell_data(rows, name_map, desc_map, tip_map)
    write_raw_data(rows)
    write_compat_loaders()
    print(f"Wrote {OUT_SPELL} with {len(rows)} spells.")
    print(f"Wrote {OUT_RAW} with raw name mappings.")
    print("Wrote empty season override loader.")


if __name__ == "__main__":
    main()
