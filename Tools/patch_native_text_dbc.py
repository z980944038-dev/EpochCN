from pathlib import Path
import re
import shutil
import struct


ROOT = Path(r"D:\1927\Ascension Launcher\resources\epoch-live")
ADDONS = ROOT / "Interface" / "AddOns"
WORK = Path(r"D:\1927\Ascension Launcher\resources\_cn_work_native_text_dbc")
SRC = WORK / "source" / "DBFilesClient"
SRC_FALLBACK = WORK / "all_source" / "DBFilesClient"
OUT = WORK / "patched_safe" / "DBFilesClient"
REPORT = WORK / "TEXT_DBC_PATCH_REPORT_SAFE.md"

NAME_RE = re.compile(r'\[(\d+)\]\s*=\s*"((?:\\.|[^"\\])*)"')
LUA_PAIR_RE = re.compile(r'\[["\']((?:\\.|[^"\'\\]){2,})["\']\]\s*=\s*["\']((?:\\.|[^"\'\\]){1,})["\']')

FIELD_SPECS = {
    "CharTitles.dbc": [2, 19],
    "CreatureFamily.dbc": [10],
    "ItemClass.dbc": [3],
    "ItemSubClass.dbc": [10, 27],
    "ItemSet.dbc": [1],
    "WorldMapArea.dbc": [3],
    "TaxiNodes.dbc": [5],
    "DungeonEncounter.dbc": [5],
    "BattlemasterList.dbc": [11, 31],
    "WorldStateUI.dbc": [5, 22],
    "AreaPOI.dbc": [18],
    "WorldSafeLocs.dbc": [5],
}

