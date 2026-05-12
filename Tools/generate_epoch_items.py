#!/usr/bin/env python3
"""Generate Data/EpochItemData.lua from the all-item EpochHead cache."""

from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import re


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "SourceData" / "EpochHead" / "items" / "items.json"
CACHE = ROOT / "Tools" / "cache" / "epochhead_items" / "items.json"
OUT = ROOT / "Data" / "EpochItemData.lua"
ITEM_DATA = ROOT / "Data" / "ItemData.lua"
ITEM_NAME_MAP = ROOT / "Data" / "ItemNameMap.lua"
CONSUMABLE_GENERATOR = ROOT / "Tools" / "generate_epoch_consumables.py"


spec = importlib.util.spec_from_file_location("generate_epoch_consumables", CONSUMABLE_GENERATOR)
consumables = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(consumables)


STRING = r'"((?:\\.|[^"\\])*)"'


def has_cn(text: str) -> bool:
    return bool(text and re.search(r"[\u4e00-\u9fff]", text))


def has_ascii_letters(text: str) -> bool:
    return bool(text and re.search(r"[A-Za-z]", text))


def is_skipped_english_name(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return True
    if re.match(r"^Item \d+$", text, re.I):
        return True
    return bool(re.search(r"(Deprecated|Unused|OLD|Monster -|\(TEST\)|\bTEST\b)", text, re.I))


def lua_unescape(text: str) -> str:
    return consumables.lua_unescape(text)


def lua_escape(text: str) -> str:
    return consumables.lua_escape(text)


SCHOOL = {
    "Arcane": "奥术",
    "Fire": "火焰",
    "Frost": "冰霜",
    "Holy": "神圣",
    "Nature": "自然",
    "Shadow": "暗影",
}

PROC_NAMES = {
    "Flaming Cannonball": "烈焰炮弹",
    "Frost Arrow": "冰霜箭",
    "Keeper's Sting": "守护者之刺",
    "Searing Arrow": "灼热箭",
}


def translate_proc_name(name: str) -> str:
    name = re.sub(r"^(?:a|an|the)\s+", "", name or "", flags=re.I)
    return PROC_NAMES.get(name, name)

ROMAN_NUMERAL = {
    "I": "一",
    "II": "二",
    "III": "三",
    "IV": "四",
    "V": "五",
    "VI": "六",
    "VII": "七",
    "VIII": "八",
    "IX": "九",
    "X": "十",
}

DIRECT_ITEM_NAMES = {
    'Fire Sword of Crippling': '致残火焰剑',
    'Tablet of Serpent Totem': '毒蛇图腾石板',
    'BKP 2700 \\"Enforcer\\"': '执法者霰弹枪',
    'BKP 42 \\"Ultra\\"': '超级霰弹枪',
    'BKP \\"Sparrow\\" Smallbore': '麻雀小口径步枪',
    'NG-5 Explosives (Red)': '五号炸药（红色）',
    'NG-5 Explosives (Blue)': '五号炸药（蓝色）',
    'NG-5': '五号炸药',
    'Model 4711-FTZ Power Source': '四七一一型动力源',
    'OOX-17/TN Distress Beacon': '欧欧艾克斯十七号塔纳利斯求救信标',
    'OOX-09/HL Distress Beacon': '欧欧艾克斯九号辛特兰求救信标',
    'OOX-22/FE Distress Beacon': '欧欧艾克斯二十二号菲拉斯求救信标',
    'Super Snapper FX': '超级拍摄器',
    'Techbot CPU Shell': '尖端机器人的核心外壳',
    'M73 Frag Grenade': '七三式破片手雷',
    'Field Repair Bot 74A': '七四甲型战地修理机器人',
    'Biznicks 247x128 Accurascope': '比兹尼克二四七乘一二八精确瞄准镜',
    'Goblin Jumper Cables XL': '高级地精起搏器',
    'Schematic: Goblin Jumper Cables XL': '结构图：高级地精起搏器',
    'Ez-Thro Dynamite II': '简易投掷炸药二型',
    'Schematic: EZ-Thro Dynamite II': '结构图：简易投掷炸药二型',
    "Nat Pagle's Extreme Angler FC-5000": '纳特·帕格的五千型超级钓鱼竿',
    'Arena Team Charter (2v2)': '二对二竞技场战队登记表',
    'Book of Ferocious Bite V': '凶猛撕咬教程五',
    'Manual of Eviscerate IX': '剔骨手册九',
    'Codex: Levitate II': '漂浮术秘典二',
    'Mecha X-850 "Squawker" Rifle': '八五零型尖啸者机械步枪',
    'Weird Thing': '奇怪的东西',
    "Bonzo's Brass Buttons": '邦佐的黄铜纽扣',
    'Feathered Cap of Deflection': '偏斜羽饰帽',
    'Crestfall Crab Taco': '克雷斯特福蟹肉玉米卷',
    'Recipe: Crestfall Crab Taco': '食谱：克雷斯特福蟹肉玉米卷',
    'Tome of Conjure Water VII': '造水术宝典七',
    "Engineer's Tunic": '工程师外套',
    "Skirmisher's Treads": '散兵便鞋',
    "Skirmisher's Bracers": '散兵护腕',
    "Skirmisher's Cinch": '散兵腰带',
    'Pattern: Onyxia Scale Mask': '图样：奥妮克希亚鳞片面具',
    'Venture Co. Tredders': '风险投资公司长靴',
    'Hemovac Max': '大型血液收集器',
    'SI:7 Shiv': '军情七处短匕',
    'Formula: Enchant 2H Weapon - Elusive': '公式：附魔双手武器 - 飘忽',
    'Formula: Enchant Weapon - Panacea': '公式：附魔武器 - 万应',
    'Revil\'s "Special" Tools.': '雷维尔的“特殊”工具',
    'Brightwood Bloom': '亮木花',
    "Serae's Final Experiment": '塞瑞的最终实验',
    "Nelle's Diary": '内尔的日记',
    'Cask of Brightwood White': '一桶亮木白葡萄酒',
    'SI:7 Standard Staff': '军情七处制式法杖',
    'SI:7 Standard Firearm': '军情七处制式枪械',
    'SI:7 Standard Shield': '军情七处制式盾牌',
    'Daltry Perfume': '达尔特里的香水',
    'Daltry Lantern': '达尔特里的灯笼',
    'Daltry Book': '达尔特里的书',
    'Daltry Jewelry': '达尔特里的珠宝',
    'Tremormatic MK I': '震颤仪一型',
    'Tremormatic MK II': '震颤仪二型',
    'Tremormatic MK III': '震颤仪三型',
    'Beezil Location Clue I': '比兹尔位置线索一',
    'Beezil Location Clue II': '比兹尔位置线索二',
    'Beezil Location Clue III': '比兹尔位置线索三',
    'Sniffotron Kit': '嗅探器套件',
    'Sniffotron MK IV': '嗅探器四型',
    'Marai\'s "Supplies"': '玛莱的“补给品”',
    'Marai\'s "Supplies" Leftovers': '玛莱“补给品”的剩余物',
    'Hazzali Wasp Stinger': '哈扎里黄蜂毒刺',
    'Box of Aru-Talis Research Materials': '一箱阿鲁塔利斯研究材料',
    "J.D. Collie's Report": '科里的报告',
    'Sea Shanty Shinkickers': '海歌踢胫靴',
    'G.E.A.R. Galoshes': '齿轮套鞋',
    'G.E.A.R. Gaiters': '齿轮护胫',
    'G.E.A.R. Gloves': '齿轮手套',
    'G.E.A.R. Guards': '齿轮护腕',
    'G.E.A.R. Girdle': '齿轮腰带',
    "Layla Sprocketspark's Report": '莱拉·扳火花的报告',
    'G.E.A.R. Sword': '齿轮剑',
    'G.E.A.R. Dagger': '齿轮匕首',
    'G.E.A.R. Mace': '齿轮锤',
    'G.E.A.R. Staff': '齿轮法杖',
    'G.E.A.R. Robes': '齿轮长袍',
    'G.E.A.R. Vest': '齿轮外衣',
    'EZ-Thro "Da Bomba"': '易投“大炸弹”',
    'Drakonid Horn': '龙人号角',
    "Contender's Waistband of Spellcasting": '竞争者的施法腰带',
    "Contender's Wrists of Assault": '竞争者的突袭护腕',
    "Contender's Wrists of Spellcasting": '竞争者的施法护腕',
    "Contender's Wrists of Preservation": '竞争者的守护护腕',
    "Contender's Truthful Helm": '竞争者的真诚头盔',
    "Contender's Truthful Spaulders": '竞争者的真诚肩铠',
    "Contender's Truthful Breastplate": '竞争者的真诚胸甲',
    "Contender's Truthful Gauntlets": '竞争者的真诚护手',
    "Contender's Truthful Legplates": '竞争者的真诚腿铠',
    "Contender's Truthful Boots": '竞争者的真诚战靴',
    'Medallion of Gnomeregan': '诺莫瑞根奖章',
    "Medallion of Sen'jin": '森金奖章',
    'Formula: Lesson of the Doom Lord': '公式：末日领主的教训',
    'Requires Week 3 of PvP Season': '需要玩家对战赛季第三周',
    'Grumbscrew Supply Box': '格拉姆螺钉补给箱',
    'Yeyewata Supply Box': '叶叶瓦塔补给箱',
    'Grumbscrew Merit Token': '格拉姆螺钉功绩徽记',
    'Yeyewata Merit Token': '叶叶瓦塔功绩徽记',
}

NAME_WORDS = {
    "Agility": "敏捷",
    "Protection": "防护",
    "Stamina": "耐力",
    "Spirit": "精神",
    "Strength": "力量",
    "Intellect": "智力",
    "Restoration": "复原术",
    "Mind-numbing Poison": "麻痹毒药",
}


def load_item_data() -> dict[int, tuple[str, str, str]]:
    result: dict[int, tuple[str, str, str]] = {}
    row_re = re.compile(r"\[(\d+)\]\s*=\s*\{\s*" + STRING + r"\s*,\s*" + STRING + r"\s*,\s*" + STRING)
    for match in row_re.finditer(ITEM_DATA.read_text(encoding="utf-8", errors="replace")):
        result[int(match.group(1))] = tuple(lua_unescape(match.group(i)) for i in (2, 3, 4))
    return result


def load_name_map() -> dict[str, str]:
    result: dict[str, str] = {}
    row_re = re.compile(r"\[\s*" + STRING + r"\s*\]\s*=\s*" + STRING)
    text = ITEM_NAME_MAP.read_text(encoding="utf-8", errors="replace")
    first_table = text.split("EpochCN_ItemSearchAliases", 1)[0]
    for match in row_re.finditer(first_table):
            result[lua_unescape(match.group(1))] = lua_unescape(match.group(2))
    return result


def normalize_item_name_key(name: str) -> str:
    return (name or "").replace('\\"', '"').strip()


def zh_roman(value: str) -> str:
    return ROMAN_NUMERAL.get(value.upper(), value)


def clean_generated_name(name: str) -> str:
    return re.sub(r"\s+", "", name or "").strip()


def translate_item_name(name: str, existing_items: dict[int, tuple[str, str, str]], objective_names: dict[str, str]) -> str:
    key = normalize_item_name_key(name)
    direct_key = key.replace('"', '\\"')
    if direct_key in DIRECT_ITEM_NAMES:
        return DIRECT_ITEM_NAMES[direct_key]
    if key in DIRECT_ITEM_NAMES:
        return DIRECT_ITEM_NAMES[key]
    if key in objective_names and has_cn(objective_names[key]) and not has_ascii_letters(objective_names[key]):
        return objective_names[key]

    translated = consumables.translate_name(name, existing_items, objective_names)
    if translated and has_cn(translated):
        translated = re.sub(r"\b(IX|VIII|VII|VI|IV|III|II|X|V|I)\b", lambda m: zh_roman(m.group(1)), translated)
        if not has_ascii_letters(translated):
            return clean_generated_name(translated)

    match = re.match(r"^Scroll of (Agility|Protection|Stamina|Spirit|Strength|Intellect) (I|II|III|IV|V|VI|VII|VIII|IX|X)$", key)
    if match:
        return f"{NAME_WORDS[match.group(1)]}卷轴{zh_roman(match.group(2))}"
    match = re.match(r"^Tablet of Restoration (I|II|III|IV|V|VI|VII|VIII|IX|X)$", key)
    if match:
        return f"复原术石板{zh_roman(match.group(1))}"
    match = re.match(r"^Mind-numbing Poison (I|II|III|IV|V|VI|VII|VIII|IX|X)$", key)
    if match:
        return f"麻痹毒药{zh_roman(match.group(1))}"
    match = re.match(r"^Defias Notes - (I|II|III|IV|V|VI|VII|VIII|IX|X)$", key)
    if match:
        return f"迪菲亚笔记（{zh_roman(match.group(1))}）"

    for prefix, cn_prefix in [
        ("Recipe: ", "食谱："),
        ("Formula: ", "公式："),
        ("Pattern: ", "图样："),
        ("Schematic: ", "结构图："),
        ("Book of ", "书籍："),
        ("Manual of ", "手册："),
        ("Codex: ", "秘典："),
        ("Tome of ", "宝典："),
    ]:
        if key.startswith(prefix):
            inner = translate_item_name(key[len(prefix):], existing_items, objective_names)
            if inner and has_cn(inner) and not has_ascii_letters(inner):
                return cn_prefix + inner

    return ""


def translate_effect_line(line: str, objective_names: dict[str, str]) -> str:
    text = (line or "").strip()
    prefix = ""
    body = text
    for raw_prefix, cn_prefix in [
        ("Equip: ", "装备："),
        ("Chance on hit: ", "击中时可能："),
        ("Use: ", "使用："),
    ]:
        if body.startswith(raw_prefix):
            prefix = cn_prefix
            body = body[len(raw_prefix):]
            break

    cooldown = ""
    cool = re.search(r"\((\d+\s*(?:Sec|Second|Seconds|Min|Minute|Minutes|Hr|Hour|Hours)) Cooldown\)$", body, re.I)
    if cool:
        cooldown = f"（{consumables.translate_time(cool.group(1))}冷却）"
        body = body[:cool.start()].strip()

    patterns = [
        (r"^Increases healing done by up to ([\d,]+) and damage done by up to ([\d,]+) for all magical spells and effects\.?$",
         lambda m: f"{prefix}所有魔法法术和效果的治疗效果最多提高 {m.group(1)} 点，造成的伤害最多提高 {m.group(2)} 点。{cooldown}"),
        (r"^Increases damage done by up to ([\d,]+) and healing done by up to ([\d,]+) for all magical spells and effects\.?$",
         lambda m: f"{prefix}所有魔法法术和效果造成的伤害最多提高 {m.group(1)} 点，治疗效果最多提高 {m.group(2)} 点。{cooldown}"),
        (r"^Chance on successful spellcast to restore ([\d,]+) Mana over (\d+)\s*sec\.?$",
         lambda m: f"{prefix}成功施法时有几率在 {m.group(2)} 秒内恢复 {m.group(1)} 点法力值。{cooldown}"),
        (r"^Chance to strike your ranged target with (.+?) for ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow) damage\.?$",
         lambda m: f"{prefix}有一定几率用{translate_proc_name(m.group(1))}打击你的远程目标，造成 {m.group(2)} 到 {m.group(3)} 点{SCHOOL.get(m.group(4), m.group(4))}伤害。{cooldown}"),
        (r"^Chance to strike your target with (.+?) for ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow) damage\.?$",
         lambda m: f"{prefix}有一定几率用{translate_proc_name(m.group(1))}打击你的目标，造成 {m.group(2)} 到 {m.group(3)} 点{SCHOOL.get(m.group(4), m.group(4))}伤害。{cooldown}"),
        (r"^Blasts a target for ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow) damage\.?$",
         lambda m: f"{prefix}轰击目标，造成 {m.group(1)} 到 {m.group(2)} 点{SCHOOL.get(m.group(3), m.group(3))}伤害。{cooldown}"),
        (r"^Deals ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow) damage\.?$",
         lambda m: f"{prefix}造成 {m.group(1)} 到 {m.group(2)} 点{SCHOOL.get(m.group(3), m.group(3))}伤害。{cooldown}"),
        (r"^Wounds the target causing them to bleed for ([\d,]+) damage over (\d+\s*(?:sec|second|seconds|min|minute|minutes))\.?$",
         lambda m: f"{prefix}使目标受伤流血，在 {consumables.translate_time(m.group(2))} 内造成 {m.group(1)} 点伤害。{cooldown}"),
        (r"^Increases damage and healing done by magical spells and effects by up to ([\d,]+)\.?$",
         lambda m: f"{prefix}魔法法术和效果造成的伤害与治疗效果最多提高 {m.group(1)} 点。{cooldown}"),
        (r"^Increases healing done by spells and effects by up to ([\d,]+)\.?$",
         lambda m: f"{prefix}法术和效果造成的治疗最多提高 {m.group(1)} 点。{cooldown}"),
        (r"^Increases attack power by ([\d,]+)\.?$",
         lambda m: f"{prefix}攻击强度提高 {m.group(1)} 点。{cooldown}"),
        (r"^Increases ranged attack power by ([\d,]+)\.?$",
         lambda m: f"{prefix}远程攻击强度提高 {m.group(1)} 点。{cooldown}"),
        (r"^Increases spell power by ([\d,]+)\.?$",
         lambda m: f"{prefix}法术强度提高 {m.group(1)} 点。{cooldown}"),
        (r"^Restores ([\d,]+) to ([\d,]+) (health|mana)\.?$",
         lambda m: f"{prefix}恢复 {m.group(1)} 到 {m.group(2)} 点{'生命值' if m.group(3).lower() == 'health' else '法力值'}。{cooldown}"),
    ]
    for pattern, build in patterns:
        match = re.match(pattern, body, re.I)
        if match:
            return build(match)

    translated = consumables.translate_line(text, objective_names)
    if translated and translated != text:
        return translated

    body = consumables.replace_terms(consumables.translate_time(body)).strip()
    if not re.search(r"[。.!?]$", body):
        body += "。"
    return prefix + body + cooldown if prefix else body


def translate_tooltip_line(line: str, objective_names: dict[str, str]) -> str:
    text = (line or "").strip()
    direct = {
        "Binds when picked up": "拾取后绑定",
        "Binds when equipped": "装备后绑定",
        "Binds when used": "使用后绑定",
        "Binds to account": "账号绑定",
        "Unique": "唯一",
        "Unique-Equipped": "唯一装备",
        "One-Hand": "单手",
        "Two-Hand": "双手",
        "Main Hand": "主手",
        "Off Hand": "副手",
        "Held In Off-hand": "副手物品",
        "Ranged": "远程",
        "Thrown": "投掷",
        "Gun": "枪",
        "Bow": "弓",
        "Crossbow": "弩",
        "Wand": "魔杖",
        "Cloth": "布甲",
        "Leather": "皮甲",
        "Mail": "锁甲",
        "Plate": "板甲",
        "Head": "头部",
        "Neck": "颈部",
        "Shoulder": "肩部",
        "Back": "背部",
        "Chest": "胸部",
        "Wrist": "手腕",
        "Hands": "手",
        "Waist": "腰部",
        "Legs": "腿部",
        "Feet": "脚",
        "Finger": "手指",
        "Trinket": "饰品",
        "Shirt": "衬衣",
        "Tabard": "战袍",
        "Shield": "盾牌",
        "Relic": "圣物",
        "INVTYPE_BAG": "背包",
        "INVTYPE_AMMO": "弹药",
        "Projectile": "弹药",
        "Locked": "已锁住",
        "Already known": "已经学会",
        "Poor": "粗糙",
        "This Item Begins a Quest": "该物品将触发一个任务",
        "Cannot be disenchanted": "无法分解",
        '"Needed by Enchanters."': "“附魔师需要的物品。”",
        '"Venture Company Supplies"': "“风险投资公司补给品”",
        '"It is not known what the reward will be..."': "“不知道奖励会是什么……”",
        '"Used to enhance the flavor in cooking recipes."': "“用于提升烹饪食谱的风味。”",
        '"Used by Blacksmiths to remove impurities."': "“铁匠用来去除杂质。”",
        '"Used by blacksmiths to remove impurities."': "“铁匠用来去除杂质。”",
        '"Stone of the Tides"': "“海潮之石”",
        '"How To Serve Man"': "“如何烹制人类”",
        '"An old, worthless tome."': "“一本陈旧且毫无价值的书。”",
    }
    if text in direct:
        return direct[text]

    match = re.match(r"^(\d+) Slot Bag$", text)
    if match:
        return f"{match.group(1)} 格背包"
    match = re.match(r"^(\d+) Slot Quiver$", text)
    if match:
        return f"{match.group(1)} 格箭袋"
    match = re.match(r"^(\d+) Slot Ammo Pouch$", text)
    if match:
        return f"{match.group(1)} 格弹药袋"
    match = re.match(r"^Adds ([\d.]+) damage per second$", text)
    if match:
        return f"每秒伤害提高 {match.group(1)}"
    match = re.match(r"^Requires Lockpicking \((\d+)\)$", text)
    if match:
        return f"需要 开锁 ({match.group(1)})"
    match = re.match(r"^Use: Teaches you how to summon this companion\.?$", text)
    if match:
        return "使用：教你学会召唤这个伙伴。"
    match = re.match(r"^Use: Opens a Stratholme postbox\.?$", text)
    if match:
        return "使用：打开一个斯坦索姆邮箱。"
    match = re.match(r"^Use: Combine the Ace through Eight of (Beasts|Elementals|Portals|Warlords) to complete the set\.?$", text)
    if match:
        decks = {
            "Beasts": "野兽",
            "Elementals": "元素",
            "Portals": "入口",
            "Warlords": "督军",
        }
        return f"使用：将{decks.get(match.group(1), match.group(1))}套牌的一到八号牌合成为完整套牌。"
    match = re.match(r"^Use: Bind pages (\d+)-(\d+) into Chapter (\d+) of the Shredder Operating Manual\.?$", text)
    if match:
        return f"使用：将第 {match.group(1)}-{match.group(2)} 页装订成《伐木机操作手册》第 {match.group(3)} 章。"
    match = re.match(r"^Use: Join together the Lower, Middle and Upper Map Fragments\.?$", text)
    if match:
        return "使用：将下部、中部和上部地图碎片拼合在一起。"
    match = re.match(r"^Use: Eat me\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：吃掉我。（{match.group(1)}秒冷却）"
    match = re.match(r"^Use: Take control of a Steam Tonk\.?$", text)
    if match:
        return "使用：控制一辆蒸汽车。"
    match = re.match(r"^Use: Shoots a firework into the air that bursts in a yellow pattern\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：向空中发射一枚烟花，爆出黄色图案。（{match.group(1)}秒冷却）"
    match = re.match(r"^Use: Shoots a firework into the air that bursts into a thousand (red|blue) stars\. \((\d+) Sec Cooldown\)$", text)
    if match:
        color = "红色" if match.group(1).lower() == "red" else "蓝色"
        return f"使用：向空中发射一枚烟花，爆成千颗{color}星光。（{match.group(2)}秒冷却）"
    match = re.match(r"^Use: Shoots a firework into the air that bursts into red streaks\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：向空中发射一枚烟花，爆出红色光带。（{match.group(1)}秒冷却）"
    match = re.match(r"^Use: An extremely potent alcoholic beverage\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：一种极其烈性的酒精饮料。（{match.group(1)}秒冷却）"
    match = re.match(r"^Use: Increase sharp weapon damage by (\d+) for (\d+) minutes\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：使锐器武器伤害提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。（{match.group(3)}秒冷却）"
    match = re.match(r"^Use: Increase the damage of a blunt weapon by (\d+) for (\d+) minutes\. \((\d+) Sec Cooldown\)$", text)
    if match:
        return f"使用：使钝器武器伤害提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。（{match.group(3)}秒冷却）"
    match = re.match(r"^Use: Increases physical damage by (\d+) for (\d+) min\.?$", text)
    if match:
        return f"使用：物理伤害提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。"
    match = re.match(r"^Use: Opens certain Dalaran-sealed containers\.?$", text)
    if match:
        return "使用：打开某些达拉然密封的容器。"
    match = re.match(r"^Use: Opens a Black Vault Relic Coffer Door\.?$", text)
    if match:
        return "使用：打开黑色宝库圣物宝箱门。"
    match = re.match(r"^Use: Turn three lesser (magic|astral|mystic|nether|eternal) essences into a greater one\.?$", text)
    if match:
        essence = {"magic": "魔法", "astral": "星界", "mystic": "秘法", "nether": "虚空", "eternal": "不灭"}
        return f"使用：将三个次级{essence[match.group(1).lower()]}精华转化为一个强效精华。"
    match = re.match(r"^Use: Turn a greater (magic|astral|mystic|nether|eternal) essence into three lesser ones\.?$", text)
    if match:
        essence = {"magic": "魔法", "astral": "星界", "mystic": "秘法", "nether": "虚空", "eternal": "不灭"}
        return f"使用：将一个强效{essence[match.group(1).lower()]}精华转化为三个次级精华。"

    match = re.match(r"^Speed ([\d.]+)$", text)
    if match:
        return f"速度 {match.group(1)}"
    match = re.match(r"^([\d,]+) - ([\d,]+) Damage$", text)
    if match:
        return f"{match.group(1)} - {match.group(2)} 伤害"
    match = re.match(r"^\(([\d.]+) damage per second\)$", text)
    if match:
        return f"（每秒造成 {match.group(1)} 点伤害）"
    match = re.match(r"^Requires Level (\d+)$", text)
    if match:
        return f"需要等级 {match.group(1)}"
    match = re.match(r"^Item Level (\d+)$", text)
    if match:
        return f"物品等级 {match.group(1)}"
    match = re.match(r"^(\d+) Armor$", text)
    if match:
        return f"{match.group(1)} 护甲"
    match = re.match(r"^\+([\d,]+) (Strength|Agility|Stamina|Intellect|Spirit|Armor|Attack Power|All Resistances|Fire Resistance|Frost Resistance|Nature Resistance|Shadow Resistance|Arcane Resistance)$", text)
    if match:
        return f"+{match.group(1)} {consumables.replace_terms(match.group(2))}"

    return translate_effect_line(text, objective_names)


def main() -> None:
    source = SNAPSHOT if SNAPSHOT.exists() else CACHE
    items = json.loads(source.read_text(encoding="utf-8"))
    existing_items = load_item_data()
    name_map = load_name_map()
    objective_names = consumables.load_objective_names()
    rows = []

    for item in sorted(items, key=lambda row: int(row["id"])):
        item_id = int(item["id"])
        en_name = item.get("name") or ""
        if is_skipped_english_name(en_name):
            continue
        tooltip_lines = []
        for row in item.get("tooltip") or []:
            if isinstance(row, dict) and row.get("text"):
                tooltip_lines.append(row["text"])
        if not tooltip_lines:
            tooltip_lines = item.get("green") or []
        base = existing_items.get(item_id)
        mapped_name = name_map.get(en_name)
        cn_name = base[0] if base and has_cn(base[0]) else mapped_name or translate_item_name(en_name, existing_items, objective_names)

        translated_pairs = []
        for raw in tooltip_lines:
            translated = translate_tooltip_line(raw, objective_names)
            if translated and not has_ascii_letters(translated):
                translated_pairs.append((raw, translated))

        if not translated_pairs and base and has_cn(base[0]):
            continue
        if not translated_pairs and not (cn_name and has_cn(cn_name)):
            continue
        if not translated_pairs and has_ascii_letters(cn_name):
            continue
        if translated_pairs and (not has_cn(cn_name) or has_ascii_letters(cn_name)):
            cn_name = translate_item_name(en_name, existing_items, objective_names)

        generated_desc = "\n".join(translated for _, translated in translated_pairs)
        base_desc = base[1] if base and has_cn(base[1]) else ""
        desc = base_desc or generated_desc
        rows.append((item_id, cn_name, desc, "EpochHead 物品", en_name, translated_pairs))

    lines = [
        "-- Generated by Tools/generate_epoch_items.py.",
        "-- Source: https://epochhead.com/items",
        "function LoadEpochCNItemOverlayData()",
        "  EpochCN_ItemOverlayData = {",
    ]
    for item_id, cn_name, desc, source, en_name, translated_pairs in rows:
        pairs = []
        for raw, translated in translated_pairs:
            if raw != translated:
                pairs.append(f'["{lua_escape(raw)}"] = "{lua_escape(translated)}"')
        map_literal = "{ " + ", ".join(pairs) + " }" if pairs else "{}"
        lines.append(
            f'    [{item_id}] = {{"{lua_escape(cn_name)}", "{lua_escape(desc)}", "{lua_escape(source)}", "item", {map_literal}, "{lua_escape(en_name)}"}},'
        )
    lines.extend(["  }", "end", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")

    green_rows = sum(1 for *_, pairs in rows if pairs)
    missing_names = sum(1 for _, name, *_ in rows if not has_cn(name))
    ascii_desc = sum(1 for _, _, desc, *_ in rows if desc and re.search(r"[A-Za-z]", desc))
    print(f"wrote {OUT}")
    print(f"rows={len(rows)} green_rows={green_rows} missing_cn_names={missing_names} ascii_desc={ascii_desc}")


if __name__ == "__main__":
    main()
