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

DRUID_SKILLS = {"134", "573", "574"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")

NAME_ZH = {
    "Abolish Poison": "驱毒术", "Abolish Poison Effect": "驱毒效果", "Aquatic Form": "水栖形态",
    "Aquatic Form (Passive)": "水栖形态（被动）", "Balance of Power": "能量平衡",
    "Barkskin": "树皮术", "Bash": "重击", "Bear Form": "熊形态",
    "Bear Form (Passive)": "熊形态（被动）", "Bear Form (Passive2)": "熊形态（被动2）",
    "Berserk": "狂暴", "Blood Frenzy": "血之狂热", "Brambles": "荆棘",
    "Brutal Impact": "野蛮冲撞", "Cat Form": "猎豹形态", "Cat Form (Passive)": "猎豹形态（被动）",
    "Celestial Focus": "星空专注", "Challenging Roar": "挑战咆哮", "Claw": "爪击",
    "Control of Nature": "自然控制", "Cower": "畏缩", "Cure Poison": "消毒术",
    "Cyclone": "旋风", "Dash": "急奔", "Demoralizing Roar": "挫志咆哮",
    "Dire Bear Form": "巨熊形态", "Dire Bear Form (Passive)": "巨熊形态（被动）",
    "Dreamstate": "梦境", "Earth and Moon": "大地与月亮", "Eclipse": "日月双蚀",
    "Empowered Rejuvenation": "强化回春术", "Empowered Touch": "强化治疗之触",
    "Enervate": "虚弱", "Enrage": "激怒", "Entangling Roots": "纠缠根须",
    "Faerie Fire": "精灵之火", "Faerie Fire (Feral)": "精灵之火（野性）",
    "Feline Grace": "豹之优雅", "Feral Aggression": "野性侵略", "Feral Attack": "野性攻击",
    "Feral Charge": "野性冲锋", "Feral Charge - Cat": "野性冲锋 - 猎豹",
    "Feral Instinct": "野性本能", "Feral Swiftness": "野性迅捷", "Ferocity": "凶暴",
    "Ferocious Bite": "凶猛撕咬", "Flight Form": "飞行形态", "Force of Nature": "自然之力",
    "Focused Starlight": "专注星光", "Frenzied Regeneration": "狂暴回复",
    "Furor": "激怒", "Gale Winds": "狂风", "Genesis": "起源", "Gift of Nature": "自然赐福",
    "Gift of the Earthmother": "大地之母的赐福", "Gift of the Wild": "野性赐福",
    "Glyph of Rejuvenation": "回春术雕文", "Growl": "低吼", "Healing Touch": "治疗之触",
    "Heart of the Wild": "野性之心", "Hibernate": "休眠", "Hurricane": "飓风",
    "Improved Barkskin": "强化树皮术", "Improved Barkskin (Passive)": "强化树皮术（被动）",
    "Improved Faerie Fire": "强化精灵之火", "Improved Insect Swarm": "强化虫群",
    "Improved Leader of the Pack": "强化兽群领袖", "Improved Mangle": "强化裂伤",
    "Improved Mark of the Wild": "强化野性印记", "Improved Moonfire": "强化月火术",
    "Improved Moonkin Form": "强化枭兽形态", "Improved Nature's Grasp": "强化自然之握",
    "Improved Regrowth": "强化愈合", "Improved Rejuvenation": "强化回春术",
    "Improved Tree of Life": "强化生命之树", "Improved Tranquility": "强化宁静",
    "Infected Wounds": "感染伤口", "Innervate": "激活", "Insect Swarm": "虫群",
    "Intensity": "强烈", "King of the Jungle": "丛林之王", "Lacerate": "割伤",
    "Leader of the Pack": "兽群领袖", "Lifebloom": "生命绽放", "Living Seed": "生命之种",
    "Living Spirit": "生命之魂", "Lunar Guidance": "月神指引", "Maim": "割碎",
    "Mangle": "裂伤", "Mangle (Bear)": "裂伤（熊）", "Mangle (Cat)": "裂伤（猎豹）",
    "Mark of the Wild": "野性印记", "Master Shapeshifter": "变形大师", "Maul": "重殴",
    "Moonfire": "月火术", "Moonfury": "月怒", "Moonglow": "月光", "Moonkin Aura": "枭兽光环",
    "Moonkin Form": "枭兽形态", "Moonkin Form (Passive)": "枭兽形态（被动）",
    "Natural Perfection": "自然完美", "Natural Reaction": "自然反应",
    "Natural Shapeshifter": "自然变形", "Naturalist": "自然主义者", "Nature's Focus": "自然集中",
    "Nature's Grace": "自然之赐", "Nature's Grasp": "自然之握", "Nature's Reach": "自然延伸",
    "Nature's Splendor": "自然的威严", "Nature's Swiftness": "自然迅捷",
    "Nourish": "滋养", "Nurturing Instinct": "治愈本能", "Omen of Clarity": "清晰预兆",
    "Overgrowth": "滋长", "Owlkin Frenzy": "枭兽狂怒", "Pounce": "突袭",
    "Pounce Bleed": "突袭流血", "Predatory Instincts": "掠食者本能",
    "Predatory Strikes": "猛兽攻击", "Primal Fury": "原始狂怒", "Primal Gore": "原始血腥",
    "Primal Precision": "原始精准", "Protector of the Pack": "兽群守护者", "Prowl": "潜行",
    "Rake": "扫击", "Ravage": "毁灭", "Rebirth": "复生", "Regrowth": "愈合",
    "Rejuvenation": "回春术", "Remove Curse": "解除诅咒", "Rend and Tear": "割碎",
    "Revitalize": "回春", "Revive": "复活", "Rip": "割裂", "Savage Defense": "野蛮防御",
    "Savage Fury": "野蛮暴怒", "Savage Roar": "野蛮咆哮", "Sharpened Claws": "锋利兽爪",
    "Shred": "撕碎", "Shredding Attacks": "撕碎攻击", "Soothe Animal": "安抚动物",
    "Southsea Cannon Fire": "南海火炮", "Spark of Nature": "自然火花", "Starfall": "星辰坠落",
    "Starfire": "星火术", "Starlight Wrath": "星光之怒", "Subtlety": "微妙",
    "Survival Instincts": "生存本能", "Survival of the Fittest": "适者生存",
    "Swift Flight Form": "迅捷飞行形态", "Swift Flight Form Passive": "迅捷飞行形态被动",
    "Swiftmend": "迅捷治愈", "Swipe": "横扫", "Swipe (Bear)": "横扫（熊）",
    "Swipe (Cat)": "横扫（猎豹）", "Teleport: Moonglade": "传送：月光林地",
    "Thick Hide": "厚皮", "Thorns": "荆棘术", "Tiger's Fury": "猛虎之怒",
    "Track Humanoids": "追踪人型生物", "Tranquil Spirit": "宁静之魂", "Tranquility": "宁静",
    "Travel Form": "旅行形态", "Tree of Life": "生命之树", "Typhoon": "台风",
    "Vengeance": "复仇", "Wild Growth": "野性成长", "Wrath": "愤怒",
    "Wrath of Cenarius": "塞纳留斯之怒", "Zenith": "天顶",
}

TERM_FIXES = [
    ("Druid", "德鲁伊"), ("druid", "德鲁伊"), ("Balance", "平衡"), ("Feral", "野性"),
    ("Restoration", "恢复"), ("Bear Form", "熊形态"), ("Dire Bear Form", "巨熊形态"),
    ("Cat Form", "猎豹形态"), ("Moonkin Form", "枭兽形态"), ("Tree of Life", "生命之树"),
    ("Travel Form", "旅行形态"), ("Aquatic Form", "水栖形态"), ("Flight Form", "飞行形态"),
    ("Wrath", "愤怒"), ("Starfire", "星火术"), ("Moonfire", "月火术"), ("Hurricane", "飓风"),
    ("Typhoon", "台风"), ("Zenith", "天顶"), ("Enervate", "虚弱"), ("Entangling Roots", "纠缠根须"),
    ("Cyclone", "旋风"), ("Faerie Fire", "精灵之火"), ("Insect Swarm", "虫群"),
    ("Thorns", "荆棘术"), ("Healing Touch", "治疗之触"), ("Regrowth", "愈合"),
    ("Rejuvenation", "回春术"), ("Lifebloom", "生命绽放"), ("Nourish", "滋养"),
    ("Wild Growth", "野性成长"), ("Tranquility", "宁静"), ("Mark of the Wild", "野性印记"),
    ("Gift of the Wild", "野性赐福"), ("Maul", "重殴"), ("Swipe", "横扫"), ("Claw", "爪击"),
    ("Rake", "扫击"), ("Rip", "割裂"), ("Shred", "撕碎"), ("Ravage", "毁灭"),
    ("Pounce", "突袭"), ("Mangle", "裂伤"), ("Lacerate", "割伤"), ("Ferocious Bite", "凶猛撕咬"),
    ("Tiger's Fury", "猛虎之怒"), ("Bash", "重击"), ("Prowl", "潜行"), ("Dash", "急奔"),
    ("attack power", "攻击强度"), ("Attack Power", "攻击强度"), ("spell power", "法术强度"),
    ("Spell Power", "法术强度"), ("damage", "伤害"), ("Damage", "伤害"), ("healing", "治疗"),
    ("Healing", "治疗"), ("health", "生命值"), ("Health", "生命值"), ("mana", "法力值"),
    ("Mana", "法力值"), ("Energy", "能量"), ("Rage", "怒气"), ("armor", "护甲"), ("Armor", "护甲"),
    ("Spirit", "精神"), ("Agility", "敏捷"), ("Stamina", "耐力"), ("Intellect", "智力"),
    ("Nature", "自然"), ("Arcane", "奥术"), ("Physical", "物理"), ("Fire", "火焰"),
    ("bleed", "流血"), ("Bleed", "流血"), ("critical strike", "暴击"), ("critical", "暴击"),
    ("Critical", "暴击"), ("haste", "急速"), ("threat", "威胁值"), ("cooldown", "冷却时间"),
    ("stun", "昏迷"), ("Stun", "昏迷"), ("Fear", "恐惧"), ("Curse", "诅咒"), ("Poison", "中毒"),
    ("Beast", "野兽"), ("Dragonkin", "龙类"), ("Humanoid", "人型生物"), ("Polymorph", "变形"),
    ("movement speed", "移动速度"), ("combo point", "连击点数"), ("combo points", "连击点数"),
    ("party and raid", "小队和团队"), ("party or raid", "小队或团队"), ("friendly target", "友方目标"),
    ("nearby enemies", "附近敌人"), ("enemies", "敌人"), ("enemy", "敌人"), ("caster", "施法者"),
    ("yards", "码"), ("yard", "码"), ("seconds", "秒"), ("sec.", "秒"), ("爆击", "暴击"),
    ("Banish", "旋风"),
]

DURATION_BY_NAME = {
    "Abolish Poison": "8秒", "Barkskin": "12秒", "Bash": "4秒", "Berserk": "15秒",
    "Challenging Roar": "6秒", "Cyclone": "6秒", "Dash": "15秒", "Demoralizing Roar": "30秒",
    "Enrage": "10秒", "Entangling Roots": "27秒", "Faerie Fire": "5分钟",
    "Faerie Fire (Feral)": "5分钟", "Feral Charge": "4秒", "Feral Charge - Cat": "3秒",
    "Flight Form": "直到取消", "Frenzied Regeneration": "10秒", "Hibernate": "40秒",
    "Hurricane": "10秒", "Innervate": "20秒", "Insect Swarm": "12秒", "Lacerate": "15秒",
    "Lifebloom": "7秒", "Mark of the Wild": "30分钟", "Gift of the Wild": "1小时",
    "Mangle": "12秒", "Mangle (Bear)": "12秒", "Mangle (Cat)": "12秒", "Moonfire": "12秒",
    "Nature's Grasp": "45秒", "Pounce": "3秒", "Pounce Bleed": "18秒", "Prowl": "直到取消",
    "Rake": "9秒", "Regrowth": "21秒", "Rejuvenation": "12秒", "Rip": "12秒",
    "Savage Roar": "34秒", "Soothe Animal": "15秒", "Starfall": "10秒", "Survival Instincts": "20秒",
    "Thorns": "10分钟", "Tiger's Fury": "6秒", "Tranquility": "8秒", "Tree of Life": "直到取消",
    "Typhoon": "6秒", "Wild Growth": "7秒",
    "虫群": "12秒", "精灵之火": "5分钟", "精灵之火（野性）": "5分钟",
    "自然之力": "30秒", "裂伤": "12秒",
}

ID_DURATION = {
    16922: "3秒", 16886: "15秒", 19675: "4秒", 24932: "直到取消", 33891: "15秒",
    45281: "8秒", 48391: "10秒", 48504: "15秒", 48517: "15秒", 48518: "15秒",
    50259: "3秒", 58179: "12秒", 60431: "12秒", 61391: "6秒",
}

RADIUS_BY_NAME = {
    "Tranquility": 40, "Hurricane": 10, "Starfall": 30, "Wild Growth": 15, "Typhoon": 20,
    "Challenging Roar": 10, "Demoralizing Roar": 10, "Swipe": 8, "Swipe (Bear)": 8,
    "Swipe (Cat)": 8, "Overgrowth": 25,
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
    return DURATION_BY_NAME.get(rec.name, "持续时间")


def duration_seconds(rec: SpellRec, fallback: int = 1) -> int:
    text = duration(rec)
    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    value = int(match.group(1))
    return value * 60 if "分钟" in text or "小时" in text else value


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 3
        ticks = max(1, duration_seconds(rec, seconds) // seconds)
    return rec.s(n) * ticks


def positive(value: int) -> int:
    return abs(value)


def ms(value: int) -> str:
    return f"{abs(value) / 1000:g}"


def read_number_from_text(text: str, pattern: str, default: int) -> int:
    match = re.search(pattern, text or "")
    return int(match.group(1)) if match else default


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
    if token in ("t", "a"):
        if token == "t":
            return str(target.amp_sec(index) or 1)
        return str(RADIUS_BY_NAME.get(target.name) or target.s(index) or 30)
    if token == "q":
        return str(abs(target.q(index)))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 1)
    if token == "h":
        return str(target.h() if 0 < target.h() <= 100 else abs(target.s(index)))
    return ""


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
    text = re.sub(r"\$[<A-Za-z0-9_/.*;:-]+|\$", "", text)
    text = re.sub(r"\s+([，。；：、])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    text = re.sub(r"(降低|缩短|减少|延长|提高)-(\d)", r"\1\2", text)
    text = re.sub(r"(伤害|恢复|拥有|以|为)-(\d)", r"\1\2", text)
    text = text.replace("持续持续时间", "持续时间").replace("按属性计算的数值点", "按属性计算的数值")
    return text.strip()


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    text = text.replace("$D", duration(rec)).replace("$d", duration(rec)).replace("$e", "1")
    text = re.sub(r"\$\{\$m(\d+)/-?1000\}", lambda m: ms(rec.s(int(m.group(1)))), text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/-?1000\}", lambda m: ms(records.get(int(m.group(1)), rec).s(int(m.group(2)))), text)
    text = re.sub(r"\$\{\$m(\d+)/(\d+)\}", lambda m: f"{rec.s(int(m.group(1))) / int(m.group(2)):g}", text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/(\d+)\}", lambda m: f"{records.get(int(m.group(1)), rec).s(int(m.group(2))) / int(m.group(3)):g}", text)
    text = re.sub(r"\$\{\$h\*0\.6\}", lambda _: f"{(rec.h() if rec.h() <= 100 else rec.s(1)) * 0.6:g}", text)
    text = re.sub(r"\$\{\$AP\*0\.012\+\$m1\}", f"{rec.s(1)}点加攻击强度1.2%", text)
    text = re.sub(r"\$\{\$m2\*4\+\$AP\*0\.096\}", f"{rec.s(2) * 4}点加攻击强度9.6%", text)
    text = re.sub(r"\$\{\$m1\*\$m3/100\}", f"{int(rec.s(1) * rec.s(3) / 100)}", text)
    text = re.sub(r"\$\*([0-9]+);([sm])(\d*)", lambda m: str(int(m.group(1)) * int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0)), text, flags=re.I)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: f"{int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1)):g}", text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: f"{int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1)):g}", text)
    text = re.sub(r"\$(\d+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: str(over_time(rec, int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)", lambda _: str(RADIUS_BY_NAME.get(rec.name, 30)), text, flags=re.I)
    text = re.sub(r"\$q(\d*)", lambda m: str(abs(rec.q(int(m.group(1) or "1")))), text, flags=re.I)
    text = re.sub(r"\$u(\d*)|\$n(\d*)|\$i(\d*)|\$x(\d*)", lambda _: str(rec.stack() or 1), text, flags=re.I)
    text = text.replace("$h1", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    text = text.replace("$h", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    text = text.replace("$H", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    return cleanup(text)


def form_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name == "Aquatic Form":
        swim = records.get(5421, rec).s(1)
        return f"变身为水栖形态，使游泳速度提高 {swim}%，并允许德鲁伊在水下呼吸。同时保护施法者免疫变形效果。\n\n变形会使施法者解除变形和移动限制效果。"
    if name == "Aquatic Form (Passive)":
        return f"游泳速度提高 {rec.s(1)}%，并允许德鲁伊在水下呼吸。"
    if name == "Bear Form":
        p = records.get(1178, rec)
        return f"进入熊形态，近战攻击强度提高 {p.s(3)} 点，从物品获得的护甲提高 {p.s(1)}%，耐力提高 {p.s(2)}%。同时保护施法者免疫变形效果，并允许使用熊形态技能。\n\n变形会解除变形和移动限制效果。"
    if name == "Dire Bear Form":
        p = records.get(9635, rec)
        return f"进入巨熊形态，近战攻击强度提高 {p.s(3)} 点，从物品获得的护甲提高 {p.s(1)}%，耐力提高 {p.s(2)}%。同时保护施法者免疫变形效果，并允许使用熊形态技能。\n\n变形会解除变形和移动限制效果。"
    if name in ("Cat Form", "Cat Form (Passive)"):
        return "进入猎豹形态，提高攻击速度，并允许使用猎豹形态技能。变形会解除变形和移动限制效果。"
    if name == "Travel Form":
        return "变身为旅行形态，提高移动速度。只能在户外使用。变形会解除变形和移动限制效果。"
    if name == "Flight Form":
        speed = records.get(33948, rec).s(2)
        return f"变身为飞行形态，移动速度提高 {speed}%，并允许飞行。无法在战斗中使用，只能在外域使用。\n\n变形会解除变形和移动限制效果。"
    if name == "Swift Flight Form":
        speed = records.get(40121, rec).s(2)
        return f"变身为迅捷飞行形态，移动速度提高 {speed}%，并允许飞行。无法在战斗中使用，只能在外域使用。\n\n变形会解除变形和移动限制效果。"
    if name in ("Bear Form (Passive)", "Bear Form (Passive2)", "Dire Bear Form (Passive)", "Swift Flight Form Passive"):
        return f"{NAME_ZH.get(name, name)}。"
    if name == "Moonkin Form":
        p = records.get(24905, rec)
        aura = records.get(24907, rec)
        return f"进入枭兽形态，免疫变形效果，从物品获得的护甲提高 {p.s(1)}%，攻击强度提高相当于等级 150% 的数值，法术暴击几率提高 {aura.s(3)}%。多数近战攻击命中时有几率按攻击强度恢复法力值。\n\n变形会解除变形和移动限制效果。"
    if name == "Moonkin Form (Passive)":
        return "免疫变形效果，并获得枭兽形态的护甲、攻击强度、法术暴击和近战回蓝效果。"
    if name == "Moonkin Aura":
        return f"使法术暴击几率提高 {rec.s(1)}%。"
    if name == "Tree of Life":
        return "变身为生命之树。该形态下你的治疗能力提高，并使附近小队和团队成员受到你的治疗效果增强。"
    return ""


def ability_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    text = form_desc(name, rec, records)
    if text:
        return text
    if name == "Wrath":
        return f"对目标造成 {rec.s(1)} 点自然伤害。"
    if name == "Starfire":
        return f"对目标造成 {rec.s(1)} 点奥术伤害。"
    if name == "Moonfire":
        return f"灼烧敌人，造成 {rec.s(2)} 点奥术伤害，并在 {duration(rec)} 内额外造成 {over_time(rec, 1)} 点奥术伤害。"
    if name == "Insect Swarm":
        return f"虫群包围敌方目标，使其命中几率降低 {positive(rec.s(2))}%，并在 {duration(rec)} 内造成 {over_time(rec, 1)} 点自然伤害。"
    if name == "Entangling Roots":
        return f"将目标缠绕在原地，并在 {duration(rec)} 内造成 {over_time(rec, 2)} 点自然伤害。受到伤害可能中断效果。只能在户外使用。"
    if name == "Hurricane":
        pulse = records.get(42231, records.get(42230, rec))
        return f"在目标区域制造猛烈风暴，每 {rec.amp_sec(3) or 1} 秒对敌人造成 {pulse.s(1)} 点自然伤害，并使敌人的攻击间隔延长 {positive(rec.s(2))}%。持续 {duration(rec)}。德鲁伊必须引导以维持法术。"
    if name == "Starfall":
        star = records.get(50288, rec)
        splash = records.get(50294, rec)
        return f"从天空召唤流星攻击施法者周围 {RADIUS_BY_NAME['Starfall']} 码内的所有目标，每颗流星造成 {star.s(1)} 点奥术伤害，并对目标周围 {splash.s(1) if splash.s(1) > 5 else 5} 码内其他敌人造成 {splash.s(1)} 点奥术伤害。最多召唤 20 颗流星，持续 {duration(rec)}。动物形态、坐骑或失去角色控制会压制该效果。"
    if name == "Typhoon":
        return f"召唤猛烈台风，接触敌方目标时造成 {rec.s(2)} 点自然伤害，将其击退并眩晕，持续 {duration(records.get(61391, rec))}。"
    if name == "Zenith":
        splash = records.get(150099, rec)
        return f"对目标造成 {rec.s(1)} 点奥术伤害，并对目标周围 {splash.s(1) if splash.s(1) > 5 else 10} 码内最多 {splash.stack() or splash.s(1) or 3} 个敌人造成 {splash.s(1)} 点伤害。只能在施放 3 次星火术后使用。"
    if name == "Enervate":
        return f"对目标造成 {rec.s(1)} 点伤害，并使其基于精神的法力恢复降低 {positive(rec.s(2))}%。只能在施放 3 次愤怒后使用。"
    if name == "Healing Touch":
        return f"为友方目标恢复 {rec.s(1)} 点生命值。"
    if name == "Rejuvenation":
        return f"在 {duration(rec)} 内为目标恢复 {over_time(rec, 1)} 点生命值。"
    if name == "Regrowth":
        return f"为友方目标恢复 {rec.s(1)} 点生命值，并在 {duration(rec)} 内额外恢复 {over_time(rec, 2)} 点生命值。"
    if name == "Lifebloom":
        return f"在 {duration(rec)} 内为目标恢复 {over_time(rec, 1)} 点生命值。生命绽放结束或被驱散时，目标立即恢复 {rec.s(2)} 点生命值。该效果在同一目标身上最多叠加 {rec.stack() or 3} 次。"
    if name == "Nourish":
        return f"为友方目标恢复 {rec.s(1)} 点生命值。如果目标身上已有你的回春术、愈合、生命绽放或野性成长效果，则治疗效果额外提高 20%。"
    if name == "Wild Growth":
        return f"在 {duration(rec)} 内为目标 {RADIUS_BY_NAME['Wild Growth']} 码范围内最多 {rec.s(3)} 名友方小队或团队成员恢复 {over_time(rec, 1)} 点生命值。治疗量开始较高，随后逐渐降低。"
    if name == "Tranquility":
        return f"每 {rec.amp_sec(2) or 2} 秒为小队或团队中最多 5 名受伤盟友恢复 {rec.s(1)} 点生命值，持续 {duration(rec)}。德鲁伊必须引导以维持法术。"
    if name == "Swiftmend":
        return "消耗目标身上的回春术或愈合效果，立即恢复相当于该持续治疗效果剩余治疗量的生命值。"
    if name == "Mark of the Wild":
        parts = [f"护甲提高 {rec.s(1)} 点"]
        if rec.s(2) > 1:
            parts.append(f"所有属性提高 {rec.s(2)} 点")
        if rec.s(3) > 1:
            parts.append(f"所有抗性提高 {rec.s(3)} 点")
        return f"使友方目标的{'，'.join(parts)}，持续 {duration(rec)}。"
    if name == "Gift of the Wild":
        return f"为小队或团队成员施加强效野性印记，使护甲提高 {rec.s(1)} 点，所有属性提高 {rec.s(2)} 点，所有抗性提高 {rec.s(3)} 点，持续 {duration(rec)}。"
    if name == "Thorns":
        return f"使友方目标长出荆棘，被击中时对攻击者造成 {rec.s(1)} 点自然伤害，持续 {duration(rec)}。"
    if name == "Remove Curse":
        return f"移除友方目标身上的 {rec.s(1)} 个诅咒效果。"
    if name in ("Cure Poison", "Abolish Poison"):
        if name == "Cure Poison":
            return f"移除目标身上的 {rec.s(1)} 个中毒效果。"
        return f"尝试移除目标身上的 {rec.s(2)} 个中毒效果，并在接下来的 {duration(rec)} 内每 {rec.amp_sec(1) or 2} 秒额外尝试移除 {records.get(3137, rec).s(1)} 个中毒效果。"
    if name == "Abolish Poison Effect":
        return f"每 {rec.amp_sec(1) or 2} 秒尝试移除 {rec.s(1)} 个中毒效果。"
    if name == "Rebirth":
        return f"使死去的玩家复活，并使其拥有 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。可在战斗中使用。"
    if name == "Revive":
        return f"使灵魂回归身体，复活死亡目标，并使其拥有 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。无法在战斗中施放。"
    if name == "Innervate":
        return f"使目标基于精神的法力恢复提高 {rec.s(2)}%，并在施法时保持完整法力恢复，持续 {duration(rec)}。"
    if name == "Barkskin":
        return f"受到的所有伤害降低 {positive(rec.s(2))}%。在保护期间，受到伤害不会导致施法延迟。持续 {duration(rec)}。"
    if name == "Cyclone":
        return f"将敌方目标抛到空中，使其无法行动但免疫伤害，最多持续 {duration(rec)}。同一时间只能有一个目标受到你的旋风影响。"
    if name == "Hibernate":
        return f"使敌方目标沉睡，最多持续 {duration(rec)}。任何伤害都会唤醒目标。同一时间只能休眠一个目标。只对野兽和龙类有效。"
    if name == "Soothe Animal":
        return f"安抚目标野兽，使其攻击你的范围缩小 {rec.s(1)} 码。只影响 40 级或以下野兽，持续 {duration(rec)}。"
    if name == "Faerie Fire" or name == "Faerie Fire (Feral)":
        return f"使目标护甲降低 {positive(rec.s(1))} 点，持续 {duration(rec)}。效果期间目标无法潜行或隐形。"
    if name == "Track Humanoids":
        return "在小地图上显示附近所有人型生物的位置。同一时间只能激活一种追踪。"
    if name == "Teleport: Moonglade":
        return "将施法者传送到月光林地。"
    if name == "Southsea Cannon Fire":
        return f"对敌人造成 {rec.s(1)} 点火焰伤害。"
    if name == "Growl":
        return "嘲讽目标攻击你；如果目标已经在攻击你，则没有效果。"
    if name == "Challenging Roar":
        return f"强迫附近所有敌人攻击你，持续 {duration(rec)}。"
    if name == "Demoralizing Roar":
        return f"德鲁伊发出咆哮，使附近敌人的近战攻击强度降低 {positive(rec.s(1))} 点，持续 {duration(rec)}。"
    if name == "Bash":
        return f"使目标昏迷 {duration(rec)}。"
    if name == "Dash":
        return f"使移动速度提高 {rec.s(1)}%，持续 {duration(rec)}。不会打破潜行。"
    if name == "Prowl":
        return f"允许德鲁伊潜行，但移动速度降低 {positive(rec.s(2))}%。持续直到取消。"
    if name == "Enrage":
        return f"在 {duration(rec)} 内产生 20 点怒气，但使熊形态下的基础护甲降低 27%，巨熊形态下的基础护甲降低 16%。"
    if name == "Frenzied Regeneration":
        return f"每秒将最多 {rec.s(2)} 点怒气转化为生命值，持续 {duration(rec)}。每点怒气恢复总生命值的 {rec.s(1)}%。"
    if name == "Survival Instincts":
        return f"激活后，临时获得相当于当前最大生命值 {rec.s(1)}% 的生命值，持续 {duration(rec)}。只能在熊形态、猎豹形态或巨熊形态下使用。效果结束后，增加的生命值会消失。"
    if name == "Berserk":
        return f"激活后，使裂伤（熊）可命中最多 {records.get(58923, rec).s(1)} 个目标且没有冷却时间，并使所有猎豹形态技能的能量消耗降低 {positive(rec.s(1))}%，持续 {duration(rec)}。期间无法使用猛虎之怒。\n\n移除所有恐惧效果，并在效果期间免疫恐惧。"
    if name == "Maul":
        return f"使德鲁伊的下一次攻击额外造成 {rec.s(1)} 点伤害。"
    if name in ("Swipe", "Swipe (Bear)"):
        return f"横扫附近敌人，造成 {rec.s(1)} 点伤害。伤害受攻击强度加成。"
    if name == "Swipe (Cat)":
        return f"横扫附近敌人，造成 {rec.s(1)}% 武器伤害。"
    if name == "Claw":
        return f"抓击敌人，额外造成 {rec.s(1)} 点伤害，奖励 {rec.s(2)} 个连击点数。"
    if name == "Rake":
        return f"扫击目标，造成 {rec.s(1)} 点加攻击强度 1.2% 的流血伤害，并在 {duration(rec)} 内额外造成 {rec.s(2) * 4} 点加攻击强度 9.6% 的伤害。奖励 {rec.s(3)} 个连击点数。"
    if name == "Rip":
        return "终结技，造成持续流血伤害。伤害随连击点数和攻击强度提高：1 点造成 42 点伤害，2 点造成 66 点伤害，3 点造成 90 点伤害，4 点造成 114 点伤害，5 点造成 138 点伤害，持续 12秒。"
    if name == "Shred":
        return f"撕碎目标，造成 {rec.s(3)}% 武器伤害外加 {read_number_from_text(rec.desc, r'plus (\\d+)', rec.s(1))} 点伤害。必须位于目标背后。奖励 {rec.s(2)} 个连击点数。"
    if name == "Ravage":
        return f"毁灭目标，造成 {rec.s(2)}% 武器伤害外加 {read_number_from_text(rec.desc, r'plus (\\d+)', rec.s(1))} 点伤害。必须在潜行状态并位于目标背后。奖励 {rec.s(3)} 个连击点数。"
    if name == "Pounce":
        bleed = records.get(9007, rec)
        return f"突袭目标，使其昏迷 {duration(rec)}，并在 {duration(bleed)} 内造成 {over_time(bleed, 1)} 点伤害。必须在潜行状态下使用。奖励 {rec.s(3)} 个连击点数。"
    if name == "Pounce Bleed":
        return f"突袭造成的流血效果，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点伤害。"
    if name == "Ferocious Bite":
        return "终结技，按连击点数造成伤害，并可额外消耗最多 30 点能量转化为额外伤害。"
    if name == "Cower":
        return "畏缩，不造成伤害，但会少量降低你的威胁值，使敌人较不愿攻击你。"
    if name in ("Mangle", "Mangle (Bear)", "Mangle (Cat)"):
        if name == "Mangle":
            return "裂伤目标，造成伤害，并使目标受到的流血效果伤害提高，持续 12秒。此技能可在猎豹形态或巨熊形态下使用。"
        combo = f"奖励 {records.get(34071, rec).s(1)} 个连击点数。" if name == "Mangle (Cat)" else ""
        return f"裂伤目标，造成 {rec.s(3)}% 普通伤害外加 {int(rec.s(1) * rec.s(3) / 100)} 点伤害，并使目标在 {duration(rec)} 内受到的撕碎和流血效果伤害提高 {rec.s(2)}%。{combo}"
    if name == "Lacerate":
        return f"割伤敌方目标，造成 {rec.s(2)} 点流血伤害，并在 {duration(rec)} 内额外造成 {over_time(rec, 1)} 点流血伤害，产生大量威胁值。伤害受攻击强度加成，最多叠加 {rec.stack() or 5} 次。"
    if name == "Feral Charge":
        return f"冲向敌人，使其无法移动并打断正在施放的法术，持续 {duration(records.get(19675, rec))}。"
    if name == "Feral Charge - Cat":
        return f"跳到敌人身后，使其眩晕，持续 {duration(records.get(50259, rec))}。"
    if name == "Tiger's Fury":
        bonus = records.get(84736 + max(0, rank_num({"rank_en": rec.rank}) - 1), rec).s(1) if rec.id < 80000 else rec.s(1)
        return f"使造成的物理伤害提高 {bonus} 点，持续 {duration(rec)}。流血伤害会使该效果额外提高 {rec.s(1)} 点，最多叠加 10 次。"
    if name == "Savage Roar":
        return f"终结技，使造成的物理伤害提高 {rec.s(2)}%。只能在猎豹形态下使用。时长随连击点数提高：1 点 14 秒，2 点 19 秒，3 点 24 秒，4 点 29 秒，5 点 34 秒。"
    if name == "Savage Defense":
        return f"在熊形态或巨熊形态下每次造成暴击，都会获得野蛮防御，使下一次命中你的物理攻击伤害降低，数值相当于攻击强度的 {rec.s(1)}%。"
    if name == "Force of Nature":
        return f"召唤 {rec.s(1)} 个树人攻击敌方目标，持续 {duration(rec)}。"
    if name == "Overgrowth":
        return "为友方目标及其 25 码内的小队成员施加回春术（等级 3）。"
    if name == "Glyph of Rejuvenation":
        return "为友方目标恢复生命值，数值相当于回春术的 50%。"
    if name == "Feral Attack":
        return "所有可装备武器都会根据武器每秒伤害获得额外野性攻击强度。只有德鲁伊可以看到此属性。"
    return ""


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    table = {
        "Starlight Wrath": f"使你的愤怒和星火术施法时间缩短 {ms(rec.s(1))} 秒。",
        "Nature's Reach": f"使你的平衡系法术和精灵之火（野性）技能射程提高 {rec.s(1)}%。",
        "Improved Moonfire": f"使你的月火术伤害和暴击几率提高 {rec.s(1)}%。",
        "Natural Shapeshifter": f"使所有变形的法力值消耗降低 {positive(rec.s(1))}%。",
        "Brambles": f"使你的荆棘术和纠缠根须造成的伤害提高 {rec.s(1)}%。",
        "Moonglow": f"使你的月火术、星火术、愤怒、飓风、虚弱、治疗之触、愈合和回春术的法力值消耗降低 {positive(rec.s(1))}%。",
        "Celestial Focus": f"使你的星火术有 {rec.h() if rec.h() <= 100 else 5}% 几率使目标昏迷 {duration(records.get(16922, rec))}，并使你施放愤怒、虚弱、星火术或天顶时抵抗施法打断的几率提高 {rec.s(2)}%。",
        "Feral Aggression": f"使你的挫志咆哮降低攻击强度的效果提高 {rec.s(1)}%，凶猛撕咬造成的伤害提高 {rec.s(2)}%。",
        "Omen of Clarity": f"你的近战攻击有几率使你进入节能施法状态，使下一个伤害或治疗法术、或攻击性技能的法力值、怒气或能量消耗降低 {positive(records.get(16870, rec).s(1))}%。",
        "Nature's Grace": f"你的所有法术暴击都会获得自然恩赐，使下一个法术的施法时间缩短 {ms(records.get(16886, rec).s(1))} 秒。",
        "Moonfury": f"使你的星火术、月火术、天顶、愤怒和虚弱造成的伤害提高 {rec.s(1)}%。",
        "Vengeance": f"使你的平衡系法术暴击伤害加成提高 {rec.s(1)}%。",
        "Control of Nature": f"使你施放纠缠根须和旋风时有 {rec.s(1)}% 几率避免因受到伤害而被打断。",
        "Thick Hide": f"使你从物品获得的护甲提高 {rec.s(1)}%。",
        "Ferocity": f"使你的重殴、横扫、爪击、扫击和裂伤技能消耗降低 {positive(rec.s(1)) / 10:g} 点怒气或能量。",
        "Brutal Impact": f"使你的重击和突袭昏迷时长延长 {ms(rec.s(1))} 秒。",
        "Sharpened Claws": f"在熊形态、巨熊形态、猎豹形态或枭兽形态下，近战暴击几率提高 {rec.s(1)}%。",
        "Feral Instinct": f"使你在熊形态和巨熊形态下造成的威胁值提高 {rec.s(2)}%，并降低敌人在你潜行时侦测到你的几率。",
        "Blood Frenzy": f"你的猎豹形态下可产生连击点数的技能造成暴击时，有 {rec.h() if rec.h() <= 100 else 50}% 几率额外获得 1 个连击点数。",
        "Primal Fury": f"你在熊形态和巨熊形态下造成暴击时，有 {rec.h() if rec.h() <= 100 else 50}% 几率额外获得 {records.get(16959, rec).s(1) / 10:g} 点怒气。",
        "Shredding Attacks": f"使你的撕碎能量消耗降低 {positive(rec.s(1))} 点，割伤怒气消耗降低 {positive(rec.s(2)) / 10:g} 点。",
        "Savage Fury": f"猛虎之怒现在还会使你的能量恢复速度每层提高 {rec.s(1)}%，并使凶猛撕咬对生命值低于 20% 的目标造成的伤害提高 {rec.s(2)}%。",
        "Feral Swiftness": f"在户外猎豹形态下移动速度提高 {records.get(24867, rec).s(1)}%，并在猎豹、熊和巨熊形态下躲闪几率提高 {rec.s(2)}%。",
        "Heart of the Wild": f"使你的智力提高 {rec.s(1)}%。此外，在熊或巨熊形态下耐力提高 {rec.s(1)}%，在猎豹形态下攻击强度提高 {rec.s(2)}%。",
        "Leader of the Pack": f"在猎豹、熊或巨熊形态下，使 {records.get(24932, rec).s(1) if records.get(24932, rec).s(1) > 5 else 45} 码范围内所有小队和团队成员的远程和近战暴击几率提高 {records.get(24932, rec).s(1)}%。此外，你自己的近战暴击几率额外提高。",
        "Improved Mark of the Wild": f"使你的野性印记和野性赐福效果提高 {rec.s(1)}%。",
        "Furor": f"你变为熊形态或巨熊形态时有 {rec.s(1)}% 几率获得 {records.get(17057, rec).s(1) / 10:g} 点怒气，变为猎豹形态时有 {rec.s(1)}% 几率获得 {records.get(17099, rec).s(1)} 点能量。",
        "Nature's Focus": f"使你施放治疗之触、愈合和宁静时有 {rec.s(1)}% 几率避免因受到伤害而被打断。",
        "Naturalist": f"使你的治疗之触施法时间缩短 {ms(rec.s(1))} 秒，并使你在所有形态下造成的物理攻击伤害提高 {rec.s(2)}%。",
        "Improved Regrowth": f"使你的愈合法术暴击几率提高 {rec.s(1)}%。",
        "Gift of Nature": f"使所有治疗法术效果提高 {rec.s(1)}%。",
        "Intensity": f"使你在施法时仍保持 {rec.s(1)}% 的法力恢复，并使激怒技能立即产生 {records.get(17080, rec).s(1) / 10:g} 点怒气。",
        "Improved Rejuvenation": f"使你的回春术效果提高 {rec.s(1)}%。",
        "Subtlety": f"使你的恢复法术产生的威胁值降低 {positive(rec.s(1))}%，并使你的有益法术被驱散的几率降低 {rec.s(2)}%。",
        "Tranquil Spirit": f"使你的治疗之触和宁静法力值消耗降低 {positive(rec.s(1))}%。",
        "Improved Tranquility": f"使你的宁静产生的威胁值降低 {positive(rec.s(1))}%。",
        "Nature's Swiftness": "激活后，你的下一个施法时间少于 10 秒的自然法术变为瞬发。",
        "Improved Nature's Grasp": f"使你的自然之握触发几率提高 {rec.s(1)}%。",
        "Maim": f"终结技，使目标昏迷并造成伤害。伤害和时长随连击点数提高。",
        "Balance of Power": f"使你的法术命中几率提高 {rec.s(1)}%，并使你受到法术命中的几率降低 {positive(rec.s(2))}%。",
        "Lunar Guidance": f"使你的法术伤害和治疗效果提高，数值相当于你的智力的 {rec.s(1)}%。",
        "Dreamstate": f"即使在施法时，每 5 秒仍恢复相当于智力 {rec.s(1)}% 的法力值。",
        "Improved Faerie Fire": f"你的精灵之火还会使目标被法术命中的几率提高 {rec.s(1)}%，并使你对受精灵之火影响的目标造成的法术暴击几率提高 {rec.s(2)}%。",
        "Primal Tenacity": f"使你抵抗昏迷和恐惧机制的几率提高 {rec.s(1)}%。",
        "Survival of the Fittest": f"使所有属性提高 {rec.s(1)}%，并使你被近战攻击暴击的几率降低 {positive(rec.s(2))}%。",
        "Predatory Instincts": f"在猎豹、熊或巨熊形态下，使近战暴击伤害提高 {rec.s(1)}%，躲避范围效果攻击的几率提高 {rec.s(2)}%。",
        "Nurturing Instinct": f"使你的治疗法术效果最多提高敏捷值的 {rec.s(1)}%，并使你在猎豹形态下受到的治疗效果提高 {records.get(47179, rec).s(1)}%。",
        "Empowered Touch": f"你的治疗之触额外获得相当于治疗加成 {rec.s(1)}% 的收益。",
        "Natural Perfection": f"你的所有法术暴击几率提高 {rec.s(2)}%，且你受到暴击时获得自然完美效果，使受到的所有伤害降低 {positive(records.get(45281, rec).s(1))}%。最多叠加 {records.get(45281, rec).stack() or 3} 次，持续 {duration(records.get(45281, rec))}。",
        "Empowered Rejuvenation": f"使你的持续治疗法术获得的额外治疗加成提高 {rec.s(1)}%。",
        "Living Spirit": f"使你的精神总值提高 {rec.s(1)}%。",
        "Improved Leader of the Pack": f"你的兽群领袖还会使受影响目标在近战或远程攻击暴击时有 {rec.s(2)}% 几率恢复总生命值的 {rec.s(1)}%。该治疗效果每 6 秒最多触发一次。",
        "Focused Starlight": f"使你的愤怒、虚弱、星火术和天顶法术暴击几率提高 {rec.s(1)}%。",
        "Improved Moonkin Form": f"你的枭兽光环还会使受影响目标获得 {records.get(50170, rec).s(1)}% 急速，并使你获得额外法术伤害，数值相当于精神的 {rec.s(2)}%。",
        "Owlkin Frenzy": f"在枭兽形态下受到攻击时，有 {rec.h() if rec.h() <= 100 else 15}% 几率进入狂乱，使你造成的伤害提高 {records.get(48391, rec).s(2)}%，施放平衡系法术时免疫施法延迟，并每 {records.get(48391, rec).amp_sec(3) or 2} 秒恢复 {records.get(48391, rec).s(3)}% 基础法力值，持续 {duration(records.get(48391, rec))}。",
        "Primal Precision": f"使你的精准提高 {rec.s(1)}，如果终结技未命中，则返还其能量消耗的 {rec.s(2)}%。",
        "Master Shapeshifter": f"根据当前变形形态获得效果：熊形态物理伤害提高 {rec.s(1)}%，猎豹形态暴击几率提高 {rec.s(1)}%，枭兽形态法术伤害提高 {rec.s(1)}%，生命之树形态治疗效果提高 {rec.s(1)}%。",
        "Rend and Tear": f"使你的重殴和撕碎对流血目标造成的伤害提高 {rec.s(1)}%，并使凶猛撕咬对流血目标的暴击几率提高 {rec.s(2)}%。",
        "Spark of Nature": f"使你的迅捷治愈和滋养暴击几率提高 {rec.s(1)}%。",
        "Infected Wounds": f"你的撕碎、重殴和裂伤会使目标感染伤口，使其移动速度降低 {positive(records.get(58179, rec).s(1))}%，攻击速度降低 {positive(records.get(58179, rec).s(2))}%，持续 {duration(records.get(58179, rec))}。",
        "Gale Winds": f"使你的飓风和台风造成的伤害提高 {rec.s(1)}%，旋风射程延长 {rec.s(2)} 码。",
        "Improved Mangle": f"使你的裂伤（熊）冷却时间缩短 {ms(rec.s(1))} 秒，并使裂伤（猎豹）能量消耗降低 {positive(rec.s(2))} 点。",
        "King of the Jungle": f"在熊或巨熊形态下使用激怒时，你造成的伤害提高 {rec.s(1)}%；猛虎之怒还会立即恢复 {rec.s(2)} 点能量。此外，熊形态、猎豹形态和巨熊形态的法力值消耗降低 {positive(rec.s(3))}%。",
        "Gift of the Earthmother": f"使你的总法术急速提高 {rec.s(1)}%，并使生命绽放基础冷却时间缩短 {positive(rec.s(2)) / 15:g}%。",
        "Genesis": f"使你的持续性法术伤害和持续治疗效果提高 {rec.s(1)}%。",
        "Improved Insect Swarm": f"使你的愤怒对受虫群影响的目标造成的伤害提高 {rec.s(1)}%，并使星火术对受月火术影响的目标暴击几率提高 {rec.s(2)}%。",
        "Nature's Splendor": f"使你的月火术和回春术时长延长 {positive(rec.s(1)) / 1000:g} 秒，愈合延长 {positive(rec.s(2)) / 1000:g} 秒，虫群和生命绽放延长 {positive(rec.s(3)) / 1000:g} 秒。",
        "Protector of the Pack": f"在熊或巨熊形态下，攻击强度提高 {rec.s(1)}%，受到的伤害降低 {positive(rec.s(2))}%。",
        "Natural Reaction": f"在熊或巨熊形态下躲闪几率提高 {rec.s(1)}%，并且每次成功躲闪时恢复 {rec.s(2)} 点怒气。",
        "Primal Gore": "使你的割伤和割裂的周期性伤害可以暴击。",
        "Improved Barkskin": f"在旅行形态或未变形时，使布甲和皮甲提供的护甲额外提高 {rec.s(2)}%，使树皮术提供的伤害减免提高 {positive(rec.s(1))}%，并使树皮术被驱散的几率降低 {rec.s(3)}%。",
        "Improved Barkskin (Passive)": "强化树皮术的被动效果。",
        "Wrath of Cenarius": f"你的星火术额外获得相当于法术伤害加成 {rec.s(1)}% 的收益，愤怒额外获得相当于法术伤害加成 {rec.s(2)}% 的收益。",
        "Revitalize": f"你的回春术和野性成长每次生效时有 {rec.s(1)}% 几率恢复 {records.get(48540, rec).s(1)} 点能量、{records.get(48541, rec).s(1) / 10:g} 点怒气、{records.get(48542, rec).s(1)}% 法力值或 {records.get(48543, rec).s(1) / 10:g} 点符文能量。",
        "Earth and Moon": f"你的愤怒和星火术有 {rec.h() if rec.h() <= 100 else 100}% 几率施加大地与月亮效果，使目标受到的法术伤害提高 {records.get(60431, rec).s(1)}%，持续 {duration(records.get(60431, rec))}。此外，你的法术伤害提高 {rec.s(2)}%。",
        "Eclipse": f"当星火术暴击时，有 {rec.h() if rec.h() <= 100 else 60}% 几率使愤怒伤害提高 {records.get(48517, rec).s(1)}%。当愤怒暴击时，有 {(rec.h() if rec.h() <= 100 else 60) * 0.6:g}% 几率使星火术暴击几率提高 {records.get(48518, rec).s(1)}%。每种效果持续 {duration(records.get(48518, rec))}，各自拥有 {rec.s(1)} 秒独立冷却时间，且不能同时发生。",
    }
    return table.get(name, "")


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    text = ability_desc(name, rec, records) or talent_desc(name, rec, row, records)
    if text:
        return text
    source = row.get("description_zh") or row.get("description_en") or rec.desc
    resolved = resolve_tokens(source, rec, records)
    if CJK_RE.search(resolved) and not ASCII_WORD_RE.search(resolved) and "$" not in resolved and "按属性计算的数值" not in resolved:
        return resolved
    return f"{NAME_ZH.get(name, name)}。"


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    if ability_desc(row["name_en"], rec, records) or talent_desc(row["name_en"], rec, row, records):
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


def is_druid(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & DRUID_SKILLS)


def process_rows(rows: list[dict[str, str]], records: dict[int, SpellRec]) -> tuple[dict[str, dict[str, str]], int]:
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_druid(row):
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
    return updates, changed


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates, changed = process_rows(rows, records)
    write_tsv(PRIORITY, fields, rows)

    full_fields, full_rows = read_tsv(FULL)
    full_updates, full_changed = process_rows(full_rows, records)
    full_updates.update(updates)
    for row in full_rows:
        update = full_updates.get(row["spell_id"])
        if update:
            row.update(update)
    write_tsv(FULL, full_fields, full_rows)

    bad = [
        row for row in rows
        if is_druid(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or ASCII_WORD_RE.search(row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority druid rows changed: {changed}")
    print(f"full rows changed directly: {full_changed}")
    print(f"druid spell ids synced: {len(full_updates)}")
    print(f"druid zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:40]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