MANUAL = {
    # Zone names where upstream data can reflect later expansions.
    "Barrens": "贫瘠之地",

    # ItemClass / ItemSubClass
    "Consumable": "消耗品",
    "Container": "容器",
    "Weapon": "武器",
    "Gem": "宝石",
    "Armor": "护甲",
    "Reagent": "材料",
    "Projectile": "弹药",
    "Trade Goods": "商品",
    "Generic(OBSOLETE)": "通用（废弃）",
    "Recipe": "配方",
    "Money": "金钱",
    "Quiver": "箭袋",
    "Quest": "任务",
    "Key": "钥匙",
    "Permanent(OBSOLETE)": "永久（废弃）",
    "Miscellaneous": "其他",
    "Glyph": "雕文",
    "Food & Drink": "食物和饮料",
    "Potion": "药水",
    "Elixir": "药剂",
    "Flask": "合剂",
    "Bandage": "绷带",
    "Item Enhancement": "物品强化",
    "Scroll": "卷轴",
    "Other": "其他",
    "Bag": "背包",
    "Soul Bag": "灵魂袋",
    "Herb Bag": "草药袋",
    "Enchanting Bag": "附魔材料袋",
    "Engineering Bag": "工程学材料袋",
    "Gem Bag": "宝石袋",
    "Mining Bag": "矿石袋",
    "Leatherworking Bag": "制皮材料袋",
    "Inscription Bag": "铭文包",
    "One-Handed Axes": "单手斧",
    "Two-Handed Axes": "双手斧",
    "Bows": "弓",
    "Guns": "枪械",
    "One-Handed Maces": "单手锤",
    "Two-Handed Maces": "双手锤",
    "Polearms": "长柄武器",
    "One-Handed Swords": "单手剑",
    "Two-Handed Swords": "双手剑",
    "Staves": "法杖",
    "Fist Weapons": "拳套武器",
    "Daggers": "匕首",
    "Thrown": "投掷武器",
    "Crossbows": "弩",
    "Wands": "魔杖",
    "Fishing Poles": "鱼竿",
    "Plate": "板甲",
    "Mail": "锁甲",
    "Shields": "盾牌",
    "Librams": "圣契",
    "Idols": "神像",
    "Totems": "图腾",
    "Sigils": "魔印",
    "Cloth": "布甲",
    "Leather": "皮甲",
    "Book": "书籍",
    "Leatherworking": "制皮",
    "Tailoring": "裁缝",
    "Engineering": "工程学",
    "Blacksmithing": "锻造",
    "Cooking": "烹饪",
    "Alchemy": "炼金术",
    "First Aid": "急救",
    "Enchanting": "附魔",
    "Fishing": "钓鱼",
    "Jewelcrafting": "珠宝加工",
    "Inscription": "铭文",
    "Elemental": "元素",
    "Metal & Stone": "金属和矿石",
    "Meat": "肉类",
    "Herb": "草药",
    "Parts": "零件",
    "Devices": "装置",
    "Explosives": "爆炸物",
    "Materials": "材料",
    "Armor Enchantment": "护甲附魔",
    "Weapon Enchantment": "武器附魔",
    # CreatureFamily
    "Wolf": "狼",
    "Cat": "豹",
    "Spider": "蜘蛛",
    "Bear": "熊",
    "Boar": "野猪",
    "Crocolisk": "鳄鱼",
    "Carrion Bird": "食腐鸟",
    "Crab": "螃蟹",
    "Gorilla": "猩猩",
    "Raptor": "迅猛龙",
    "Tallstrider": "陆行鸟",
    "Felhunter": "地狱猎犬",
    "Voidwalker": "虚空行者",
    "Succubus": "魅魔",
    "Doomguard": "末日守卫",
    "Scorpid": "蝎子",
    "Turtle": "海龟",
    "Imp": "小鬼",
    "Bat": "蝙蝠",
    "Hyena": "土狼",
    "Bird of Prey": "猛禽",
    "Wind Serpent": "风蛇",
    "Remote Control": "遥控",
    "Felguard": "恶魔卫士",
    "Dragonhawk": "龙鹰",
    "Ravager": "掠食者",
    "Warp Stalker": "迁跃捕猎者",
    "Sporebat": "孢子蝠",
    "Nether Ray": "虚空鳐",
    "Serpent": "蛇",
    "Moth": "蛾子",
    "Chimaera": "奇美拉",
    "Devilsaur": "魔暴龙",
    "Ghoul": "食尸鬼",
    "Silithid": "异种虫",
    "Worm": "蠕虫",
    "Rhino": "犀牛",
    "Wasp": "黄蜂",
    "Core Hound": "熔岩犬",
    "Spirit Beast": "灵魂兽",
    # BattlemasterList / common zones
    "Alterac Valley": "奥特兰克山谷",
    "Warsong Gulch": "战歌峡谷",
    "Arathi Basin": "阿拉希盆地",
    "Eye of the Storm": "风暴之眼",
    "Strand of the Ancients": "远古海滩",
    "Isle of Conquest": "征服之岛",
    "Arena": "竞技场",
    "Arenas": "竞技场",
    "Nagrand Arena": "纳格兰竞技场",
    "Blade's Edge Arena": "刀锋山竞技场",
    "Ruins of Lordaeron": "洛丹伦废墟",
    "Dalaran Sewers": "达拉然下水道",
    "The Ring of Valor": "勇气竞技场",
    "Time Remaining": "剩余时间",
    # Titles
    "Private %s": "列兵 %s",
    "Corporal %s": "下士 %s",
    "Sergeant %s": "中士 %s",
    "Master Sergeant %s": "军士长 %s",
    "Sergeant Major %s": "士官长 %s",
    "Knight %s": "骑士 %s",
    "Knight-Lieutenant %s": "骑士中尉 %s",
    "Knight-Captain %s": "骑士队长 %s",
    "Knight-Champion %s": "护卫骑士 %s",
    "Lieutenant Commander %s": "少校 %s",
    "Commander %s": "指挥官 %s",
    "Marshal %s": "统帅 %s",
    "Field Marshal %s": "元帅 %s",
    "Grand Marshal %s": "大元帅 %s",
    "Scout %s": "斥候 %s",
    "Grunt %s": "步兵 %s",
    "Senior Sergeant %s": "高阶军士 %s",
    "First Sergeant %s": "一等军士长 %s",
    "Stone Guard %s": "石头守卫 %s",
    "Blood Guard %s": "血卫士 %s",
    "Legionnaire %s": "军团士兵 %s",
    "Centurion %s": "百夫长 %s",
    "Champion %s": "勇士 %s",
    "Lieutenant General %s": "中将 %s",
    "General %s": "将军 %s",
    "Warlord %s": "督军 %s",
    "High Warlord %s": "高阶督军 %s",
}


