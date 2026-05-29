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

PALADIN_SKILLS = {"184", "267", "594"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")

NAME_ZH = {
    "Anticipation": "预知", "Ardent Defender": "炽热防御者", "Aura Mastery": "光环掌握",
    "Avenger's Shield": "复仇者之盾", "Avenging Wrath": "复仇之怒", "Beacon of Light": "圣光道标",
    "Benediction": "祈福", "Blessed Hands": "神佑之手", "Blessed Life": "神佑人生",
    "Blessing of Kings": "王者祝福", "Blessing of Light": "光明祝福", "Blessing of Might": "力量祝福",
    "Blessing of Salvation": "拯救祝福", "Blessing of Sanctuary": "庇护祝福", "Blessing of Wisdom": "智慧祝福",
    "Blood Corruption": "鲜血腐蚀", "Cleanse": "清洁术", "Combat Expertise": "战斗专精",
    "Concentration Aura": "专注光环", "Consecration": "奉献", "Conviction": "定罪",
    "Crusade": "十字军", "Crusader Aura": "十字军光环", "Crusader Strike": "十字军打击",
    "Deflection": "偏斜", "Devotion Aura": "虔诚光环", "Divine Favor": "神恩术",
    "Divine Guardian": "神圣守护者", "Divine Illumination": "神圣照明", "Divine Intellect": "神圣智力",
    "Divine Intervention": "神圣干涉", "Divine Plea": "神圣恳求", "Divine Protection": "圣佑术",
    "Divine Purpose": "神圣意志", "Divine Sacrifice": "神圣牺牲", "Divine Shield": "圣盾术",
    "Divine Storm": "神圣风暴", "Divine Strength": "神圣力量", "Divinity": "神圣",
    "Enlightened Judgements": "开悟审判", "Exorcism": "驱邪术", "Eye for an Eye": "以眼还眼",
    "Fanaticism": "狂热", "Fire Resistance Aura": "火焰抗性光环", "Flash of Light": "圣光闪现",
    "Frost Resistance Aura": "冰霜抗性光环", "Glyph of Holy Light": "圣光术雕文",
    "Greater Blessing of Kings": "强效王者祝福", "Greater Blessing of Light": "强效光明祝福",
    "Greater Blessing of Might": "强效力量祝福", "Greater Blessing of Salvation": "强效拯救祝福",
    "Greater Blessing of Sanctuary": "强效庇护祝福", "Greater Blessing of Wisdom": "强效智慧祝福",
    "Guarded by the Light": "圣光守护", "Guardian's Favor": "守护者的宠爱",
    "Hammer of Justice": "制裁之锤", "Hammer of the Righteous": "正义之锤", "Hammer of Wrath": "愤怒之锤",
    "Hand of Freedom": "自由之手", "Hand of Protection": "保护之手", "Hand of Reckoning": "清算之手",
    "Hand of Sacrifice": "牺牲之手", "Healing Light": "治愈之光", "Holy Guidance": "神圣指引",
    "Holy Light": "圣光术", "Holy Mending": "神圣治疗", "Holy Power": "神圣之力",
    "Holy Shield": "神圣之盾", "Holy Shock": "神圣震击", "Holy Vengeance": "神圣复仇",
    "Holy Wrath": "神圣愤怒", "Illumination": "启发", "Improved Blessing of Might": "强化力量祝福",
    "Improved Blessing of Wisdom": "强化智慧祝福", "Improved Concentration Aura": "强化专注光环",
    "Improved Crusader Strike": "强化十字军打击", "Improved Devotion Aura": "强化虔诚光环",
    "Improved Flash of Light": "强化圣光闪现", "Improved Hammer of Justice": "强化制裁之锤",
    "Improved Holy Shield": "强化神圣之盾", "Improved Judgement": "强化审判",
    "Improved Lay on Hands": "强化圣疗术", "Improved Retribution Aura": "强化惩罚光环",
    "Improved Righteous Fury": "强化正义之怒", "Improved Sanctity Aura": "强化圣洁光环",
    "Improved Seal of Righteousness": "强化正义圣印", "Infusion of Light": "圣光灌注",
    "Judgement": "审判", "Judgement Anti-Parry/Dodge Passive": "审判反招架/躲闪被动",
    "Judgement of Command": "命令审判", "Judgement of Corruption": "腐蚀审判",
    "Judgement of Justice": "公正审判", "Judgement of Light": "光明审判",
    "Judgement of Penitence": "悔罪审判", "Judgement of Righteousness": "正义审判",
    "Judgement of the Martyr": "殉道者审判", "Judgement of Vengeance": "复仇审判",
    "Judgement of Wisdom": "智慧审判", "Judgements of the Just": "公正审判",
    "Judgements of the Pure": "纯净审判", "Lay on Hands": "圣疗术", "Light's Beacon": "圣光道标",
    "Light's Grace": "圣光恩赐", "Mass Resurrection": "群体复活", "One-Handed Weapon Specialization": "单手武器专精",
    "Precision": "精确", "Pursuit of Justice": "正义追击", "Pure of Heart": "纯净心灵",
    "Purify": "纯净术", "Purifying Power": "净化之力", "Reckoning": "清算",
    "Redemption": "救赎", "Redoubt": "盾牌壁垒", "Repentance": "忏悔",
    "Retribution Aura": "惩罚光环", "Righteous Defense": "正义防御", "Righteous Fury": "正义之怒",
    "Righteous Vengeance": "正义复仇", "Risen Charger": "复生战马", "Risen Warhorse": "复生军马",
    "Sacred Cleansing": "神圣净化", "Sacred Duty": "神圣使命", "Sacred Shield": "圣洁护盾",
    "Sanctified Judgement": "神圣审判", "Sanctified Light": "神圣圣光", "Sanctified Seals": "神圣圣印",
    "Sanctified Wrath": "神圣愤怒", "Sanctity Aura": "圣洁光环", "Seal of Command": "命令圣印",
    "Seal of Corruption": "腐蚀圣印", "Seal of Dedication": "奉献圣印", "Seal of Justice": "公正圣印",
    "Seal of Light": "光明圣印", "Seal of Righteousness": "正义圣印", "Seal of Vengeance": "复仇圣印",
    "Seal of Wisdom": "智慧圣印", "Seal of the Crusader": "十字军圣印", "Sense Undead": "感知亡灵",
    "Shadow Resistance Aura": "暗影抗性光环", "Sheath of Light": "圣光出鞘",
    "Shield Specialization": "盾牌专精", "Shield of Righteousness": "正义盾击",
    "Shield of the Templar": "圣殿骑士之盾", "Spell Warding": "法术屏障",
    "Spiritual Attunement": "精神协调", "Spiritual Focus": "精神集中", "Stoicism": "坚韧不拔",
    "Summon Charger": "召唤战马", "Summon Warhorse": "召唤军马", "Swift Retribution": "迅捷惩戒",
    "The Art of War": "战争艺术", "Touched by the Light": "圣光之触", "Toughness": "坚韧",
    "Turn Evil": "驱邪术", "Turn Undead": "超度亡灵", "Two-Handed Weapon Specialization": "双手武器专精",
    "Unyielding Faith": "不屈信念", "Vengeance": "复仇", "Verdict": "裁决", "Vindication": "辩护",
}

TERM_FIXES = [
    ("Paladin", "圣骑士"), ("paladin", "圣骑士"), ("Holy", "神圣"), ("holy", "神圣"),
    ("Physical", "物理"), ("Fire", "火焰"), ("Frost", "冰霜"), ("Shadow", "暗影"),
    ("Nature", "自然"), ("Arcane", "奥术"), ("Undead", "亡灵"), ("Demon", "恶魔"),
    ("Humanoids", "人型生物"), ("Elementals", "元素生物"), ("attack power", "攻击强度"),
    ("Attack Power", "攻击强度"), ("spell power", "法术强度"), ("Spell Power", "法术强度"),
    ("damage", "伤害"), ("Damage", "伤害"), ("healing", "治疗"), ("Healing", "治疗"),
    ("health", "生命值"), ("Health", "生命值"), ("mana", "法力值"), ("Mana", "法力值"),
    ("armor", "护甲"), ("Armor", "护甲"), ("resistance", "抗性"), ("Resistance", "抗性"),
    ("threat", "威胁值"), ("Threat", "威胁值"), ("critical strike", "暴击"), ("critical", "暴击"),
    ("Critical", "暴击"), ("cooldown", "冷却时间"), ("Cooldown", "冷却时间"),
    ("Silence", "沉默"), ("Interrupt", "打断"), ("Fear", "恐惧"), ("Disorient", "迷惑"),
    ("Stun", "昏迷"), ("Curse", "诅咒"), ("Disease", "疾病"), ("Magic", "魔法"), ("Poison", "中毒"),
    ("Warhorse", "军马"), ("Charger", "战马"), ("Risen", "复生"), ("Blessing", "祝福"),
    ("Judgement", "审判"), ("Judgments", "审判"), ("Seals", "圣印"), ("Seal", "圣印"),
    ("Auras", "光环"), ("Aura", "光环"), ("Hand", "之手"), ("Light", "光明"), ("Wisdom", "智慧"),
    ("Righteousness", "正义"), ("Vengeance", "复仇"), ("Corruption", "腐蚀"), ("Martyr", "殉道者"),
    ("Command", "命令"), ("Justice", "公正"), ("Crusader", "十字军"), ("Holy Light", "圣光术"),
    ("Flash of Light", "圣光闪现"), ("Holy Shock", "神圣震击"), ("Hammer of Wrath", "愤怒之锤"),
    ("Crusader Strike", "十字军打击"), ("Divine Storm", "神圣风暴"), ("Avenger's Shield", "复仇者之盾"),
    ("爆击", "暴击"), ("护护甲", "护甲"), ("小队 and 团队", "小队和团队"),
    ("$ghimself:herself;", "自己"), ("$ghe:she;", "其"), ("$ghis:her;", "其"),
]

DURATION_BY_NAME = {
    "Avenger's Shield": "10秒", "Avenging Wrath": "20秒", "Beacon of Light": "1分钟",
    "Blessing of Kings": "10分钟", "Blessing of Light": "10分钟", "Blessing of Might": "10分钟",
    "Blessing of Salvation": "10分钟", "Blessing of Sanctuary": "10分钟", "Blessing of Wisdom": "10分钟",
    "Consecration": "8秒", "Divine Guardian": "6秒", "Divine Illumination": "15秒",
    "Divine Intervention": "3分钟", "Divine Plea": "15秒", "Divine Protection": "12秒",
    "Divine Sacrifice": "10秒", "Divine Shield": "12秒", "Greater Blessing of Kings": "30分钟",
    "Greater Blessing of Light": "30分钟", "Greater Blessing of Might": "30分钟",
    "Greater Blessing of Salvation": "30分钟", "Greater Blessing of Sanctuary": "30分钟",
    "Greater Blessing of Wisdom": "30分钟", "Hammer of Justice": "6秒", "Hand of Freedom": "10秒",
    "Hand of Protection": "10秒", "Hand of Sacrifice": "12秒", "Holy Shield": "10秒",
    "Judgement of Justice": "20秒", "Judgement of Wisdom": "20秒", "Judgements of the Pure": "1分钟",
    "Holy Vengeance": "15秒", "Blood Corruption": "15秒", "Flash of Light": "12秒",
    "Light's Grace": "15秒", "Reckoning": "8秒", "Redoubt": "10秒", "Repentance": "1分钟",
    "Righteous Fury": "直到取消", "Righteous Vengeance": "8秒", "Sacred Cleansing": "10秒",
    "Sacred Shield": "30秒", "Seal of Command": "30分钟", "Seal of Corruption": "30分钟",
    "Seal of Dedication": "30分钟", "Seal of Justice": "30分钟", "Seal of Light": "30分钟",
    "Seal of Righteousness": "30分钟", "Seal of Vengeance": "30分钟", "Seal of Wisdom": "30分钟",
    "Seal of the Crusader": "30分钟", "Shield of the Templar": "3秒", "Turn Evil": "20秒",
    "Turn Undead": "20秒", "Vengeance": "15秒", "Vindication": "10秒", "Holy Mending": "12秒",
    "Improved Lay on Hands": "2分钟", "Seal of Dedication": "12秒",
}

RADIUS_BY_NAME = {
    "Devotion Aura": 40, "Retribution Aura": 40, "Concentration Aura": 40, "Shadow Resistance Aura": 40,
    "Frost Resistance Aura": 40, "Fire Resistance Aura": 40, "Sanctity Aura": 40, "Crusader Aura": 40,
    "Consecration": 8, "Holy Wrath": 10, "Mass Resurrection": 100, "Divine Sacrifice": 30,
    "Divine Guardian": 30, "Divine Storm": 8,
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
    return rank.replace("Rank", "等级").replace("Summon", "召唤").replace("Passive", "被动")


def duration(rec: SpellRec) -> str:
    return DURATION_BY_NAME.get(rec.name, "")


def duration_seconds(rec: SpellRec, fallback: int = 1) -> int:
    text = duration(rec)
    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    value = int(match.group(1))
    return value * 60 if "分钟" in text else value


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 1
        ticks = max(1, duration_seconds(rec, seconds) // seconds)
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
    text = re.sub(r"\?A\d+\[([^\]]*)\]\[([^\]]*)\]", lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"\$\{[^{}]*\}", "数值", text)
    text = re.sub(r"\$[<A-Za-z0-9_/.*;:-]+|\$", "", text)
    text = re.sub(r"\s+([，。；：、])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    text = re.sub(r"(降低|缩短|减少|延长|提高)-(\d)", r"\1\2", text)
    text = re.sub(r"(伤害|恢复|拥有|以)-(\d)", r"\1\2", text)
    text = text.replace("在内", "在持续时间内")
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
    if token == "q":
        return str(abs(target.q(index)))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 1)
    return ""


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    text = text.replace("$D", duration(rec)).replace("$d", duration(rec)).replace("$e", "1")
    text = re.sub(r"\$\{\$m(\d+)/-1000\}", lambda m: f"{abs(rec.s(int(m.group(1)))) / 1000:g}", text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/-1000\}", lambda m: f"{abs(records.get(int(m.group(1)), rec).s(int(m.group(2)))) / 1000:g}", text)
    text = re.sub(r"\$\{\$m(\d+)/4\}", lambda m: f"{rec.s(int(m.group(1))) / 4:g}", text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/4\}", lambda m: f"{records.get(int(m.group(1)), rec).s(int(m.group(2))) / 4:g}", text)
    text = re.sub(r"\$\{\$m(\d+)\*3\*\$<mult>\}", lambda m: str(rec.s(int(m.group(1))) * 3), text)
    text = re.sub(r"\$\{8\*\(\$m(\d+)\+0\.04\*\$SPH\+0\.04\*\$AP\)\}", lambda m: f"{rec.s(int(m.group(1))) * 8}点加法术强度32%与攻击强度32%", text)
    text = re.sub(r"\$\{\$m(\d+)\+0\.15\*\$SPH\+0\.15\*\$AP\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度15%与攻击强度15%", text)
    text = re.sub(r"\$\{\$M(\d+)\+0\.15\*\$SPH\+0\.15\*\$AP\}", lambda m: f"{rec.maxv(int(m.group(1)))}点加法术强度15%与攻击强度15%", text)
    text = re.sub(r"\$\{\$m(\d+)\+0\.07\*\$SPH\+0\.07\*\$AP\}", lambda m: f"{rec.s(int(m.group(1)))}点加法术强度7%与攻击强度7%", text)
    text = re.sub(r"\$\{\$M(\d+)\+0\.07\*\$SPH\+0\.07\*\$AP\}", lambda m: f"{rec.maxv(int(m.group(1)))}点加法术强度7%与攻击强度7%", text)
    text = re.sub(r"\$\{1\+0\.5\*\$AP\}", "1点加攻击强度50%", text)
    text = re.sub(r"\$\{1\+0\.22\*\$SPH\+0\.14\*\$AP\}", "1点加法术强度22%与攻击强度14%", text)
    text = re.sub(r"\$\{\$i-1\}", lambda _: str(max(0, rec.stack() - 1) or 3), text)
    text = re.sub(r"\$\{\$x1-1\}", lambda _: str(max(0, rec.stack() - 1) or 2), text)
    text = re.sub(r"\$\*([0-9]+);([sm])(\d*)", lambda m: str(int(m.group(1)) * int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0)), text, flags=re.I)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: f"{int(int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1))):g}", text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: f"{int(int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1))):g}", text)
    text = re.sub(r"\$(\d+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: str(over_time(rec, int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)", lambda _: str(RADIUS_BY_NAME.get(rec.name, 40)), text, flags=re.I)
    text = re.sub(r"\$q(\d*)", lambda m: str(abs(rec.q(int(m.group(1) or "1")))), text, flags=re.I)
    text = re.sub(r"\$u(\d*)|\$n(\d*)|\$i(\d*)|\$x(\d*)", lambda _: str(rec.stack() or 1), text, flags=re.I)
    text = text.replace("$h", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    text = text.replace("$H", str(rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))))
    return cleanup(text)


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]

    if name in ("Holy Light", "Flash of Light"):
        if row["spell_id"] == "66922":
            return "圣光闪现的持续治疗效果。"
        return f"为友方目标恢复 {rec.s(1)} 点生命值。"
    if name == "Holy Shock":
        return f"用神圣能量冲击目标，造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害，或为友方目标恢复 {rec.s(2)} 到 {rec.maxv(2)} 点生命值。"
    if name == "Exorcism":
        return f"对敌方目标造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害。如果目标是亡灵或恶魔，则必定暴击。"
    if name == "Consecration":
        return f"奉献圣骑士脚下的土地，在 {duration(rec)} 内对进入该区域的敌人造成 {over_time(rec, 1, 8)} 点神圣伤害。"
    if name == "Hammer of Wrath":
        return f"投掷神圣之锤，造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害。只能对生命值低于 20% 的敌人使用。"
    if name == "Crusader Strike":
        return f"一次瞬发打击，造成相当于武器伤害 {rec.s(2)}% 的神圣伤害，并刷新目标身上的所有审判效果。"
    if name == "Divine Storm":
        return f"瞬发武器攻击，对 8 码范围内最多 4 个敌人造成 {rec.s(1)}% 武器伤害，并为最多 3 名小队或团队成员恢复相当于该伤害总量 {rec.s(2)}% 的生命值。"
    if name == "Hammer of the Righteous":
        return f"打击当前目标和附近最多 2 个额外目标，造成相当于主手每秒伤害 {rec.s(3)} 倍的神圣伤害。"
    if name == "Shield of Righteousness":
        return f"用盾牌猛击目标，造成基于格挡值并额外附加 {rec.s(1)} 点的神圣伤害。"
    if name == "Hand of Reckoning":
        return "嘲讽目标攻击你。如果目标可以被嘲讽且当前目标不是你，则造成 1 点加攻击强度 50% 的神圣伤害。"
    if name == "Avenger's Shield":
        return f"向敌人掷出神圣盾牌，造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害，使其眩晕并弹跳到附近额外敌人身上。总共影响 {rec.stack() or 3} 个目标，持续 {duration(rec)}。"
    if name == "Holy Wrath":
        return f"向四周发射神圣能量，对 {RADIUS_BY_NAME['Holy Wrath']} 码范围内所有亡灵和恶魔目标造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害。"

    if name == "Seal of Righteousness":
        return f"圣光灌注圣骑士，持续 {duration(rec)}，使每次近战攻击额外造成基于武器速度和法术强度计算的神圣伤害。切换到其他圣印时保留 0.5 秒。\n\n释放此圣印的能量会审判敌人，立即造成神圣伤害。圣骑士同一时间只能激活一个圣印。"
    if name == "Seal of Command":
        return f"使圣骑士有几率额外造成相当于普通武器伤害 {records.get(20424, rec).s(1)}% 的神圣伤害，持续 {duration(rec)}。切换到其他圣印时保留 0.5 秒。\n\n释放此圣印的能量会审判敌人，立即造成神圣伤害；若目标昏迷或瘫痪，则造成全额伤害。"
    if name == "Seal of Vengeance":
        dot = records.get(31803, rec)
        return f"圣骑士充满神圣之力，持续 {duration(rec)}，使每次近战攻击有几率触发神圣复仇，在 {duration(dot)} 内造成 {dot.s(1)} 点神圣伤害。该效果最多叠加 {dot.stack() or 5} 次。同一时间只能激活一种圣印。\n\n释放此圣印的能量会审判敌人，按目标身上每层神圣复仇立即造成 {records.get(31804, rec).s(1)} 点神圣伤害。"
    if name == "Seal of Corruption":
        dot = records.get(53742, records.get(31803, rec))
        return f"圣骑士充满神圣能量，持续 {duration(rec)}。攻击会使目标感染鲜血腐蚀，在 {duration(dot)} 内造成神圣伤害，最多叠加 {dot.stack() or 5} 层。叠满后，你的每次攻击还会造成相当于武器伤害 {records.get(53739, rec).s(1)}% 的额外神圣伤害。同一时间只能激活一种圣印。\n\n释放此圣印的能量会审判敌人，立即造成 1 点加法术强度 22% 与攻击强度 14% 的神圣伤害；目标身上每有一层鲜血腐蚀，伤害提高 10%。"
    if name == "Holy Vengeance":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点神圣伤害，持续 {duration(rec)}。"
    if name == "Blood Corruption":
        return f"每 {rec.amp_sec(1) or 3} 秒造成神圣伤害，持续 {duration(rec)}。"
    if name == "Seal of Dedication":
        return f"意志之力灌注圣骑士，持续 {DURATION_BY_NAME['Seal of Righteousness']}，使你的攻击对目标和附近一个额外目标造成 {records.get(84524, rec).s(1)}% 武器伤害（神圣）。\n\n释放此圣印的能量会在你面前释放圣光波，对击中的目标造成 {records.get(84525, rec).s(2)} 点神圣伤害；该伤害的 {records.get(84525, rec).s(3)}% 会在 {duration(records.get(84523, rec)) or '12秒'} 内反噬你。"
    if name in ("Seal of Light", "Seal of Wisdom", "Seal of Justice", "Seal of the Crusader", "Seal of Vengeance", "Seal of Corruption", "Seal of Dedication"):
        source = row.get("description_zh") or row.get("description_en") or rec.desc
        resolved = resolve_tokens(source, rec, records)
        if not ASCII_WORD_RE.search(resolved) and "$" not in resolved and resolved:
            return resolved

    if name in ("Blessing of Might", "Greater Blessing of Might"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}力量祝福，使攻击强度提高 {rec.s(1)} 点，持续 {duration(rec)}。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name in ("Blessing of Wisdom", "Greater Blessing of Wisdom"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}智慧祝福，每 5 秒恢复 {rec.s(1)} 点法力值，持续 {duration(rec)}。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name in ("Blessing of Kings", "Greater Blessing of Kings"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}王者祝福，使所有属性提高 {rec.s(1)}%，持续 {duration(rec)}。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name in ("Blessing of Salvation", "Greater Blessing of Salvation"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}拯救祝福，使产生的所有威胁值降低 {abs(rec.s(1))}%，持续 {duration(rec)}。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name in ("Blessing of Light", "Greater Blessing of Light"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}光明祝福，使目标受到圣光术治疗时效果最多提高 {rec.s(1)} 点，受到圣光闪现治疗时效果最多提高 {rec.s(2)} 点，持续 {duration(rec)}。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name in ("Blessing of Sanctuary", "Greater Blessing of Sanctuary"):
        return f"为友方目标施加{'强效' if name.startswith('Greater') else ''}庇护祝福，使其受到的所有来源伤害最多降低 {abs(rec.s(1))} 点，持续 {duration(rec)}。此外，当目标格挡一次近战攻击时，攻击者受到 {rec.s(2)} 点神圣伤害。每个玩家同一时间只能获得一名圣骑士提供的一种祝福。"
    if name == "Devotion Aura":
        return f"使 40 码范围内的小队和团队成员护甲值提高 {rec.s(1)} 点。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Retribution Aura":
        return f"对击中 40 码范围内小队或团队成员的任何敌人造成 {rec.s(1)} 点神圣伤害。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Concentration Aura":
        return f"使 40 码范围内所有小队和团队成员在受到伤害时有 {rec.s(1)}% 几率避免施法被打断。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Shadow Resistance Aura":
        return f"使 40 码范围内所有小队和团队成员暗影抗性提高 {rec.s(1)} 点。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Frost Resistance Aura":
        return f"使 40 码范围内所有小队和团队成员冰霜抗性提高 {rec.s(1)} 点。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Fire Resistance Aura":
        return f"使 40 码范围内所有小队和团队成员火焰抗性提高 {rec.s(1)} 点。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Sanctity Aura":
        return f"使 40 码范围内小队和团队成员造成的神圣伤害提高 {rec.s(1)}%。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。"
    if name == "Crusader Aura":
        return f"使 40 码范围内所有小队和团队成员骑乘速度提高 {rec.s(1)}%。每个玩家同一时间只能获得一名圣骑士提供的一种光环效果。此效果不与其他移动速度提高效果叠加。"

    if name == "Redemption":
        return f"使一名死去的玩家复活，并使其拥有 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。不能在战斗中使用。"
    if name == "Mass Resurrection":
        return f"使 {RADIUS_BY_NAME['Mass Resurrection']} 码范围内所有小队成员复活，恢复 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。无法在战斗中施放。"
    if name == "Lay on Hands":
        mana = f"，并为其恢复 {rec.s(2)} 点法力值" if rec.s(2) > 1 else ""
        return f"为友方目标恢复等同于圣骑士最大生命值的生命值{mana}。使用后耗尽圣骑士剩余法力值。"
    if name == "Purify":
        return f"净化友方目标，移除 {rec.s(1)} 个疾病效果和 {rec.s(2)} 个中毒效果。"
    if name == "Cleanse":
        return f"净化友方目标，移除 {rec.s(1)} 个中毒效果、{rec.s(2)} 个疾病效果和 {rec.s(3)} 个魔法效果。"
    if name == "Sense Undead":
        return "在小地图上显示附近所有亡灵的位置，直到取消。同一时间只能激活一种追踪。"
    if name in ("Turn Undead", "Turn Evil"):
        target = "亡灵或恶魔" if name == "Turn Evil" else "亡灵"
        return f"使目标{target}敌人因恐惧逃跑，最多持续 {duration(rec)}。造成伤害可能打断该效果。同一时间只能超度一个目标。"
    if name == "Repentance":
        return f"使敌方目标进入冥想状态，瘫痪最多 {duration(rec)}。任何伤害都会唤醒目标。只对人型生物有效。"
    if name == "Hammer of Justice":
        return f"使目标昏迷 {duration(rec)}。"
    if name in ("Divine Shield", "Divine Protection"):
        penalty = f"，但造成的伤害降低 {abs(rec.s(2))}%" if rec.s(2) < 0 else ""
        return f"保护圣骑士免疫所有伤害和法术，持续 {duration(rec)}{penalty}。一旦获得保护，目标在 2 分钟内无法再次通过圣盾术、圣佑术或保护之手获得免疫效果，也无法使用复仇之怒。"
    if name == "Hand of Protection":
        return f"使目标小队成员免疫所有物理攻击，持续 {duration(rec)}，但期间无法攻击或使用物理技能。每个圣骑士同一时间只能对玩家施加一个之手法术。"
    if name == "Hand of Freedom":
        return f"为友方目标施加自由之手，使其免疫移动限制效果，持续 {duration(rec)}。每个圣骑士同一时间只能对玩家施加一个之手法术。"
    if name == "Hand of Sacrifice":
        return f"为小队成员施加牺牲之手，每次受到伤害时将 {rec.s(1)} 点伤害转移给施法者，持续 {duration(rec)}。每个圣骑士同一时间只能对玩家施加一个之手法术。"
    if name == "Divine Intervention":
        return f"圣骑士牺牲自己，使目标小队成员脱离险境。敌人会停止攻击受保护的小队成员；该成员免疫所有有害攻击，但无法采取任何行动，持续 {duration(records.get(19753, rec)) or '3分钟'}。"
    if name == "Righteous Defense":
        return "保护友方目标，命令最多 3 个正在攻击该目标的敌人转而攻击圣骑士。"
    if name == "Righteous Fury":
        return f"使你的神圣法术产生的威胁值提高 {rec.s(1)}%。持续直到取消。"
    if name == "Holy Shield":
        charges = rec.stack() or 8
        return f"格挡几率提高 {rec.s(1)}%，持续 {duration(rec)}；激活期间每次格挡攻击都会造成 {rec.s(2)} 点神圣伤害。神圣之盾造成的伤害产生额外 35% 威胁值，拥有 {charges} 次充能。"
    if name == "Sacred Shield":
        shield = records.get(58597, rec)
        return f"每当目标受到伤害时获得圣洁护盾，吸收 {shield.s(1)} 点伤害，并使圣骑士对该目标施放圣光闪现的暴击几率提高 {shield.s(2)}%，最多持续 {duration(shield) or '6秒'}。目标每 {rec.s(2)} 秒最多触发一次，法术持续 {duration(rec)}。同一时间只能作用于一个目标。"
    if name in ("Beacon of Light", "Light's Beacon"):
        return f"目标成为圣光道标。你对 60 码范围内小队或团队成员施放的任何治疗法术，都会为圣光道标恢复相当于治疗量 {rec.s(1)}% 的生命值。同一时间只能有一个圣光道标，持续 {duration(rec)}。"
    if name == "Divine Plea":
        return f"你在 {duration(rec)} 内恢复相当于总法力值 {over_time(rec, 1)}% 的法力值，但你的圣光闪现、圣光术和神圣震击治疗量降低 {abs(rec.s(2))}%。"
    if name == "Avenging Wrath":
        return f"造成的所有伤害提高 {rec.s(1)}%，持续 {duration(rec)}。产生自律，使你在 2 分钟内无法再次使用圣盾术、圣佑术或保护之手。"
    if name == "Divine Illumination":
        return f"使所有圣骑士法术的施法速度提高 {rec.s(1)}%，持续 {duration(rec)}。产生自律，使你在 2 分钟内无法再次使用圣盾术、圣佑术或保护之手。"
    if name == "Divine Sacrifice":
        return f"{RADIUS_BY_NAME['Divine Sacrifice']} 码范围内所有小队成员受到伤害的 {rec.s(1)}% 由圣骑士分担，最多为圣骑士最大生命值的 {rec.s(3)}% 乘以小队成员人数。如果伤害使圣骑士生命值降至 {rec.s(2)}% 以下，该效果消失。持续 {duration(rec)}。"
    if name.startswith("Summon ") or name.startswith("Risen "):
        mount = NAME_ZH.get(name, name).replace("召唤", "")
        return f"召唤或解散可骑乘的{mount}。移动速度根据你的骑术技能提高。"

    talent = talent_desc(name, rec, row, records)
    if talent:
        return talent

    source = row.get("description_zh") or row.get("description_en") or rec.desc
    resolved = resolve_tokens(source, rec, records)
    if CJK_RE.search(resolved) and not ASCII_WORD_RE.search(resolved) and "$" not in resolved and "数值" not in resolved:
        return resolved
    if CJK_RE.search(resolved) and not ASCII_WORD_RE.search(resolved) and "$" not in resolved:
        return resolved
    return f"{NAME_ZH.get(name, name)}：获得第 {rank_num(row)} 级圣骑士效果。"


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    if name == "Vindication":
        return f"圣骑士的近战伤害攻击有几率使目标所有属性降低 {abs(rec.s(1))}%，持续 {duration(rec)}。"
    if name == "Unyielding Faith":
        return f"使你抵抗恐惧和迷惑效果的几率额外提高 {rec.s(1)}%。"
    if name == "Eye for an Eye":
        return f"对你造成的所有法术暴击也会将 {rec.s(1)}% 的伤害反弹给施法者。以眼还眼造成的伤害不会超过圣骑士最大生命值的 50%。"
    if name == "Holy Power":
        return f"使你的神圣法术暴击几率提高 {rec.s(1)}%。"
    if name == "Guardian's Favor":
        return f"使你的保护之手冷却时间缩短 {abs(rec.s(1)) // 1000:g} 秒，并使自由之手持续时间延长 {abs(rec.s(2)) // 1000:g} 秒。"
    if name == "Improved Lay on Hands":
        return f"使你的圣疗术目标从物品获得的护甲值提高 {records.get(20233, rec).s(1)}%，持续 {duration(records.get(20233, rec)) or '2分钟'}。此外，圣疗术冷却时间缩短 {abs(rec.s(2)) // 60000:g} 分钟。"
    if name == "Improved Concentration Aura":
        return f"使你的专注光环效果额外提高 {rec.s(1)}%，并使受影响的小队成员受到的沉默或打断效果持续时间缩短 {abs(rec.s(2))}%。该效果不与其他类似效果叠加。"
    if name == "Improved Hammer of Justice":
        return f"使你的制裁之锤冷却时间缩短 {abs(rec.s(1))} 秒。"
    if name == "Improved Judgement":
        return f"使你的审判法术冷却时间缩短 {abs(rec.s(1))} 秒。"
    if name == "Sacred Duty":
        return f"使你的总耐力提高 {rec.s(3)}%，并使圣盾术冷却时间缩短 {abs(rec.s(1)) // 1000:g} 秒。"
    if name == "Sanctified Wrath":
        return f"使愤怒之锤暴击几率提高 {rec.s(2)}%，复仇之怒冷却时间缩短 {abs(rec.s(1)) // 1000:g} 秒；复仇之怒激活时，你造成的所有伤害有 {rec.s(3)}% 无视伤害减免效果。"
    if name == "Stoicism":
        return f"使你受到的昏迷效果持续时间缩短 {abs(rec.s(1))}%，并使你的有益法术和周期性伤害效果被驱散的几率降低 {abs(rec.s(2))}%。"
    if name == "Infusion of Light":
        haste = abs(records.get(53672 if rank_num(row) == 1 else 54149, rec).s(2)) / 1000
        crit = records.get(53672 if rank_num(row) == 1 else 54149, rec).s(1)
        return f"你的神圣震击暴击会使下一个圣光闪现施法时间缩短 {haste:g} 秒，或使下一个圣光术暴击几率提高 {crit}%。此外，使你对拥有圣洁护盾的目标施放圣光闪现时，在 12 秒内额外恢复 {rec.s(3)}% 的治疗量。"
    if name == "Judgements of the Just":
        return f"使你的制裁之锤冷却时间缩短 {abs(rec.s(2)) // 1000:g} 秒，正义圣印效果持续时间延长 {abs(rec.s(3)) // 1000:g} 秒，并使你的审判法术额外使目标近战攻击速度降低 {abs(rec.s(1))}%。"
    if name == "Shield of the Templar":
        return f"使你受到的所有伤害降低 {abs(rec.s(2))}%，并使复仇者之盾有 {rec.h()}% 几率使目标沉默，持续 {duration(records.get(63529, rec)) or '3秒'}。"
    if name == "Divine Plea":
        return f"你在 {duration(rec)} 内恢复相当于总法力值 {over_time(rec, 1)}% 的法力值，但圣光闪现、圣光术和神圣震击治疗量降低 {abs(rec.s(2))}%。"
    if name == "Judgement Anti-Parry/Dodge Passive":
        return "你的审判不会被招架或躲闪。"
    return judgement_desc(name, rec, records)


