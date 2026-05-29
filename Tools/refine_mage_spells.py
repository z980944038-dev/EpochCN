# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import os
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "SpellTranslation" / "spell_english_spellbook_priority.tsv"
FULL = ROOT / "SpellTranslation" / "spell_english_full_for_translation.tsv"
DEFAULT_DBC = ROOT / "汉化补丁" / "_cn_work_spell_patchB" / "overlay" / "DBFilesClient" / "Spell.dbc"
DBC = Path(os.environ.get("EPOCHCN_SPELL_DBC", DEFAULT_DBC))

MAGE_SKILLS = {"6", "8", "237"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")

NAME_ZH = {
    "Amplify Magic": "魔法增效", "Arcane Barrage": "奥术弹幕", "Arcane Blast": "奥术冲击",
    "Arcane Brilliance": "奥术光辉", "Arcane Concentration": "奥术专注", "Arcane Explosion": "魔爆术",
    "Arcane Flows": "奥术涌动", "Arcane Focus": "奥术集中", "Arcane Fortitude": "奥术坚韧",
    "Arcane Impact": "奥术冲击", "Arcane Instability": "奥术增效", "Arcane Intellect": "奥术智慧",
    "Arcane Meditation": "奥术冥想", "Arcane Mind": "奥术心智", "Arcane Missile": "奥术飞弹",
    "Arcane Missiles": "奥术飞弹", "Arcane Potency": "奥术潜能", "Arcane Power": "奥术强化",
    "Arcane Subtlety": "奥术精妙", "Arctic Reach": "极寒延伸", "Arctic Winds": "极寒之风",
    "Blast Wave": "冲击波", "Blazing Speed": "炽热疾速", "Blink": "闪现术",
    "Blizzard": "暴风雪", "Brain Freeze": "冰冷智慧", "Burning Determination": "燃烧意志",
    "Burning Soul": "燃烧之魂", "Burnout": "燃尽", "Chilled": "冰冷", "Chilled to the Bone": "透骨之寒",
    "Clearcasting": "节能施法", "Cold Snap": "急速冷却", "Combustion": "燃烧",
    "Cone of Cold": "冰锥术", "Conjure Food": "造食术", "Conjure Mana Citrine": "制造法力黄水晶",
    "Conjure Mana Emerald": "制造法力翡翠", "Conjure Mana Gem": "制造法力宝石",
    "Conjure Mana Jade": "制造法力翡翠", "Conjure Mana Ruby": "制造法力红宝石",
    "Conjure Refreshment": "制造魔法点心", "Conjure Water": "造水术", "Conjure Weapon": "魔法武器",
    "Counterspell": "法术反制", "Critical Mass": "火焰重击", "Dalaran Brilliance": "达拉然光辉",
    "Dalaran Intellect": "达拉然智慧", "Dampen Magic": "魔法抑制", "Deep Freeze": "深度冻结",
    "Deep Freeze Immunity State": "深度冻结免疫状态", "Dragon's Breath": "龙息术",
    "Elemental Precision": "元素精准", "Empowered Arcane Missiles": "强化奥术飞弹",
    "Empowered Fireball": "强化火球术", "Empowered Frostbolt": "强化寒冰箭",
    "Enduring Winter": "寒冬持久", "Evocation": "唤醒", "Felfire": "邪火",
    "Fiery Payback": "火焰回馈", "Fingers of Frost": "寒冰指", "Fire Blast": "火焰冲击",
    "Fire Power": "火焰强化", "Fire Ward": "防护火焰结界", "Fire Vulnerability": "火焰易伤",
    "Fireball": "火球术", "Flame Throwing": "烈焰投掷", "Flamestrike": "烈焰风暴",
    "Firestarter": "纵火", "Focus Magic": "专注魔法", "Frost Armor": "霜甲术",
    "Frost Channeling": "冰霜导能", "Frost Nova": "冰霜新星", "Frost Ward": "防护冰霜结界",
    "Frost Warding": "冰霜障壁", "Frostbite": "霜寒刺骨", "Frostbolt": "寒冰箭",
    "Frostfire Bolt": "霜火之箭", "Frozen Core": "冰冷核心", "Hot Streak": "法术连击",
    "Ice Armor": "冰甲术", "Ice Barrier": "寒冰护体", "Ice Block": "寒冰屏障",
    "Ice Floes": "浮冰", "Ice Lance": "冰枪术", "Ice Shards": "寒冰碎片",
    "Icy Veins": "冰冷血脉", "Ignite": "点燃", "Impact": "冲击", "Incineration": "烧尽",
    "Improved Arcane Intellect": "强化奥术智慧", "Improved Arcane Missiles": "强化奥术飞弹",
    "Improved Blizzard": "强化暴风雪", "Improved Blasting": "强化冲击",
    "Improved Cone of Cold": "强化冰锥术", "Improved Counterspell": "强化法术反制",
    "Improved Fireball": "强化火球术", "Improved Flamestrike": "强化烈焰风暴",
    "Improved Frost Nova": "强化冰霜新星", "Improved Frostbolt": "强化寒冰箭",
    "Improved Scorch": "强化灼烧", "Improved Shielding": "强化护盾",
    "Incanter's Absorption": "咒术吸收", "Invisibility": "隐形术", "Living Bomb": "活动炸弹",
    "Mage Armor": "法师护甲", "Magic Absorption": "魔法吸收", "Magic Attunement": "魔法协调",
    "Mana Shield": "法力护盾", "Master of Schools": "学派大师", "Mind Mastery": "心灵掌握",
    "Mirror Image": "镜像", "Missile Barrage": "飞弹速射", "Molten Armor": "熔岩护甲",
    "Molten Fury": "熔岩之怒", "Molten Shields": "熔岩护盾", "Netherwind Presence": "灵风拂面",
    "Permafrost": "永冻", "Piercing Ice": "刺骨寒冰", "Playing with Fire": "玩火自焚",
    "Polymorph": "变形术", "Portal: Dalaran": "传送门：达拉然", "Portal: Darnassus": "传送门：达纳苏斯",
    "Portal: Exodar": "传送门：埃索达", "Portal: Ironforge": "传送门：铁炉堡",
    "Portal: Orgrimmar": "传送门：奥格瑞玛", "Portal: Shattrath": "传送门：沙塔斯",
    "Portal: Silvermoon": "传送门：银月城", "Portal: Stonard": "传送门：斯通纳德",
    "Portal: Stormwind": "传送门：暴风城", "Portal: Theramore": "传送门：塞拉摩",
    "Portal: Thunder Bluff": "传送门：雷霆崖", "Portal: Undercity": "传送门：幽暗城",
    "Presence of Mind": "气定神闲", "Prismatic Cloak": "棱光屏障", "Pyroblast": "炎爆术",
    "Pyromaniac": "纵火狂", "Remove Lesser Curse": "解除次级诅咒",
    "Ritual of Refreshment": "餐桌仪式", "Rune of Power": "能量符文", "Scorch": "灼烧",
    "Shatter": "碎冰", "Shattered Barrier": "碎裂屏障", "Slow": "减速术", "Slow Fall": "缓落术",
    "Spell Power": "法术能量", "Spellsteal": "法术偷取", "Student of the Mind": "心灵学者",
    "Summon Water Elemental": "召唤水元素", "Summon Water Elemental (Prototype)": "召唤水元素（原型）",
    "Teleport: Dalaran": "传送：达拉然", "Teleport: Darnassus": "传送：达纳苏斯",
    "Teleport: Exodar": "传送：埃索达", "Teleport: Ironforge": "传送：铁炉堡",
    "Teleport: Orgrimmar": "传送：奥格瑞玛", "Teleport: Shattrath": "传送：沙塔斯",
    "Teleport: Silvermoon": "传送：银月城", "Teleport: Stonard": "传送：斯通纳德",
    "Teleport: Stormwind": "传送：暴风城", "Teleport: Theramore": "传送：塞拉摩",
    "Teleport: Thunder Bluff": "传送：雷霆崖", "Teleport: Undercity": "传送：幽暗城",
    "Torment the Weak": "欺凌弱小", "Wand Specialization": "魔杖专精", "Winter's Chill": "深冬之寒",
}

TERM_FIXES = [
    ("Arcane", "奥术"), ("Fire", "火焰"), ("Frost", "冰霜"), ("Shadow", "暗影"),
    ("damage", "伤害"), ("Damage", "伤害"), ("mana", "法力值"), ("Mana", "法力值"),
    ("spell", "法术"), ("spells", "法术"), ("Spell", "法术"), ("critical strike", "暴击"),
    ("Critical Strike", "暴击"), ("critical", "暴击"), ("Crit", "暴击"),
    ("Intellect", "智力"), ("Spirit", "精神"), ("Armor", "护甲"), ("resistance", "抗性"),
    ("resistances", "抗性"), ("threat", "威胁值"), ("cooldown", "冷却时间"), ("Mage", "法师"),
    ("Fireball", "火球术"), ("Frostbolt", "寒冰箭"), ("Arcane Missiles", "奥术飞弹"),
    ("Fire Blast", "火焰冲击"), ("Arcane Blast", "奥术冲击"), ("Scorch", "灼烧"),
    ("Pyroblast", "炎爆术"), ("Blizzard", "暴风雪"), ("Cone of Cold", "冰锥术"),
    ("Frost Nova", "冰霜新星"), ("Mana Shield", "法力护盾"), ("Mage Armor", "法师护甲"),
    ("爆击", "暴击"), ("他:她;", ""),
]

DURATION_BY_NAME = {
    "Invisibility": "20秒", "Frostbolt": "5秒", "Polymorph": "50秒", "Cone of Cold": "8秒",
    "Frost Nova": "8秒", "Slow Fall": "30秒", "Fireball": "8秒", "Frost Armor": "30分钟",
    "Ice Armor": "30分钟", "Molten Armor": "30分钟", "Mage Armor": "30分钟", "Fire Ward": "30秒",
    "Frost Ward": "30秒", "Dampen Magic": "10分钟", "Amplify Magic": "10分钟", "Arcane Intellect": "30分钟",
    "Arcane Brilliance": "1小时", "Dalaran Intellect": "30分钟", "Dalaran Brilliance": "1小时",
    "Mana Shield": "1分钟", "Counterspell": "8秒", "Flamestrike": "8秒", "Arcane Missiles": "5秒",
    "Arcane Missile": "5秒", "Blizzard": "8秒", "Pyroblast": "12秒", "Ice Barrier": "1分钟",
    "Living Bomb": "12秒", "Icy Veins": "20秒", "Combustion": "直到取消", "Arcane Power": "15秒",
    "Evocation": "8秒", "Slow": "15秒", "Mirror Image": "30秒", "Focus Magic": "30分钟",
    "Deep Freeze": "5秒", "Dragon's Breath": "5秒", "Ice Block": "10秒", "Rune of Power": "1分钟",
}

RADIUS_BY_NAME = {
    "Arcane Explosion": 10, "Blizzard": 8, "Blast Wave": 10, "Dragon's Breath": 10, "Flamestrike": 8,
    "Frost Nova": 12, "Mirror Image": 0,
}

FOOD_BY_RANK = {
    1: "小松饼", 2: "面包", 3: "黑麦面包", 4: "粗黑麦面包", 5: "酸面包", 6: "甜面包",
    7: "肉桂卷", 8: "牛角面包",
}
WATER_BY_RANK = {
    1: "水", 2: "清水", 3: "纯净水", 4: "泉水", 5: "矿泉水", 6: "苏打水",
    7: "晶水", 8: "山泉水", 9: "冰川之水",
}
CITY_BY_NAME = {
    "Stormwind": "暴风城", "Ironforge": "铁炉堡", "Undercity": "幽暗城", "Darnassus": "达纳苏斯",
    "Thunder Bluff": "雷霆崖", "Orgrimmar": "奥格瑞玛", "Shattrath": "沙塔斯", "Exodar": "埃索达",
    "Silvermoon": "银月城", "Stonard": "斯通纳德", "Theramore": "塞拉摩", "Dalaran": "达拉然",
}


def signed(value: int) -> int:
    return value if value < 2**31 else value - 2**32


class SpellRec:
    def __init__(self, values: tuple[int, ...], strings: bytes, string_size: int):
        self.id = values[0]
        self.values = values
        self.name = self._read(strings, string_size, values[136])
        self.rank = self._read(strings, string_size, values[153])
        self.desc = self._read(strings, string_size, values[170])
        self.aura = self._read(strings, string_size, values[187])

    @staticmethod
    def _read(strings: bytes, string_size: int, offset: int) -> str:
        if offset >= string_size:
            return ""
        end = strings.find(b"\0", offset)
        if end < 0:
            return ""
        return strings[offset:end].decode("utf-8", errors="replace")

    def s(self, n: int) -> int:
        return signed(self.values[80 + n - 1]) + 1

    def maxv(self, n: int) -> int:
        return self.s(n) + signed(self.values[74 + n - 1])

    def h(self) -> int:
        return signed(self.values[35])

    def stack(self) -> int:
        return signed(self.values[49])

    def amp_sec(self, n: int) -> int:
        amp = signed(self.values[98 + n - 1])
        return int(amp / 1000) if amp > 0 else 0


def load_spell_dbc() -> dict[int, SpellRec]:
    data = DBC.read_bytes()
    magic, record_count, field_count, record_size, string_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise RuntimeError(f"{DBC} is not WDBC")
    record_start = 20
    string_start = record_start + record_count * record_size
    strings = data[string_start:string_start + string_size]
    records = {}
    for index in range(record_count):
        values = struct.unpack_from("<" + "I" * field_count, data, record_start + index * record_size)
        records[values[0]] = SpellRec(values, strings, string_size)
    return records


def rank_num(row: dict[str, str]) -> int:
    match = re.search(r"(\d+)", row.get("rank_en", ""))
    return int(match.group(1)) if match else 1


def rank_zh(rank: str) -> str:
    if not rank:
        return ""
    match = re.fullmatch(r"Rank (\d+)", rank)
    if match:
        return f"等级 {match.group(1)}"
    return rank.replace("Rank", "等级").replace("Passive", "被动")


def duration(rec: SpellRec) -> str:
    return DURATION_BY_NAME.get(rec.name, "")


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 2
        dur = duration(rec)
        match = re.search(r"(\d+)", dur)
        ticks = int(match.group(1)) // seconds if match else 1
    return rec.s(n) * ticks


def cleanup(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\\n", "\n")
    for old, new in sorted(NAME_ZH.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(old, new)
    for old, new in TERM_FIXES:
        text = text.replace(old, new)
    text = re.sub(r"\$l([^:;]*):([^;]*);", lambda m: m.group(1) or m.group(2) or "", text)
    text = re.sub(r"\$g([^:;]*):([^;]*);", lambda m: m.group(1) or m.group(2) or "", text)
    text = text.replace("降低-", "降低").replace("提高-", "降低").replace("减少-", "减少")
    text = text.replace("有一定几率", "有几率")
    text = re.sub(r"\$\{[^{}]*\}|\$[<A-Za-z0-9_/.*;:-]+|\$", "", text)
    text = re.sub(r" +([，。；：、])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    return text.strip()


def ref_value(spell_id: int, token: str, number: str, records: dict[int, SpellRec], rec: SpellRec) -> str:
    target = records.get(spell_id, rec)
    index = int(number or "1")
    token = token.lower()
    if token in ("s", "m"):
        return str(target.s(index))
    if token == "o":
        return str(over_time(target, index))
    if token == "d":
        return duration(target)
    if token == "t":
        return str(target.amp_sec(index) or 1)
    if token == "a":
        return str(RADIUS_BY_NAME.get(target.name, target.s(index)))
    if token in ("u", "n", "i"):
        return str(target.stack() or target.s(index) or 1)
    return ""


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    text = text.replace("$D", duration(rec)).replace("$d", duration(rec)).replace("$e", "1")
    text = re.sub(r"\$\{\$(\d+)m(\d+)\*8\}", lambda m: str(records[int(m.group(1))].s(int(m.group(2))) * 8), text)
    text = re.sub(r"\$\{\$m(\d+)\*8\}", lambda m: str(rec.s(int(m.group(1))) * 8), text)
    text = re.sub(r"\$\{\$SP\*0\.193\+\$m(\d+)\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度19.3%", text)
    text = re.sub(r"\$\{\$SP\*0\.386\+\$m(\d+)\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度38.6%", text)
    text = re.sub(r"\$\{\$m(\d+)\+\$SP\*0\.15\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度15%", text)
    text = re.sub(r"\$\{\$m(\d+)\+\$SP\*0\.2\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度20%", text)
    text = re.sub(r"\$\{\$m(\d+)\*\$<mult>\}", lambda m: str(rec.s(int(m.group(1)))), text)
    text = re.sub(r"\$\{\$M(\d+)\*\$<mult>\}", lambda m: str(rec.maxv(int(m.group(1)))), text)
    text = re.sub(r"\$\{[^{}]*\}", "基于属性计算的数值", text)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: str(int(int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1)))), text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: str(int(int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1)))), text)
    text = re.sub(r"\$([0-9]+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: str(over_time(rec, int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)", lambda _: str(RADIUS_BY_NAME.get(rec.name, 0) or 10), text, flags=re.I)
    text = text.replace("$h", str(rec.h())).replace("$H", str(rec.h()))
    return cleanup(text)


