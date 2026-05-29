#!/usr/bin/env python3
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

SHAMAN_SKILLS = {"373", "374", "375"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")

NAME_ZH = {
    "Ancestral Awakening": "先祖觉醒", "Ancestral Fortitude": "先祖坚韧",
    "Ancestral Healing": "先祖治疗", "Ancestral Knowledge": "先祖知识",
    "Ancestral Spirit": "先祖之魂", "Anticipation": "预知", "Astral Recall": "星界传送",
    "Astral Shift": "星界转移", "Blessing of the Eternals": "永恒祝福",
    "Bloodlust": "嗜血", "Booming Echoes": "轰鸣回响", "Call of Flame": "烈焰召唤",
    "Call of Thunder": "雷霆召唤", "Call of the Ancestors": "先祖的召唤",
    "Call of the Elements": "元素的召唤", "Call of the Spirits": "灵魂的召唤",
    "Chain Heal": "治疗链", "Chain Lightning": "闪电链", "Chained Heal": "链式治疗",
    "Cleanse Spirit": "净化灵魂", "Concussion": "震荡", "Convection": "传导",
    "Cure Disease": "祛病术", "Cure Poison": "消毒术", "Disease Cleansing Totem": "祛病图腾",
    "Earth Elemental Totem": "土元素图腾", "Earth Shield": "大地之盾",
    "Earth Shock": "大地震击", "Earth's Grasp": "大地之握", "Earthbind Totem": "地缚图腾",
    "Earthen Power": "大地之力", "Earthliving Weapon": "大地生命武器",
    "Elemental Devastation": "元素浩劫", "Elemental Focus": "元素集中",
    "Elemental Fury": "元素之怒", "Elemental Mastery": "元素掌握",
    "Elemental Oath": "元素誓约", "Elemental Overload": "元素过载",
    "Elemental Precision": "元素精准", "Elemental Shields": "元素护盾",
    "Elemental Warding": "元素防护", "Elemental Weapons": "元素武器",
    "Enhancing Totems": "强化图腾", "Far Sight": "视界术", "Feral Spirit": "野性狼魂",
    "Fire Elemental Totem": "火元素图腾", "Fire and Lightning Mastery": "火焰与闪电掌握",
    "Fire Nova": "火焰新星", "Fire Nova Totem": "火焰新星图腾",
    "Fire Resistance Totem": "火焰抗性图腾", "Flame Shock": "烈焰震击",
    "Flame Shock Passive": "烈焰震击被动", "Flametongue Totem": "火舌图腾",
    "Flametongue Weapon": "火舌武器", "Flurry": "乱舞", "Focused": "专注",
    "Focused Mind": "专注意志", "Freeze": "冻结", "Frost Resistance Totem": "冰霜抗性图腾",
    "Frost Shock": "冰霜震击", "Frostbrand Weapon": "冰封武器", "Frozen Power": "冰霜之力",
    "Ghost Wolf": "幽魂之狼", "Gift of the Water Spirit": "水灵之赐",
    "Glyph of Healing Wave": "治疗波雕文", "Grace of Air Totem": "风之优雅图腾",
    "Grounding Totem": "根基图腾", "Guardian Totems": "守护图腾", "Eye of the Storm": "风暴之眼",
    "Healing Focus": "治疗专注",
    "Healing Grace": "治疗之赐", "Healing Stream Totem": "治疗之泉图腾",
    "Healing Wave": "治疗波", "Healing Way": "治疗之道", "Heroism": "英勇", "Hex": "妖术",
    "Improved Chain Heal": "强化治疗链", "Improved Earth Shield": "强化大地之盾",
    "Improved Fire Totems": "强化火焰图腾", "Improved Ghost Wolf": "强化幽魂之狼",
    "Improved Healing Wave": "强化治疗波", "Improved Lightning Shield": "强化闪电之盾",
    "Improved Reincarnation": "强化重生", "Improved Shields": "强化护盾",
    "Improved Stormstrike": "强化风暴打击", "Improved Weapon Totems": "强化武器图腾",
    "Lava Burst": "熔岩爆裂", "Lava Flows": "熔岩涌动", "Lava Lash": "熔岩猛击",
    "Lesser Healing Wave": "次级治疗波", "Lightning Bolt": "闪电箭",
    "Lightning Shield": "闪电之盾", "Maelstrom Ready!": "漩涡就绪！",
    "Maelstrom Weapon": "漩涡武器", "Magma Totem": "熔岩图腾", "Mana Spring Totem": "法力之泉图腾",
    "Mana Tide Totem": "法力之潮图腾", "Mental Dexterity": "精神敏锐",
    "Mental Quickness": "精神敏捷", "Molten Blast": "熔岩冲击", "Nature Resistance Totem": "自然抗性图腾",
    "Nature's Blessing": "自然赐福", "Nature's Guardian": "自然守护者",
    "Nature's Guidance": "自然指引", "Nature's Swiftness": "自然迅捷",
    "Poison Cleansing Totem": "清毒图腾", "Primal Wielding": "原始持武",
    "Purge": "净化术", "Purification": "净化", "Reincarnation": "重生",
    "Restorative Totems": "恢复图腾", "Reverberation": "回响", "Riptide": "激流",
    "Rockbiter Weapon": "石化武器", "Rolling Thunder": "滚滚雷霆", "Searing Totem": "灼热图腾",
    "Sentry Totem": "岗哨图腾", "Shamanism": "萨满教义", "Shamanistic Focus": "萨满专注",
    "Shamanistic Rage": "萨满之怒", "Shield Specialization": "盾牌专精",
    "Soothe Elemental": "安抚元素", "Spirit Weapons": "灵魂武器",
    "Static Shock": "静电震击", "Stoneclaw Totem": "石爪图腾", "Stoneskin Totem": "石肤图腾",
    "Storm Reach": "风暴来临", "Storm, Earth and Fire": "风暴、大地与火焰",
    "Stormstrike": "风暴打击", "Strength of Earth Totem": "大地之力图腾",
    "Thundering Strikes": "雷鸣猛击", "Thunderstorm": "雷霆风暴",
    "Tidal Focus": "潮汐集中", "Tidal Force": "潮汐之力", "Tidal Mastery": "潮汐掌握",
    "Tidal Waves": "潮汐奔涌", "Totem of Wrath": "愤怒图腾", "Totemic Call": "图腾召回",
    "Totemic Focus": "图腾集中", "Totemic Mastery": "图腾掌握", "Toughness": "坚韧",
    "Tranquil Air Totem": "宁静之风图腾", "Tremor Totem": "战栗图腾",
    "Unleashed Rage": "释放怒火", "Unrelenting Storm": "无尽风暴",
    "Water Breathing": "水下呼吸", "Water Shield": "水之护盾", "Water Walking": "水上行走",
    "Weapon Mastery": "武器掌握", "Weapon Specialization": "武器专精",
    "Wind Shear": "风剪", "Windfury Totem": "风怒图腾", "Windfury Weapon": "风怒武器",
    "Windwall Totem": "风墙图腾", "Wrath of Air Totem": "空气之怒图腾",
}

TERM_FIXES = [
    ("Shaman", "萨满"), ("shaman", "萨满"), ("Lightning Bolt", "闪电箭"), ("Chain Lightning", "闪电链"),
    ("Lightning Shield", "闪电之盾"), ("Molten Blast", "熔岩冲击"), ("Lava Burst", "熔岩爆裂"),
    ("Lava Lash", "熔岩猛击"), ("Shock", "震击"), ("Shocks", "震击"), ("Fire Totems", "火焰图腾"),
    ("Fire Totem", "火焰图腾"), ("Earth Totems", "大地图腾"), ("Earth Totem", "大地图腾"),
    ("Totems", "图腾"), ("totems", "图腾"), ("Totem", "图腾"), ("totem", "图腾"),
    ("Healing Wave", "治疗波"), ("Lesser Healing Wave", "次级治疗波"), ("Chain Heal", "治疗链"),
    ("Riptide", "激流"), ("Stormstrike", "风暴打击"), ("Earthbind Totem", "地缚图腾"),
    ("Stoneclaw Totem", "石爪图腾"), ("Magma Totem", "熔岩图腾"), ("Fire Nova Totem", "火焰新星图腾"),
    ("Windfury Totem", "风怒图腾"), ("Flametongue Totem", "火舌图腾"), ("Water Shield", "水之护盾"),
    ("Earth Shield", "大地之盾"), ("Frostbrand", "冰封"), ("Flametongue", "火舌"),
    ("Earthliving", "大地生命"), ("Fire", "火焰"), ("Frost", "冰霜"), ("Nature", "自然"),
    ("Physical", "物理"), ("Silence", "沉默"), ("Interrupt", "打断"), ("Fear", "恐惧"),
    ("Charm", "魅惑"), ("Sleep", "睡眠"), ("Stun", "昏迷"), ("Curse", "诅咒"),
    ("Disease", "疾病"), ("Poison", "中毒"), ("Magic", "魔法"), ("Elemental", "元素"),
    ("Humanoid", "人型生物"), ("Beast", "野兽"), ("Clearcasting", "节能施法"),
    ("Focused Casting", "专注施法"), ("Focused", "专注"), ("critical strike", "暴击"),
    ("critical", "暴击"), ("Critical", "暴击"), ("spell critical", "法术暴击"),
    ("spell damage", "法术伤害"), ("Spell damage", "法术伤害"), ("damage", "伤害"),
    ("Damage", "伤害"), ("healing", "治疗"), ("Healing", "治疗"), ("health", "生命值"),
    ("Health", "生命值"), ("mana", "法力值"), ("Mana", "法力值"), ("armor", "护甲"),
    ("Armor", "护甲"), ("agility", "敏捷"), ("strength", "力量"), ("Intellect", "智力"),
    ("Attack Power", "攻击强度"), ("attack power", "攻击强度"), ("movement speed", "移动速度"),
    ("melee attack power", "近战攻击强度"), ("threat", "威胁值"), ("cooldown", "冷却时间"),
    ("duration", "持续时间"), ("caster", "施法者"), ("party and raid", "小队和团队"),
    ("party or raid", "小队或团队"), ("party members", "小队成员"), ("party member", "小队成员"),
    ("nearby friendly targets", "附近友方目标"), ("friendly target", "友方目标"),
    ("nearby enemies", "附近敌人"), ("enemies", "敌人"), ("enemy", "敌人"),
    ("main-hand", "主手"), ("off-hand", "副手"), ("weapon", "武器"), ("Weapon", "武器"),
    ("proc", "触发"), ("range", "范围"), ("yards", "码"), ("yard", "码"), ("sec.", "秒"),
    ("seconds", "秒"), ("second", "秒"), ("爆击", "暴击"), ("连锁闪电", "闪电链"),
    ("链状闪电", "闪电链"), ("熔岩爆裂法术", "熔岩爆裂"), ("萨满祭司", "萨满"),
    ("召唤s", "召唤"), ("s a ", "一个"), ("$ghis:her;", "其"), ("$ghe:she;", "其"),
    ("$ghimself:herself;", "自己"),
]

DURATION_BY_NAME = {
    "Ancestral Fortitude": "15秒", "Ancestral Healing": "15秒", "Ancestral Spirit": "复活后",
    "Bloodlust": "40秒", "Chained Heal": "10秒", "Earth Elemental Totem": "2分钟",
    "Earth Shield": "10分钟", "Earth Shock": "2秒", "Earthbind Totem": "45秒",
    "Earthliving Weapon": "30分钟", "Elemental Devastation": "10秒", "Elemental Mastery": "15秒",
    "Feral Spirit": "45秒", "Fire Elemental Totem": "2分钟", "Fire Nova": "5秒",
    "Fire Nova Totem": "5秒", "Flame Shock": "18秒", "Flametongue Weapon": "30分钟",
    "Flurry": "15秒", "Frost Shock": "8秒", "Frostbrand Weapon": "30分钟", "Frozen Power": "5秒",
    "Gift of the Water Spirit": "10秒", "Ghost Wolf": "直到取消", "Grounding Totem": "45秒",
    "Healing Way": "15秒", "Heroism": "40秒", "Hex": "30秒", "Lava Flows": "6秒",
    "Lightning Shield": "10分钟", "Maelstrom Weapon": "30秒", "Magma Totem": "20秒",
    "Mana Tide Totem": "12秒", "Nature's Guardian": "5秒", "Reincarnation": "复活后",
    "Riptide": "15秒", "Rockbiter Weapon": "30分钟", "Searing Totem": "1分钟",
    "Sentry Totem": "5分钟", "Shamanistic Rage": "15秒", "Soothe Elemental": "15秒",
    "Stoneclaw Totem": "15秒", "Stormstrike": "12秒", "Tidal Force": "20秒",
    "Totem of Wrath": "5分钟", "Tremor Totem": "5分钟", "Water Breathing": "10分钟",
    "Water Shield": "10分钟", "Water Walking": "10分钟", "Wind Shear": "2秒",
    "Windfury Weapon": "30分钟",
}

ID_DURATION = {
    974: "10分钟", 39796: "3秒", 8034: "8秒", 29063: "6秒", 64695: "5秒",
    51945: "12秒", 84647: "4秒", 63685: "5秒", 16190: "12秒", 17364: "12秒",
    30706: "2分钟", 30823: "15秒",
}

TOTEM_DURATIONS = {
    "Disease Cleansing Totem": "2分钟", "Fire Resistance Totem": "2分钟",
    "Flametongue Totem": "2分钟", "Frost Resistance Totem": "2分钟",
    "Grace of Air Totem": "2分钟", "Healing Stream Totem": "2分钟",
    "Mana Spring Totem": "2分钟", "Nature Resistance Totem": "2分钟",
    "Poison Cleansing Totem": "2分钟", "Stoneskin Totem": "2分钟",
    "Strength of Earth Totem": "2分钟", "Tranquil Air Totem": "2分钟",
    "Windfury Totem": "2分钟", "Windwall Totem": "2分钟", "Wrath of Air Totem": "2分钟",
}

RADIUS_BY_NAME = {
    "Earthbind Totem": 10, "Fire Nova": 10, "Fire Nova Totem": 10, "Magma Totem": 8,
    "Searing Totem": 20, "Stoneclaw Totem": 8, "Thunderstorm": 10,
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
        return "" if end < 0 else strings[offset:end].decode("utf-8", errors="replace")

    def s(self, n: int) -> int:
        return signed(self.values[80 + n - 1]) + 1

    def maxv(self, n: int) -> int:
        return self.s(n) + signed(self.values[74 + n - 1])

    def h(self) -> int:
        return signed(self.values[35])

    def q(self, n: int) -> int:
        return signed(self.values[92 + n - 1]) or self.s(n)

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
    if rec.id in ID_DURATION:
        return ID_DURATION[rec.id]
    return DURATION_BY_NAME.get(rec.name) or TOTEM_DURATIONS.get(rec.name) or "持续时间"


def duration_seconds(rec: SpellRec, fallback: int = 1) -> int:
    text = duration(rec)
    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    value = int(match.group(1))
    return value * 60 if "分钟" in text else value


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 3
        ticks = max(1, duration_seconds(rec, seconds) // seconds)
    return rec.s(n) * ticks


def positive(value: int) -> int:
    return abs(value)


def scaled_ms(value: int) -> str:
    return f"{abs(value) / 1000:g}"


def first_ref_rec(text: str, records: dict[int, SpellRec], token: str = "s") -> SpellRec | None:
    match = re.search(r"\$(\d+)" + re.escape(token) + r"\d*", text or "", flags=re.I)
    if not match:
        return None
    return records.get(int(match.group(1)))


def unleashed_rage_ap(rec: SpellRec) -> int:
    text = f"{rec.desc} {rec.aura}"
    match = re.search(r"攻击强度(?:都会)?(?:增加|提高)\s*(\d+)\s*点?", text)
    if match:
        return int(match.group(1))
    return rec.s(1)


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
    text = re.sub(r"\?A\d+\[([^\]]*)\]\[([^\]]*)\]", lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"\$\{[^{}]*\}", "按属性计算的数值", text)
    text = re.sub(r"\$<chance>", "20", text)
    text = re.sub(r"\$[<A-Za-z0-9_/.*;:-]+|\$", "", text)
    text = re.sub(r"\s+([，。；：、])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    text = re.sub(r"(降低|缩短|减少|延长|提高)-(\d)", r"\1\2", text)
    text = re.sub(r"(伤害|恢复|拥有|以|为)-(\d)", r"\1\2", text)
    text = text.replace("内造成总计", "内造成")
    text = text.replace("持续持续时间", "持续时间")
    text = text.replace("。 。", "。")
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
    if token in ("a", "r"):
        return str(RADIUS_BY_NAME.get(target.name) or RADIUS_BY_NAME.get(rec.name) or target.s(index) or 30)
    if token == "q":
        return str(abs(target.q(index)))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 3)
    if token == "h":
        return str(target.h() if 0 < target.h() <= 100 else abs(target.s(index)))
    return ""


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    text = text.replace("$z", "炉石绑定地点")
    text = text.replace("$D", duration(rec)).replace("$d", duration(rec)).replace("$e", "1")
    text = text.replace("$<chance>", "20")
    text = re.sub(r"\$\{\$d-1\}", lambda _: str(max(1, duration_seconds(rec) - 1)), text)
    text = re.sub(r"\$\{\(\$AP/12\)\*\$COND\([^{}]+\)\}", "按攻击强度和武器速度计算的法力值", text)
    text = re.sub(r"\$\{\$m(\d+)/-1000\}", lambda m: scaled_ms(rec.s(int(m.group(1)))), text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/-1000\}", lambda m: scaled_ms(records.get(int(m.group(1)), rec).s(int(m.group(2)))), text)
    text = re.sub(r"\$\{\$i-1\}", lambda _: str(max(0, rec.stack() - 1) or 2), text)
    text = re.sub(r"\$\{\$x1-1\}", lambda _: str(max(0, rec.stack() - 1) or 2), text)
    text = re.sub(r"\$\*([0-9]+);([sm])(\d*)", lambda m: str(int(m.group(1)) * int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0)), text, flags=re.I)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: f"{int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1)):g}", text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: f"{int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1)):g}", text)
    text = re.sub(r"\$(\d+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: str(over_time(rec, int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)|\$r(\d*)", lambda _: str(RADIUS_BY_NAME.get(rec.name, 30)), text, flags=re.I)
    text = re.sub(r"\$q(\d*)", lambda m: str(abs(rec.q(int(m.group(1) or "1")))), text, flags=re.I)
    text = re.sub(r"\$u(\d*)|\$n(\d*)|\$i(\d*)|\$x(\d*)", lambda _: str(rec.stack() or 3), text, flags=re.I)
    text = text.replace("$h", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    text = text.replace("$H", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    return cleanup(text)


def ability_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name in ("Healing Wave", "Lesser Healing Wave"):
        return f"为友方目标恢复 {rec.s(1)} 点生命值。"
    if name == "Chain Heal":
        return f"为友方目标恢复 {rec.s(1)} 点生命值，然后跳跃治疗附近额外目标。若对小队成员施放，只会跳向其他小队成员。每次跳跃使治疗量降低 50%，总共治疗 {rec.stack() or 3} 个目标。"
    if name == "Riptide":
        return f"为友方目标恢复 {rec.s(1)} 点生命值，并在 {duration(rec)} 内额外恢复 {over_time(rec, 2)} 点生命值。你在 {duration(rec)} 内对该目标施放的下一个治疗链会消耗持续治疗效果，并使治疗链治疗量提高 {rec.s(3)}%。"
    if name == "Lightning Bolt":
        return f"向目标发射闪电箭，造成 {rec.s(1)} 点自然伤害。"
    if name == "Chain Lightning":
        return f"向敌人投掷闪电，造成 {rec.s(1)} 点自然伤害，然后跳向附近额外敌人。每次跳跃使伤害降低 30%，总共影响 {rec.stack() or 3} 个目标。"
    if name == "Molten Blast":
        return f"向目标投掷熔岩球，造成 {rec.s(1)} 点火焰伤害，并刷新目标身上你施加的烈焰震击。"
    if name == "Lava Burst":
        return f"向目标投掷熔岩，造成 {rec.s(1)} 点火焰伤害。如果目标受到你的烈焰震击影响，熔岩爆裂必定暴击。"
    if name == "Earth Shock":
        return f"立即以震荡力量冲击目标，造成 {rec.s(2)} 点自然伤害，并打断施法，使其在 {duration(rec)} 内无法施放同系法术。"
    if name == "Flame Shock":
        return f"立即以火焰灼烧目标，造成 {rec.s(1)} 点火焰伤害，并在 {duration(rec)} 内额外造成 {over_time(rec, 2)} 点火焰伤害。"
    if name == "Frost Shock":
        return f"立即以寒冰冲击目标，造成 {rec.s(2)} 点冰霜伤害，并使其移动速度降低 {positive(rec.s(1))}%，持续 {duration(rec)}。产生大量威胁值。"
    if name == "Lightning Shield":
        bolt = records.get(26364, rec)
        return f"施法者被 {rec.stack() or 3} 个闪电球环绕。法术、近战或远程攻击命中施法者时，攻击者受到 {bolt.s(1)} 点自然伤害，并消耗 1 个闪电球。闪电球每几秒最多触发一次，持续 {duration(rec)}。萨满同一时间只能激活一种元素护盾。"
    if name == "Water Shield":
        orb = records.get(52128, rec)
        restore = orb.s(1) if orb and orb.name else max(1, rec.s(1))
        return f"施法者被水之护盾环绕，每 5 秒恢复 {rec.s(2)} 点法力值。法术、近战或远程攻击命中施法者时，恢复 {restore} 点法力值，并消耗 1 层护盾。每几秒最多触发一次，持续 {duration(rec)}。萨满同一时间只能激活一种元素护盾。"
    if name == "Earth Shield":
        charges = rec.stack() or 6
        heal = rec.s(1) if rec.s(1) > 0 else records.get(974, rec).s(1)
        interrupt = rec.s(2) if 0 < rec.s(2) <= 100 else 30
        return f"以大地之盾保护目标，使其受到伤害时有 {interrupt}% 几率避免施法被打断，并使攻击治疗被护盾保护的目标 {heal} 点生命值。该效果每几秒最多触发一次，共有 {charges} 层，持续 {duration(rec)}。同一时间只能对一个目标施放大地之盾，且一个目标同一时间只能拥有一种元素护盾。"
    if name == "Ancestral Spirit":
        return f"使灵魂回归肉体，复活一名死亡目标，并使其拥有 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。无法在战斗中施放。"
    if name == "Reincarnation":
        return "允许你在死亡后复活，并拥有 20% 的生命值和法力值。"
    if name == "Purge":
        return f"净化敌方目标，移除 {rec.s(1)} 个有益魔法效果。"
    if name == "Cure Poison":
        return f"移除目标身上的 {rec.s(1)} 个中毒效果。"
    if name == "Cure Disease":
        return f"移除目标身上的 {rec.s(1)} 个疾病效果。"
    if name == "Cleanse Spirit":
        return "净化友方目标的灵魂，移除 1 个中毒效果、1 个疾病效果和 1 个诅咒效果。"
    if name == "Water Breathing":
        return f"使目标可以在水下呼吸，持续 {duration(rec)}。"
    if name == "Water Walking":
        return f"使友方目标可以在水面上行走，持续 {duration(rec)}。受到任何伤害或变形都会取消该效果。"
    if name == "Astral Recall":
        return "将施法者传送回炉石绑定地点。与其他地点的旅店老板交谈可以更改你的家。"
    if name == "Ghost Wolf":
        return f"使萨满变成幽魂之狼，移动速度提高 {rec.s(2)}%。只能在户外使用。"
    if name == "Far Sight":
        return "将施法者的视角移动到目标地点，持续 1分钟。只能在户外使用。"
    if name in ("Bloodlust", "Heroism"):
        exhausted = "饱足" if name == "Bloodlust" else "力竭"
        return f"使所有小队和团队成员的近战、远程攻击和施法速度提高 {rec.s(1)}%，持续 {duration(rec)}。\n\n获得该效果的盟友会获得{exhausted}效果，在 10 分钟内无法再次受益于嗜血或英勇。"
    if name == "Hex":
        return f"将敌人变成青蛙。妖术期间目标无法攻击或施法，受到伤害可能中断效果。持续 {duration(rec)}。同一时间只能妖术一个目标。只对人型生物和野兽有效。"
    if name == "Wind Shear":
        return f"立即以强风冲击目标，不造成伤害，但会打断施法，并使其在 {duration(rec)} 内无法施放同系法术。同时降低你的威胁值，使敌人较不愿攻击你。"
    if name == "Thunderstorm":
        return f"召唤一道闪电为你注入能量并伤害 {RADIUS_BY_NAME['Thunderstorm']} 码范围内附近敌人。为你恢复 {rec.s(2)}% 法力值，对附近所有敌人造成 {rec.s(1)} 点自然伤害，并将其击退 20 码。可在昏迷状态下使用。"
    if name == "Feral Spirit":
        return f"召唤两只受萨满指挥的幽灵狼，持续 {duration(rec)}。"
    if name == "Lava Lash":
        return f"用熔岩灌注你的副手武器，立即造成 {rec.s(1)}% 副手武器伤害。如果副手武器附有火舌效果，伤害提高 {rec.s(2)}%。"
    if name == "Stormstrike":
        return f"立即使用两把武器攻击敌人，并使你接下来 2 次自然伤害攻击对该目标造成的伤害提高 {rec.s(1)}%，持续 {duration(rec)}。"
    if name in ("Call of the Elements", "Call of the Ancestors", "Call of the Spirits"):
        extra = "可以召唤与其他图腾套组不同的图腾。" if name != "Call of the Elements" else ""
        return f"同时放置图腾栏中指定的最多 4 个图腾。{extra}可在移动中施放。"
    if name == "Totemic Call":
        return f"将你的图腾回收至大地，返还每个被图腾召回摧毁的图腾所需法力值的 {rec.s(1)}%。"
    return ""


def weapon_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name == "Rockbiter Weapon":
        return f"为萨满的武器灌注大地之力，使每秒伤害提高 {rec.s(2)} 点，并使使用该武器进行的近战攻击产生额外威胁值。持续 {duration(rec)}。"
    if name == "Flametongue Weapon":
        bonus = records.get(10400, rec).s(2)
        hit = records.get(8026, rec)
        return f"为萨满的武器灌注火焰，使总法术伤害提高 {bonus} 点。每次命中根据武器速度额外造成 {hit.s(1) / 77:g} 到 {hit.maxv(1) / 25:g} 点火焰伤害；速度较慢的武器每次攻击造成更多火焰伤害。持续 {duration(rec)}。"
    if name == "Frostbrand Weapon":
        hit = records.get(8034, rec)
        return f"为萨满的武器灌注冰霜。每次命中可触发额外效果，造成 {hit.s(2)} 点冰霜伤害，并使目标移动速度降低 {positive(hit.s(1))}%，持续 {duration(hit)}。持续 {duration(rec)}。"
    if name == "Windfury Weapon":
        ap = records.get(33757, rec).s(1)
        return f"为萨满的武器灌注风之力。每次命中有 36% 几率造成相当于两次额外攻击的额外伤害，并获得 {ap} 点额外攻击强度。持续 {duration(rec)}。"
    if name == "Earthliving Weapon":
        bonus = records.get(51940, rec).s(2)
        hot = records.get(51945, rec)
        return f"为萨满的武器灌注大地生命，使治疗效果提高 {bonus} 点。每次治疗有 20% 几率触发大地生命，在 {duration(hot)} 内额外恢复 {over_time(hot, 1)} 点生命值。持续 {duration(rec)}。"
    return ""


def totem_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name == "Searing Totem":
        bolt = records.get(3606, rec)
        return f"在你脚下召唤一个拥有 {rec.s(1)} 点生命值的灼热图腾，持续 {duration(rec)}，反复攻击 {RADIUS_BY_NAME['Searing Totem']} 码范围内的一个敌人，造成 {bolt.s(1)} 点火焰伤害。"
    if name == "Fire Nova Totem":
        nova = records.get(8349, rec)
        delay = records.get(8443, rec)
        return f"召唤一个拥有 {rec.s(1)} 点生命值的火焰新星图腾，持续 {duration(rec)}。若图腾在 {delay.amp_sec(1) or 5} 秒内没有被摧毁，则对 {RADIUS_BY_NAME['Fire Nova Totem']} 码范围内的敌人造成 {nova.s(1)} 点火焰伤害。"
    if name == "Fire Nova":
        nova = records.get(8349, rec)
        base = records.get(1535, rec)
        delay = records.get(8443, rec)
        return f"召唤一个拥有 {base.s(1)} 点生命值并持续 {duration(base)} 的火焰新星图腾。若图腾在 {delay.amp_sec(1) or 5} 秒内没有被摧毁，则对 {RADIUS_BY_NAME['Fire Nova']} 码范围内的敌人造成 {nova.s(1)} 点火焰伤害。"
    if name == "Magma Totem":
        pulse = records.get(8187, rec)
        tick = records.get(8188, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的熔岩图腾，持续 {duration(rec)}。它每 {tick.amp_sec(1) or 2} 秒对 {RADIUS_BY_NAME['Magma Totem']} 码范围内的生物造成 {pulse.s(1)} 点火焰伤害。"
    if name == "Stoneclaw Totem":
        taunt = records.get(5729, rec)
        stun = records.get(5728, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的石爪图腾，持续 {duration(rec)}。它会嘲讽 {RADIUS_BY_NAME['Stoneclaw Totem']} 码范围内的生物攻击自己。攻击石爪图腾的敌人有 {stun.h() if stun.h() <= 100 else 50}% 几率昏迷，持续 3秒。"
    if name == "Earthbind Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的地缚图腾，持续 {duration(rec)}，使 {RADIUS_BY_NAME['Earthbind Totem']} 码范围内敌人的移动速度降低。"
    if name == "Grounding Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的根基图腾。它会将施放在附近小队成员身上的一个有害法术吸引到自己身上并被摧毁。不会吸引范围伤害法术。持续 {duration(rec)}。"
    if name == "Tremor Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的战栗图腾，震动周围地面，驱散 30 码范围内小队成员身上的恐惧、魅惑和睡眠效果。持续 {duration(rec)}。"
    if name == "Poison Cleansing Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的清毒图腾，每 {records.get(8167, rec).amp_sec(1) or 5} 秒尝试移除 30 码范围内小队成员身上的 1 个中毒效果。持续 {duration(rec)}。"
    if name == "Disease Cleansing Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的祛病图腾，每 {records.get(8172, rec).amp_sec(1) or 5} 秒尝试移除 30 码范围内小队成员身上的 1 个疾病效果。持续 {duration(rec)}。"
    if name == "Healing Stream Totem":
        heal = records.get(5672, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的治疗之泉图腾，持续 {duration(rec)}。它每 {heal.amp_sec(1) or 2} 秒为 30 码范围内最多 5 名小队或团队成员恢复 {heal.s(1)} 点生命值。"
    if name == "Mana Spring Totem":
        mana = records.get(5677, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的法力之泉图腾，持续 {duration(rec)}。它每 {mana.amp_sec(1) or 2} 秒为 30 码范围内的小队成员恢复 {mana.s(1)} 点法力值。"
    if name == "Mana Tide Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的法力之潮图腾，持续 {duration(rec)}，周期性为附近小队成员恢复法力值。"
    if name == "Stoneskin Totem":
        effect = first_ref_rec(rec.desc, records) or records.get(8072, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的石肤图腾，使 30 码范围内小队成员受到的近战伤害降低 {positive(effect.s(1))} 点，持续 {duration(rec)}。"
    if name == "Strength of Earth Totem":
        effect = first_ref_rec(rec.desc, records) or records.get(8076, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的大地之力图腾，使 30 码范围内小队和团队成员的力量提高 {effect.s(1)} 点，持续 {duration(rec)}。"
    if name == "Grace of Air Totem":
        effect = first_ref_rec(rec.desc, records) or records.get(8836, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的风之优雅图腾，使 30 码范围内小队和团队成员的敏捷提高 {effect.s(1)} 点，持续 {duration(rec)}。"
    if name == "Windwall Totem":
        effect = first_ref_rec(rec.desc, records) or records.get(15108, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的风墙图腾，使 30 码范围内小队成员受到的远程伤害降低 {positive(effect.s(1))} 点，持续 {duration(rec)}。"
    if name in ("Fire Resistance Totem", "Frost Resistance Totem", "Nature Resistance Totem"):
        ids = {"Fire Resistance Totem": 8185, "Frost Resistance Totem": 8182, "Nature Resistance Totem": 10596}
        school = {"Fire Resistance Totem": "火焰", "Frost Resistance Totem": "冰霜", "Nature Resistance Totem": "自然"}[name]
        effect = first_ref_rec(rec.desc, records) or records.get(ids[name], rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的{school}抗性图腾，使 30 码范围内小队和团队成员的{school}抗性提高 {effect.s(1)} 点，持续 {duration(rec)}。"
    if name == "Flametongue Totem":
        effect = records.get(84633, records.get(8230, rec))
        hit = records.get(8253, rec)
        return f"召唤一个火舌图腾，为 {records.get(8230, rec).s(1) if records.get(8230, rec).s(1) > 5 else 30} 码范围内小队成员的主手武器附加火焰效果，使总法术伤害提高 {effect.s(2)} 点，每次命中根据武器速度额外造成 {hit.s(1) / 77:g} 到 {hit.maxv(1) / 25:g} 点火焰伤害。持续 {duration(rec)}。"
    if name == "Windfury Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的风怒图腾。图腾为附近小队和团队成员的主手武器灌注风之力，每次命中有 20% 几率获得额外攻击。持续 {duration(rec)}。"
    if name == "Wrath of Air Totem":
        effect = first_ref_rec(rec.desc, records) or records.get(2895, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的空气之怒图腾，使 30 码范围内小队和团队成员的法术伤害和治疗效果最多提高 {effect.s(1)} 点，持续 {duration(rec)}。"
    if name == "Totem of Wrath":
        effect = records.get(30708, rec)
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的愤怒图腾，使 20 码范围内所有小队和团队成员的法术命中和法术暴击几率提高 {effect.s(1)}%。持续 {duration(rec)}。\n\n学会该天赋还会使你的火元素图腾获得愤怒图腾的效果。"
    if name == "Tranquil Air Totem":
        return f"在施法者脚下召唤一个拥有 {rec.s(1)} 点生命值的宁静之风图腾，使附近小队成员产生的威胁值降低，持续 {duration(rec)}。"
    if name == "Sentry Totem":
        return f"在你脚下召唤一个拥有 {rec.s(1)} 点生命值的岗哨图腾，持续 {duration(rec)}。它允许你观察图腾周围区域，提高潜行侦测，并在受到攻击时发出警告。再次施放可在图腾视角和萨满视角之间切换。"
    if name == "Earth Elemental Totem":
        return f"召唤一个元素图腾，呼唤强大的土元素保护施法者和盟友，持续 {duration(rec)}。"
    if name == "Fire Elemental Totem":
        return f"召唤一个元素图腾，呼唤强大的火元素攻击施法者的敌人，持续 {duration(rec)}。"
    return ""


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    table = {
        "Concussion": f"使你的闪电箭、熔岩冲击、闪电链和震击法术造成的伤害提高 {rec.s(1)}%。",
        "Call of Flame": f"使你的火焰图腾造成的伤害提高 {rec.s(1)}%，并使熔岩冲击的暴击几率额外提高 {rec.s(2)}%。",
        "Convection": f"使你的震击、熔岩冲击、闪电箭和闪电链法术的法力值消耗降低 {positive(rec.s(1))}%。",
        "Reverberation": f"使你的震击法术冷却时间缩短 {scaled_ms(rec.s(1))} 秒。",
        "Call of Thunder": f"使你的闪电箭、闪电链和闪电之盾法术的暴击几率与暴击伤害额外提高 {rec.s(1)}%。",
        "Earth's Grasp": f"你的大地图腾使你施放萨满伤害法术时有 {rec.s(3)}% 几率避免因受到伤害而被打断。石爪图腾的生命值提高 {rec.s(1)}%，地缚图腾的影响半径扩大 {rec.s(2)}%。",
        "Improved Fire Totems": f"使你的火焰新星图腾激活延迟缩短 {scaled_ms(rec.s(1))} 秒，并使熔岩图腾产生的威胁值降低 {positive(rec.s(3))}%。",
        "Elemental Fury": f"使你的灼热图腾、熔岩图腾、火焰新星图腾以及火焰、冰霜和自然法术的暴击伤害加成提高 {rec.s(1)}%。",
        "Elemental Focus": f"当你的火焰、冰霜或自然伤害法术造成暴击后，你进入节能施法状态，使接下来 {records.get(16246, rec).stack() or 2} 个伤害法术的法力值消耗降低 {positive(records.get(16246, rec).s(1))}%。",
        "Elemental Mastery": f"激活后，你的下一个火焰、冰霜或自然伤害法术暴击几率提高 {rec.s(1)}%，并返还而不是消耗法力值。",
        "Totemic Focus": f"使你施放图腾的法力值消耗降低 {positive(rec.s(1))}%。",
        "Purification": f"使你的治疗法术效果提高 {rec.s(1)}%。",
        "Tidal Focus": f"使你的治疗法术法力值消耗降低 {positive(rec.s(1))}%。",
        "Healing Focus": f"使你施放萨满治疗法术时有 {rec.s(1)}% 几率避免因受到伤害而被打断。",
        "Improved Healing Wave": f"使你的治疗波施法时间缩短 {scaled_ms(rec.s(1))} 秒。",
        "Ancestral Healing": f"你的治疗法术造成暴击效果后，使目标护甲值提高 {records.get(16177, rec).s(1)}%，持续 {duration(records.get(16177, rec))}。",
        "Ancestral Fortitude": f"治疗法术暴击后，目标护甲值提高 {rec.s(1)}%，持续 {duration(rec)}。",
        "Restorative Totems": f"使你的法力之泉图腾效果提高 {rec.s(1)}%，治疗之泉图腾效果提高 {rec.s(2)}%。",
        "Tidal Mastery": f"使你的治疗和闪电法术的暴击几率提高 {rec.s(1)}%。",
        "Healing Way": f"你的治疗波有 {rec.s(1)}% 几率使后续治疗波对该目标的效果提高 {records.get(29203, rec).s(1)}%，持续 {duration(records.get(29203, rec))}。最多叠加 {records.get(29203, rec).stack() or 3} 层。",
        "Nature's Swiftness": "激活后，你的下一个施法时间少于 10 秒的自然法术变为瞬发。",
        "Nature's Guidance": f"使你的法术和近战攻击命中几率提高 {rec.s(1)}%。",
        "Totemic Mastery": f"使你影响友方目标的图腾半径提高 {rec.s(1)} 码。",
        "Mana Tide Totem": "在施法者脚下召唤一个法力之潮图腾，周期性为附近小队成员恢复法力值。",
        "Improved Reincarnation": f"使你的重生冷却时间缩短 {positive(rec.s(1)) // 60000:g} 分钟，并使重生后恢复的生命值和法力值提高 {rec.s(2)}%。",
        "Nature's Blessing": f"使你的法术伤害和治疗效果提高，数值相当于你智力的 {rec.s(1)}%。",
        "Improved Chain Heal": f"使你的治疗链治疗量提高 {rec.s(1)}%。",
        "Improved Earth Shield": f"使你的大地之盾层数增加 {rec.s(1)} 层，并使大地之盾治疗效果提高 {rec.s(2)}%。",
        "Tidal Waves": f"当你施放治疗链或激流时，有 {rec.s(1)}% 几率使治疗波施法时间缩短 {positive(records.get(53390, rec).s(1))}%，并使次级治疗波暴击几率提高 {records.get(53390, rec).s(2)}%，直到你施放 2 个此类法术。此外，治疗波额外获得相当于治疗加成 {rec.s(2)}% 的收益，次级治疗波额外获得相当于治疗加成 {rec.s(3)}% 的收益。",
        "Blessing of the Eternals": f"使你的法术暴击几率提高 {rec.s(1)}%，并在目标生命值不高于 35% 时，使你施加大地生命持续治疗效果的几率提高 {rec.s(2)}%。",
        "Ancestral Awakening": f"当你的治疗波、次级治疗波或激流造成暴击治疗时，召唤先祖之魂协助你，立即为 40 码内生命值百分比最低的友方小队或团队目标恢复相当于本次治疗量 {rec.s(1)}% 的生命值。",
        "Tidal Force": f"使你的治疗波、次级治疗波和治疗链暴击几率提高 {records.get(55198, rec).s(1)}%。每次暴击治疗会使该几率降低 20%。持续 {duration(rec)}。",
        "Shield Specialization": f"使你使用盾牌格挡攻击的几率提高 {rec.s(1)}%，格挡值提高 {rec.s(2)}%。",
        "Thundering Strikes": f"使你的武器攻击暴击几率提高 {rec.s(1)}%。",
        "Flurry": f"你造成近战暴击后，接下来 3 次攻击的攻击速度提高 {records.get(16257, rec).s(1)}%，持续 15秒。",
        "Toughness": f"使你从装备获得的护甲值提高 {rec.s(1)}%，并使移动限制的时长缩短 {positive(rec.s(2))}%。",
        "Anticipation": f"使你的躲闪几率额外提高 {rec.s(1)}%。",
        "Ancestral Knowledge": f"使你的智力总值提高 {rec.s(1)}%。",
        "Spirit Weapons": f"使你的近战攻击产生的威胁值降低 {positive(rec.s(1))}%，并允许招架正面近战攻击。",
        "Elemental Weapons": f"使你的石化武器提供的攻击强度加成提高 {rec.s(1)}%，风怒武器提供的攻击强度加成提高 {rec.s(2)}%，火舌武器和冰封武器造成的伤害提高 {rec.s(3)}%。",
        "Weapon Mastery": f"使你使用所有武器造成的伤害提高 {rec.s(1)}%。",
        "Weapon Specialization": f"使你使用所有武器的命中几率额外提高 {rec.s(1)}%。",
        "Mental Quickness": f"使你的瞬发萨满法术法力值消耗降低 {positive(rec.s(1))}%，并使你的法术伤害和治疗效果提高，数值相当于攻击强度的 {rec.s(2)}%。",
        "Mental Dexterity": f"使你的攻击强度提高，数值相当于智力的 {rec.s(1)}%。",
        "Shamanistic Rage": f"使你受到的所有伤害降低 {positive(rec.s(2))}%，并使你的成功近战攻击恢复按攻击强度和武器速度计算的法力值。持续 {duration(rec)}。",
        "Improved Stormstrike": f"当你使用风暴打击时，有 {rec.h() if rec.h() <= 100 else 50}% 几率立即获得相当于基础法力值 {records.get(63375, rec).s(1)}% 的法力值。",
        "Earthen Power": f"你的地缚图腾脉冲有 {rec.s(1)}% 几率同时移除你和附近友方目标身上的所有移动限制效果，并使你的大地震击额外降低敌人攻击速度 {positive(rec.s(2)) / 10:g}%。",
        "Static Shock": f"当你用近战攻击和技能造成伤害时，有 {rec.s(1)}% 几率消耗一层闪电之盾充能击中目标；你的闪电之盾额外获得 {rec.s(2)} 层充能。",
        "Maelstrom Weapon": f"当你使用近战武器造成伤害时，有几率使你下一个闪电箭、闪电链、次级治疗波、治疗波、治疗链或妖术的施法时间缩短 {positive(records.get(53817, rec).s(1))}%。最多叠加 5 次，持续 {duration(records.get(53817, rec))}。",
        "Improved Shields": f"使你的闪电之盾球体造成的伤害提高 {rec.s(1)}%，水之护盾球体恢复的法力值提高 {rec.s(2)}%，大地之盾球体治疗量提高 {rec.s(2)}%。",
        "Unleashed Rage": f"你的近战暴击会使 20 码范围内所有小队和团队成员的近战攻击强度提高 {unleashed_rage_ap(rec)} 点，持续 10秒。",
        "Enhancing Totems": f"使你的大地之力图腾和风之优雅图腾效果提高 {rec.s(1)}%。",
        "Improved Weapon Totems": f"使你的风怒图腾提供的近战攻击强度加成提高 {rec.s(1)}%，并使火舌图腾造成的伤害和提供的法术伤害提高 {rec.s(2)}%。",
        "Shamanistic Focus": f"你的近战攻击造成暴击后进入专注状态，使你的下一个震击法术法力值消耗降低 {positive(records.get(43339, rec).s(1))}%。",
        "Focused": f"你的近战攻击造成暴击后进入专注状态，使你的下一个震击法术法力值消耗降低 {positive(records.get(43339, rec).s(1))}%。",
        "Primal Wielding": f"允许在副手装备单手武器和副手武器。\n\n此外，你的闪电箭和熔岩冲击不再延迟下一次近战攻击，但若在近战攻击后的 {duration(records.get(84647, rec))} 内施放，造成的伤害降低 {positive(records.get(84647, rec).s(1))}%。",
        "Fire and Lightning Mastery": f"使你的熔岩冲击、闪电箭和闪电链施法时间缩短 {scaled_ms(rec.s(1))} 秒。",
        "Unrelenting Storm": f"即使在施法时，每 5 秒仍恢复相当于智力 {rec.s(1)}% 的法力值。",
        "Elemental Shields": f"使你被近战和远程攻击造成暴击的几率降低 {positive(rec.s(1))}%，并且受到直接伤害时有 {rec.h() if rec.h() <= 100 else 10}% 几率获得专注施法效果，持续 {duration(records.get(29063, rec))}。专注施法可防止你施放萨满法术时因受到伤害而损失施法时间。",
        "Elemental Precision": f"使你的法术命中几率提高 {rec.s(1)}%，火焰、冰霜和自然法术产生的威胁值降低 {positive(rec.s(2))}%。",
        "Elemental Overload": f"使你的熔岩冲击、闪电箭和闪电链有 {rec.s(1)}% 几率在同一目标上额外施放一个类似法术，不消耗额外资源，造成一半伤害且不产生威胁值。",
        "Elemental Oath": f"当元素集中触发的节能施法激活时，你造成的法术伤害提高 {rec.s(2)}%。此外，{rec.s(1) if rec.s(1) > 5 else 30} 码范围内的小队和团队成员获得 {rec.s(1)}% 法术暴击几率加成。",
        "Astral Shift": f"当你被昏迷、恐惧或沉默时，转入星界位面，在该效果持续期间受到的所有伤害降低 {rec.s(1)}%。",
        "Lava Flows": f"使你的熔岩爆裂暴击伤害加成额外提高 {rec.s(2)}%；当你的烈焰震击被驱散时，施法速度提高 {rec.s(1)}%，持续 {duration(records.get(64694, rec))}。",
        "Storm, Earth and Fire": f"使你的闪电链冷却时间缩短 0.75 秒；你的地缚图腾施放时有 {rec.s(2)}% 几率将目标定身，持续 {duration(records.get(64695, rec))}；烈焰震击的周期性伤害提高 {rec.s(3)}%。",
        "Shamanism": f"你的闪电箭和闪电链额外获得相当于法术伤害加成 {rec.s(1)}% 的收益，熔岩爆裂额外获得相当于法术伤害加成 {rec.s(2)}% 的收益。",
        "Booming Echoes": f"使你的烈焰震击和冰霜震击冷却时间额外缩短 {scaled_ms(rec.s(1))} 秒，并使它们造成的直接伤害提高 {rec.s(2)}%。",
        "Frozen Power": f"你的闪电箭、闪电链、熔岩猛击和震击法术对受到冰封武器效果影响的目标造成的伤害提高 {rec.s(1)}%；当你对距离 {records.get(63685, rec).s(1)} 码或更远的目标使用冰霜震击时，有 {rec.s(2)}% 几率将其冻结在原地，持续 {duration(records.get(63685, rec))}。",
        "Rolling Thunder": f"当你拥有激活的闪电之盾时，你的闪电箭和闪电链暴击有 {rec.h() if rec.h() <= 100 else 33}% 几率使闪电之盾增加 1 层，最多 9 层。达到 9 层后，任何增加层数的尝试都会改为向目标发射一个闪电球。\n\n当你拥有超过 3 层闪电之盾时，你的大地震击会在 2 秒后消耗最多 1 层额外闪电之盾，并将其射向目标。",
        "Focused Mind": f"使任何对萨满施加的沉默或打断效果时长缩短 {positive(rec.s(1))}%。该效果不与其他类似效果叠加。",
        "Healing Grace": f"使你的治疗法术产生的威胁值降低 {positive(rec.s(1))}%，并使你的法术被驱散的几率降低 {rec.s(2)}%。",
        "Improved Lightning Shield": f"使你的闪电之盾造成的伤害提高 {rec.s(1)}%。",
        "Guardian Totems": f"使你的石爪图腾吸收伤害效果提高 {rec.s(1)}%，根基图腾冷却时间缩短 {positive(rec.s(2)) // 1000:g} 秒。",
        "Improved Ghost Wolf": f"使你的幽魂之狼施法时间缩短 {scaled_ms(rec.s(1))} 秒。",
        "Storm Reach": f"使你的闪电箭和闪电链射程延长 {rec.s(1)} 码。",
        "Elemental Warding": f"使你受到的火焰、冰霜和自然伤害降低 {positive(rec.s(1))}%。",
        "Eye of the Storm": f"当你受到近战或远程暴击后，有 {rec.h() if rec.h() <= 100 else rec.s(1)}% 几率获得专注施法效果，持续 {duration(records.get(29063, rec))}。专注施法可防止你施放萨满法术时因受到伤害而损失施法时间。",
        "Nature's Guardian": f"当一次伤害性攻击使你的生命值降至 30% 以下时，有 {rec.h() if rec.h() <= 100 else 50}% 几率恢复总生命值的 {rec.s(1)}%，并降低你在该目标身上的威胁值。5 秒冷却。",
        "Soothe Elemental": f"安抚目标元素生物，使其攻击你的范围缩小 {rec.s(1)} 码。只影响 40 级或以下元素生物，持续 {duration(rec)}。",
        "Gift of the Water Spirit": f"在 {duration(rec)} 内恢复你总生命值和法力值的 {over_time(rec, 1)}%。",
        "Flame Shock Passive": "你的烈焰震击造成的伤害现在可以暴击。",
        "Chained Heal": f"在 {duration(rec)} 内恢复生命值，恢复量相当于最近一次暴击治疗链治疗量的 {records.get(70808, rec).s(1)}%。",
        "Freeze": f"你的闪电箭、闪电链、熔岩猛击和震击法术对受到冰封攻击效果影响的目标造成更高伤害。此外，当你对距离 {rec.s(1)} 码或更远的目标使用冰霜震击时，有几率将其冻结在原地，持续 {duration(rec)}。",
        "Maelstrom Ready!": "你的漩涡武器已达到最大层数，下一个可受影响的法术会变为瞬发。",
        "Glyph of Healing Wave": "治疗一个友方目标。",
    }
    return table.get(name, "")


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    for func in (ability_desc, weapon_desc, totem_desc):
        text = func(name, rec, records)
        if text:
            return text
    talent = talent_desc(name, rec, row, records)
    if talent:
        return talent
    source = row.get("description_zh") or row.get("description_en") or rec.desc
    resolved = resolve_tokens(source, rec, records)
    if CJK_RE.search(resolved) and not ASCII_WORD_RE.search(resolved) and "$" not in resolved and "按属性计算的数值" not in resolved:
        return resolved
    return f"{NAME_ZH.get(name, name)}效果。"


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    if talent_desc(row["name_en"], rec, row, records):
        return ""
    source = row.get("tooltip_zh") or row.get("tooltip_en") or rec.aura
    if not source:
        return ""
    tip = resolve_tokens(source, rec, records)
    if CJK_RE.search(tip) and not ASCII_WORD_RE.search(tip) and "$" not in tip and "按属性计算的数值" not in tip:
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


def is_shaman(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & SHAMAN_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_shaman(row):
            continue
        before = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        row["name_zh"] = NAME_ZH.get(row["name_en"], row.get("name_zh") or row["name_en"])
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
        if is_shaman(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or ASCII_WORD_RE.search(row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority shaman rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"shaman spell ids synced: {len(updates)}")
    print(f"shaman zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:30]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
