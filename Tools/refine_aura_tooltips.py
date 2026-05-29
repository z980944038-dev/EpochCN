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

CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")

DAMAGE_SCHOOL = {
    "Arcane": "奥术", "Fire": "火焰", "Frost": "冰霜", "Holy": "神圣",
    "Nature": "自然", "Physical": "物理", "Shadow": "暗影",
}

TERM_MAP = {
    "Agility": "敏捷", "all attributes": "所有属性", "all resistances": "所有抗性",
    "all stats": "所有属性", "armor": "护甲", "Armor": "护甲",
    "attack power": "攻击强度", "Attack power": "攻击强度", "Attack Power": "攻击强度",
    "block rating": "格挡等级", "block value": "格挡值",
    "casting speed": "施法速度", "critical strike chance": "暴击几率",
    "critical strike rating": "暴击等级", "damage caused": "造成的伤害",
    "damage done": "造成的伤害", "damage taken": "受到的伤害",
    "defense": "防御", "defense rating": "防御等级", "dodge": "躲闪",
    "dodge rating": "躲闪等级", "healing": "治疗效果",
    "healing done": "治疗效果", "healing effects": "治疗效果",
    "healing effectiveness": "治疗效果", "health": "生命值",
    "haste rating": "急速等级", "hit rating": "命中等级",
    "Intellect": "智力", "intellect": "智力",
    "magical damage and healing done": "法术伤害和治疗效果",
    "melee attack power": "近战攻击强度", "Melee attack power": "近战攻击强度",
    "melee and ranged attack power": "近战和远程攻击强度",
    "melee and ranged attack speed": "近战和远程攻击速度",
    "movement speed": "移动速度", "parry rating": "招架等级",
    "ranged attack power": "远程攻击强度", "Ranged attack power": "远程攻击强度",
    "resilience rating": "韧性等级", "Shadow resistance": "暗影抗性",
    "spell critical strike chance": "法术暴击几率", "spell damage": "法术伤害",
    "spell damage and healing": "法术伤害和治疗效果",
    "spell haste": "法术急速", "spell power": "法术强度",
    "Spirit": "精神", "spirit": "精神", "Stamina": "耐力", "stamina": "耐力",
    "Strength": "力量", "threat": "威胁值",
    "Physical damage done": "物理伤害", "physical damage done": "物理伤害",
    "Offensive ability damage": "攻击性技能伤害", "offensive ability damage": "攻击性技能伤害",
    "Total stats": "所有属性", "total stats": "所有属性",
    "Arcane resistance": "奥术抗性", "Fire resistance": "火焰抗性",
    "Frost resistance": "冰霜抗性", "Nature resistance": "自然抗性",
    "Shadow resistance": "暗影抗性",
}

STATUS_MAP = {
    "Absorbing magic.": "吸收魔法。",
    "Asleep.": "沉睡。",
    "Charmed.": "被魅惑。",
    "Dazed.": "眩晕。",
    "Detect greater invisibility.": "侦测强效隐形。",
    "Detect lesser invisibility.": "侦测次级隐形。",
    "Detect Invisibility.": "侦测隐形。",
    "Detecting Demons.": "正在追踪恶魔。",
    "Detecting traps.": "正在侦测陷阱。",
    "Disarmed.": "被缴械。",
    "Disoriented.": "迷惑。",
    "Enslaved.": "被奴役。",
    "Feared.": "恐惧。",
    "Frozen in place.": "被冻结在原地。",
    "Horrified.": "惊骇。",
    "Immobilized.": "无法移动。",
    "Immobile.": "无法移动。",
    "Incapacitated.": "瘫痪。",
    "Invulnerable, but unable to act.": "无敌，但无法行动。",
    "Levitating.": "漂浮。",
    "Polymorphed.": "被变形。",
    "Reduced distance at which target will attack.": "目标攻击你的距离缩短。",
    "Reduced threat level.": "威胁值降低。",
    "Rooted.": "被定身。",
    "Rooted in place.": "被定身。",
    "Sapped.": "被闷棍。",
    "Silenced.": "沉默。",
    "Stealthed.": "潜行。",
    "Stunned.": "昏迷。",
    "Taunted.": "被嘲讽。",
    "Transferring Life.": "正在传输生命值。",
    "Unconscious.": "昏迷。",
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


def clean_num(value: str | int | float) -> str:
    try:
        number = float(value)
    except Exception:
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:g}"