def has_cn(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def unescape_lua(text: str) -> str:
    return text.replace(r"\"", '"').replace(r"\'", "'").replace(r"\\", "\\").replace(r"\n", "\n")


def add_mapping(mapping: dict[str, str], key: str, value: str, override: bool = False) -> None:
    key = unescape_lua(key).strip()
    value = unescape_lua(value).strip()
    if not key or not value or key == value or has_cn(key) or not has_cn(value) or key.isdigit():
        return
    if override:
        mapping[key] = value
    else:
        mapping.setdefault(key, value)


def parse_pf_names(mapping: dict[str, str], db_name: str) -> None:
    pairs = [
        (ADDONS / f"pfQuest-wotlk/db/enUS/{db_name}.lua", ADDONS / f"pfQuest-wotlk/db/zhCN/{db_name}.lua"),
        (ADDONS / f"pfQuest-wotlk/db/enUS/{db_name}-tbc.lua", ADDONS / f"pfQuest-wotlk/db/zhCN/{db_name}-tbc.lua"),
        (ADDONS / f"pfQuest-epoch/db/enUS/{db_name}-epoch.lua", ADDONS / f"pfQuest-epoch/db/zhCN/{db_name}-epoch.lua"),
    ]
    for en_path, zh_path in pairs:
        if not en_path.exists() or not zh_path.exists():
            continue
        en = {
            int(row_id): unescape_lua(text)
            for row_id, text in NAME_RE.findall(en_path.read_text(encoding="utf-8", errors="ignore"))
        }
        zh = {
            int(row_id): unescape_lua(text)
            for row_id, text in NAME_RE.findall(zh_path.read_text(encoding="utf-8", errors="ignore"))
        }
        for row_id, key in en.items():
            if row_id in zh:
                add_mapping(mapping, key, zh[row_id])


def parse_safe_lua(mapping: dict[str, str]) -> None:
    for root in [ADDONS / "AtlasLoot", ADDONS / "Leatrix_Plus"]:
        if not root.exists():
            continue
        for path in root.rglob("*.lua"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for key, value in LUA_PAIR_RE.findall(text):
                add_mapping(mapping, key, value)


def read_cstring(blob: bytes, offset: int) -> str:
    end = blob.find(b"\0", offset)
    if end < 0:
        end = len(blob)
    return blob[offset:end].decode("utf-8", errors="replace")


def build_translation_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    parse_safe_lua(mapping)
    for db_name in ("zones", "items", "units", "objects"):
        parse_pf_names(mapping, db_name)
    for key, value in MANUAL.items():
        add_mapping(mapping, key, value, override=True)
    return mapping


def translate_text(text: str, mapping: dict[str, str]) -> str | None:
    if not text or has_cn(text):
        return None
    if text in mapping:
        return mapping[text]
    if ", " in text:
        parts = text.split(", ")
        translated = [mapping.get(part) for part in parts]
        if all(translated):
            return "，".join(translated)
    return None


def patch_dbc(path: Path, fields: list[int], mapping: dict[str, str]) -> tuple[int, list[tuple[str, str]]]:
    data = bytearray(path.read_bytes())
    magic, record_count, field_count, record_size, string_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise ValueError(f"Not a WDBC file: {path}")

    record_start = 20
    string_start = record_start + record_count * record_size
    old_strings = bytes(data[string_start : string_start + string_size])
    new_strings = bytearray(old_strings)
    new_offsets: dict[str, int] = {}
    examples: list[tuple[str, str]] = []

    for record_index in range(record_count):
        for field in fields:
            if field >= field_count:
                continue
            pos = record_start + record_index * record_size + field * 4
            old_offset = struct.unpack_from("<I", data, pos)[0]
            if old_offset >= string_size:
                continue
            old_text = read_cstring(old_strings, old_offset)
            new_text = translate_text(old_text, mapping)
            if not new_text or new_text == old_text:
                continue
            if old_text not in new_offsets:
                new_offsets[old_text] = len(new_strings)
                new_strings.extend(new_text.encode("utf-8") + b"\0")
            struct.pack_into("<I", data, pos, new_offsets[old_text])
            if len(examples) < 30:
                examples.append((old_text, new_text))

    if not new_offsets:
        return 0, []

    struct.pack_into("<I", data, 16, len(new_strings))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / path.name).write_bytes(data[:string_start] + new_strings)
    return len(new_offsets), examples


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    mapping = build_translation_map()
    lines = [
        "# Native Text DBC Patch Report (Safe Batch)",
        "",
        f"Exact translation entries loaded: {len(mapping)}",
        "",
        "| DBC | Fields | Unique strings patched |",
        "| --- | --- | ---: |",
    ]
    all_examples: list[tuple[str, list[tuple[str, str]]]] = []
    for dbc_name, fields in FIELD_SPECS.items():
        source_path = SRC / dbc_name
        if not source_path.exists():
            source_path = SRC_FALLBACK / dbc_name
        count, examples = patch_dbc(source_path, fields, mapping)
        lines.append(f"| {dbc_name} | {', '.join(map(str, fields))} | {count} |")
        if examples:
            all_examples.append((dbc_name, examples))

    for dbc_name, examples in all_examples:
        lines.extend(["", f"## {dbc_name}", ""])
        lines.extend(f"- `{old}` -> `{new}`" for old, new in examples[:20])

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