def judgement_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name == "Judgement of Light":
        return f"审判目标，使攻击该目标的近战攻击有几率为攻击者恢复 {rec.s(1)} 点生命值。"
    if name == "Judgement of Wisdom":
        return f"审判目标，使攻击该目标的攻击和法术有几率为攻击者恢复 {rec.s(1)} 点法力值。"
    if name == "Judgement of Righteousness":
        return f"释放正义圣印的能量，立即对敌人造成 {rec.s(1)} 到 {rec.maxv(1)} 点神圣伤害。"
    if name == "Judgement of Command":
        return f"释放命令圣印的能量，立即对敌人造成神圣伤害；若目标昏迷或瘫痪，则造成全额伤害。"
    if name == "Judgement of Vengeance":
        return f"释放复仇圣印的能量，按目标身上每层神圣复仇效果立即造成 {rec.s(1)} 点神圣伤害。"
    if name == "Judgement of Corruption":
        return "释放腐蚀圣印的能量，对敌人造成 1 点加法术强度 22% 与攻击强度 14% 的神圣伤害；目标身上每有一层鲜血腐蚀，伤害提高 10%。"
    if name == "Judgement of the Martyr":
        return "释放殉道者圣印的能量审判敌人，立即造成神圣伤害，同时圣骑士受到相当于该伤害 33% 的伤害。"
    if name == "Judgement of Penitence":
        return f"释放圣印能量审判敌人，立即造成 {rec.s(1)} 点神圣伤害，同时消耗相当于伤害量 33% 的生命值。"
    return ""


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    source = row.get("tooltip_zh") or row.get("tooltip_en") or rec.aura
    if not source:
        return ""
    if name == "Flash of Light" and row["spell_id"] == "66922":
        return "在 12 秒内持续治疗。"
    if name in ("Seal of Vengeance", "Seal of Corruption"):
        return ""
    if name in ("Holy Vengeance", "Blood Corruption"):
        return f"每 {rec.amp_sec(1) or 3} 秒造成神圣伤害。"
    if name == "Divine Plea":
        return f"获得总法力值的 {over_time(rec, 1)}%。\n治疗法术效果降低 {abs(rec.s(2))}%。"
    tip = resolve_tokens(source, rec, records)
    if CJK_RE.search(tip) and not ASCII_WORD_RE.search(tip) and "$" not in tip:
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


def is_paladin(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & PALADIN_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_paladin(row):
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
        if is_paladin(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or ASCII_WORD_RE.search(row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority paladin rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"paladin spell ids synced: {len(updates)}")
    print(f"paladin zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:30]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
