#!/usr/bin/env python3
"""
UnitData 单位名称补全脚本。
策略：
1. 从 ObjectiveNameData 传播翻译到 UnitData 中仍为英文的条目
2. 扩展词根翻译词典，覆盖更多常见 NPC 名称模式
3. 跳过 test/deprecated/placeholder 等无意义条目
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

# Skip patterns for untranslatable entries
SKIP_RE = re.compile(
    r'DEPRECATED|deprecated|UNUSED|Unused|\(PH\)|Placeholder|placeholder|'
    r'\bTEST\b|Test Dummy|DND|\[DND\]|Trigger|trigger|Bunny|bunny|'
    r'Credit|credit|Invisible|invisible|Visual|visual|Controller|controller|'
    r'Proxy|proxy|Spawner|spawner|Waypoint|waypoint|'
    r'Only GM|only gm|Marker|marker|Event|event|Transform|transform|'
    r'Invis\b|invis\b|DEBUG|debug|^\(|^\[|^<',
    re.IGNORECASE
)

# Extended word map for unit name translation
WORD_MAP = {
    # Titles / Professions
    "Apprentice": "学徒", "Journeyman": "熟练工", "Adept": "大师",
    "Trainer": "训练师", "Vendor": "商人", "Merchant": "商贩",
    "Quartermaster": "军需官", "Innkeeper": "旅店老板", "Barkeep": "酒保",
    "Flight Master": "飞行管理员", "Auctioneer": "拍卖师", "Banker": "银行家",
    "Bouncer": "保镖", "Recruit": "新兵", "Footman": "步兵",
    "Guard": "卫兵", "Guardian": "守护者", "Sentinel": "哨兵",
    "Scout": "侦察兵", "Warrior": "战士", "Priest": "牧师",
    "Mage": "法师", "Shaman": "萨满", "Rogue": "潜行者",
    "Hunter": "猎人", "Warlock": "术士", "Paladin": "圣骑士",
    "Druid": "德鲁伊", "Deathguard": "死亡卫士", "Lieutenant": "副队长",
    "Captain": "队长", "Marshal": "治安官", "Commander": "指挥官",
    "General": "将军", "Sergeant": "中士", "Corporal": "下士",
    "Champion": "勇士", "Chieftain": "酋长", "Warlord": "督军",
    "Overseer": "监工", "Foreman": "工头", "Peasant": "农夫",
    "Worker": "工人", "Peon": "苦工", "Miner": "矿工",
    "Thug": "暴徒", "Bandit": "强盗", "Cutthroat": "刺客",
    "Brute": "暴徒", "Spirit Healer": "灵魂医者",
    # Combat roles
    "Spellcaster": "施法者", "Geomancer": "风水师", "Necromancer": "通灵师",
    "Summoner": "召唤师", "Healer": "治疗者", "Berserker": "狂战士",
    "Assassin": "刺客", "Archer": "射手", "Gunner": "枪手",
    "Raider": "袭击者", "Rider": "骑手", "Forager": "觅食者",
    "Reaver": "劫掠者", "Enforcer": "打手", "Thief": "盗贼",
    "Looter": "掠夺者", "Ambusher": "伏击者", "Defender": "防御者",
    "Warmaster": "统帅", "Surveyor": "勘测员", "Explorer": "探险者",
    "Veteran": "老兵", "Stalker": "潜伏者", "Watcher": "守望者",
    "Sentry": "哨兵", "Keeper": "守护者", "Weaver": "编织者",
    "Constructor": "构造者", "Executioner": "行刑者", "Vanquisher": "征服者",
    "Chronomancer": "时空法师", "Invader": "入侵者", "Spellbreaker": "破法者",
    "Binder": "缚法者", "Mercenary": "雇佣兵", "Soldier": "士兵",
    "Prisoner": "囚犯", "Refugee": "难民", "Slave": "奴隶",
    # NEW: Additional roles/titles
    "Initiate": "新手", "Acolyte": "侍僧", "Disciple": "门徒",
    "Mystic": "神秘者", "Seer": "先知", "Oracle": "神谕者",
    "Prophet": "先知", "Sage": "贤者", "Scholar": "学者",
    "Arcanist": "奥术师", "Conjurer": "魔法师", "Enchanter": "附魔师",
    "Illusionist": "幻术师", "Diviner": "占卜师", "Evoker": "唤魔者",
    "Elementalist": "元素师", "Pyromancer": "火法师", "Cryomancer": "冰法师",
    "Hydromancer": "水法师", "Aeromancer": "风法师",
    "Shadowcaster": "暗影施法者", "Shadowmancer": "暗影法师",
    "Demonologist": "恶魔学者", "Felguard": "恶魔卫士",
    "Knight": "骑士", "Crusader": "十字军", "Templar": "圣殿骑士",
    "Vindicator": "维护者", "Protector": "保护者", "Avenger": "复仇者",
    "Inquisitor": "审判官", "Chaplain": "牧师",
    "Grunt": "步兵", "Blademaster": "剑圣", "Headhunter": "猎头者",
    "Witch Doctor": "巫医", "Shadow Hunter": "暗影猎手",
    "Gladiator": "角斗士", "Duelist": "决斗者", "Brawler": "格斗者",
    "Pugilist": "拳师", "Monk": "武僧",
    "Sniper": "狙击手", "Marksman": "射手", "Rifleman": "步枪手",
    "Cannoneer": "炮手", "Bombardier": "投弹手",
    "Engineer": "工程师", "Mechanic": "机械师", "Tinker": "工匠",
    "Inventor": "发明家", "Technician": "技师",
    "Alchemist": "炼金术士", "Herbalist": "草药师", "Apothecary": "药剂师",
    "Blacksmith": "铁匠", "Armorer": "护甲匠", "Weaponsmith": "武器匠",
    "Leatherworker": "制皮匠", "Tailor": "裁缝", "Jeweler": "珠宝匠",
    "Cook": "厨师", "Fisher": "渔夫", "Fisherman": "渔夫",
    "Farmer": "农夫", "Shepherd": "牧羊人", "Lumberjack": "伐木工",
    "Woodcutter": "伐木工", "Gravedigger": "掘墓人",
    "Spy": "间谍", "Infiltrator": "渗透者", "Agent": "特工",
    "Saboteur": "破坏者", "Smuggler": "走私者",
    "Pirate": "海盗", "Corsair": "海盗", "Buccaneer": "海盗",
    "Sailor": "水手", "Deckhand": "水手", "Navigator": "领航员",
    "Harbinger": "先驱", "Herald": "传令官", "Emissary": "使者",
    "Ambassador": "大使", "Envoy": "特使", "Diplomat": "外交官",
    "Courier": "信使", "Messenger": "信使",
    "Warden": "典狱官", "Jailer": "狱卒", "Taskmaster": "监工",
    "Slavedriver": "奴隶主",
    "Chieftain": "酋长", "Elder": "长者", "Patriarch": "族长",
    "Matriarch": "女族长", "High Priest": "大祭司", "High Priestess": "大女祭司",
    "Archdruid": "大德鲁伊", "Archmage": "大法师",
    "Battlemage": "战斗法师", "Spellblade": "魔刃师",
    "Deathstalker": "亡灵哨兵", "Dark Ranger": "黑暗游侠",
    "Blightcaller": "枯萎使者", "Plaguebringer": "瘟疫使者",
    "Dreadlord": "恐惧魔王", "Pit Lord": "深渊领主",
    "Lich": "巫妖", "Death Knight": "死亡骑士",
    "Gryphon Rider": "狮鹫骑士", "Wind Rider": "风骑士",
    "Bat Rider": "蝙蝠骑士", "Wyvern Rider": "双足飞龙骑士",
    "Stable Master": "马厩管理员", "Pet Trainer": "宠物训练师",
    "Weapon Master": "武器大师", "Battle Master": "战场军官",
    "Arena Master": "竞技场管理员",
    "Mailbox": "邮箱", "Repair": "修理",
    "Supply Officer": "补给官", "Provisioner": "供给者",
    "Recruiter": "征兵官", "Drill Sergeant": "教官",
    "Patroller": "巡逻兵", "Outrider": "先驱者",
    "Mountaineer": "登山者", "Pathfinder": "探路者",
    "Tracker": "追踪者", "Trapper": "捕兽者",
    "Tamer": "驯兽师", "Beastmaster": "驯兽师",
    "Falconer": "驯鹰人", "Handler": "驯养员",
}

# Continue word map - Creatures/Races
WORD_MAP.update({
    # Creatures
    "Steed": "战马", "Rhino": "犀牛", "Fox": "狐狸",
    "Gnoll": "豺狼人", "Murloc": "鱼人", "Kobold": "狗头人",
    "Ogre": "食人魔", "Satyr": "萨特", "Harpy": "鹰身人",
    "Centaur": "半人马", "Naga": "纳迦", "Raptor": "迅猛龙",
    "Dragonkin": "龙人", "Dragonspawn": "龙人",
    "Whelp": "雏龙", "Whelpling": "雏龙", "Drake": "幼龙",
    "Dragon": "龙", "Demon": "恶魔", "Imp": "小鬼",
    "Felhunter": "魔犬", "Succubus": "魅魔", "Voidwalker": "虚空行者",
    "Infernal": "地狱火", "Skeleton": "骷髅", "Zombie": "僵尸",
    "Ghoul": "食尸鬼", "Abomination": "憎恶", "Banshee": "女妖",
    "Ghost": "幽灵", "Soul": "灵魂", "Void": "虚空",
    "Portal": "传送门", "Troll": "巨魔",
    # NEW: More creatures
    "Wolf": "狼", "Worg": "座狼", "Bear": "熊",
    "Spider": "蜘蛛", "Scorpion": "蝎子", "Serpent": "蛇",
    "Viper": "毒蛇", "Cobra": "眼镜蛇", "Basilisk": "石化蜥蜴",
    "Crocolisk": "鳄鱼", "Turtle": "海龟", "Crab": "螃蟹",
    "Bat": "蝙蝠", "Owl": "猫头鹰", "Eagle": "鹰",
    "Hawk": "鹰", "Falcon": "猎鹰", "Raven": "乌鸦",
    "Crow": "乌鸦", "Vulture": "秃鹫", "Condor": "秃鹰",
    "Boar": "野猪", "Stag": "雄鹿", "Doe": "母鹿",
    "Ram": "公羊", "Tallstrider": "陆行鸟", "Plainstrider": "平原陆行鸟",
    "Kodo": "科多兽", "Thunder Lizard": "雷霆蜥蜴",
    "Hyena": "土狼", "Lion": "狮子", "Lioness": "母狮",
    "Tiger": "老虎", "Panther": "黑豹", "Leopard": "豹",
    "Gorilla": "猩猩", "Ape": "猿猴", "Monkey": "猴子",
    "Critter": "小动物", "Rat": "老鼠", "Rabbit": "兔子",
    "Squirrel": "松鼠", "Deer": "鹿", "Fawn": "小鹿",
    "Frog": "青蛙", "Toad": "蟾蜍", "Snake": "蛇",
    "Beetle": "甲虫", "Wasp": "黄蜂", "Moth": "飞蛾",
    "Firefly": "萤火虫", "Maggot": "蛆虫", "Larva": "幼虫",
    "Slime": "软泥怪", "Ooze": "软泥怪",
    "Elemental": "元素", "Revenant": "亡灵",
    "Golem": "傀儡", "Construct": "构造体",
    "Gargoyle": "石像鬼", "Shade": "暗影",
    "Wraith": "怨灵", "Specter": "幽灵", "Spectre": "幽灵",
    "Wisp": "小精灵", "Sprite": "精灵",
    "Treant": "树人", "Bog Beast": "沼泽兽",
    "Fungal": "真菌", "Sporeling": "孢子人",
    "Ravager": "破坏者", "Nether Ray": "虚空鳐",
    "Sporebat": "孢子蝙蝠", "Clefthoof": "裂蹄牛",
    "Talbuk": "塔布羊", "Elekk": "雷象",
    "Warp Stalker": "扭曲潜行者", "Flayer": "剥皮者",
    "Fel Reaver": "地狱火傀儡",
    "Proto-Drake": "始祖龙", "Storm Drake": "风暴幼龙",
    "Mammoth": "猛犸象", "Shoveltusk": "铲牙象",
    "Jormungar": "蛴螬", "Magnataur": "雪人",
    "Nerub": "蛛魔",
    # Factions/Groups
    "Defias": "迪菲亚", "Scarlet": "血色", "Forsaken": "被遗忘者",
    "Bloodsail": "血帆", "Syndicate": "辛迪加", "Infinite": "无尽",
    "Frostwolf": "霜狼", "Stormpike": "雷矛",
    "Irondeep": "铁深", "Coldmine": "冷矿",
    "Skybreaker": "破天者", "Kor'kron": "库卡隆",
    "Anub'ar": "阿努巴尔", "Drakkari": "达卡莱",
    "Scourge": "天灾", "Ethereal": "虚灵", "Riverpaw": "河爪",
    "Forest Troll": "森林巨魔", "Bronze Dragonspawn": "青铜龙人",
    "Green Dragonspawn": "绿龙人", "White Dragonspawn": "白龙人",
    "Blackrock": "黑石", "Twilight": "暮光",
    "Burning Blade": "火刃", "Shadow Council": "暗影议会",
    "Iron Dwarf": "铁矮人", "Iron Giant": "铁巨人",
    "Iron Vrykul": "铁维库人", "Vrykul": "维库人",
    "Kvaldir": "克瓦迪尔", "Vargul": "瓦格尔",
    "Ymirjar": "伊米隆", "Nerub'ar": "蛛魔",
    "Wolvar": "狼人", "Gorloc": "鱼人",
    # Modifiers
    "Greater": "强大的", "Lesser": "次级", "Young": "年幼的",
    "Ancient": "远古的", "Elder": "年长的", "Wounded": "受伤的",
    "Injured": "受伤的", "Dying": "垂死的", "Captured": "被俘的",
    "Freed": "获释的", "Obedient": "驯服的", "Juvenile": "幼年的",
    "Savage": "野蛮", "Fierce": "凶猛的", "Wild": "野性的",
    "Haunted": "闹鬼的", "Cursed": "被诅咒的",
    "Enraged": "激怒的", "Frenzied": "狂暴的", "Rabid": "疯狂的",
    "Diseased": "染病的", "Plagued": "被瘟疫感染的", "Corrupted": "被腐蚀的",
    "Tainted": "被污染的", "Withered": "枯萎的", "Decayed": "腐烂的",
    "Frozen": "冰冻的", "Burning": "燃烧的", "Molten": "熔火",
    "Arcane": "奥术", "Fel": "邪能", "Shadow": "暗影",
    "Dark": "黑暗", "Spectral": "幽灵", "Ethereal": "虚灵",
    "Undead": "亡灵", "Skeletal": "骷髅",
    "Giant": "巨型", "Colossal": "巨大的", "Massive": "庞大的",
    "Tiny": "微小的", "Small": "小型",
    "Alpha": "首领", "Matriarch": "女族长", "Patriarch": "族长",
    "Feral": "野性的", "Rabid": "疯狂的",
    "Armored": "装甲", "Battle": "战斗",
    "War": "战争", "Storm": "风暴", "Frost": "冰霜",
    "Fire": "火焰", "Ice": "冰", "Thunder": "雷霆",
    "Iron": "钢铁", "Steel": "钢", "Stone": "石头",
    "Crystal": "水晶", "Obsidian": "黑曜石",
    "Emerald": "翡翠", "Ruby": "红宝石", "Sapphire": "蓝宝石",
    "Golden": "金色的", "Silver": "银色的",
    "Black": "黑色", "White": "白色", "Red": "红色",
    "Blue": "蓝色", "Green": "绿色",
    "Crimson": "深红", "Azure": "碧蓝",
})

MODIFIER_ONLY = {
    "Greater", "Lesser", "Young", "Ancient", "Elder", "Wounded", "Injured",
    "Dying", "Savage", "Fierce", "Wild", "Haunted", "Cursed",
    "Enraged", "Frenzied", "Rabid", "Diseased", "Plagued", "Corrupted",
    "Tainted", "Withered", "Decayed", "Frozen", "Burning", "Molten",
    "Arcane", "Fel", "Shadow", "Dark", "Spectral", "Ethereal",
    "Undead", "Skeletal", "Giant", "Colossal", "Massive", "Tiny", "Small",
    "Alpha", "Feral", "Armored", "Battle", "War", "Storm", "Frost",
    "Fire", "Ice", "Thunder", "Iron", "Steel", "Stone", "Crystal",
    "Obsidian", "Emerald", "Ruby", "Sapphire", "Golden", "Silver",
    "Black", "White", "Red", "Blue", "Green", "Crimson", "Azure",
    "Captured", "Freed", "Obedient", "Juvenile",
}


def translate_by_words(name: str) -> str | None:
    """Try to translate a name using word roots. All words must be translatable."""
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
    # Must have at least one non-modifier word
    non_modifier = [w for w in used_words if w not in MODIFIER_ONLY]
    if not non_modifier:
        return None
    return "".join(out)


def main():
    # Load UnitData
    unit_path = DATA / "UnitData.lua"
    with open(unit_path, encoding="utf-8") as f:
        unit_text = f.read()

    # Parse unit entries: [id] = {"name","subname","source"},
    unit_re = re.compile(r'^\[(\d+)\]\s*=\s*\{"((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)"\},?$', re.MULTILINE)
    units = {}
    for m in unit_re.finditer(unit_text):
        uid = int(m.group(1))
        units[uid] = {
            "name": unesc(m.group(2)),
            "subname": unesc(m.group(3)),
            "source": unesc(m.group(4)),
            "original": m.group(0),
        }

    # Load ObjectiveNameData
    obj_path = DATA / "ObjectiveNameData.lua"
    with open(obj_path, encoding="utf-8") as f:
        obj_text = f.read()
    obj_pairs = re.findall(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', obj_text)
    obj_map = {unesc(k): unesc(v) for k, v in obj_pairs if has_cjk(unesc(v))}

    # Load Glossary text section
    glossary_path = DATA / "Glossary.lua"
    with open(glossary_path, encoding="utf-8") as f:
        glossary_text = f.read()
    glossary_pairs = re.findall(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', glossary_text)
    glossary_map = {unesc(k): unesc(v) for k, v in glossary_pairs if has_cjk(unesc(v))}

    # Load EpochHeadData names
    ehd_path = DATA / "EpochHeadData.lua"
    ehd_map = {}
    if ehd_path.exists():
        with open(ehd_path, encoding="utf-8") as f:
            ehd_text = f.read()
        ehd_pairs = re.findall(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', ehd_text)
        ehd_map = {unesc(k): unesc(v) for k, v in ehd_pairs if has_cjk(unesc(v))}

    # Load ItemNameMap for cross-reference
    inm_path = DATA / "ItemNameMap.lua"
    inm_map = {}
    if inm_path.exists():
        with open(inm_path, encoding="utf-8") as f:
            inm_text = f.read()
        inm_pairs = re.findall(r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', inm_text)
        inm_map = {unesc(k): unesc(v) for k, v in inm_pairs if has_cjk(unesc(v))}

    # Process: find English-only unit names and try to translate
    updated = 0
    skipped = 0
    methods = {"objective": 0, "glossary": 0, "epochhead": 0, "itemname": 0, "wordroot": 0}

    new_lines = []
    for uid in sorted(units.keys()):
        entry = units[uid]
        name = entry["name"]

        if not is_english(name):
            new_lines.append(entry["original"])
            continue

        if SKIP_RE.search(name):
            new_lines.append(entry["original"])
            skipped += 1
            continue

        # Try translation sources in priority order
        translated = None
        method = None

        # 1. ObjectiveNameData exact match
        if name in obj_map:
            translated = obj_map[name]
            method = "objective"
        # 2. Glossary
        elif name in glossary_map:
            translated = glossary_map[name]
            method = "glossary"
        # 3. EpochHeadData
        elif name in ehd_map:
            translated = ehd_map[name]
            method = "epochhead"
        # 4. ItemNameMap (some NPC names match item names)
        elif name in inm_map:
            translated = inm_map[name]
            method = "itemname"
        # 5. Word-root translation
        else:
            translated = translate_by_words(name)
            if translated:
                method = "wordroot"

        if translated and has_cjk(translated) and translated != name:
            new_line = f'[{uid}] = {{"{esc(translated)}","{esc(entry["subname"])}","{esc(entry["source"])}"}},\n' if entry["original"].endswith(",") else f'[{uid}] = {{"{esc(translated)}","{esc(entry["subname"])}","{esc(entry["source"])}"}}'
            # Keep original formatting
            new_line = f'[{uid}] = {{"{esc(translated)}","","汉化组"}},'
            new_lines.append(new_line)
            updated += 1
            methods[method] += 1
        else:
            new_lines.append(entry["original"])

    # Write updated UnitData.lua
    header = "function LoadTPCNUnitData()\n    TPCN_UnitData = {\n"
    footer = "}\nend\n"
    body = "\n".join(new_lines)

    with open(unit_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("\n")
        f.write(footer)

    total = len(units)
    chinese_before = sum(1 for u in units.values() if has_cjk(u["name"]))
    chinese_after = chinese_before + updated

    print(f"=== UnitData 补全结果 ===")
    print(f"总条目: {total}")
    print(f"补全前中文: {chinese_before} ({chinese_before*100/total:.1f}%)")
    print(f"新增翻译: {updated}")
    print(f"  - ObjectiveNameData: {methods['objective']}")
    print(f"  - Glossary: {methods['glossary']}")
    print(f"  - EpochHeadData: {methods['epochhead']}")
    print(f"  - ItemNameMap: {methods['itemname']}")
    print(f"  - 词根翻译: {methods['wordroot']}")
    print(f"跳过(test/deprecated): {skipped}")
    print(f"补全后中文: {chinese_after} ({chinese_after*100/total:.1f}%)")


if __name__ == "__main__":
    main()