def missile_effect(row: dict[str, str], records: dict[int, SpellRec]) -> SpellRec:
    match = re.search(r"\$(\d+)s1", row.get("description_en", ""))
    return records.get(int(match.group(1)), records[int(row["spell_id"])]) if match else records[int(row["spell_id"])]


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    rank = rank_num(row)
    desc_en = row.get("description_en") or rec.desc

    if name == "Fireball":
        return f"发射一枚火球，造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害，并在 8 秒内额外造成 {over_time(rec, 2, 4)} 点火焰伤害。"
    if name == "Frostbolt":
        return f"向敌人发射寒冰箭，造成 {rec.s(2)} 到 {rec.maxv(2)} 点冰霜伤害，并使其移动速度降低 {abs(rec.s(1))}%，持续 5 秒。"
    if name == "Arcane Missiles" or name == "Arcane Missile":
        eff = missile_effect(row, records)
        return f"向敌人发射奥术飞弹，每秒造成 {eff.s(1)} 点奥术伤害，持续 5 秒。"
    if name == "Blizzard":
        match = re.search(r"\$(\d+)m1\*8", desc_en)
        eff = records.get(int(match.group(1)), rec) if match else rec
        return f"冰片落向目标区域，在 8 秒内对 8 码范围内的敌人造成 {eff.s(1) * 8} 点冰霜伤害。"
    if name == "Fire Blast":
        return f"冲击敌人，造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害。"
    if name == "Scorch":
        return f"灼烧敌人，造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害。"
    if name == "Arcane Explosion":
        return f"在施法者周围引发奥术爆炸，对 10 码范围内所有敌人造成 {rec.s(1)} 到 {rec.maxv(1)} 点奥术伤害。"
    if name == "Cone of Cold":
        return f"施法者前方锥形区域内的目标受到 {rec.s(2)} 到 {rec.maxv(2)} 点冰霜伤害，移动速度降低 {abs(rec.s(1))}%，持续 8 秒。"
    if name == "Frost Nova":
        return f"冲击施法者附近的敌人，造成 {rec.s(1)} 到 {rec.maxv(1)} 点冰霜伤害，并将其冻结在原地，最多持续 8 秒。受到伤害可能打断该效果。"
    if name == "Flamestrike":
        return f"召唤火柱灼烧区域内所有敌人，造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害，并在 8 秒内额外造成 {over_time(rec, 2, 4)} 点火焰伤害。"
    if name == "Pyroblast":
        return f"投掷巨大的火焰巨石，造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害，并在 12 秒内额外造成 {over_time(rec, 2, 4)} 点火焰伤害。"
    if name == "Blast Wave":
        return f"从施法者身边放出烈焰波，对 10 码范围内所有敌人造成 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害，并使其眩晕 6 秒。"
    if name == "Dragon's Breath":
        return f"施法者前方锥形区域内的目标受到 {rec.s(1)} 到 {rec.maxv(1)} 点火焰伤害，并迷惑 5 秒。任何直接伤害都会取消该效果。"
    if name == "Ice Lance":
        return f"快速对目标造成 {rec.s(1)} 到 {rec.maxv(1)} 点冰霜伤害。对被冻结的目标造成三倍伤害。"
    if name == "Frostfire Bolt":
        return f"向敌人发射霜火之箭，造成 {rec.s(2)} 到 {rec.maxv(2)} 点霜火伤害，使其移动速度降低 {abs(rec.s(1))}%，并在 9 秒内额外造成 {over_time(rec, 3, 3)} 点霜火伤害。"
    if name == "Arcane Blast":
        return f"用能量冲击目标，造成 {rec.s(1)} 到 {rec.maxv(1)} 点奥术伤害。每次施放都会强化后续奥术法术效果，但提高奥术冲击的法力消耗，最多叠加 4 次。"
    if name == "Arcane Barrage":
        return f"向敌方目标发射数枚飞弹，造成 {rec.s(1)} 到 {rec.maxv(1)} 点奥术伤害。"
    if name == "Living Bomb":
        explosion = records.get(rec.s(2), rec)
        return f"目标变成活动炸弹，在 12 秒内受到 {over_time(rec, 1, 4)} 点火焰伤害。效果结束或被驱散时，目标会爆炸，对 10 码范围内所有敌人造成 {explosion.s(1)} 到 {explosion.maxv(1)} 点火焰伤害。"
    if name == "Deep Freeze":
        return "使目标昏迷 5 秒。只能对被冻结的目标使用。"

    if name == "Polymorph":
        return "将敌人变成绵羊，使其到处游荡，最多持续 50 秒。期间目标无法攻击或施法，但生命值恢复速度极快。任何伤害都会使目标恢复原状。同一时间只能变形一个目标。"
    if name == "Invisibility":
        return "使施法者在 5 秒内逐渐隐形，每秒降低威胁值。执行或受到任何动作都会取消该效果。隐形后只能看见其他隐形目标和能够看见隐形的目标，持续 20 秒。"
    if name == "Slow Fall":
        return "使友方小队或团队目标的坠落速度降低，持续 30 秒。"
    if name == "Blink":
        return "使施法者向前传送 20 码，除非有障碍物阻挡。同时解除昏迷和束缚效果。"
    if name == "Counterspell":
        return "反制敌人的施法，使其在 8 秒内无法施放该系任何法术，并产生大量威胁值。"
    if name == "Remove Lesser Curse":
        return f"移除友方目标身上的 {rec.s(1)} 个诅咒。"
    if name == "Spellsteal":
        return "从目标身上偷取一个有益魔法效果。该效果最多持续 2 分钟。"
    if name == "Slow":
        return f"使目标移动速度降低 {abs(rec.s(1))}%，远程攻击间隔延长 {rec.s(2)}%，施法时间延长 {rec.s(3)}%，持续 15 秒。"
    if name == "Evocation":
        return "引导期间每 2 秒恢复 15% 法力值，持续 8 秒。"
    if name == "Presence of Mind":
        return "激活后，你下一个施法时间低于 10 秒的法师法术会变为瞬发。"
    if name == "Arcane Power":
        return f"激活后，你的法术伤害提高 {rec.s(1)}%，施法法力消耗提高 {rec.s(2)}%，持续 15 秒。"
    if name == "Combustion":
        return "激活后，每次火焰伤害法术命中都会使你的火焰法术暴击几率提高 10%。该效果持续到你造成 3 次火焰法术暴击为止。"
    if name == "Cold Snap":
        return "激活后，立即结束所有冰霜法术的冷却时间。"
    if name == "Icy Veins":
        return "加速你的施法，使施法速度提高 20%，并使你施法时因受到伤害而损失的施法时间减少 100%，持续 20 秒。"
    if name == "Ice Block":
        return "你被包裹在寒冰屏障中，免疫所有物理和法术攻击，持续 10 秒，但期间无法攻击、移动或施法。"
    if name == "Mirror Image":
        return "在施法者附近制造 3 个镜像，它们会施放法术并攻击法师的敌人，持续 30 秒。"
    if name == "Summon Water Elemental" or name == "Summon Water Elemental (Prototype)":
        return "召唤一个水元素为施法者作战，持续 45 秒。"
    if name == "Rune of Power":
        return "在地面放置一枚能量符文，站在符文上时法术伤害提高，持续 1 分钟。"

    if name == "Fire Ward":
        return f"吸收 {rec.s(1)} 点火焰伤害，持续 30 秒。"
    if name == "Frost Ward":
        return f"吸收 {rec.s(1)} 点冰霜伤害，持续 30 秒。"
    if name == "Mana Shield":
        return f"吸收 {rec.s(1)} 点伤害，改为消耗法力值。每吸收 1 点伤害消耗 1 点法力值，持续 1 分钟。"
    if name == "Ice Barrier":
        return f"立即为你施加护盾，吸收 {rec.s(1)} 点伤害，持续 1 分钟。护盾存在时，受到伤害不会延迟施法。"
    if name == "Frost Armor":
        return f"使护甲值提高 {rec.s(1)} 点。敌人击中施法者时，可能会使其移动速度降低 30%、攻击间隔延长 25%，持续 5 秒。同一时间只能激活一种护甲法术，持续 30 分钟。"
    if name == "Ice Armor":
        return f"使护甲值提高 {rec.s(1)} 点，冰霜抗性提高 {rec.s(3)} 点。敌人击中施法者时，可能会使其移动速度降低 30%、攻击间隔延长 25%，持续 5 秒。同一时间只能激活一种护甲法术，持续 30 分钟。"
    if name == "Mage Armor":
        extra = f"此外，施加在你身上的有害魔法效果持续时间缩短 {abs(rec.s(3))}%。" if rec.s(3) < 0 else ""
        return f"使你的所有魔法抗性提高 {rec.s(1)} 点，并允许你在施法时保持 {rec.s(2)}% 的法力恢复速度。{extra}同一时间只能激活一种护甲法术，持续 30 分钟。"
    if name == "Molten Armor":
        return f"被击中时对攻击者造成火焰伤害，使你被暴击的几率降低 {abs(rec.s(2))}%，法术暴击几率提高 {rec.s(3)}%。同一时间只能激活一种护甲法术，持续 30 分钟。"
    if name == "Dampen Magic":
        return f"抑制施放在队友身上的魔法，使其受到的法术伤害最多降低 {rec.s(1)} 点，受到的治疗效果最多降低 {rec.s(2)} 点，持续 10 分钟。"
    if name == "Amplify Magic":
        return f"增强施放在队友身上的魔法，使其受到的法术伤害最多提高 {rec.s(1)} 点，受到的治疗效果最多提高 {rec.s(2)} 点，持续 10 分钟。"
    if name in ("Arcane Intellect", "Dalaran Intellect"):
        return f"使目标智力提高 {rec.s(1)} 点，持续 30 分钟。"
    if name in ("Arcane Brilliance", "Dalaran Brilliance"):
        return f"使小队和团队成员的智力提高 {rec.s(1)} 点，持续 1 小时。"

    if name == "Conjure Food":
        return f"制造 {rec.s(1)} 个{FOOD_BY_RANK.get(rank, '魔法食物')}，为法师及其盟友提供食物。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Conjure Water":
        return f"制造 {rec.s(1)} 瓶{WATER_BY_RANK.get(rank, '魔法水')}，为法师及其盟友提供饮品。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name in ("Conjure Refreshment", "Ritual of Refreshment"):
        return f"制造 {rec.s(1)} 个魔法点心，为法师及其盟友提供食物和饮品。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name.startswith("Conjure Mana"):
        restore = re.search(r"\$(\d+)s1", desc_en)
        amount = records[int(restore.group(1))].s(1) if restore else rec.s(1)
        return f"制造一颗法力宝石，使用后可立即恢复 {amount} 点法力值。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Conjure Weapon":
        return "制造一件耐久度为 50 的魔法武器，任何可以使用该类型武器的人都可以装备。武器造成的伤害取决于法师等级。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name.startswith("Teleport:"):
        city = CITY_BY_NAME.get(name.split(": ", 1)[1], name.split(": ", 1)[1])
        return f"将施法者传送到{city}。"
    if name.startswith("Portal:"):
        city = CITY_BY_NAME.get(name.split(": ", 1)[1], name.split(": ", 1)[1])
        return f"制造一个传送门，使用它的小队成员会被传送到{city}。"

    talent = talent_desc(name, rec, row, records)
    if talent:
        return talent
    resolved = resolve_tokens(desc_en, rec, records)
    if CJK_RE.search(resolved) and not re.search(r"[A-Za-z]{3,}", resolved) and "基于属性计算的数值" not in resolved:
        return resolved
    return f"{NAME_ZH.get(name, name)}。"


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rank = rank_num(row)
    if name in ("Improved Fireball", "Improved Frostbolt"):
        spell = "火球术" if "Fireball" in name else "寒冰箭"
        return f"使你的{spell}施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒。"
    if name in ("Fire Power", "Piercing Ice", "Arctic Winds", "Molten Fury", "Torment the Weak"):
        target = {"Fire Power": "火焰法术", "Piercing Ice": "冰霜法术", "Arctic Winds": "所有冰霜伤害", "Molten Fury": "对生命值低于 35% 目标的法术", "Torment the Weak": "对被减速或诱捕目标的法术"}.get(name, "法术")
        return f"使你的{target}伤害提高 {rec.s(1)}%。"
    if name in ("Critical Mass", "Incineration", "Arcane Impact", "Killer Instinct"):
        return f"使相关法术的暴击几率提高 {rec.s(1)}%。"
    if name == "Ignite":
        return f"你的火焰法术暴击会使目标在 4 秒内额外受到相当于该次法术伤害 {rec.s(1)}% 的火焰伤害。"
    if name == "Impact":
        return f"你的火焰法术有 {rec.s(1)}% 几率使目标昏迷 2 秒。"
    if name == "Improved Scorch":
        return f"你的灼烧有 {rec.s(1)}% 几率使目标更容易受到火焰伤害，受到的火焰伤害提高 3%，持续 30 秒，最多叠加 5 次。"
    if name == "Improved Flamestrike":
        return f"使你的烈焰风暴暴击几率提高 {rec.s(1)}%，施法时间缩短 {abs(rec.s(2)) / 1000:g} 秒。"
    if name == "Flame Throwing":
        return f"使你的火焰法术射程提高 {rec.s(1)} 码。"
    if name == "Burning Soul":
        return f"使你的火焰法术因受到伤害而损失的施法时间缩短 {abs(rec.s(1))}%，并使火焰法术造成的威胁值降低 {abs(rec.s(2))}%。"
    if name == "Molten Shields":
        return f"使你的防护火焰结界有 {rec.s(1)}% 几率反射火焰法术，并使熔岩护甲有 {rec.s(2)}% 几率影响远程和法术攻击者。"
    if name == "Playing with Fire":
        return f"使你造成的所有法术伤害提高 {rec.s(1)}%，受到的所有法术伤害提高 {rec.s(2)}%。"
    if name == "Pyromaniac":
        return f"使你的火焰法术暴击几率提高 {rec.s(1)}%，并使精神总值提高 {rec.s(2)}%。"
    if name == "Burnout":
        return f"使你的法术暴击伤害加成提高 {rec.s(1)}%，但非周期性法术暴击会额外消耗基础法力值的 {rec.s(2)}%。"
    if name == "Hot Streak":
        return f"当你的火球术、霜火之箭、灼烧、火焰冲击或炎爆术连续 2 次造成暴击后，有 {rec.h()}% 几率使下一个炎爆术变为瞬发。"
    if name == "Firestarter":
        return "你的熔岩护甲激活时，灼烧不消耗法力且可在移动中施放；你的冲击波和龙息术造成伤害后，有几率使下一个烈焰风暴变为瞬发且不消耗法力。"
    if name == "Fiery Payback":
        return f"当生命值低于 35% 时，你受到的所有伤害降低 {abs(rec.s(1))}%，炎爆术施法时间缩短 {abs(rec.s(2)) / 1000:g} 秒，冷却时间缩短 {abs(rec.s(3)) / 1000:g} 秒。"

    if name == "Ice Shards":
        return f"使你的冰霜法术暴击伤害加成提高 {rec.s(1)}%。"
    if name == "Frostbite":
        return f"你的寒冷效果有 {rec.s(1)}% 几率将目标冻结 5 秒。如果目标免疫冻结，则会被视为被冻结。"
    if name == "Improved Frost Nova":
        return f"使你的冰霜新星冷却时间缩短 {abs(rec.s(1))} 秒。"
    if name == "Permafrost":
        return f"使你的寒冷效果持续时间延长 {rec.s(1)}%，目标移动速度额外降低 {abs(rec.s(2))}%，并使目标受到的治疗效果降低 {rec.s(3)}%。"
    if name == "Improved Blizzard":
        return f"使你的暴风雪附带寒冷效果，令目标移动速度降低 {abs(rec.s(1))}%，持续 1.5 秒。"
    if name == "Frost Channeling":
        return f"使你的所有法术法力消耗降低 {abs(rec.s(1))}%，冰霜法术造成的威胁值降低 {abs(rec.s(2))}%。"
    if name == "Shatter":
        return f"使你的所有法术对被冻结目标的暴击几率提高 {rec.s(1)}%。"
    if name == "Improved Cone of Cold":
        return f"使你的冰锥术伤害提高 {rec.s(1)}%。"
    if name == "Winter's Chill":
        return f"你的冰霜伤害法术有 {rec.h()}% 几率使目标受到冰霜法术暴击几率提高 {rec.s(1)}%，持续 15 秒，最多叠加 5 次。"
    if name == "Frozen Core":
        return f"使你受到的法术伤害降低 {abs(rec.s(1))}%，冰冷血脉激活时受到的伤害额外降低 {abs(rec.s(2))}%。"
    if name == "Ice Floes":
        return f"使你的冰霜新星、冰锥术、寒冰屏障和冰冷血脉冷却时间缩短 {abs(rec.s(1))}%。"
    if name == "Fingers of Frost":
        return f"你的寒冷效果有几率使你接下来 {rec.s(1)} 个法术将目标视为被冻结，持续 15 秒。"
    if name == "Brain Freeze":
        return f"你的带有寒冷效果的冰霜伤害法术有 {rec.h()}% 几率使下一个火球术变为瞬发且不消耗法力。"
    if name == "Enduring Winter":
        return f"使你的水元素持续时间延长 {rec.s(1)} 秒，你的寒冰箭有 {rec.h()}% 几率为最多 10 名小队或团队成员提供恢复法力效果。"
    if name == "Chilled to the Bone":
        return f"使你的寒冰箭、霜火之箭和冰枪术伤害提高 {rec.s(1)}%，并使寒冷效果额外降低目标移动速度 {abs(rec.s(2))}%。"
    if name == "Shattered Barrier":
        return f"你的寒冰护体被摧毁时，有 {rec.h()}% 几率冻结 10 码范围内所有敌人，持续 8 秒。"
    if name == "Cold as Ice":
        return f"使你的急速冷却、冰冷血脉、寒冰护体和召唤水元素冷却时间缩短 {abs(rec.s(1))}%。"
    if name == "Empowered Frostbolt":
        return f"使你的寒冰箭从法术强度获得的伤害加成提高 {rec.s(1)}%，暴击几率提高 {rec.s(2)}%。"

    if name == "Wand Specialization":
        return f"使你的魔杖伤害提高 {rec.s(1)}%。"
    if name == "Arcane Subtlety":
        return f"使目标对你所有法术的抗性降低 {rec.s(2)} 点，并使奥术法术造成的威胁值降低 {abs(rec.s(1))}%。"
    if name == "Arcane Concentration":
        return f"你的伤害法术命中目标后，有 {rec.h()}% 几率进入节能施法状态，使下一个伤害法术法力消耗降低 100%。"
    if name == "Arcane Focus":
        return f"使目标抵抗你的奥术法术的几率降低 {abs(rec.s(1))}%。"
    if name == "Arcane Mind":
        return f"使你的智力总值提高 {rec.s(1)}%，护甲值提高相当于智力 {rec.s(2)}% 的数值。"
    if name == "Improved Arcane Missiles":
        return f"引导奥术飞弹时，有 {rec.s(1)}% 几率避免因受到伤害而被打断。"
    if name == "Improved Shielding":
        return f"法力护盾激活时，每点伤害损失的法力值降低 {abs(rec.s(1))}%，法师护甲提供的抗性提高 {rec.s(2)}%。"
    if name == "Magic Attunement":
        return f"使你的魔法抑制和魔法增效效果提高 {rec.s(1)}%，奥术法术射程提高 {rec.s(2)} 码。"
    if name == "Improved Counterspell":
        return f"使你的法术反制有 {rec.s(1)}% 几率使目标沉默 4 秒。"
    if name == "Arcane Meditation":
        return f"使你在施法时仍保持 {rec.s(1)}% 的法力恢复速度。"
    if name == "Improved Arcane Intellect":
        return f"使你的奥术智慧和奥术光辉效果提高 {rec.s(1)}%。"
    if name == "Arcane Fortitude":
        return f"使你的护甲值提高，数值相当于智力的 {rec.s(1)}%。"
    if name == "Arcane Potency":
        return f"节能施法或气定神闲激活后，你下一个伤害法术暴击几率提高 {rec.s(1)}%。"
    if name == "Prismatic Cloak":
        return f"使你受到的所有伤害降低 {abs(rec.s(1))}%，并使隐形术渐隐时间缩短 {abs(rec.s(2))} 秒。"
    if name == "Mind Mastery":
        return f"使你的法术强度提高，数值相当于智力总值的 {rec.s(1)}%。"
    if name == "Incanter's Absorption":
        return f"你的法力护盾、霜火结界、寒冰护体吸收伤害时，法术伤害提高，数值最多相当于吸收量的 {rec.s(1)}%，持续 10 秒。"
    if name == "Student of the Mind":
        return f"使你的精神总值提高 {rec.s(1)}%。"
    if name == "Netherwind Presence":
        return f"使你的法术急速提高 {rec.s(1)}%。"
    if name == "Spell Power":
        return f"使你的法术暴击伤害加成提高 {rec.s(1)}%。"
    if name == "Arcane Flows":
        return f"使你的气定神闲、奥术强化和隐形术冷却时间缩短 {abs(rec.s(1))}%。"
    if name == "Missile Barrage":
        return "你的奥术冲击、奥术弹幕、火球术、霜火之箭和寒冰箭有几率使下一个奥术飞弹引导时间缩短 2.5 秒、法力消耗降低 100%，且飞弹每 0.5 秒发射一次。"
    if name == "Magic Absorption":
        return f"使你的所有抗性提高 {rec.s(1)} 点，并使你完全抵抗一个法术时恢复总法力值的 {rec.s(2)}%。"
    if name == "Elemental Precision":
        return f"使你的火焰和冰霜法术法力消耗降低 {abs(rec.s(1))}%，并使这些法术命中几率提高 {rec.s(2)}%。"
    if name == "Master of Schools":
        return f"使你的奥术、火焰和冰霜法术伤害提高 {rec.s(1)}%。"
    return ""


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    if name in ("Frostbolt", "Cone of Cold", "Slow"):
        return f"移动速度降低 {abs(rec.s(1))}%。"
    if name == "Frost Nova":
        return "被冻结在原地。"
    if name == "Polymorph":
        return "无法攻击或施法，生命恢复速度提高。"
    if name == "Slow Fall":
        return "坠落速度降低。"
    if name == "Fireball":
        return f"每 {rec.amp_sec(2) or 2} 秒造成 {rec.s(2)} 点火焰伤害。"
    if name == "Flamestrike" or name == "Pyroblast":
        return f"每 {rec.amp_sec(2) or 2} 秒造成 {rec.s(2)} 点火焰伤害。"
    if name == "Blizzard":
        eff = records.get(int(re.search(r"\$(\d+)s1", row.get("tooltip_en", "") or "0s1").group(1)), rec) if re.search(r"\$(\d+)s1", row.get("tooltip_en", "")) else rec
        return f"每秒造成 {eff.s(1)} 点冰霜伤害。"
    if name == "Living Bomb":
        explosion = records.get(rec.s(2), rec)
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点火焰伤害。效果结束或被驱散时爆炸，造成 {explosion.s(1)} 点火焰伤害。"
    if name == "Arcane Intellect" or name == "Dalaran Intellect":
        return f"智力提高 {rec.s(1)} 点。"
    if name == "Arcane Brilliance" or name == "Dalaran Brilliance":
        return f"智力提高 {rec.s(1)} 点。"
    if name == "Dampen Magic":
        return f"受到的法术伤害最多降低 {rec.s(1)} 点，治疗效果最多降低 {rec.s(2)} 点。"
    if name == "Amplify Magic":
        return f"受到的法术伤害最多提高 {rec.s(1)} 点，治疗效果最多提高 {rec.s(2)} 点。"
    if name in ("Fire Ward", "Frost Ward"):
        return "吸收对应系法术伤害。"
    if name == "Mana Shield":
        return "吸收伤害，改为消耗法力值。"
    if name == "Ice Barrier":
        return "吸收伤害。"
    if name == "Frost Armor":
        return f"护甲值提高 {rec.s(1)} 点，并可能使攻击者减速。"
    if name == "Ice Armor":
        return f"护甲值提高 {rec.s(1)} 点，冰霜抗性提高 {rec.s(3)} 点，并可能使攻击者减速。"
    if name == "Mage Armor":
        return f"所有魔法抗性提高 {rec.s(1)} 点，并允许施法时保持 {rec.s(2)}% 的法力恢复速度。"
    if name == "Molten Armor":
        return f"被击中时对攻击者造成火焰伤害，被暴击几率降低 {abs(rec.s(2))}%，法术暴击几率提高 {rec.s(3)}%。"
    if name == "Blink":
        return "正在闪现。"
    if name == "Invisibility":
        return "正在渐隐。"
    if name == "Deep Freeze":
        return "昏迷。"
    if name == "Dragon's Breath":
        return "迷惑。"
    if name == "Ice Block":
        return "免疫所有攻击和法术，但无法行动。"
    if name == "Mirror Image":
        return "施法者的镜像正在自行攻击。"
    if name == "Arcane Power":
        return "法术伤害和法力消耗提高。"
    if name == "Presence of Mind":
        return "下一个施法时间低于 10 秒的法师法术会变为瞬发。"
    if name == "Icy Veins":
        return "施法速度提高，施法不会因受到伤害而延迟。"
    source = row.get("tooltip_en") or rec.aura
    tip = resolve_tokens(source, rec, records)
    if CJK_RE.search(tip) and not re.search(r"[A-Za-z]{3,}", tip) and "基于属性计算的数值" not in tip:
        return tip
    return ""


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {field: (row.get(field, "") or "").replace("\t", " ").replace("\r", "").replace("\n", "\\n") for field in fields}
            writer.writerow(out)


def is_mage(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & MAGE_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_mage(row):
            continue
        rec = records[int(row["spell_id"])]
        before = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        row["name_zh"] = NAME_ZH.get(row["name_en"], row.get("name_zh") or rec.name)
        row["rank_zh"] = rank_zh(row.get("rank_en", ""))
        row["description_zh"] = desc_for(row, records)
        row["tooltip_zh"] = tip_for(row, records)
        after = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        if after != before:
            changed += 1
        updates[row["spell_id"]] = {key: row[key] for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh")}
    write_tsv(PRIORITY, fields, rows)

    full_fields, full_rows = read_tsv(FULL)
    full_changed = 0
    for row in full_rows:
        update = updates.get(row["spell_id"])
        if not update:
            continue
        before = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        row.update(update)
        after = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        if after != before:
            full_changed += 1
    write_tsv(FULL, full_fields, full_rows)

    bad = [
        row for row in rows
        if is_mage(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or re.search(r"[A-Za-z]{3,}", row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority mage rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"mage spell ids synced: {len(updates)}")
    print(f"mage zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:30]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