def abs_num(value: str | int | float) -> str:
    try:
        return clean_num(abs(float(value)))
    except Exception:
        return str(value).lstrip("-")


def term_zh(term: str) -> str:
    term = re.sub(r"^(your|the target's|the caster's|caster's)\s+", "", term.strip(), flags=re.I)
    return TERM_MAP.get(term) or TERM_MAP.get(term.lower()) or term


def school_zh(school: str) -> str:
    return DAMAGE_SCHOOL.get(school, school)


def ref_value(spell_id: int, token: str, number: str, records: dict[int, SpellRec], rec: SpellRec) -> str:
    target = records.get(spell_id, rec)
    index = int(number or "1")
    token = token.lower()
    if token in ("s", "m"):
        return str(target.s(index))
    if token == "t":
        return str(target.amp_sec(index) or 1)
    if token == "q":
        return str(abs(target.q(index)))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 1)
    if token == "h":
        h = target.h()
        return str(h if 0 <= h <= 100 else target.s(index))
    return ""


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    text = text.replace("\\n", "\n")
    text = re.sub(r"\$l([^:;]*):([^;]*);", lambda m: m.group(1) or m.group(2) or "", text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)\*(\d+)\}", lambda m: clean_num(records.get(int(m.group(1)), rec).s(int(m.group(2))) * int(m.group(3))), text)
    text = re.sub(r"\$\{\$(\d+)i-(\d+)\}", lambda m: clean_num(max(0, (records.get(int(m.group(1)), rec).stack() or records.get(int(m.group(1)), rec).s(1)) - int(m.group(2)))), text)
    text = re.sub(r"\$\{\$m(\d+)\*(\d+)\}", lambda m: clean_num(rec.s(int(m.group(1))) * int(m.group(2))), text)
    text = re.sub(r"\$\{\$i-(\d+)\}", lambda m: clean_num(max(0, (rec.stack() or rec.s(1)) - int(m.group(1)))), text)
    text = re.sub(r"\$\{\$m(\d+)/(\d+)\}", lambda m: clean_num(rec.s(int(m.group(1))) / int(m.group(2))), text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)/(\d+)\}", lambda m: clean_num(records.get(int(m.group(1)), rec).s(int(m.group(2))) / int(m.group(3))), text)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: clean_num(int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1))), text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: clean_num(int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1))), text)
    text = re.sub(r"\$\*([\d.]+);(\d+)([A-Za-z])(\d*)", lambda m: clean_num(float(m.group(1)) * int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0)), text)
    text = re.sub(r"\$\*([\d.]+);([A-Za-z])(\d*)", lambda m: clean_num(float(m.group(1)) * int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0)), text)
    text = re.sub(r"\$(\d+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$q(\d*)", lambda m: str(abs(rec.q(int(m.group(1) or "1")))), text, flags=re.I)
    text = re.sub(r"\$u(\d*)|\$n(\d*)|\$i(\d*)|\$x(\d*)", lambda _: str(rec.stack() or 1), text, flags=re.I)
    return re.sub(r"[ \t]+", " ", text).strip()


