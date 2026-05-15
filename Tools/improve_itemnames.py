#!/usr/bin/env python3
"""
ItemNameMap 物品名称改进脚本。
通过模式匹配翻译以下类型的物品名：
1. PvP 套装名（Gladiator→角斗士, Wrathful→愤怒的）
2. 装备部件名（Gloves→手套, Boots→靴子）
3. 图纸/配方前缀（Pattern→图纸, Design→设计图）
4. 常见物品后缀/前缀
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"

def has_cjk(s):
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s or "")

def is_english(s):
    return bool(re.search(r'[A-Za-z]', s or "")) and not has_cjk(s)

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def unesc(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

# PvP season prefixes
PVP_PREFIXES = {
    "Gladiator's": "角斗士的",
    "Merciless Gladiator's": "残酷角斗士的",
    "Vengeful Gladiator's": "复仇角斗士的",
    "Brutal Gladiator's": "野蛮角斗士的",
    "Hateful Gladiator's": "仇恨角斗士的",
    "Deadly Gladiator's": "致命角斗士的",
    "Furious Gladiator's": "狂怒角斗士的",
    "Relentless Gladiator's": "无情角斗士的",
    "Wrathful Gladiator's": "愤怒角斗士的",
    # Honor gear
    "Savage Gladiator's": "野蛮角斗士的",
    "Titan-Forged": "泰坦铸造",
    "Wintergrasp": "冬拥湖",
}

# Equipment slot names
EQUIPMENT_SLOTS = {
    "Helm": "头盔", "Helmet": "头盔", "Hood": "兜帽", "Crown": "王冠",
    "Headpiece": "头饰", "Headguard": "护头", "Coif": "头巾",
    "Circlet": "头环", "Cowl": "兜帽", "Faceguard": "面甲",
    "Visor": "面甲", "Headband": "头带", "Cap": "帽子",
    "Shoulderpads": "护肩", "Shoulderguards": "护肩", "Shoulders": "护肩",
    "Pauldrons": "肩铠", "Spaulders": "肩甲", "Mantle": "披肩",
    "Shoulderplates": "肩板", "Epaulets": "肩章",
    "Chestpiece": "胸甲", "Chestguard": "胸甲", "Chestplate": "胸铠",
    "Breastplate": "胸甲", "Tunic": "外衣", "Robes": "长袍",
    "Robe": "长袍", "Hauberk": "锁甲", "Vest": "背心",
    "Jerkin": "皮甲", "Vestments": "法衣", "Raiment": "圣衣",
    "Legguards": "护腿", "Leggings": "护腿", "Legplates": "腿铠",
    "Legwraps": "绑腿", "Pants": "裤子", "Kilt": "战裙",
    "Greaves": "胫甲", "Trousers": "裤子", "Breeches": "马裤",
    "Gauntlets": "护手", "Gloves": "手套", "Handguards": "护手",
    "Grips": "握套", "Mitts": "手套", "Grasps": "手套",
    "Fists": "拳套", "Handwraps": "手包",
    "Boots": "靴子", "Sabatons": "马靴", "Treads": "战靴",
    "Footguards": "护足", "Footwraps": "裹足", "Sandals": "凉鞋",
    "Slippers": "便鞋", "Stompers": "重靴", "Shoes": "鞋子",
    "Belt": "腰带", "Girdle": "束腰", "Waistguard": "护腰",
    "Cord": "腰绳", "Sash": "腰带", "Cinch": "束带",
    "Waistband": "腰带",
    "Bracers": "护腕", "Wristguards": "护腕", "Cuffs": "袖口",
    "Armguards": "臂甲", "Bindings": "绑带", "Wristbands": "腕带",
    "Vambraces": "护臂", "Armwraps": "臂包",
    "Cloak": "披风", "Cape": "斗篷", "Drape": "披风",
    "Shroud": "裹布",
    # Weapons
    "Sword": "剑", "Axe": "斧", "Mace": "锤",
    "Dagger": "匕首", "Staff": "法杖", "Polearm": "长柄武器",
    "Bow": "弓", "Gun": "枪", "Crossbow": "弩",
    "Wand": "魔杖", "Shield": "盾牌", "Fist Weapon": "拳套",
    "Thrown": "投掷武器",
    "Blade": "利刃", "Cleaver": "砍刀", "Hatchet": "手斧",
    "Hammer": "锤子", "Scepter": "权杖", "Gavel": "法槌",
    "Spear": "矛", "Pike": "长矛", "Halberd": "戟",
    "Longbow": "长弓", "Shortbow": "短弓", "Rifle": "步枪",
    "Musket": "火枪", "Shanker": "刺刀", "Shiv": "小刀",
    # Accessories
    "Ring": "戒指", "Band": "指环", "Signet": "印戒",
    "Loop": "环", "Seal": "封印",
    "Necklace": "项链", "Pendant": "坠饰", "Amulet": "护符",
    "Choker": "项圈", "Chain": "链子", "Medallion": "徽章",
    "Trinket": "饰品", "Idol": "神像", "Totem": "图腾",
    "Libram": "圣契", "Sigil": "符印",
    # Suffixes
    "of the Phoenix": "凤凰之", "of the Eagle": "鹰之",
    "of the Bear": "熊之", "of the Whale": "鲸鱼之",
    "of the Owl": "猫头鹰之", "of the Monkey": "猴子之",
    "of the Tiger": "老虎之", "of the Gorilla": "猩猩之",
    "of the Boar": "野猪之", "of the Falcon": "猎鹰之",
    "of the Wolf": "狼之", "of the Bandit": "强盗之",
    "of Salvation": "救赎之", "of Dominance": "统御之",
    "of Triumph": "凯旋之", "of Conquest": "征服之",
    "of the Third Wind": "狂风之", "of Indomitability": "无畏之",
    "of the Leviathan": "利维坦之", "of Subjugation": "征服之",
}

# Crafting prefixes
CRAFTING_PREFIXES = {
    "Pattern:": "图纸：", "Pattern: ": "图纸：",
    "Plans:": "设计图：", "Plans: ": "设计图：",
    "Schematic:": "结构图：", "Schematic: ": "结构图：",
    "Formula:": "公式：", "Formula: ": "公式：",
    "Recipe:": "配方：", "Recipe: ": "配方：",
    "Design:": "设计图：", "Design: ": "设计图：",
    "Manual:": "手册：", "Manual: ": "手册：",
    "Technique:": "技术：", "Technique: ": "技术：",
    "Book of:": "之书：", "Book of ": "之书：",
}

# Material/quality prefixes for items
MATERIAL_PREFIXES = {
    "Titansteel": "泰坦钢", "Saronite": "萨隆邪铁",
    "Cobalt": "钴蓝", "Frostweave": "霜纹",
    "Imbued Frostweave": "灌注霜纹", "Moonshroud": "月布",
    "Spellweave": "魔纹", "Ebonweave": "乌纹",
    "Borean": "北地", "Nerubian": "蛛魔",
    "Frosthide": "霜皮", "Iceborne": "冰铸",
    "Stormhide": "风暴皮", "Swiftarrow": "迅箭",
    "Overcast": "阴云", "Duskweave": "暮纹",
}


def translate_item_name(english: str) -> str | None:
    """Try to translate an item name using pattern matching."""
    if not english or not is_english(english):
        return None

    # Skip test/deprecated items
    skip_re = re.compile(
        r'DEPRECATED|deprecated|UNUSED|Unused|\(PH\)|Placeholder|'
        r'\bTEST\b|DND|\[DND\]|DEBUG|Monster -|<UNUSED|<TXT>|<NYI>|'
        r'<TEST>|PLACEHOLDER|^\[|^OLD[A-Z]|\(old\)|\(Old\)',
        re.IGNORECASE
    )
    if skip_re.search(english):
        return None

    # Strategy 1: PvP prefix + equipment slot
    for prefix, prefix_zh in sorted(PVP_PREFIXES.items(), key=lambda x: -len(x[0])):
        if english.startswith(prefix + " "):
            remainder = english[len(prefix) + 1:]
            # Try to translate the remainder (equipment slot + suffix)
            translated_remainder = translate_equipment_part(remainder)
            if translated_remainder:
                return prefix_zh + translated_remainder
            # Even if we can't translate the remainder fully, translate what we can
            break

    # Strategy 2: Crafting prefix
    for prefix, prefix_zh in sorted(CRAFTING_PREFIXES.items(), key=lambda x: -len(x[0])):
        if english.startswith(prefix):
            remainder = english[len(prefix):].strip()
            # Try to translate the crafted item name
            translated_remainder = translate_equipment_part(remainder)
            if translated_remainder:
                return prefix_zh + translated_remainder
            break

    # Strategy 3: Simple equipment name (Slot + of the X)
    translated = translate_equipment_part(english)
    if translated:
        return translated

    return None


def translate_equipment_part(text: str) -> str | None:
    """Translate an equipment name like 'Leather Boots of the Bear'."""
    if not text:
        return None

    # Check for suffix first
    suffix_zh = ""
    base = text
    for suffix, s_zh in sorted(EQUIPMENT_SLOTS.items(), key=lambda x: -len(x[0])):
        if text.endswith(" " + suffix):
            # This is a suffix like "of the Phoenix"
            pass

    # Try: [Material] [Slot] [of the X]
    # Split off "of the/of" suffix
    of_match = re.search(r'\s+(of\s+(?:the\s+)?\w+)$', text)
    of_zh = ""
    if of_match:
        of_part = of_match.group(1)
        # Check if we know this suffix
        for suffix, s_zh in sorted(EQUIPMENT_SLOTS.items(), key=lambda x: -len(x[0])):
            if of_part == suffix or ("of " in suffix and of_part.lower() == suffix.lower()):
                of_zh = s_zh
                break
        base = text[:of_match.start()]
    else:
        base = text

    # Try to match the base as [Material] [Slot] or just [Slot]
    slot_zh = None
    material_zh = ""

    # Check for slot match (longest first)
    for slot, sl_zh in sorted(EQUIPMENT_SLOTS.items(), key=lambda x: -len(x[0])):
        if base == slot:
            slot_zh = sl_zh
            break
        if base.endswith(" " + slot):
            material_part = base[:-(len(slot) + 1)]
            # Try to translate material
            for mat, m_zh in sorted(MATERIAL_PREFIXES.items(), key=lambda x: -len(x[0])):
                if material_part == mat:
                    material_zh = m_zh
                    slot_zh = sl_zh
                    break
            if slot_zh:
                break
            # Even without material translation, if it's a known slot, accept
            slot_zh = sl_zh
            material_zh = material_part + " "  # Keep English material
            break

    if slot_zh:
        result = material_zh + slot_zh
        if of_zh:
            result += of_zh
        # Only return if we actually translated something meaningful
        if has_cjk(result):
            return result

    return None


def main():
    # Load current ItemNameMap
    inm_path = DATA / "ItemNameMap.lua"
    with open(inm_path, encoding="utf-8") as f:
        inm_text = f.read()

    # Parse existing entries
    existing = {}
    for m in re.finditer(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', inm_text):
        existing[unesc(m.group(1))] = unesc(m.group(2))

    # Load all item names from data files
    all_english_items = set()
    for fname in ["ItemData.lua", "EpochConsumableData.lua", "EpochItemData.lua"]:
        fpath = DATA / fname
        if fpath.exists():
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
            names = re.findall(r'\[\d+\]\s*=\s*\{"((?:[^"\\]|\\.)*)"', text)
            for name in names:
                name = unesc(name)
                if is_english(name) and name not in existing:
                    all_english_items.add(name)

    # Also check ObjectiveNameData for item translations we can use
    obj_path = DATA / "ObjectiveNameData.lua"
    with open(obj_path, encoding="utf-8") as f:
        obj_text = f.read()
    obj_pairs = re.findall(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', obj_text)
    obj_map = {unesc(k): unesc(v) for k, v in obj_pairs if has_cjk(unesc(v))}

    # Try to translate unmapped items
    new_mappings = {}
    method_counts = {"objective": 0, "pattern": 0}

    for name in sorted(all_english_items):
        # First try ObjectiveNameData
        if name in obj_map:
            new_mappings[name] = obj_map[name]
            method_counts["objective"] += 1
            continue

        # Then try pattern-based translation
        translated = translate_item_name(name)
        if translated and has_cjk(translated):
            new_mappings[name] = translated
            method_counts["pattern"] += 1

    # Now also add PvP gear translations for items already in the map
    # that have English values (meaning they weren't translated)
    pvp_additions = 0
    for en, zh in list(existing.items()):
        if has_cjk(zh):
            continue  # Already translated
        translated = translate_item_name(en)
        if translated and has_cjk(translated):
            new_mappings[en] = translated
            pvp_additions += 1

    print(f"=== ItemNameMap 改进结果 ===")
    print(f"现有条目: {len(existing)}")
    print(f"新增翻译: {len(new_mappings)}")
    print(f"  - ObjectiveNameData: {method_counts['objective']}")
    print(f"  - 模式匹配: {method_counts['pattern']}")
    print(f"  - PvP/装备修正: {pvp_additions}")

    if new_mappings:
        # Add new entries to the ItemNameMap
        # Find the insertion point (before the closing of EpochCN_ItemNameMap)
        # We'll add them to the existing map
        insert_marker = "  EpochCN_ItemSearchAliases = {"
        if insert_marker in inm_text:
            new_entries = ""
            for en, zh in sorted(new_mappings.items()):
                new_entries += f'    ["{esc(en)}"] = "{esc(zh)}",\n'
            # Insert before the search aliases section
            inm_text = inm_text.replace(
                insert_marker,
                new_entries + "  }\n" + insert_marker,
                1
            )
            # Wait, that would break the structure. Let me find the right spot.
            pass

        # Better approach: insert new entries before the closing "}" of EpochCN_ItemNameMap
        # Find "  }\n  EpochCN_ItemSearchAliases"
        close_pattern = "  }\n  EpochCN_ItemSearchAliases"
        if close_pattern in inm_text:
            new_entries = ""
            for en, zh in sorted(new_mappings.items()):
                new_entries += f'    ["{esc(en)}"] = "{esc(zh)}",\n'
            inm_text = inm_text.replace(
                close_pattern,
                new_entries + close_pattern,
                1
            )

        with open(inm_path, "w", encoding="utf-8") as f:
            f.write(inm_text)

        print(f"\n[OK] 已写入 {len(new_mappings)} 条新映射到 ItemNameMap.lua")

        # Show samples
        print(f"\n示例 (前20条):")
        for en, zh in sorted(new_mappings.items())[:20]:
            print(f"  {en} → {zh}")


if __name__ == "__main__":
    main()
