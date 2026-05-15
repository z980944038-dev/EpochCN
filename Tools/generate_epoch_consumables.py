#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "epochhead_consumables" / "items.json"
OUT = ROOT / "Data" / "EpochConsumableData.lua"
ITEM_DATA = ROOT / "Data" / "ItemData.lua"
OBJECTIVE_DATA = ROOT / "Data" / "ObjectiveNameData.lua"
TOOLTIP_LINE_DATA = ROOT / "Data" / "TooltipLineData.lua"
TOOLTIP_OVERRIDE = ROOT / "Tools" / "tooltip_line_overrides.json"


def load_tooltip_line_translations():
    """Load existing green text translations from TooltipLineData.lua and overrides JSON."""
    result = {}
    if TOOLTIP_LINE_DATA.exists():
        content = TOOLTIP_LINE_DATA.read_text(encoding="utf-8")
        for m in re.finditer(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', content):
            key = m.group(1).replace(r'\"', '"').replace(r'\\', '\\')
            val = m.group(2).replace(r'\"', '"').replace(r'\\', '\\').replace(r'\n', '\n')
            result[key] = val
    if TOOLTIP_OVERRIDE.exists():
        overrides = json.loads(TOOLTIP_OVERRIDE.read_text(encoding="utf-8"))
        for k, v in overrides.items():
            if v and not re.search(r'[A-Za-z]{3,}', v):
                result[k] = v
    return result


_TOOLTIP_LINE_CACHE = None


def get_tooltip_line_translation(text):
    """Look up a green text line in the pre-loaded TooltipLineData cache."""
    global _TOOLTIP_LINE_CACHE
    if _TOOLTIP_LINE_CACHE is None:
        _TOOLTIP_LINE_CACHE = load_tooltip_line_translations()
    return _TOOLTIP_LINE_CACHE.get(text)



def has_cn(text):
    return bool(text and re.search(r"[\u4e00-\u9fff]", text))


def lua_unescape(text):
    return (
        text.replace(r"\\", "\\")
        .replace(r"\"", '"')
        .replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\t", "\t")
    )


def lua_escape(text):
    return (
        str(text or "")
        .replace("\\", r"\\")
        .replace('"', r"\"")
        .replace("\r", "")
        .replace("\n", r"\n")
    )


STRING = r'"((?:\\.|[^"\\])*)"'


def load_item_data():
    result = {}
    row_re = re.compile(r"\[(\d+)\]\s*=\s*\{\s*" + STRING + r"\s*,\s*" + STRING + r"\s*,\s*" + STRING)
    for match in row_re.finditer(ITEM_DATA.read_text(encoding="utf-8", errors="replace")):
        item_id = int(match.group(1))
        result[item_id] = tuple(lua_unescape(match.group(i)) for i in (2, 3, 4))
    return result


def load_objective_names():
    result = {}
    row_re = re.compile(r"\[\s*" + STRING + r"\s*\]\s*=\s*" + STRING)
    for match in row_re.finditer(OBJECTIVE_DATA.read_text(encoding="utf-8", errors="replace")):
        result[lua_unescape(match.group(1))] = lua_unescape(match.group(2))
    return result


STAT = {
    "Strength": "力量",
    "Agility": "敏捷",
    "Stamina": "耐力",
    "Intellect": "智力",
    "Spirit": "精神",
    "Armor": "护甲",
    "Defense": "防御",
    "Dodge": "躲闪",
    "Parry": "招架",
    "Block": "格挡",
    "Haste": "急速",
    "Hit": "命中",
    "Critical Strike": "爆击",
    "Crit": "爆击",
    "Attack Power": "攻击强度",
    "Spell Power": "法术强度",
    "Healing": "治疗效果",
    "Mana Regen": "法力回复",
    "Armor Penetration": "护甲穿透",
    "All Resistances": "所有抗性",
    "all primary stats": "所有主属性",
    "primary stats": "主属性",
    "all resistances": "所有抗性",
    "Fire Resistance": "火焰抗性",
    "Frost Resistance": "冰霜抗性",
    "Nature Resistance": "自然抗性",
    "Shadow Resistance": "暗影抗性",
    "Arcane Resistance": "奥术抗性",
}

RACES = {
    "Human": "人类",
    "Orc": "兽人",
    "Dwarf": "矮人",
    "Night Elf": "暗夜精灵",
    "Undead": "亡灵",
    "Tauren": "牛头人",
    "Gnome": "侏儒",
    "Troll": "巨魔",
    "Blood Elf": "血精灵",
    "Draenei": "德莱尼",
}

CLASSES = {
    "Warrior": "战士",
    "Paladin": "圣骑士",
    "Hunter": "猎人",
    "Rogue": "潜行者",
    "Priest": "牧师",
    "Death Knight": "死亡骑士",
    "Shaman": "萨满祭司",
    "Mage": "法师",
    "Warlock": "术士",
    "Druid": "德鲁伊",
}

WORD = {
    "Faction": "阵营",
    "Race": "种族",
    "Appearance": "外观",
    "Transmutation": "转化",
    "Potion": "药水",
    "Elixir": "药剂",
    "Flask": "合剂",
    "Scroll": "卷轴",
    "Sealed": "密封",
    "Title": "称号",
    "Glyph": "雕文",
    "Negation": "否定",
    "Leyline": "魔脉",
    "Shard": "碎片",
    "Seed": "种子",
    "Crystal": "水晶",
    "Blue": "蓝色",
    "Rune": "符文",
    "Copper": "铜",
    "Iron": "铁",
    "Silver": "银",
    "Mithril": "秘银",
    "Thorium": "瑟银",
    "Truesilver": "真银",
    "Belt": "腰带",
    "Buckle": "带扣",
    "Protector": "防护者",
    "Sorcerer": "巫师",
    "Warrior": "战士",
    "Kit": "护甲片",
    "Embroidery": "刺绣",
    "Linen": "亚麻",
    "Silk": "丝质",
    "Mageweave": "魔纹",
    "Runecloth": "符文布",
    "Rugged": "硬甲",
    "Heavy": "重型",
    "Medium": "中型",
    "Light": "轻型",
    "Minor": "初级",
    "Lesser": "次级",
    "Greater": "强效",
    "Major": "特效",
    "Superior": "优质",
    "Mighty": "强力",
    "Brilliant": "卓越",
    "Honey": "蜂蜜",
    "Butter": "黄油",
    "Bread": "面包",
    "Healing": "治疗",
    "Mana": "法力",
    "Strength": "力量",
    "Agility": "敏捷",
    "Stamina": "耐力",
    "Intellect": "智力",
    "Spirit": "精神",
    "Protection": "防护",
    "Fire": "火焰",
    "Frost": "冰霜",
    "Nature": "自然",
    "Shadow": "暗影",
    "Arcane": "奥术",
    "Holy": "神圣",
    "EZ-Thro": "EZ-Thro",
    "Bomba": "炸弹",
    "Gillijim": "吉利吉姆",
    "Isle": "岛",
    "Resistance": "抗性",
    "Enchant": "附魔",
    "Weapon": "武器",
    "Executioner": "斩杀",
    "Winter": "寒冬",
    "Might": "之力",
}


def replace_terms(text):
    for en in sorted(STAT, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(en)}\b", STAT[en], text, flags=re.I)
    replacements = [
        ("health", "生命值"),
        ("mana", "法力值"),
        ("rage", "怒气"),
        ("energy", "能量"),
        ("armor", "护甲"),
        ("melee weapon", "近战武器"),
        ("weapon", "武器"),
        ("belt", "腰带"),
        ("pants", "裤子"),
        ("cloak", "披风"),
        ("boots", "靴子"),
        ("item", "物品"),
        ("effect", "效果"),
        ("soulbound", "灵魂绑定"),
        ("account", "账号"),
        ("cooldown", "冷却"),
        ("damage", "伤害"),
        ("spell power", "法术强度"),
        ("attack speed", "攻击速度"),
        ("movement speed", "移动速度"),
        ("run speed", "奔跑速度"),
        ("fishing pole", "鱼竿"),
        ("Fishing", "钓鱼"),
        ("demons", "恶魔"),
        ("harmful magic effect", "有害魔法效果"),
        ("imbiber", "饮用者"),
        ("caster", "施法者"),
        ("enemies", "敌人"),
        ("maximum", "最大"),
        ("all schools of magic", "所有魔法系"),
        ("Fire damage", "火焰伤害"),
        ("Frost damage", "冰霜伤害"),
        ("Nature damage", "自然伤害"),
        ("Shadow damage", "暗影伤害"),
        ("Arcane damage", "奥术伤害"),
        ("Holy damage", "神圣伤害"),
        ("physical attacks", "物理攻击"),
        ("poisons", "毒药效果"),
        ("diseases", "疾病效果"),
        ("the target's", "目标的"),
        ("target's", "目标的"),
        ("the player's", "玩家的"),
        ("your", "你的"),
        ("rating", "等级"),
        ("Battle Elixir", "战斗药剂"),
        ("Guardian Elixir", "守护药剂"),
        ("Conjured Item", "魔法制造的物品"),
        ("Quest Item", "任务物品"),
        # --- Additional common terms ---
        ("Level", "等级"),
        ("Spells", "法术"),
        ("spells", "法术"),
        ("Spell", "法术"),
        ("spell", "法术"),
        ("Set:", "套装："),
        ("Equip:", "装备："),
        ("Chance on hit:", "击中时可能："),
        ("Chance on melee attack", "近战攻击时有几率"),
        ("melee attack", "近战攻击"),
        ("melee attacks", "近战攻击"),
        ("ranged attacks", "远程攻击"),
        ("ranged attack", "远程攻击"),
        ("normal ranged attacks", "普通远程攻击"),
        ("magical spells and effects", "魔法法术和效果"),
        ("Increases damage and healing done by", "使伤害和治疗效果提高"),
        ("Increases damage done by", "使伤害提高"),
        ("Increases healing done by", "使治疗效果提高"),
        ("Improves your chance to get a critical strike", "使你的暴击几率提高"),
        ("Improves your chance to hit", "使你的命中几率提高"),
        ("critical strike", "暴击"),
        ("critical strikes", "暴击"),
        ("Decreases", "降低"),
        ("Increases", "提高"),
        ("Equipped", "装备后"),
        ("chance", "几率"),
        ("restore", "恢复"),
        ("restoring", "恢复"),
        ("heal you for", "为你治疗"),
        ("heals you for", "为你治疗"),
        (" up to ", "最多"),
        ("Begins a quest", "开始一个任务"),
        ("This item begins a quest", "这件物品开始一个任务"),
        ("Held In Off-Hand", "副手物品"),
        ("Held In Off-hand", "副手物品"),
        (" and ", "和"),
    ]
    for en, cn in replacements:
        text = re.sub(rf"\b{re.escape(en)}\b", cn, text, flags=re.I)
    text = text.replace(" and ", "和")
    text = text.replace("Frost和Shadow", "冰霜和暗影")
    text = text.replace("Fire和Frost", "火焰和冰霜")
    return text


def translate_time(text):
    def repl(match):
        num, unit = match.group(1), match.group(2).lower()
        if "." in num:
            num = num.rstrip("0").rstrip(".")
        if unit.startswith("sec"):
            return f"{num}秒"
        if unit.startswith("min"):
            return f"{num}分钟"
        if unit.startswith("day"):
            return f"{num}天"
        return f"{num}小时"

    return re.sub(r"(\d+(?:\.\d+)?)\s*(Seconds|Second|Sec|Minutes|Minute|Min|Hours|Hour|Hr|Days|Day)s?\b", repl, text, flags=re.I)


def translate_list(value, mapping):
    parts = [p.strip() for p in value.split(",")]
    return "、".join(mapping.get(part, part) for part in parts if part)


def translate_recipe_target(text, objective_names):
    if text in objective_names:
        return objective_names[text]
    if text.startswith("Enchant "):
        return "附魔" + translate_name(text[8:], {}, objective_names)
    return translate_name(text, {}, objective_names)


def translate_name(name, existing_items, objective_names):
    if name in objective_names and has_cn(objective_names[name]):
        return objective_names[name]
    direct = {
        'EZ-Thro "Da Bomba"': 'EZ-Thro“炸弹”',
        'EZ-Thro "Da Bomba" Gillijim\'s Isle': 'EZ-Thro“炸弹”吉利吉姆岛',
    }
    if name in direct:
        return direct[name]

    for prefix, cn_prefix in [
        ("Recipe: ", "食谱："),
        ("Formula: ", "公式："),
        ("Pattern: ", "图样："),
        ("Plans: ", "设计图："),
        ("Manual: ", "手册："),
        ("Book: ", "书籍："),
        ("Scroll of ", "卷轴："),
    ]:
        if name.startswith(prefix):
            return cn_prefix + translate_recipe_target(name[len(prefix):], objective_names)

    text = name
    text = text.replace("'s", "的")
    text = text.replace(" - ", " - ")
    for en in sorted(WORD, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(en)}\b", WORD[en], text)
    text = re.sub(r"\s+", "", text)
    return text if has_cn(text) else name


MIXED_CONSUMABLE_TEXT_MAP = {
    "A small satchel containing various trade goods.": "一个装有各种贸易物资的小挎包。",
    "An extremely potent alcoholic beverage.": "一种效力极强的酒精饮料。",
    "Allows the shaman to see elemental spirits.": "使萨满祭司能够看见元素之灵。",
    "Requires Argent Dawn - Revered": "需要银色黎明 - 崇敬",
    "需要 Argent Dawn - Revered": "需要银色黎明 - 崇敬",
    "需要 Feastof寒冬Veil": "需要冬幕节",
    "Cure for the Touch of Zanzil.": "赞吉尔之触的解药。",
    "Transforms your mount into something more festive.": "将你的坐骑变得更有节日气氛。",
    "Transforms 你的 mount into something more festive.": "将你的坐骑变得更有节日气氛。",
    "Increases Stamina by 10 for 15 min and gets you drunk to boot!": "使耐力提高 10 点，持续 15分钟，并让你喝得酩酊大醉！",
    "Increases 耐力 by 10 for 15分钟和gets you drunk to boot!": "使耐力提高 10 点，持续 15分钟，并让你喝得酩酊大醉！",
    "Shoots a firework into the air that bursts in a yellow pattern.": "向空中发射一枚烟花，并绽放出黄色图案。",
    "Shoots a firework into the air that bursts into a thousand red stars.": "向空中发射一枚烟花，并绽放成无数红色星芒。",
}

MIXED_CONSUMABLE_TARGETS = {
    "Burning Exile": "炽燃流放者",
}

TIME_TOKEN_RE = r"\d+(?:\.\d+)?\s*(?:Seconds?|Second|Secs?|Sec|Minutes?|Minute|Mins?|Min|Hours?|Hour|Hrs?|Hr|Days?|Day|秒|分钟|小时|天)"


def strip_leading_article(text):
    return re.sub(r"^(?:a|an|the)\s+", "", text or "", flags=re.I).strip()


def translate_consumable_target(name, objective_names):
    stripped = strip_leading_article(name)
    if stripped in objective_names and has_cn(objective_names[stripped]):
        return objective_names[stripped]
    if stripped in MIXED_CONSUMABLE_TARGETS:
        return MIXED_CONSUMABLE_TARGETS[stripped]
    translated = translate_name(stripped, {}, objective_names)
    return translated if has_cn(translated) else stripped


def normalize_mixed_consumable_text(text, objective_names=None):
    if not text:
        return text

    objective_names = objective_names or {}
    text = text.strip()

    direct = MIXED_CONSUMABLE_TEXT_MAP.get(text)
    if direct:
        return direct

    match = re.match(
        rf"^Decrease the (?:armor|护甲) of the target by ([\d,]+) for ({TIME_TOKEN_RE})\. While affected, the target cannot stealth or turn invisible\.?$",
        text,
        re.I,
    )
    if match:
        return f"使目标的护甲降低 {match.group(1)} 点，持续 {translate_time(match.group(2))}。在效果持续期间，目标无法潜行或隐形。"

    match = re.match(rf"^Allows the (?:drinker|饮用者) to breathe water for ({TIME_TOKEN_RE})\.?$", text, re.I)
    if match:
        return f"使饮用者可以在水下呼吸，持续 {translate_time(match.group(1))}。"

    match = re.match(r"^Instantly restores ([\d,]+) (?:life|health)\.?$", text, re.I)
    if match:
        return f"立即恢复 {match.group(1)} 点生命值。"

    match = re.match(r"^([\d,]+) increased (?:攻击强度|attack power) against undead$", text, re.I)
    if match:
        return f"对亡灵的攻击强度提高 {match.group(1)} 点"

    match = re.match(r"^([\d,]+) increased (?:法术伤害|spell damage) against undead$", text, re.I)
    if match:
        return f"对亡灵的法术伤害提高 {match.group(1)} 点"

    match = re.match(r"^Banishes\s+(.+?)\.?$", text, re.I)
    if match:
        raw_target = match.group(1).strip()
        translated_target = translate_consumable_target(raw_target, objective_names)
        classifier = "一名" if re.match(r"^(?:a|an)\s+", raw_target, re.I) else ""
        return f"放逐{classifier}{translated_target}。"

    return text


def translate_flavor(text, objective_names=None):
    flavor = {
        "Drink up!": "一饮而尽！",
        "This rare ingredient is practically shaking with remnant arcane energy.": "这种稀有材料几乎因残存的奥术能量而震颤。",
        "Your quest log and some reputations will be wiped, does not change your racials. ": "你的任务日志和部分声望会被清空，不会改变你的种族技能。",
        "Does not change your racials, that is controlled by the Racial Knowledge system.": "不会改变你的种族技能，种族技能由种族知识系统控制。",
        "Also allows to change your name, limited to two times per character.": "同时允许改名，每个角色最多两次。",
        "So good you don't even want to share it with anyone.": "好吃到你根本不想和任何人分享。",
        "Quality controlled at EZ-Thro headquarters.": "EZ-Thro 总部品质监控。",
        "Protects the brood against Mother's Milk. Efficacy decays over time.": "保护幼体免受母乳影响。效力会随时间衰减。",
        "Fresh from the oven": "刚出炉",
        "Carefully extracted for warfare use.": "为战争用途精心提取。",
        "Looks stable enough...?": "看起来足够稳定……？",
    }
    translated = flavor.get(text)
    if translated:
        return translated
    return normalize_mixed_consumable_text(replace_terms(translate_time(text)), objective_names)


def translate_line(line, objective_names):
    original = line.strip()
    text = original.strip()

    # --- Early return from TooltipLineData (2,848 pre-translated green text lines) ---
    tooltip_translation = get_tooltip_line_translation(text)
    if tooltip_translation and not re.search(r'[A-Za-z]{3,}', tooltip_translation):
        return tooltip_translation

    quoted = re.match(r'^"(.*)"$', text)
    if quoted:
        return translate_flavor(quoted.group(1), objective_names)

    direct = {
        "Binds to account": "账号绑定",
        "Binds when picked up": "拾取后绑定",
        "Binds when equipped": "装备后绑定",
        "Binds when used": "使用后绑定",
        "Unique": "唯一",
        "Artifact": "神器",
        "Legendary": "传说",
        "Epic": "史诗",
        "Rare": "精良",
        "Uncommon": "优秀",
        "Common": "普通",
        "Conjured Item": "魔法制造的物品",
        "Quest Item": "任务物品",
        "Gillijim's Isle": "吉利吉姆岛",
        # --- 装备栏位 ---
        "Main Hand": "主手",
        "Off Hand": "副手",
        "One-Hand": "单手",
        "Two-Hand": "双手",
        "Ranged": "远程",
        "Thrown": "投掷",
        "Head": "头部",
        "Shoulder": "肩部",
        "Chest": "胸部",
        "Legs": "腿部",
        "Hands": "手",
        "Feet": "脚",
        "Waist": "腰部",
        "Wrist": "手腕",
        "Back": "背部",
        "Finger": "手指",
        "Neck": "颈部",
        "Shirt": "衬衣",
        "Tabard": "战袍",
        "Trinket": "饰品",
        "Relic": "圣物",
        "Held In Off-hand": "副手物品",
        "Held In Off-Hand": "副手物品",
        "Random Enchantment": "随机附魔",
        "Retrieving item information": "正在获取物品信息",
    }
    if text in direct:
        return direct[text]

    match = re.match(r"^Unique \((\d+)\)$", text)
    if match:
        return f"唯一（{match.group(1)}）"
    # --- 物品等级 ---
    match = re.match(r"^Item Level (\d+)$", text)
    if match:
        return f"物品等级 {match.group(1)}"
    # --- 速度 ---
    match = re.match(r"^Speed ([\d.]+)$", text)
    if match:
        return f"速度 {match.group(1)}"
    # --- 伤害 ---
    match = re.match(r"^(\d+) - (\d+) Damage$", text)
    if match:
        return f"{match.group(1)} - {match.group(2)} 伤害"
    # --- 每秒伤害 ---
    match = re.match(r"^\(([\d.]+) damage per second\)$", text)
    if match:
        return f"（每秒造成 {match.group(1)} 点伤害）"
    # --- 护甲值 ---
    match = re.match(r"^(\d+) Armor$", text)
    if match:
        return f"{match.group(1)} 护甲"
    # --- 格挡值 ---
    match = re.match(r"^(\d+) Block$", text)
    if match:
        return f"{match.group(1)} 格挡"
    # --- 基础属性 ---
    match = re.match(r"^\+(\d+) (Strength|Agility|Stamina|Intellect|Spirit)$", text)
    if match:
        stat_map = {"Strength": "力量", "Agility": "敏捷", "Stamina": "耐力", "Intellect": "智力", "Spirit": "精神"}
        return f"+{match.group(1)} {stat_map[match.group(2)]}"
    # --- 耐久度 ---
    match = re.match(r"^Durability (\d+) / (\d+)$", text)
    if match:
        return f"耐久度 {match.group(1)} / {match.group(2)}"
    # --- 开始任务 ---
    match = re.match(r"^Begins a quest$", text, re.I)
    if match:
        return "开始一个任务"
    # --- 额外伤害 ---
    match = re.match(r"^\+(\d+) - (\d+) (Fire|Frost|Nature|Shadow|Arcane|Holy) Damage$", text)
    if match:
        school_map = {"Fire": "火焰", "Frost": "冰霜", "Nature": "自然", "Shadow": "暗影", "Arcane": "奥术", "Holy": "神圣"}
        return f"+{match.group(1)} - {match.group(2)} {school_map[match.group(3)]}伤害"
    # --- 唯一装备 ---
    match = re.match(r"^Unique-Equipped$", text)
    if match:
        return "唯一装备"
    match = re.match(r"^Unique-Equipped \((\d+)\)$", text)
    if match:
        return f"唯一装备（{match.group(1)}）"
    match = re.match(r"^Requires Level (\d+)$", text)
    if match:
        return f"需要等级 {match.group(1)}"
    match = re.match(r"^Requires a level (\d+) or higher item\.?$", text, re.I)
    if match:
        return f"需要等级 {match.group(1)} 或更高的物品。"
    # --- 骑术要求 ---
    match = re.match(r"^Requires (.+?) Riding \((\d+)\)$", text)
    if match:
        riding_map = {
            "Ram": "山羊骑术", "Horse": "马骑术", "Wolf": "狼骑术",
            "Raptor": "迅猛龙骑术", "Mechanostrider": "机械陆行鸟骑术",
            "Kodo": "科多兽骑术", "Undead": "亡灵骑术", "Tiger": "虎骑术",
            "Hawkstrider": "陆行鸟骑术", "Elekk": "雷象骑术",
        }
        name = riding_map.get(match.group(1), match.group(1) + "骑术")
        return f"需要 {name}（{match.group(2)}）"
    match = re.match(r"^Requires Riding \((\d+)\)$", text)
    if match:
        return f"需要骑术（{match.group(1)}）"
    match = re.match(r"^Requires (.+)$", text)
    if match:
        req = match.group(1)
        warmode = re.match(r"^Warmode\. Only usable within the Eastern Kingdoms and Kalimdor\. \((\d+\s*(?:Sec|Second|Seconds|Min|Minute|Minutes|Hr|Hour|Hours)) Cooldown\)$", req, re.I)
        if warmode:
            return f"需要战争模式。只能在东部王国和卡利姆多使用。（{translate_time(warmode.group(1))}冷却）"
        combined = re.match(r"^(.+?)\s+(Use: .+)$", req)
        if combined:
            return "需要 " + translate_name(combined.group(1), {}, objective_names) + "\n" + translate_line(combined.group(2), objective_names)
        profession = {
            "First Aid": "急救",
            "Alchemy": "炼金术",
            "Cooking": "烹饪",
            "Enchanting": "附魔",
            "Engineering": "工程学",
            "Leatherworking": "制皮",
            "Blacksmithing": "锻造",
            "Tailoring": "裁缝",
            "Fishing": "钓鱼",
            "Herbalism": "草药学",
            "Mining": "采矿",
            "Skinning": "剥皮",
            "Jewelcrafting": "珠宝加工",
            "Inscription": "铭文",
        }
        for en, cn in profession.items():
            req = req.replace(en, cn)
        return normalize_mixed_consumable_text("需要 " + (req if has_cn(req) else translate_name(req, {}, objective_names)), objective_names)
    match = re.match(r"^Races: (.+)$", text)
    if match:
        return "种族：" + translate_list(match.group(1), RACES)
    match = re.match(r"^Classes: (.+)$", text)
    if match:
        return "职业：" + translate_list(match.group(1), CLASSES)
    match = re.match(r"^Duration: (.+)$", text)
    if match:
        return "持续时间：" + translate_time(match.group(1))
    match = re.match(r"^Requires Warmode\. Only usable within the Eastern Kingdoms and Kalimdor\. \((\d+\s*(?:Sec|Second|Seconds|Min|Minute|Minutes|Hr|Hour|Hours)) Cooldown\)$", text, re.I)
    if match:
        return f"需要战争模式。只能在东部王国和卡利姆多使用。（{translate_time(match.group(1))}冷却）"

    prefix = ""
    body = text
    for raw_prefix, cn_prefix in [
        ("Use: ", "使用："),
        ("Equip: ", "装备："),
        ("Chance on hit: ", "击中时可能："),
    ]:
        if body.startswith(raw_prefix):
            prefix = cn_prefix
            body = body[len(raw_prefix):]
            break

    cooldown = ""
    cool = re.search(r"\((\d+\s*(?:Sec|Second|Seconds|Min|Minute|Minutes|Hr|Hour|Hours)) Cooldown\)$", body, re.I)
    if cool:
        cooldown = f"（{translate_time(cool.group(1))}冷却）"
        body = body[:cool.start()].strip()

    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) health\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点生命值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) mana\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点法力值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) health and mana\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点生命值和法力值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) health and ([\d,]+) to ([\d,]+) mana\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点生命值和 {match.group(3)} 到 {match.group(4)} 点法力值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) mana and ([\d,]+) to ([\d,]+) health\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点法力值和 {match.group(3)} 到 {match.group(4)} 点生命值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) mana and health\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点法力值和生命值。{cooldown}"
    match = re.match(r"^Restores ([\d,]+)% of your health per second for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\.?$", body, re.I)
    if match:
        return f"{prefix}每秒恢复你 {match.group(1)}% 的生命值，持续 {translate_time(match.group(2))}。进食时必须保持坐姿。{cooldown}"
    match = re.match(r"^Restores ([\d,]+)% of your mana per second for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\.?$", body, re.I)
    if match:
        return f"{prefix}每秒恢复你 {match.group(1)}% 的法力值，持续 {translate_time(match.group(2))}。饮用时必须保持坐姿。{cooldown}"
    match = re.match(r"^Restores ([\d,]+)% of your health and mana per second for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\.(?: (.+))?$", body, re.I)
    if match:
        extra = translate_line(match.group(3), objective_names) if match.group(3) else ""
        return f"{prefix}每秒恢复你 {match.group(1)}% 的生命值和法力值，持续 {translate_time(match.group(2))}。进食时必须保持坐姿。{extra}{cooldown}"
    match = re.match(r"^Restores ([\d,]+)% of your health per second for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and gain Stamina and Spirit for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. ?(?:\"(.+)\")?$", body, re.I)
    if match:
        flavor = ("\"" + translate_flavor(match.group(4), objective_names) + "\"") if match.group(4) else ""
        return f"{prefix}每秒恢复你 {match.group(1)}% 的生命值，持续 {translate_time(match.group(2))}。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果，耐力和精神提高，持续 {translate_time(match.group(3))}。{flavor}{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. Also restores ([\d,]+) (Mana|health) every 5 seconds for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        resource = "法力值" if match.group(4).lower() == "mana" else "生命值"
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。同时每 5 秒恢复 {match.group(3)} 点{resource}，持续 {translate_time(match.group(5))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. Also increases your (.+?) by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。同时使你的{replace_terms(match.group(3))}提高 {match.group(4)} 点，持续 {translate_time(match.group(5))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you eat for 10 seconds will also increase your (.+?) by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。如果进食 10 秒，还会使你的{replace_terms(match.group(3))}提高 {match.group(4)} 点，持续 {translate_time(match.group(5))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and gain ([\d,]+) (.+?) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?(?:\s+\"(.+)\")?$", body, re.I)
    if match:
        bonus = replace_terms(match.group(3) + " " + match.group(4))
        bonus = re.sub(r"(\d+) 法力值 every 5 seconds", r"每 5 秒恢复 \1 点法力值", bonus, flags=re.I)
        bonus = re.sub(r"(\d+) 生命值 every 5 seconds", r"每 5 秒恢复 \1 点生命值", bonus, flags=re.I)
        flavor = ("\"" + translate_flavor(match.group(6), objective_names) + "\"") if match.group(6) else ""
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果，{bonus}，持续 {translate_time(match.group(5))}。{flavor}{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and gain a chance upon taking damage to reduce the attack power of enemies behind you by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果：受到伤害时有几率使你身后敌人的攻击强度降低 {match.group(3)} 点，持续 {translate_time(match.group(4))}。该充分进食效果持续 {translate_time(match.group(5))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and increase your healing done by spells and abilities by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果，使你的法术和技能治疗效果提高 {match.group(3)} 点，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health and ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and gain ([\d,]+) (.+?) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        bonus = replace_terms(match.group(4) + " " + match.group(5))
        bonus = re.sub(r"(\d+) 法力值 every 5 seconds", r"每 5 秒恢复 \1 点法力值", bonus, flags=re.I)
        bonus = re.sub(r"(\d+) 生命值 every 5 seconds", r"每 5 秒恢复 \1 点生命值", bonus, flags=re.I)
        return f"{prefix}在 {translate_time(match.group(3))} 内恢复 {match.group(1)} 点生命值和 {match.group(2)} 点法力值。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果，{bonus}，持续 {translate_time(match.group(6))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. If you spend at least 10 seconds drinking you will become well quenched and gain ([\d,]+) increased spell damage against undead for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。如果饮用至少 10 秒，你会获得充分饮水效果，对亡灵的法术伤害提高 {match.group(3)} 点，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. If you spend at least 10 seconds drinking you will become well fed and gain ([\d,]+) (.+?) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。如果饮用至少 10 秒，你会获得充分进食效果，{match.group(3)} {replace_terms(match.group(4))}，持续 {translate_time(match.group(5))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. If you spend at least 10 seconds drinking you will become well quenched and gain ([\d,]+) increased spell damage against undead for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。如果饮用至少 10 秒，你会获得充分饮水效果，对亡灵的法术伤害提高 {match.group(3)} 点，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health and ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(3))} 内恢复 {match.group(1)} 点生命值和 {match.group(2)} 点法力值。进食时必须保持坐姿。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. If you spend at least 10 seconds drinking you will become well fed and gain ([\d,]+) (.+?) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. (Standard alcohol)\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。如果饮用至少 10 秒，你会获得充分进食效果，{match.group(3)} {replace_terms(match.group(4))}，持续 {translate_time(match.group(5))}。普通酒精饮料。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. If you spend at least 10 seconds drinking you will become \"well fed\" and gain ([\d,]+) (.+?) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. (Standard alcohol)\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。如果饮用至少 10 秒，你会获得“充分进食”效果，{match.group(3)} {replace_terms(match.group(4))}，持续 {translate_time(match.group(5))}。普通酒精饮料。{cooldown}"
    match = re.match(r"^Heals ([\d,]+) damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内治疗 {match.group(1)} 点伤害。{cooldown}"
    match = re.match(r"^Heals ([\d,]+) damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Usable only (?:in|inside) (PvP Battlegrounds|Arathi Basin)\.?$", body, re.I)
    if match:
        place = "PvP 战场" if match.group(3).lower() == "pvp battlegrounds" else "阿拉希盆地"
        return f"{prefix}在 {translate_time(match.group(2))} 内治疗 {match.group(1)} 点伤害。只能在{place}中使用。{cooldown}"
    match = re.match(r"^Heals ([\d,]+) damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes)), assuming you don't bite down on a poison sac\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内治疗 {match.group(1)} 点伤害，前提是你没有咬到毒囊。{cooldown}"
    match = re.match(r"^Instantly restores ([\d,]+) (health|mana)\.?$", body, re.I)
    if match:
        resource = "生命值" if match.group(2).lower() == "health" else "法力值"
        return f"{prefix}立即恢复 {match.group(1)} 点{resource}。{cooldown}"
    match = re.match(r"^Instantly heals ([\d,]+) damage\. Also restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\.?$", body, re.I)
    if match:
        return f"{prefix}立即治疗 {match.group(1)} 点伤害，并在 {translate_time(match.group(3))} 内恢复 {match.group(2)} 点法力值。饮用时必须保持坐姿。{cooldown}"
    match = re.match(r"^Increases (?:the target's |target's |your |the player's )?(.+?) by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?\s*(Battle Elixir|Guardian Elixir)?\.?$", body, re.I)
    if match:
        stat = replace_terms(match.group(1))
        suffix = " " + replace_terms(match.group(4)) + "。" if match.group(4) else ""
        return f"{prefix}使{stat}提高 {match.group(2)} 点，持续 {translate_time(match.group(3))}。{suffix}{cooldown}"
    match = re.match(r"^Increases (?:your )?(.+?) by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        stat = replace_terms(match.group(1))
        return f"{prefix}使{stat}提高 {match.group(2)} 点，持续 {translate_time(match.group(3))}。{cooldown}"
    match = re.match(r"^Increases (?:the target's |target's |your |the player's )?(.+?) by ([\d,]+)\.?$", body, re.I)
    if match:
        stat = replace_terms(match.group(1))
        return f"{prefix}使{stat}提高 {match.group(2)} 点。{cooldown}"
    match = re.match(r"^Increases (?:your )?(.+?) by up to ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        stat = replace_terms(match.group(1))
        return f"{prefix}使{stat}最多提高 {match.group(2)} 点，持续 {translate_time(match.group(3))}。{cooldown}"
    match = re.match(r"^Permanently enchant (.+?) to (.+)\.?$", body, re.I)
    if match:
        target = replace_terms(match.group(1))
        target = re.sub(r"^(a|an)\s+", "", target, flags=re.I)
        effect = replace_terms(translate_time(match.group(2))).rstrip(".")
        effect = re.sub(r"^increase the 生命值 of the wearer by ([\d,]+)", r"使穿戴者的生命值提高 \1 点", effect, flags=re.I)
        effect = re.sub(r"^increase 所有抗性 by ([\d,]+)", r"使所有抗性提高 \1 点", effect, flags=re.I)
        effect = re.sub(r"^increase (?:冰霜|Frost) 法术强度 by ([\d,]+)", r"使冰霜法术强度提高 \1 点", effect, flags=re.I)
        effect = re.sub(r"^occasionally grant you", "有时赋予你", effect, flags=re.I)
        effect = re.sub(r"^restore ([\d,]+) 生命值和法力值 every (\d+秒)", r"每 \2 恢复 \1 点生命值和法力值", effect, flags=re.I)
        effect = re.sub(r"Only one instance of this 效果 can be active at a time", "同一时间只能激活一个该效果", effect, flags=re.I)
        effect = effect.replace(". ", "。").replace(".", "")
        return f"{prefix}永久性地为{target}附魔，{effect}。{cooldown}"
    match = re.match(r"^Permanently enchant bracers so they increase the wearer's (.+?) by ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}永久性地为护腕附魔，使穿戴者的{replace_terms(match.group(1))}提高 {match.group(2)} 点。{cooldown}"
    match = re.match(r"^Requires a level (\d+) or higher item\.?$", body, re.I)
    if match:
        return f"需要等级 {match.group(1)} 或更高的物品。"
    match = re.match(r"^Permanently increase the armor value of an item worn on the chest, legs, hands or feet by ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}永久性地使穿戴在胸部、腿部、手部或脚部的物品护甲值提高 {match.group(1)} 点。{cooldown}"
    match = re.match(r"^Permanently increase the armor value of an item worn on the chest, legs, hands or feet by ([\d,]+)\. Only usable on items level ([\d,]+) and above\.?$", body, re.I)
    if match:
        return f"{prefix}永久性地使穿戴在胸部、腿部、手部或脚部的物品护甲值提高 {match.group(1)} 点。只能用于等级 {match.group(2)} 及以上的物品。{cooldown}"
    match = re.match(r"^Infuse your (.+?), permanently (.+)\.?$", body, re.I)
    if match:
        target = replace_terms(match.group(1))
        effect = replace_terms(translate_time(match.group(2))).rstrip(".")
        effect = re.sub(r"^increasing 所有主属性 by ([\d,]+)", r"使所有主属性提高 \1 点", effect, flags=re.I)
        effect = re.sub(r"Only the Blacksmith's 腰带 can be infused,和infusing a 腰带 will cause it to become 灵魂绑定", "只能灌注锻造师的腰带，灌注后会使腰带变为灵魂绑定", effect, flags=re.I)
        effect = effect.replace(". ", "。").replace(".", "")
        return f"{prefix}灌注你的{target}，永久性地{effect}。{cooldown}"
    match = re.match(r"^Permanently embed an armor kit onto your (.+?), (.+)\.?$", body, re.I)
    if match:
        target = replace_terms(match.group(1))
        effect = replace_terms(translate_time(match.group(2))).rstrip(".")
        effect = re.sub(r"^increasing 你的 (.+?) by ([\d,]+)", r"使你的\1提高 \2 点", effect, flags=re.I)
        effect = effect.replace("Only the leatherworker's 裤子 can be enchanted和embedding 裤子 will cause it to become 灵魂绑定", "只能为制皮师的裤子附魔，嵌入后会使裤子变为灵魂绑定")
        effect = re.sub(r"Only the leatherworker's 裤子 can be enchanted and embedding 裤子 will cause it to become 灵魂绑定", "只能为制皮师的裤子附魔，嵌入后会使裤子变为灵魂绑定", effect, flags=re.I)
        effect = effect.replace(". ", "。").replace(".", "")
        return f"{prefix}将护甲片永久嵌入你的{target}，{effect}。{cooldown}"
    match = re.match(r"^Teaches you how to (.+)\.?$", body, re.I)
    if match:
        return f"{prefix}教你学会{replace_terms(match.group(1)).rstrip('.')}。{cooldown}"
    match = re.match(r"^Heals the target for ([\d,]+) damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内为目标治疗 {match.group(1)} 点伤害。{cooldown}"
    match = re.match(r"^Renders a target unable to move for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}使目标无法移动，持续 {translate_time(match.group(1))}。{cooldown}"
    match = re.match(r"^Makes you immune to Stun and Movement Impairing effects for the next (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Also removes existing Stun and Movement Impairing effects\.?$", body, re.I)
    if match:
        return f"{prefix}使你免疫昏迷和移动限制效果，持续 {translate_time(match.group(1))}。同时移除已有的昏迷和移动限制效果。{cooldown}"
    match = re.match(r"^Summons a guardian (.+?) that will protect you for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}召唤一只守护型{replace_terms(match.group(1))}保护你，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Summons a mechanical (yeti|Greench) that will protect you for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        name = "雪人" if match.group(1).lower() == "yeti" else "格林奇"
        return f"{prefix}召唤一个机械{name}保护你，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Decreases target's chance to hit by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}使目标的命中几率降低 {match.group(1)}%，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Puts the enemy target to sleep for up to (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Any damage caused will awaken the target\. Only one target can be asleep at a time\.?$", body, re.I)
    if match:
        return f"{prefix}使敌方目标沉睡，最多持续 {translate_time(match.group(1))}。任何伤害都会唤醒目标，同一时间只能有一个目标处于沉睡状态。{cooldown}"
    match = re.match(r"^Regenerate ([\d,]+) health every (\d+\s*(?:sec|second|seconds|min|minute|minutes)) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?\s*(Battle Elixir|Guardian Elixir)?\.?$", body, re.I)
    if match:
        suffix = " " + replace_terms(match.group(4)) + "。" if match.group(4) else ""
        return f"{prefix}每 {translate_time(match.group(2))} 恢复 {match.group(1)} 点生命值，持续 {translate_time(match.group(3))}。{suffix}{cooldown}"
    match = re.match(r"^Imbiber is cured of up to four poisons up to level (\d+)\.?$", body, re.I)
    if match:
        return f"{prefix}饮用者最多可解除 4 个等级不高于 {match.group(1)} 的毒药效果。{cooldown}"
    match = re.match(r"^Imbiber is immune to physical attacks for the next (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}饮用者免疫物理攻击，持续 {translate_time(match.group(1))}。{cooldown}"
    match = re.match(r"^Increases run speed by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}奔跑速度提高 {match.group(1)}%，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Increases your attack speed by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}攻击速度提高 {match.group(1)}%，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\.nEach strike has a ([\d,]+)% chance of poisoning the enemy for ([\d,]+) Nature damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Stacks up to (\d+) times on a single target\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，在 {translate_time(match.group(4))} 内造成 {match.group(3)} 点自然伤害。同一目标最多叠加 {match.group(5)} 次。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\.nEach strike has a ([\d,]+)% chance of poisoning the enemy, slowing their movement speed by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，使其移动速度降低 {match.group(3)}%，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\.nEach strike has a ([\d,]+)% chance of poisoning the enemy which instantly inflicts ([\d,]+) Nature damage\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，立即造成 {match.group(3)} 点自然伤害。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\.nEach strike has a ([\d,]+)% chance of poisoning the enemy, increasing their casting time by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，使其施法时间延长 {match.group(3)}%，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\.nEach strike has a ([\d,]+)% chance of poisoning the enemy, causing ([\d,]+) Nature damage and reducing all healing effects used on them by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Stacks up to (\d+) times on a single target\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，造成 {match.group(3)} 点自然伤害，并使其受到的所有治疗效果降低 {match.group(4)}%，持续 {translate_time(match.group(5))}。同一目标最多叠加 {match.group(6)} 次。{cooldown}"
    match = re.match(r"^Coats a weapon with poison that lasts for (\d+(?:\.\d+)?\s*(?:sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours))\. Each strike has a ([\d,]+)% chance of poisoning the enemy which instantly inflicts ([\d,]+) to ([\d,]+) Nature damage, but causes no additional threat\.?$", body, re.I)
    if match:
        return f"{prefix}给武器涂毒，持续 {translate_time(match.group(1))}。每次攻击有 {match.group(2)}% 几率使敌人中毒，立即造成 {match.group(3)} 到 {match.group(4)} 点自然伤害，但不产生额外威胁值。{cooldown}"
    match = re.match(r"^Inflicts ([\d,]+) to ([\d,]+) (Fire|Holy) damage in a ([\d,]+) yard radius\.?$", body, re.I)
    if match:
        school = "火焰" if match.group(3).lower() == "fire" else "神圣"
        return f"{prefix}对 {match.group(4)} 码范围内的目标造成 {match.group(1)} 到 {match.group(2)} 点{school}伤害。{cooldown}"
    match = re.match(r"^Inflicts ([\d,]+) to ([\d,]+) (Fire|Holy) damage to Undead in a ([\d,]+) yard radius\.?$", body, re.I)
    if match:
        school = "火焰" if match.group(3).lower() == "fire" else "神圣"
        return f"{prefix}对 {match.group(4)} 码范围内的亡灵造成 {match.group(1)} 到 {match.group(2)} 点{school}伤害。{cooldown}"
    match = re.match(r"^Calls down a pillar of fire, burning all enemies within the area for ([\d,]+) to ([\d,]+) Fire damage and an additional ([\d,]+) Fire damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}召下一道火柱，灼烧区域内所有敌人，造成 {match.group(1)} 到 {match.group(2)} 点火焰伤害，并在 {translate_time(match.group(4))} 内额外造成 {match.group(3)} 点火焰伤害。{cooldown}"
    match = re.match(r"^Hurls a fiery ball that causes ([\d,]+) to ([\d,]+) Fire damage and an additional ([\d,]+) Fire damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}投掷一枚火球，造成 {match.group(1)} 到 {match.group(2)} 点火焰伤害，并在 {translate_time(match.group(4))} 内额外造成 {match.group(3)} 点火焰伤害。{cooldown}"
    match = re.match(r"^Inflicts ([\d,]+) to ([\d,]+) Fire damage and stuns targets in a ([\d,]+) yard radius for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Any damage will break the effect\.?$", body, re.I)
    if match:
        return f"{prefix}造成 {match.group(1)} 到 {match.group(2)} 点火焰伤害，并使 {match.group(3)} 码范围内的目标昏迷，持续 {translate_time(match.group(4))}。任何伤害都会打破该效果。{cooldown}"
    match = re.match(r"^A (fairly weak|typical|strong) alcoholic beverage\.?$", body, re.I)
    if match:
        strength = {"fairly weak": "较淡", "typical": "普通", "strong": "烈性"}[match.group(1).lower()]
        return f"{prefix}{strength}的酒精饮料。{cooldown}"
    match = re.match(r"^Cures ([\d,]+) diseases and neutralizes ([\d,]+) poisons\.?$", body, re.I)
    if match:
        return f"{prefix}治愈 {match.group(1)} 个疾病效果，并中和 {match.group(2)} 个毒药效果。{cooldown}"
    if body == "Drink up!":
        return f"{prefix}一饮而尽！{cooldown}"
    match = re.match(r"^Summons a tracking hound that will protect you for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}召唤一只追踪猎犬保护你，持续 {translate_time(match.group(1))}。{cooldown}"
    match = re.match(r"^Absorbs ([\d,]+) to ([\d,]+) (fire|frost|nature|shadow|arcane|holy) damage\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        school_map = {"fire": "火焰伤害", "frost": "冰霜伤害", "nature": "自然伤害", "shadow": "暗影伤害", "arcane": "奥术伤害", "holy": "神圣伤害"}
        school = school_map.get(match.group(3).lower(), replace_terms(match.group(3) + " damage"))
        return f"{prefix}吸收 {match.group(1)} 到 {match.group(2)} 点{school}。持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Inflicts ([\d,]+) to ([\d,]+) Fire damage and knocks the unfortunate victim away\.\.\. Whoever that ends up being\. ?(?:\"(.+)\")?$", body, re.I)
    if match:
        flavor = ("\"" + translate_flavor(match.group(3), objective_names) + "\"") if match.group(3) else ""
        return f"{prefix}造成 {match.group(1)} 到 {match.group(2)} 点火焰伤害，并击退那个不幸的受害者……不管最后是谁。{flavor}{cooldown}"
    match = re.match(r"^When applied to a melee weapon it gives a ([\d,]+)% chance of casting (Shadowbolt III|Frostbolt) at the opponent when it hits\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        spell = {"shadowbolt iii": "暗影箭 III", "frostbolt": "寒冰箭"}[match.group(2).lower()]
        return f"{prefix}涂在近战武器上之后，击中敌人时有 {match.group(1)}% 几率对其施放{spell}。持续 {translate_time(match.group(3))}。{cooldown}"
    match = re.match(r"^When applied to your fishing pole, increases Fishing by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}涂在你的鱼竿上之后，钓鱼技能提高 {match.group(1)} 点，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Your size is increased and your Strength goes up by ([\d,]+) to match your new size\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. Battle Elixir\.?$", body, re.I)
    if match:
        return f"{prefix}你的体型增大，力量提高 {match.group(1)} 点以匹配新的体型。持续 {translate_time(match.group(2))}。战斗药剂。{cooldown}"
    match = re.match(r"^Does ([\d,]+) fire damage to any enemies within a ([\d,]+) yard radius around the caster every (\d+\s*(?:sec|second|seconds|min|minute|minutes)) for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}每 {translate_time(match.group(3))} 对施法者周围 {match.group(2)} 码内的所有敌人造成 {match.group(1)} 点火焰伤害，持续 {translate_time(match.group(4))}。{cooldown}"
    match = re.match(r"^Increases attack power by ([\d,]+) against demons\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. Battle Elixir\.?$", body, re.I)
    if match:
        return f"{prefix}对恶魔的攻击强度提高 {match.group(1)} 点。持续 {translate_time(match.group(2))}。战斗药剂。{cooldown}"
    match = re.match(r"^Place a Battle Standard with ([\d,]+) health that increases the maximum health of all party members that stay within ([\d,]+) yards of the Battle Standard by ([\d,]+)%\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. The Battle Standard may only be used in PvP Battlegrounds\.?$", body, re.I)
    if match:
        return f"{prefix}放置一面拥有 {match.group(1)} 点生命值的战旗，使停留在战旗 {match.group(2)} 码范围内的所有小队成员最大生命值提高 {match.group(3)}%。持续 {translate_time(match.group(4))}。战旗只能在 PvP 战场中使用。{cooldown}"
    match = re.match(r"^Removes one harmful magic effect from the imbiber every 5 seconds for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$", body, re.I)
    if match:
        return f"{prefix}每 5 秒从饮用者身上移除 1 个有害魔法效果，持续 {translate_time(match.group(1))}。{cooldown}"
    match = re.match(r"^Replaces the fishing line on your fishing pole with a delicately spun truesilver line, increasing Fishing skill by ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}将你的鱼竿鱼线替换为精纺真银鱼线，使钓鱼技能提高 {match.group(1)} 点。{cooldown}"
    match = re.match(r"^Stores the friendly target's soul\. If the target dies while his soul is stored, he will be able to resurrect with ([\d,]+) health and ([\d,]+) mana\.?$", body, re.I)
    if match:
        return f"{prefix}储存友方目标的灵魂。如果目标在灵魂被储存期间死亡，将可以复活并恢复 {match.group(1)} 点生命值和 {match.group(2)} 点法力值。{cooldown}"
    match = re.match(r"^Increases resistance to shadow by ([\d,]+)\. If an enemy strikes the imbiber, the attacker has a ([\d,]+)% chance of being inflicted with disease that increases their damage taken by ([\d,]+) for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. Lasts for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. Guardian Elixir\.?$", body, re.I)
    if match:
        return f"{prefix}暗影抗性提高 {match.group(1)} 点。敌人攻击饮用者时，攻击者有 {match.group(2)}% 几率感染疾病，受到的伤害提高 {match.group(3)} 点，持续 {translate_time(match.group(4))}。效果持续 {translate_time(match.group(5))}。守护药剂。{cooldown}"
    match = re.match(r"^Use in Razorfen Kraul near buried tubers to summon a Snufflenose Gopher\.?$", body, re.I)
    if match:
        return f"{prefix}在剃刀沼泽埋藏块茎附近使用，召唤一只嗅地鼠。{cooldown}"
    match = re.match(r"^Place in the Maraudine War Horn, and blow\.?$", body, re.I)
    if match:
        return f"{prefix}放入玛洛迪战斗号角中并吹响。{cooldown}"
    match = re.match(r"^Place at a Witherbark village\.?$", body, re.I)
    if match:
        return f"{prefix}放置在枯木村中。{cooldown}"
    match = re.match(r"^Throw near a patron of the Grim Guzzler\.?$", body, re.I)
    if match:
        return f"{prefix}扔到黑铁酒吧的顾客附近。{cooldown}"
    match = re.match(r"^Attach the pieces into a whole\.?$", body, re.I)
    if match:
        return f"{prefix}将碎片拼合成完整的物件。{cooldown}"
    match = re.match(r"^Throw me!$", body, re.I)
    if match:
        return f"{prefix}把我扔出去！{cooldown}"
    match = re.match(r"^Throw a (blue|green) smoke flare at a specific location that lasts for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        color = "蓝色" if match.group(1).lower() == "blue" else "绿色"
        return f"{prefix}向指定位置投掷一枚{color}烟幕弹，持续 {translate_time(match.group(2))}。{cooldown}"
    match = re.match(r"^Cures ([\d,]+) poison effect\. ?(?:\"(.+)\")?$", body, re.I)
    if match:
        flavor = ("\"" + translate_flavor(match.group(2), objective_names) + "\"") if match.group(2) else ""
        return f"{prefix}解除 {match.group(1)} 个毒药效果。{flavor}{cooldown}"
    match = re.match(r"^Summons an Eye of Kilrogg and\.?\nbinds your vision to it\. The eye moves quickly but is very fragile\.?$", body, re.I)
    if match:
        return f"{prefix}召唤一只基尔罗格之眼，并将你的视野绑定到它身上。眼睛移动很快，但非常脆弱。{cooldown}"
    match = re.match(r"^Use to fill the Egg of Hakkar\.?$", body, re.I)
    if match:
        return f"{prefix}用于装满哈卡之卵。{cooldown}"
    match = re.match(r"^This container should be filled with water from the second tide pool in Azshara\.?$", body, re.I)
    if match:
        return f"{prefix}这个容器应装入艾萨拉第二处潮汐池的水。{cooldown}"
    match = re.match(r"^Use on the Dark Coffer in the Black Vault\.?$", body, re.I)
    if match:
        return f"{prefix}对黑色宝库中的黑暗宝箱使用。{cooldown}"
    match = re.match(r"^Wave over a Fetid skull to test its resonance\.?$", body, re.I)
    if match:
        return f"{prefix}在腐臭颅骨上挥动，以测试它的共鸣。{cooldown}"
    match = re.match(r"^Base and instructions for upgrading a Dark Iron Pick, it says you will need 20 Dark Iron Bars and 4 Arcanite Bars to build a housing and channeling vein for a Burning Essence\. Smithing not required, however a Black Forge is\.?$", body, re.I)
    if match:
        return f"{prefix}升级黑铁镐的底座和说明。上面写着你需要 20 块黑铁锭和 4 块奥金锭，为燃烧精华制作外壳和导流脉络。不需要锻造技能，但需要黑熔炉。{cooldown}"
    match = re.match(r"^This item may only be used in PvP Battlegrounds\.?$", body, re.I)
    if match:
        return f"{prefix}该物品只能在 PvP 战场中使用。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) (health|mana)\. This item may only be used in PvP Battlegrounds\.?$", body, re.I)
    if match:
        resource = "生命值" if match.group(3).lower() == "health" else "法力值"
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点{resource}。该物品只能在 PvP 战场中使用。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health and ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. Usable only in PvP Battlegrounds\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(3))} 内恢复 {match.group(1)} 点生命值和 {match.group(2)} 点法力值。进食时必须保持坐姿。只能在 PvP 战场中使用。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) mana over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while drinking\. Usable only in PvP Battlegrounds and Arenas\. ?(?:\"(.+)\")?$", body, re.I)
    if match:
        flavor = ("\"" + translate_flavor(match.group(3), objective_names) + "\"") if match.group(3) else ""
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点法力值。饮用时必须保持坐姿。只能在 PvP 战场和竞技场中使用。{flavor}{cooldown}"
    match = re.match(r"^Throw (?:the )?(rock|ball) to a friendly (?:target|player)\. If they have free room in their pack they will catch it!$", body, re.I)
    if match:
        obj = "石块" if match.group(1).lower() == "rock" else "球"
        return f"{prefix}将{obj}扔给友方目标。如果对方背包有空位，就会接住它！{cooldown}"
    match = re.match(r"^Place a (solid|dense) stone statue on the ground where it will heal you for a short time before its power fades\.?$", body, re.I)
    if match:
        stone = "坚固" if match.group(1).lower() == "solid" else "厚重"
        return f"{prefix}在地面放置一座{stone}石像，它会在力量消散前短暂治疗你。{cooldown}"
    match = re.match(r"^Exorcises a Koi-Koi Spirit from the targeted Raven's Wood Leafbeard\. Slay the Spirit as quickly as possible, for when you do, you will free the leafbeard and it will no longer be aggressive\.?$", body, re.I)
    if match:
        return f"{prefix}从目标鸦木叶须身上驱除寇寇之灵。尽快击杀这个灵魂，成功后叶须会被解救，并且不再具有攻击性。{cooldown}"
    match = re.match(r"^A delicious grilled treat of questionable nutritional value\. Must remain seated while eating\.?$", body, re.I)
    if match:
        return f"{prefix}一份美味的烤制小吃，营养价值存疑。进食时必须保持坐姿。{cooldown}"
    match = re.match(r"^Use this to cultivate a single Leyline Shard\. They are required by Karanth Ardentis to create enchantments\.?$", body, re.I)
    if match:
        return f"{prefix}用它培育一枚魔脉碎片。卡兰斯·阿登提斯需要这些碎片来制作附魔。{cooldown}"
    match = re.match(r"^Places a Land Mine on the ground\. When a hostile creature passes near, It will explode for ([\d,]+) to ([\d,]+) fire damage and knock them away\. The mine has a duration of (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\. ?(?:\"(.+)\")?$", body, re.I)
    if match:
        flavor = ("\"" + translate_flavor(match.group(4), objective_names) + "\"") if match.group(4) else ""
        return f"{prefix}在地上放置一枚地雷。当敌对生物经过附近时，地雷会爆炸，造成 {match.group(1)} 到 {match.group(2)} 点火焰伤害并将其击退。地雷持续 {translate_time(match.group(3))}。{flavor}{cooldown}"
    match = re.match(r"^Applies a blessing of Elune to the target weapon, increasing Attack Power by ([\d,]+) and Spell Power by ([\d,]+)\. Lasts for (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}为目标武器施加艾露恩的祝福，使攻击强度提高 {match.group(1)} 点、法术强度提高 {match.group(2)} 点。持续 {translate_time(match.group(3))}。{cooldown}"
    match = re.match(r"^Attach an embroidery onto your cloak, increasing (?:your )?(.+?) by ([\d,]+)\. Only the tailor's cloak can be enchanted and enchanting a cloak will cause it to become soulbound\.?$", body, re.I)
    if match:
        stat = match.group(1)
        if re.match(r"damage and healing done by magical spells and effects$", stat, re.I):
            stat = "魔法法术和效果造成的伤害与治疗效果"
        else:
            stat = replace_terms(stat)
        return f"{prefix}将刺绣附着到你的披风上，使{stat}提高 {match.group(2)} 点。只能为裁缝自己的披风附魔，附魔后披风会变为灵魂绑定。{cooldown}"
    match = re.match(r"^Attach an embroidery onto your cloak, increasing damage and healing done by magical spells and effects by ([\d,]+)\. Only the tailor's cloak can be enchanted and enchanting a cloak will cause it to become soulbound\.?$", body, re.I)
    if match:
        return f"{prefix}将刺绣附着到你的披风上，使魔法法术和效果造成的伤害与治疗效果提高 {match.group(1)} 点。只能为裁缝自己的披风附魔，附魔后披风会变为灵魂绑定。{cooldown}"
    match = re.match(r"^Captures a mounted player target up to ([\d,]+) yards away in a net for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.\nRequires Warmode\. Only usable within the Eastern Kingdoms and Kalimdor\.?$", body, re.I)
    if match:
        return f"{prefix}用网捕获最远 {match.group(1)} 码外的骑乘玩家目标，持续 {translate_time(match.group(2))}。\n需要战争模式。只能在东部王国和卡利姆多使用。{cooldown}"
    match = re.match(r"^Increases run speed by ([\d,]+)% for (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.\nRequires Warmode\. Only usable within the Eastern Kingdoms and Kalimdor\.?$", body, re.I)
    if match:
        return f"{prefix}奔跑速度提高 {match.group(1)}%，持续 {translate_time(match.group(2))}。\n需要战争模式。只能在东部王国和卡利姆多使用。{cooldown}"
    match = re.match(r"^Afflicts you with Balefire, burning you for each stack you have\. Melee damage taken has a chance to burn attackers, causing damage for every stack of Balefire you both have\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}使你受到灾火影响，每层灾火都会灼烧你。受到近战伤害时有几率灼烧攻击者，并按双方拥有的灾火层数造成伤害。持续 {translate_time(match.group(1))}。{cooldown}"
    match = re.match(r"^Transfers the Balefire curse from you to an enemy target\. Only usable in the Blasted Lands\.?$", body, re.I)
    if match:
        return f"{prefix}将你身上的灾火诅咒转移给一个敌方目标。只能在诅咒之地使用。{cooldown}"
    match = re.match(r"^Dispels the Balefire curse from a friendly target\.?$", body, re.I)
    if match:
        return f"{prefix}驱散一个友方目标身上的灾火诅咒。{cooldown}"
    match = re.match(r"^Restores ([\d,]+) health over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Must remain seated while eating\. If you spend at least 10 seconds eating you will become well fed and gain ([\d,]+)% movement speed and you will take ([\d,]+) Fire damage every (\d+\s*(?:sec|second|seconds|min|minute|minutes))\. Lasts (\d+\s*(?:sec|second|seconds|min|minute|minutes|hr|hour|hours))\.?$", body, re.I)
    if match:
        return f"{prefix}在 {translate_time(match.group(2))} 内恢复 {match.group(1)} 点生命值。进食时必须保持坐姿。如果进食至少 10 秒，你会获得充分进食效果，移动速度提高 {match.group(3)}%，但每 {translate_time(match.group(5))} 受到 {match.group(4)} 点火焰伤害。持续 {translate_time(match.group(6))}。{cooldown}"

    # --- Comprehensive fallback: translate all known terms in composite lines ---
    translated = replace_terms(translate_time(body)).strip()

    # Slot names that may appear inline
    slot_replacements = [
        ("Main Hand", "主手"), ("Off Hand", "副手"), ("One-Hand", "单手"),
        ("Two-Hand", "双手"), ("Ranged", "远程"), ("Thrown", "投掷"),
        ("Head", "头部"), ("Shoulder", "肩部"), ("Chest", "胸部"),
        ("Legs", "腿部"), ("Hands", "手"), ("Feet", "脚"),
        ("Waist", "腰部"), ("Wrist", "手腕"), ("Back", "背部"),
        ("Finger", "手指"), ("Neck", "颈部"), ("Shirt", "衬衣"),
        ("Tabard", "战袍"), ("Trinket", "饰品"), ("Relic", "圣物"),
    ]
    for en, cn in slot_replacements:
        translated = re.sub(rf"\b{re.escape(en)}\b", cn, translated)

    # Common tooltip terms
    tooltip_terms = [
        ("Item Level", "物品等级"),
        ("Requires Level", "需要等级"),
        ("damage per second", "每秒伤害"),
        ("Damage", "伤害"),
        ("Speed", "速度"),
        ("Armor", "护甲"),
        ("Block", "格挡"),
        ("Durability", "耐久度"),
        ("Begins a quest", "开始一个任务"),
        ("Unique-Equipped", "唯一装备"),
        ("Random Enchantment", "随机附魔"),
        ("Retrieving item information", "正在获取物品信息"),
        ("Binds when equipped", "装备后绑定"),
        ("Binds when picked up", "拾取后绑定"),
        ("Binds when used", "使用后绑定"),
        ("Binds to account", "账号绑定"),
        ("Quest Item", "任务物品"),
        ("Conjured Item", "魔法制造的物品"),
        ("per second", "每秒"),
        ("per 5 sec", "每 5 秒"),
        ("Improves your chance to get a critical strike with spells by", "法术爆击几率提高"),
        ("Improves your chance to get a critical strike with melee and ranged attacks by", "近战和远程攻击爆击几率提高"),
        ("Improves your chance to get a critical strike with all spells and attacks by", "所有法术和攻击的爆击几率提高"),
        ("Improves your chance to hit with spells by", "法术命中几率提高"),
        ("Improves your chance to hit with melee and ranged attacks by", "近战和远程攻击命中几率提高"),
        ("Improves your chance to hit with all spells and attacks by", "所有法术和攻击的命中几率提高"),
        ("Improves your casting speed and causes periodic effects to occur more frequently with spells by", "法术施放速度提高，且周期性法术效果触发频率提高"),
        ("Increases damage and healing done by magical spells and effects by up to", "魔法法术和效果造成的伤害与治疗效果最多提高"),
        ("Increases damage done by Arcane spells and effects by up to", "奥术法术和效果造成的伤害最多提高"),
        ("Increases damage done by Fire spells and effects by up to", "火焰法术和效果造成的伤害最多提高"),
        ("Increases damage done by Frost spells and effects by up to", "冰霜法术和效果造成的伤害最多提高"),
        ("Increases damage done by Holy spells and effects by up to", "神圣法术和效果造成的伤害最多提高"),
        ("Increases damage done by Nature spells and effects by up to", "自然法术和效果造成的伤害最多提高"),
        ("Increases damage done by Shadow spells and effects by up to", "暗影法术和效果造成的伤害最多提高"),
        ("Increases damage done by magical spells and effects by up to", "魔法法术和效果造成的伤害最多提高"),
        ("Increases healing done by up to", "治疗效果最多提高"),
        ("damage done by up to", "伤害最多提高"),
        ("for all magical spells and effects", "（所有魔法法术和效果）"),
        ("Increases your chance to dodge an attack by", "躲闪几率提高"),
        ("Increases your chance to block attacks with a shield by", "盾牌格挡几率提高"),
        ("Increases your chance to parry an attack by", "招架几率提高"),
        ("Increased Defense", "防御等级提高"),
        ("Increased Fishing", "钓鱼技能提高"),
        ("Increases attack power by", "攻击强度提高"),
        ("Increases ranged attack power by", "远程攻击强度提高"),
        ("Increases ranged attack speed by", "远程攻击速度提高"),
        ("Decreases the magical resistances of your spell targets by", "你的法术目标的魔法抗性降低"),
        ("Restores", "恢复"),
        ("health per 5 sec", "生命值/每5秒"),
        ("mana per 5 sec", "法力值/每5秒"),
        ("Run speed increased slightly", "奔跑速度略微提高"),
        ("Reduces the chance movement impairing effects will be resisted by", "移动减速效果被抵抗的几率降低"),
        ("your chance to be dodged or parried by", "你的攻击被躲闪或招架的几率降低"),
    ]
    for en, cn in tooltip_terms:
        translated = translated.replace(en, cn)

    translated = normalize_mixed_consumable_text(translated.strip(), objective_names)
    translated = re.sub(r"\bDrink up!\b", "一饮而尽！", translated)
    translated = re.sub(r"\bOnly one instance of this 效果 can be active at a time\b", "同一时间只能激活一个该效果", translated, flags=re.I)
    translated = re.sub(r"\bRequires a level (\d+) or higher 物品\b", r"需要等级 \1 或更高的物品", translated, flags=re.I)
    if prefix or translated != body:
        if not re.search(r"[。.!?]$", translated):
            translated += "。"
        return prefix + translated + cooldown
    return original


def normalize_raw_lines(lines):
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line = (line or "").strip()
        if not line:
            i += 1
            continue
        if line == "Use: Summons an Eye of Kilrogg and" and i + 1 < len(lines):
            nxt = (lines[i + 1] or "").strip()
            if nxt.startswith("binds your vision to it."):
                result.append(line + "\n" + nxt)
                i += 2
                continue
        match = re.match(r'^(.*?\([^)]*Cooldown\))\s+("[^"]+")$', line)
        if match:
            result.append(match.group(1).strip())
            result.append(match.group(2).strip())
            i += 1
            continue
        match = re.match(r"^(Requires [^(]+ \([^)]*\))\s+(Use: .+)$", line)
        if match:
            result.append(match.group(1).strip())
            result.append(match.group(2).strip())
            i += 1
            continue
        match = re.match(r"^(Races: .+?Blood Elf)\s+(Use: .+)$", line)
        if match:
            result.append(match.group(1).strip())
            result.append(match.group(2).strip())
        else:
            result.append(line)
        i += 1
    return result


def main():
    items = json.loads(CACHE.read_text(encoding="utf-8"))
    existing_items = load_item_data()
    objective_names = load_objective_names()
    rows = []

    for item in sorted(items, key=lambda x: int(x["id"])):
        item_id = int(item["id"])
        en_name = item.get("name") or ""
        base = existing_items.get(item_id)
        cn_name = base[0] if base and has_cn(base[0]) else translate_name(en_name, existing_items, objective_names)

        raw_lines = [line for line in normalize_raw_lines(item.get("tooltip") or []) if line and line != en_name]
        translated_pairs = []
        for line in raw_lines:
            translated = translate_line(line, objective_names)
            if translated:
                translated_pairs.append((line, translated))

        generated_desc = "\n".join(pair[1] for pair in translated_pairs)
        base_desc = base[1] if base and has_cn(base[1]) else ""
        desc = base_desc or generated_desc
        if not desc:
            desc = "数据库未提供可见使用效果说明。"
        source = "EpochHead 消耗品"
        rows.append((item_id, cn_name, desc, source, en_name, translated_pairs))

    lines = [
        "-- Generated by Tools/generate_epoch_consumables.py.",
        "-- Source: https://epochhead.com/items?class=consumable",
        "function LoadEpochCNConsumableData()",
        "  EpochCN_ConsumableData = {",
    ]
    for item_id, cn_name, desc, source, en_name, translated_pairs in rows:
        pairs = []
        for raw, translated in translated_pairs:
            if raw != translated:
                pairs.append(f'["{lua_escape(raw)}"] = "{lua_escape(translated)}"')
        map_literal = "{ " + ", ".join(pairs) + " }" if pairs else "{}"
        lines.append(
            f'    [{item_id}] = {{"{lua_escape(cn_name)}", "{lua_escape(desc)}", "{lua_escape(source)}", "consumable", {map_literal}, "{lua_escape(en_name)}"}},'
        )
    lines.extend([
        "  }",
        "end",
        "",
    ])
    OUT.write_text("\n".join(lines), encoding="utf-8")

    missing_names = sum(1 for _, name, *_ in rows if not has_cn(name))
    missing_desc = sum(1 for _, _, desc, *_ in rows if not has_cn(desc))
    print(f"wrote {OUT}")
    print(f"items={len(rows)} missing_cn_names={missing_names} missing_cn_desc={missing_desc}")


if __name__ == "__main__":
    main()