def punct(text: str) -> str:
    text = re.sub(r"\s+([，。；：])", r"\1", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = text.replace(" ,", "，").replace(",", "，")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace("%%", "%")
    return text.strip()


def translate_single_line(line: str) -> str:
    raw = line.strip()
    if not raw:
        return ""
    if raw in STATUS_MAP:
        return STATUS_MAP[raw]
    if raw == "Immune to Bleed, Poison, and Disease.":
        return "免疫流血、中毒和疾病效果。"
    if raw == "This damage causes no threat.":
        return "该伤害不产生威胁值。"
    if raw == "Diseases unable to be dispelled.":
        return "疾病无法被驱散。"
    match = re.fullmatch(r"(-?[\d.]+) charges?\.?", raw)
    if match:
        return f"{abs_num(match.group(1))} 次充能。"

    # Short status with a periodic secondary effect.
    match = re.fullmatch(r"Rooted\. Causes (\d+) (\w+) damage every (\d+) seconds?\.?", raw)
    if match:
        amount, school, tick = match.groups()
        return f"被定身。每 {tick} 秒造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"([\d.]+) (\w+) damage every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, school, tick = match.groups()
        return f"每 {tick} 秒造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, school, tick = match.groups()
        return f"每 {tick} 秒造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Inflicts ([\d.]+) (\w+) damage every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, school, tick = match.groups()
        return f"每 {tick} 秒造成 {amount} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"Inflicting ([\d.]+) (\w+) damage every (\d+) ?(?:sec\.?|seconds?) to enemies nearby\.?", raw)
    if match:
        amount, school, tick = match.groups()
        return f"每 {tick} 秒对附近敌人造成 {amount} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"([\d.]+) (\w+) damage every second\.?", raw)
    if match:
        amount, school = match.groups()
        return f"每秒造成 {amount} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"([\d.]+) (\w+) damage inflicted every sec\.?", raw)
    if match:
        amount, school = match.groups()
        return f"每秒造成 {amount} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"Taking (\w+) damage every ([\d.]+) sec\.?", raw)
    if match:
        school, tick = match.groups()
        return f"每 {tick} 秒受到{school_zh(school)}伤害。"

    match = re.fullmatch(r"([\d.]+) (\w+) damage over (.+)", raw)
    if match:
        amount, school, duration = match.groups()
        return f"在{duration}内造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage over (.+)", raw)
    if match:
        amount, school, duration = match.groups()
        return f"在{duration}内造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"(?:Healing|Heals) ([\d.]+)(?: damage)? every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒恢复 {amount} 点生命值。"

    match = re.fullmatch(r"Restore[s]? ([\d.]+) health every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒恢复 {amount} 点生命值。"

    match = re.fullmatch(r"Restores ([\d.]+) mana every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒恢复 {amount} 点法力值。"
    match = re.fullmatch(r"([\d.]+) mana restored every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒恢复 {amount} 点法力值。"

    match = re.fullmatch(r"([\d.]+) mana per (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒恢复 {amount} 点法力值。"

    match = re.fullmatch(r"Drains ([\d.]+) (health|mana) every (\d+) ?(?:sec\.?|seconds?) to the caster\.?", raw)
    if match:
        amount, resource, tick = match.groups()
        res = "生命值" if resource == "health" else "法力值"
        return f"每 {tick} 秒吸取 {amount} 点{res}给施法者。"

    match = re.fullmatch(r"Drains ([\d.]+) mana each second to the caster\.?", raw)
    if match:
        return f"每 1 秒吸取 {match.group(1)} 点法力值给施法者。"

    match = re.fullmatch(r"Bleeding for ([\d.]+) damage every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒受到 {amount} 点流血伤害。"

    match = re.fullmatch(r"(?:Bleed damage|Causes damage|Periodically causing damage) every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        return f"每 {match.group(1)} 秒造成一次伤害。"

    match = re.fullmatch(r"Suffering ([\d.]+) damage every (\d+) seconds?\.?", raw)
    if match:
        amount, tick = match.groups()
        return f"每 {tick} 秒受到 {amount} 点伤害。"

    match = re.fullmatch(r"Nature damage inflicted every ([\d.]+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        return f"每 {match.group(1)} 秒造成自然伤害。"

    match = re.fullmatch(r"Damage increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"伤害提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Damage reduced by (-?[\d.]+)%\.?", raw)
    if match:
        return f"伤害降低 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Healed by (-?[\d.]+)% of damage dealt\.?", raw)
    if match:
        return f"造成伤害的 {abs_num(match.group(1))}% 转化为治疗。"
    match = re.fullmatch(r"Chance to hit increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"命中几率提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Chance to hit reduced by (-?[\d.]+)%\.?", raw)
    if match:
        return f"命中几率降低 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Chance to be hit by melee and ranged attacks reduced by (-?[\d.]+)%\.?", raw)
    if match:
        return f"被近战和远程攻击击中的几率降低 {abs_num(match.group(1))}%。"

    match = re.fullmatch(r"Reduces magic damage taken by up to (-?[\d.]+) and healing by up to (-?[\d.]+)\.?", raw)
    if match:
        damage, healing = match.groups()
        return f"受到的魔法伤害最多降低 {abs_num(damage)} 点，治疗效果最多降低 {abs_num(healing)} 点。"
    match = re.fullmatch(r"Increases magic damage taken by up to (-?[\d.]+) and healing by up to (-?[\d.]+)\.?", raw)
    if match:
        damage, healing = match.groups()
        return f"受到的魔法伤害最多提高 {abs_num(damage)} 点，治疗效果最多提高 {abs_num(healing)} 点。"
    match = re.fullmatch(r"(.+?) reduced by (-?[\d.]+) and (.+?) reduced by (-?[\d.]+)%\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}降低 {abs_num(a1)} 点，{term_zh(t2)}降低 {abs_num(a2)}%。"
    match = re.fullmatch(r"(.+?) increased by (-?[\d.]+) and (.+?) increased by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点。"
    match = re.fullmatch(r"Damage reduced by (-?[\d.]+)% and time between attacks increased by (-?[\d.]+)%\.?", raw)
    if match:
        reduced, speed = match.groups()
        return f"受到的伤害降低 {abs_num(reduced)}%，攻击间隔延长 {abs_num(speed)}%。"
    match = re.fullmatch(r"Increases (\w+) resistance by (-?[\d.]+) and causes (-?[\d.]+) (\w+) damage to attacker when struck\.?", raw)
    if match:
        resist, resist_amount, damage, school = match.groups()
        return f"{school_zh(resist)}抗性提高 {abs_num(resist_amount)} 点，被击中时对攻击者造成 {abs_num(damage)} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"Causes (-?[\d.]+) (\w+) damage to attacker on hit\. This damage causes no threat\. (-?[\d.]+) charges?\.?", raw)
    if match:
        amount, school, charges = match.groups()
        return f"被击中时对攻击者造成 {abs_num(amount)} 点{school_zh(school)}伤害。该伤害不产生威胁值。{abs_num(charges)} 次充能。"

    match = re.fullmatch(r"Increases total Strength and Agility by (-?[\d.]+)\.?", raw)
    if match:
        return f"力量和敏捷总值提高 {abs_num(match.group(1))} 点。"
    match = re.fullmatch(r"Increases your total Strength and Agility by (-?[\d.]+)\.?", raw)
    if match:
        return f"你的力量和敏捷总值提高 {abs_num(match.group(1))} 点。"
    match = re.fullmatch(r"(?:Increases|Increased) (?:your )?(.+?) by (-?[\d.]+) and (?:your )?(.+?) by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点。"
    match = re.fullmatch(r"(?:Increases|Increased) (?:your )?(.+?) by (-?[\d.]+), (?:your )?(.+?) by (-?[\d.]+) and (?:your )?(.+?) by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2, t3, a3 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点，{term_zh(t3)}提高 {abs_num(a3)} 点。"
    match = re.fullmatch(r"Armor contribution from cloth, leather, mail and plate items increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"来自布甲、皮甲、锁甲和板甲的护甲值提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Time between melee and ranged attacks increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"近战和远程攻击间隔延长 {abs_num(match.group(1))}%。"

    match = re.fullmatch(r"(?:Increases|Increased|Improves) (?:your )?(.+?) by (-?[\d.]+)%?\.?", raw)
    if match:
        term, amount = match.groups()
        suffix = "%" if "%" in raw else " 点"
        return f"{term_zh(term)}提高 {abs_num(amount)}{suffix}。"

    match = re.fullmatch(r"(.+?) increased by (-?[\d.]+)%?\.?", raw)
    if match:
        term, amount = match.groups()
        suffix = "%" if "%" in raw else " 点"
        return f"{term_zh(term)}提高 {abs_num(amount)}{suffix}。"

    match = re.fullmatch(r"(?:Decreases|Reduces|Reduced) (?:your )?(.+?) by (-?[\d.]+)%?\.?", raw)
    if match:
        term, amount = match.groups()
        suffix = "%" if "%" in raw else " 点"
        return f"{term_zh(term)}降低 {abs_num(amount)}{suffix}。"

    match = re.fullmatch(r"(.+?) (?:reduced|decreased) by (-?[\d.]+)%?\.?", raw)
    if match:
        term, amount = match.groups()
        suffix = "%" if "%" in raw else " 点"
        return f"{term_zh(term)}降低 {abs_num(amount)}{suffix}。"

    match = re.fullmatch(r"(?:Increases|Increased) (?:your )?(.+?) by up to (-?[\d.]+)\.?", raw)
    if match:
        term, amount = match.groups()
        return f"{term_zh(term)}最多提高 {abs_num(amount)} 点。"

    match = re.fullmatch(r"(?:Reduces|Reduced) (?:your )?(.+?) by up to (-?[\d.]+)\.?", raw)
    if match:
        term, amount = match.groups()
        return f"{term_zh(term)}最多降低 {abs_num(amount)} 点。"

    match = re.fullmatch(r"(?:Increases|Increased) (?:your )?(.+?) by (-?[\d.]+) and (?:your )?(.+?) by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点。"

    match = re.fullmatch(r"(?:Increases|Increased) (?:your )?(.+?) by (-?[\d.]+), (?:your )?(.+?) by (-?[\d.]+) and (?:your )?(.+?) by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2, t3, a3 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点，{term_zh(t3)}提高 {abs_num(a3)} 点。"

    match = re.fullmatch(r"(.+?) increased by (-?[\d.]+) and (.+?) increased by (-?[\d.]+)\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}提高 {abs_num(a1)} 点，{term_zh(t2)}提高 {abs_num(a2)} 点。"

    match = re.fullmatch(r"(.+?) reduced by (-?[\d.]+) and (.+?) reduced by (-?[\d.]+)%\.?", raw)
    if match:
        t1, a1, t2, a2 = match.groups()
        return f"{term_zh(t1)}降低 {abs_num(a1)} 点，{term_zh(t2)}降低 {abs_num(a2)}%。"

    match = re.fullmatch(r"Chance to hit decreased by ([\d.]+)% and ([\d.]+) (\w+) damage every (\d+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        chance, amount, school, tick = match.groups()
        return f"命中几率降低 {chance}%，每 {tick} 秒造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"All damage taken increased by ([\d.]+)%, and ([\d.]+) (\w+) damage every (\d+) seconds?\.?", raw)
    if match:
        taken, amount, school, tick = match.groups()
        return f"受到的所有伤害提高 {taken}%，每 {tick} 秒受到 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage to attackers?\.?", raw)
    if match:
        amount, school = match.groups()
        return f"对攻击者造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage to attacker on hit\.?", raw)
    if match:
        amount, school = match.groups()
        return f"被击中时对攻击者造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Does ([\d.]+) (\w+) damage to anyone who strikes you\.?", raw)
    if match:
        amount, school = match.groups()
        return f"对任何攻击你的人造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage to attacker when struck\.?", raw)
    if match:
        amount, school = match.groups()
        return f"被击中时对攻击者造成 {amount} 点{school_zh(school)}伤害。"

    match = re.fullmatch(r"Causes ([\d.]+) (\w+) damage to attacker on hit\. This damage causes no threat\. ([\d.]+) charges?\.?", raw)
    if match:
        amount, school, charges = match.groups()
        return f"被击中时对攻击者造成 {amount} 点{school_zh(school)}伤害。该伤害不产生威胁值。{charges} 次充能。"

    match = re.fullmatch(r"Absorbs ([\d.]+) damage\.?", raw)
    if match:
        return f"吸收 {match.group(1)} 点伤害。"
    if raw == "Absorbs damage.":
        return "吸收伤害。"
    if raw == "Absorbs all damage.":
        return "吸收所有伤害。"
    match = re.fullmatch(r"Absorbs (\w+) damage\.?", raw)
    if match:
        return f"吸收{school_zh(match.group(1))}伤害。"
    if raw == "Absorbs damage, draining mana instead.":
        return "吸收伤害，改为消耗法力值。"

    match = re.fullmatch(r"Movement (?:speed )?(?:slowed|reduced) by (-?[\d.]+)%\.?", raw)
    if match:
        return f"移动速度降低 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Movement speed increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"移动速度提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Time between attacks increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"攻击间隔延长 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Attack speed increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"攻击速度提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Melee and ranged attack speed reduced by (-?[\d.]+)%\.?", raw)
    if match:
        return f"近战和远程攻击速度降低 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Melee attack speed slowed by (-?[\d.]+)%\.?", raw)
    if match:
        return f"近战攻击速度降低 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Casting and melee speed increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"施法和近战速度提高 {abs_num(match.group(1))}%。"

    if raw == "Increases speed depending on your Riding Skill.":
        return "根据你的骑术提高移动速度。"
    if raw == "Cannot attack or cast spells. Increased regeneration.":
        return "无法攻击或施法，生命恢复速度提高。"
    if raw == "Cannot stealth or turn invisible.":
        return "无法潜行或隐形。"
    if raw == "Melee attacks have a chance to deal additional Holy damage.":
        return "近战攻击有几率造成额外神圣伤害。"
    if raw == "Melee damage you take has a chance to entangle the enemy.":
        return "你受到近战伤害时，有几率缠绕敌人。"
    if raw == "The next damaging melee attack against you will damage and weaken the target.":
        return "下一次对你造成伤害的近战攻击会伤害并虚弱目标。"
    if raw == "Underwater Breathing.":
        return "水下呼吸。"
    if raw == "All bleed effects and Shred cause additional damage.":
        return "所有流血效果和撕碎造成额外伤害。"

    match = re.fullmatch(r"All bleed effects and Shred cause ([\d.]+)% additional damage\.?", raw)
    if match:
        return f"所有流血效果和撕碎造成的伤害提高 {match.group(1)}%。"
    match = re.fullmatch(r"Reduces threat caused by ([\d.]+)%\.?", raw)
    if match:
        return f"造成的威胁值降低 {match.group(1)}%。"
    match = re.fullmatch(r"Extra (-?[\d.]+) damage on your next Physical attack\.?", raw)
    if match:
        return f"你的下一次物理攻击额外造成 {abs_num(match.group(1))} 点伤害。"
    match = re.fullmatch(r"Offensive ability damage increased by (-?[\d.]+)%\.?", raw)
    if match:
        return f"攻击性技能伤害提高 {abs_num(match.group(1))}%。"
    match = re.fullmatch(r"Your attacks have an additional (-?[\d.]+)% chance to apply poisons\.?", raw)
    if match:
        return f"你的攻击额外有 {abs_num(match.group(1))}% 几率施加毒药。"
    match = re.fullmatch(r"Anti-magic energy will burn (-?[\d.]+) of the attacker's Mana, causing (-?[\d.]+) Shadow damage for each point of Mana burned\.?", raw)
    if match:
        mana, damage = match.groups()
        return f"反魔法能量会燃烧攻击者 {abs_num(mana)} 点法力值，每燃烧 1 点法力值造成 {abs_num(damage)} 点暗影伤害。"
    match = re.fullmatch(r"Damage reduced by (-?[\d.]+)% and time between attacks increased by (-?[\d.]+)%\.?", raw)
    if match:
        reduced, speed = match.groups()
        return f"受到的伤害降低 {abs_num(reduced)}%，攻击间隔延长 {abs_num(speed)}%。"
    match = re.fullmatch(r"Increases total Strength and Agility by (-?[\d.]+)\.?", raw)
    if match:
        return f"力量和敏捷总值提高 {abs_num(match.group(1))} 点。"
    match = re.fullmatch(r"Increases your total Strength and Agility by (-?[\d.]+)\.?", raw)
    if match:
        return f"你的力量和敏捷总值提高 {abs_num(match.group(1))} 点。"
    match = re.fullmatch(r"Increases (\w+) resistance by (-?[\d.]+) and causes (-?[\d.]+) (\w+) damage to attacker when struck\.?", raw)
    if match:
        resist, resist_amount, damage, school = match.groups()
        return f"{school_zh(resist)}抗性提高 {abs_num(resist_amount)} 点，被击中时对攻击者造成 {abs_num(damage)} 点{school_zh(school)}伤害。"
    match = re.fullmatch(r"Taking (-?[\d.]+) damage and dealing (-?[\d.]+) damage to up to (-?[\d.]+) nearby allies every (-?[\d.]+) ?(?:sec\.?|seconds?)\.?", raw)
    if match:
        taken, dealt, targets, tick = match.groups()
        return f"每 {abs_num(tick)} 秒受到 {abs_num(taken)} 点伤害，并对附近最多 {abs_num(targets)} 名盟友造成 {abs_num(dealt)} 点伤害。"
    match = re.fullmatch(r"Damage taken reduced by up to ([\d.]+) and blocked melee attacks cause ([\d.]+) (\w+) damage to the attacker\.?", raw)
    if match:
        reduced, amount, school = match.groups()
        return f"受到的伤害最多降低 {reduced} 点，格挡近战攻击时对攻击者造成 {amount} 点{school_zh(school)}伤害。"
    return ""


def translate_tooltip(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    resolved = resolve_tokens(text, rec, records)
    out = []
    for raw_line in resolved.split("\n"):
        pieces = re.split(r"(?<=\.)\s+(?=[A-Z0-9])", raw_line.strip())
        translated_pieces = []
        for piece in pieces:
            translated = translate_single_line(piece)
            if translated:
                translated_pieces.append(translated)
            elif CJK_RE.search(piece) and not ASCII_WORD_RE.search(piece) and "$" not in piece:
                translated_pieces.append(punct(piece))
            else:
                return ""
        out.append("".join(translated_pieces))
    result = "\n".join(line for line in out if line)
    result = punct(result)
    if "$" in result or ASCII_WORD_RE.search(result):
        return ""
    return result


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


def should_replace(value: str) -> bool:
    if not value:
        return True
    return "$" in value or bool(ASCII_WORD_RE.search(value)) or "降低 -" in value or "提高 -" in value


def process(path: Path, records: dict[int, SpellRec]) -> tuple[int, int]:
    fields, rows = read_tsv(path)
    changed = 0
    translated = 0
    for row in rows:
        tip_en = row.get("tooltip_en", "")
        if not tip_en:
            continue
        rec = records.get(int(row["spell_id"]))
        if not rec:
            continue
        tip = translate_tooltip(tip_en, rec, records)
        if not tip:
            continue
        translated += 1
        if should_replace(row.get("tooltip_zh", "")) and row.get("tooltip_zh", "") != tip:
            row["tooltip_zh"] = tip
            changed += 1
    write_tsv(path, fields, rows)
    return changed, translated


def main() -> None:
    records = load_spell_dbc()
    for path in (PRIORITY, FULL):
        changed, translated = process(path, records)
        print(f"{path.name}: changed {changed}, translated patterns {translated}")


if __name__ == "__main__":
    main()
