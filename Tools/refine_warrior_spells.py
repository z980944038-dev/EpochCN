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

WARRIOR_SKILLS = {"26", "256", "257"}

NAME_ZH = {
    "Anger Management": "愤怒掌控",
    "Anticipation": "预知",
    "Armored to the Teeth": "全副武装",
    "Battle Shout": "战斗怒吼",
    "Battle Stance": "战斗姿态",
    "Battle Stance Passive": "战斗姿态被动",
    "Berserker Rage": "狂暴之怒",
    "Berserker Stance": "狂暴姿态",
    "Berserker Stance Passive": "狂暴姿态被动",
    "Bladestorm": "剑刃风暴",
    "Blood Craze": "血之狂热",
    "Blood Frenzy": "血之狂乱",
    "Bloodrage": "血性狂暴",
    "Bloodsurge": "血涌",
    "Bloodthirst": "嗜血",
    "Booming Voice": "震耳嗓音",
    "Challenging Shout": "挑战怒吼",
    "Charge": "冲锋",
    "Charge Rage Bonus Effect": "冲锋怒气奖励效果",
    "Cleave": "顺劈斩",
    "Commanding Presence": "统御之力",
    "Commanding Shout": "命令怒吼",
    "Concussion Blow": "震荡猛击",
    "Critical Block": "精确格挡",
    "Cruelty": "残忍",
    "Damage Shield": "伤害护盾",
    "Death Wish": "死亡之愿",
    "Deep Wounds": "重伤",
    "Defensive Stance": "防御姿态",
    "Defensive Stance Passive": "防御姿态被动",
    "Defiance": "挑衅",
    "Defiance Expertise Passive (DND)": "挑衅精准被动",
    "Deflection": "偏斜",
    "Demoralizing Shout": "挫志怒吼",
    "Devastate": "毁灭打击",
    "Disarm": "缴械",
    "Dual Wield Specialization": "双武器专精",
    "Endless Rage": "无尽怒气",
    "Enrage": "激怒",
    "Enraged Regeneration": "狂怒回复",
    "Execute": "斩杀",
    "Flurry": "乱舞",
    "Focused Rage": "怒火专注",
    "Furious Attacks": "狂怒攻击",
    "Hamstring": "断筋",
    "Heroic Fury": "英勇之怒",
    "Heroic Strike": "英勇打击",
    "Heroic Throw": "英勇投掷",
    "Impale": "穿刺",
    "Improved Berserker Rage": "强化狂暴之怒",
    "Improved Berserker Stance": "强化狂暴姿态",
    "Improved Bloodrage": "强化血性狂暴",
    "Improved Challenging Shout": "强化挑战怒吼",
    "Improved Charge": "强化冲锋",
    "Improved Cleave": "强化顺劈斩",
    "Improved Defensive Stance": "强化防御姿态",
    "Improved Demoralizing Shout": "强化挫志怒吼",
    "Improved Disarm": "强化缴械",
    "Improved Disciplines": "强化戒律",
    "Improved Execute": "强化斩杀",
    "Improved Hamstring": "强化断筋",
    "Improved Heroic Strike": "强化英勇打击",
    "Improved Intercept": "强化拦截",
    "Improved Intimidating Shout": "强化破胆怒吼",
    "Improved Mortal Strike": "强化致死打击",
    "Improved Overpower": "强化压制",
    "Improved Rend": "强化撕裂",
    "Improved Revenge": "强化复仇",
    "Improved Shield Bash": "强化盾击",
    "Improved Shield Block": "强化盾牌格挡",
    "Improved Shield Wall": "强化盾墙",
    "Improved Slam": "强化猛击",
    "Improved Spell Reflection": "强化法术反射",
    "Improved Sunder Armor": "强化破甲攻击",
    "Improved Taunt": "强化嘲讽",
    "Improved Thunder Clap": "强化雷霆一击",
    "Improved Whirlwind": "强化旋风斩",
    "Incite": "煽动",
    "Intensify Rage": "激怒强化",
    "Intercept": "拦截",
    "Intervene": "援护",
    "Intimidating Shout": "破胆怒吼",
    "Iron Will": "钢铁意志",
    "Juggernaut": "主宰",
    "Last Stand": "破釜沉舟",
    "Long Daze": "长时间眩晕",
    "Mace Specialization": "锤类武器专精",
    "Mace Stun Effect": "锤击昏迷效果",
    "Mocking Blow": "惩戒痛击",
    "Mortal Strike": "致死打击",
    "One-Handed Weapon Specialization": "单手武器专精",
    "Overpower": "压制",
    "Piercing Howl": "刺耳怒吼",
    "Poleaxe Specialization": "长柄武器专精",
    "Precision": "精准",
    "Pummel": "拳击",
    "Rampage": "暴怒",
    "Recklessness": "鲁莽",
    "Rend": "撕裂",
    "Retaliation": "反击风暴",
    "Revenge": "复仇",
    "Revenge Stun": "复仇昏迷",
    "Safeguard": "捍卫",
    "Second Wind": "复苏之风",
    "Shattering Throw": "碎裂投掷",
    "Shield Bash": "盾击",
    "Shield Bash - Silenced": "盾击 - 沉默",
    "Shield Block": "盾牌格挡",
    "Shield Mastery": "盾牌掌握",
    "Shield Slam": "盾牌猛击",
    "Shield Specialization": "盾牌专精",
    "Shield Wall": "盾墙",
    "Shockwave": "震荡波",
    "Single-Minded Fury": "专一狂怒",
    "Slam": "猛击",
    "Slam!": "猛击！",
    "Spell Reflection": "法术反射",
    "Stance Mastery": "姿态掌握",
    "Strength of Arms": "武装到牙齿",
    "Strike": "打击",
    "Sunder Armor": "破甲攻击",
    "Sweeping Strikes": "横扫攻击",
    "Sword Specialization": "剑类武器专精",
    "Sword and Board": "剑盾猛攻",
    "Tactical Mastery": "战术掌握",
    "Taste for Blood": "血之气息",
    "Taunt": "嘲讽",
    "Thunder Clap": "雷霆一击",
    "Titan's Grip": "泰坦之握",
    "Toughness": "坚韧",
    "Trauma": "创伤",
    "Two-Handed Weapon Specialization": "双手武器专精",
    "Unbridled Wrath": "怒不可遏",
    "Unending Fury": "无尽狂怒",
    "Unrelenting Assault": "冷酷突击",
    "Victory Rush": "乘胜追击",
    "Vigilance": "警戒",
    "Vitality": "活力",
    "Warbringer": "战神",
    "Weapon Mastery": "武器掌握",
    "Whirlwind": "旋风斩",
    "Wrecking Crew": "破坏能手",
}

TERM_FIXES = [
    ("Heroic Strike", "英勇打击"),
    ("Battle Shout", "战斗怒吼"),
    ("Demoralizing Shout", "挫志怒吼"),
    ("Commanding Shout", "命令怒吼"),
    ("Bloodrage", "血性狂暴"),
    ("Berserker Rage", "狂暴之怒"),
    ("Recklessness", "鲁莽"),
    ("Bloodthirst", "嗜血"),
    ("Mortal Strike", "致死打击"),
    ("Defensive Stance", "防御姿态"),
    ("Shield Bash", "盾击"),
    ("Shield Wall", "盾墙"),
    ("Sunder Armor", "破甲攻击"),
    ("Thunder Clap", "雷霆一击"),
    ("Intimidating Shout", "破胆怒吼"),
    ("Challenging Shout", "挑战怒吼"),
    ("Sweeping Strikes", "横扫攻击"),
    ("Hamstring", "断筋"),
    ("Overpower", "压制"),
    ("Rend", "撕裂"),
    ("Cleave", "顺劈斩"),
    ("Intercept", "拦截"),
    ("Whirlwind", "旋风斩"),
    ("Slam", "猛击"),
    ("Revenge", "复仇"),
    ("Taunt", "嘲讽"),
    ("Disarm", "缴械"),
    ("Charge", "冲锋"),
    ("Shield Block", "盾牌格挡"),
    ("damage", "伤害"),
    ("Damage", "伤害"),
    ("rage", "怒气"),
    ("Rage", "怒气"),
    ("Attack Power", "攻击强度"),
    ("attack power", "攻击强度"),
    ("critical strike", "暴击"),
    ("Critical Strike", "暴击"),
    ("critical", "暴击"),
    ("Crit", "暴击"),
    ("threat", "威胁值"),
    ("Threat", "威胁值"),
    ("cooldown", "冷却时间"),
    ("Cooldown", "冷却时间"),
    ("ability", "技能"),
    ("abilities", "技能"),
    ("bleed", "流血"),
    ("Bleed", "流血"),
    ("Stunned.", "昏迷。"),
    ("Silenced.", "沉默。"),
    ("Taunted.", "被嘲讽。"),
    ("Dazed.", "眩晕。"),
    ("Disarmed!", "被缴械！"),
    ("攻击强度强度", "攻击强度"),
    ("你的的", "你的"),
    ("呐喊", "怒吼"),
    ("爆击", "暴击"),
    ("个人成员", "小队成员"),
]

DURATION_BY_ID = {
    5530: "3秒",
    7922: "1秒",
    12721: "6秒",
    12798: "5秒",
    12880: "12秒",
    12976: "20秒",
    14201: "12秒",
    14202: "12秒",
    14203: "12秒",
    14204: "12秒",
    16488: "6秒",
    16490: "6秒",
    16491: "6秒",
    18498: "3秒",
    23694: "5秒",
    29131: "10秒",
    30029: "30秒",
    30031: "30秒",
    30032: "30秒",
    29841: "10秒",
    29842: "10秒",
    32216: "20秒",
    46856: "1分钟",
    46857: "1分钟",
    46946: "6秒",
    46947: "6秒",
    46916: "5秒",
    57518: "12秒",
    57519: "12秒",
    57520: "12秒",
    57521: "12秒",
    57522: "12秒",
    60503: "9秒",
    56112: "10秒",
    64382: "10秒",
    65156: "10秒",
    150069: "6秒",
}

DURATION_BY_NAME = {
    "Battle Shout": "2分钟",
    "Commanding Shout": "2分钟",
    "Demoralizing Shout": "30秒",
    "Thunder Clap": "30秒",
    "Hamstring": "15秒",
    "Rend": "15秒",
    "Sunder Armor": "30秒",
    "Shield Bash": "6秒",
    "Pummel": "4秒",
    "Shield Block": "10秒",
    "Disarm": "10秒",
    "Shield Wall": "12秒",
    "Retaliation": "12秒",
    "Berserker Rage": "10秒",
    "Recklessness": "12秒",
    "Death Wish": "30秒",
    "Mortal Strike": "10秒",
    "Bloodthirst": "8秒",
    "Rampage": "30秒",
    "Bladestorm": "6秒",
    "Shockwave": "4秒",
    "Spell Reflection": "5秒",
    "Enraged Regeneration": "10秒",
    "Concussion Blow": "5秒",
    "Challenging Shout": "6秒",
    "Mocking Blow": "6秒",
    "Intimidating Shout": "8秒",
    "Piercing Howl": "6秒",
    "Vigilance": "持续30分钟",
}

RADIUS_BY_NAME = {
    "Battle Shout": 30,
    "Commanding Shout": 30,
    "Demoralizing Shout": 10,
    "Thunder Clap": 8,
    "Challenging Shout": 10,
    "Intimidating Shout": 8,
    "Piercing Howl": 10,
    "Whirlwind": 8,
    "Bladestorm": 8,
    "Shockwave": 10,
}

SPECIAL_N = {
    12880: 12,
    14201: 12,
    14202: 12,
    14203: 12,
    14204: 12,
    23885: 5,
    23886: 5,
    23887: 5,
    23888: 5,
    25252: 5,
    30339: 5,
    1680: 4,
    5246: 5,
    6343: 4,
    8198: 4,
    8204: 4,
    8205: 4,
    11580: 4,
    11581: 4,
    25264: 4,
    47501: 4,
    47502: 4,
    2565: 1,
    20230: 20,
    50622: 4,
}

FORCE_GENERIC = {
    "Armored to the Teeth",
    "Execute",
    "Heroic Strike",
    "Heroic Throw",
    "Improved Mortal Strike",
    "Intensify Rage",
    "Intimidating Shout",
    "Rampage",
    "Revenge",
    "Safeguard",
    "Second Wind",
    "Sword and Board",
    "Taste for Blood",
    "Thunder Clap",
    "Trauma",
    "Unrelenting Assault",
    "Vigilance",
    "Whirlwind",
    "Wrecking Crew",
}

CJK_RE = re.compile(r"[\u3400-\u9fff]")


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


def rank_zh(rank: str) -> str:
    if not rank:
        return ""
    match = re.fullmatch(r"Rank (\d+)", rank)
    if match:
        return f"等级 {match.group(1)}"
    if rank == "Passive":
        return "被动"
    return rank.replace("Rank", "等级").replace("Passive", "被动")


def duration(rec: SpellRec) -> str:
    return DURATION_BY_ID.get(rec.id) or DURATION_BY_NAME.get(rec.name) or ""


def radius(rec: SpellRec, index: int) -> str:
    if rec.name == "Intimidating Shout" and index == 2:
        return "8"
    return str(RADIUS_BY_NAME.get(rec.name, 0) or 0)


def over_time(rec: SpellRec, n: int, source_text: str) -> str:
    if rec.id in (16488, 16490, 16491):
        return str(rec.s(n) * 6)
    if rec.name == "Enraged Regeneration":
        return str(rec.s(n) * 10)
    if rec.name == "Bloodrage":
        return str(rec.s(n) * 10)
    if rec.name == "Rend":
        match = re.search(r"0\.00743\*(\d+)|0\.2\*(\d+)", source_text)
        ticks = int(match.group(1) or match.group(2)) if match else 5
        return str(rec.s(n) * ticks)
    seconds = rec.amp_sec(n)
    dur = duration(rec)
    match = re.search(r"(\d+)", dur)
    if seconds and match:
        return str(rec.s(n) * int(match.group(1)) // seconds)
    return str(rec.s(n))


def replace_formulas(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    text = re.sub(
        r"\$\{\$AP\*\$m(\d+)/100\}",
        lambda m: f"相当于攻击强度的 {rec.s(int(m.group(1)))}%",
        text,
    )
    text = re.sub(
        r"\$\{\$m(\d+)/100\*\$AP\}",
        lambda m: f"相当于攻击强度的 {rec.s(int(m.group(1)))}%",
        text,
    )
    text = re.sub(
        r"\$\{\$m(\d+)/1000\}",
        lambda m: str(int(rec.s(int(m.group(1))) / 1000)),
        text,
    )
    text = re.sub(
        r"\$\{0\.00743\*\d+\*\(\(\$MWB\+\$mwb\)/2\+\$AP/14\*\$MWS\)\}",
        "基于武器伤害和攻击强度计算的额外伤害",
        text,
    )
    text = re.sub(
        r"\$\{0\.2\*5\*\(\(\$MWB\+\$mwb\)/2\+\$AP/14\*\$MWS\)\}",
        "基于武器伤害和攻击强度计算的额外伤害",
        text,
    )
    text = text.replace(
        "${$64382m1+$AP*.50}",
        f"{records[64382].s(1)}点加攻击强度50%",
    )
    text = re.sub(r"\$\{[^{}]*\}", "基于属性计算的数值", text)
    return text


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    source_text = text
    text = text.replace("\\n", "\n")
    text = replace_formulas(text, rec, records)
    text = re.sub(r"\$l([^:;]*):([^;]*);", lambda m: m.group(1) or m.group(2) or "", text)
    text = text.replace("$<threat>", "10")

    def ref_value(spell_id: int, token: str, number: str = "") -> str:
        target = records.get(spell_id)
        if not target:
            return ""
        index = int(number or "1")
        if token in ("s", "m"):
            return str(target.s(index))
        if token == "o":
            return over_time(target, index, source_text)
        if token == "d":
            return duration(target)
        if token == "t":
            return str(target.amp_sec(index) or 1)
        if token == "a":
            return radius(target, index)
        if token in ("n", "i"):
            return str(SPECIAL_N.get(spell_id, target.stack() or target.s(index)))
        if token == "u":
            return str(target.stack() or SPECIAL_N.get(spell_id, target.s(index)))
        return ""

    text = re.sub(
        r"\$/(\d+);(\d+)([somdtauni])(\d*)",
        lambda m: str(int(int(ref_value(int(m.group(2)), m.group(3), m.group(4)) or 0) / int(m.group(1)))),
        text,
    )
    text = re.sub(
        r"\$/(\d+);([somdtauni])(\d*)",
        lambda m: str(int(int(ref_value(rec.id, m.group(2), m.group(3)) or 0) / int(m.group(1)))),
        text,
    )
    text = re.sub(
        r"\$([0-9]+)([somdtauni])(\d*)",
        lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3)),
        text,
    )
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text)
    text = re.sub(r"\$o(\d*)", lambda m: over_time(rec, int(m.group(1) or "1"), source_text), text)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text)
    text = re.sub(r"\$a(\d*)", lambda m: radius(rec, int(m.group(1) or "1")), text)
    text = text.replace("$d", duration(rec))
    text = text.replace("$h", str(rec.h()))
    text = re.sub(r"\$n", lambda _: str(SPECIAL_N.get(rec.id, rec.stack() or 1)), text)
    text = re.sub(r"\$i", lambda _: str(SPECIAL_N.get(rec.id, rec.stack() or 1)), text)
    text = re.sub(r"\$u", lambda _: str(rec.stack() or SPECIAL_N.get(rec.id, 1)), text)
    text = re.sub(r"\$[A-Za-z_]+[0-9]*", "", text)
    text = text.replace("$", "")
    text = re.sub(r"(\d+)\.0\b", r"\1", text)
    return cleanup(text)


def cleanup(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for old, new in TERM_FIXES:
        text = text.replace(old, new)
    text = text.replace("降低-", "降低")
    text = text.replace("减少-", "减少")
    text = text.replace("延长-", "延长")
    text = text.replace("缩短-", "缩短")
    text = text.replace("提高-", "降低")
    text = text.replace("持续持续", "持续")
    text = text.replace("有一定几率", "有几率")
    text = re.sub(r"([0-9]+%)点伤害", r"\1伤害", text)
    text = re.sub(r"攻击强度([0-9]+%)伤害", r"攻击强度\1的伤害", text)
    text = re.sub(
        r"外加(基于武器伤害和攻击强度计算的额外伤害)点额外伤害（基于武器伤害）",
        r"，另附加\1",
        text,
    )
    text = re.sub(r" +([，。；：、])", r"\1", text)
    text = re.sub(r"([（(]) +", r"\1", text)
    text = re.sub(r" +([）)])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    return text.strip()


def generic_desc(row: dict[str, str], rec: SpellRec, records: dict[int, SpellRec]) -> str:
    name = row["name_en"]
    desc = resolve_tokens(row.get("description_zh") or row.get("description_en") or rec.desc, rec, records)
    if name not in FORCE_GENERIC and CJK_RE.search(desc) and not re.search(r"[A-Za-z]{3,}", desc):
        return desc

    nzh = NAME_ZH.get(name, name)
    if name == "Defiance Expertise Passive (DND)":
        return "挑衅精准被动。"
    if name == "Battle Shout":
        return f"战士发出怒吼，使 30 码范围内所有小队和团队成员的攻击强度提高 {rec.s(1)} 点，持续 2 分钟。"
    if name == "Commanding Shout":
        return f"使 30 码范围内所有小队和团队成员的最大生命值提高 {rec.s(1)} 点，持续 2 分钟。"
    if name == "Demoralizing Shout":
        return f"使 10 码范围内所有敌人的近战攻击强度降低 {abs(rec.s(1))} 点，持续 30 秒。"
    if name == "Heroic Strike":
        dazed = ""
        if "Dazed targets" in (row.get("description_en") or rec.desc):
            dazed = f"对处于眩晕状态的目标额外造成 {int(rec.s(1) * 0.35)} 点伤害。"
        return f"一次强力攻击，使近战伤害提高 {rec.s(1)} 点，并产生大量威胁值。{dazed}"
    if name == "Execute":
        base = f"{rec.s(1)} 点"
        if "$AP*0.2" in (row.get("description_en") or rec.desc):
            base = f"{rec.s(1)} 点加攻击强度 20%"
        return f"尝试终结一个生命值低于 20% 的敌人，造成 {base} 伤害，并将每点额外怒气转化为 10 点额外伤害，最多消耗 30 点额外怒气。"
    if name == "Heroic Throw":
        return f"向敌人投掷武器，造成 {rec.s(1)} 点加攻击强度 50% 的伤害，并产生大量威胁值。"
    if name == "Rend":
        return f"撕裂目标，在 15 秒内造成 {over_time(rec, 1, row.get('description_en', ''))} 点流血伤害，并附加基于武器伤害和攻击强度计算的额外伤害。"
    if name == "Charge":
        return f"向敌人冲锋，产生 {rec.s(2) // 10} 点怒气，并使其昏迷 1 秒。不能在战斗中使用。"
    if name == "Thunder Clap":
        return f"震击附近敌人，造成 {rec.s(1)} 点伤害，并使其攻击间隔延长 {abs(rec.s(2))}%，持续 30 秒。该技能会产生额外威胁值，最多影响 {SPECIAL_N.get(rec.id, 4)} 个目标。"
    if name == "Overpower":
        return f"立即压制敌人，造成武器伤害再加 {rec.s(1)} 点伤害。只能在目标躲闪后使用。压制无法被格挡、躲闪或招架。"
    if name == "Sunder Armor":
        return f"破开目标的护甲，每层破甲效果使其护甲降低 {abs(rec.s(1))} 点，并产生大量威胁值。最多可叠加 5 次，持续 30 秒。"
    if name == "Revenge":
        if "$AP*0.310" in (row.get("description_en") or rec.desc):
            return f"立即反击敌人，造成 {rec.s(1)} 点加攻击强度 31% 的伤害。复仇只能在战士格挡、躲闪或招架一次攻击后使用。"
        return f"立即反击敌人，造成 {rec.s(1)} 点伤害并产生大量威胁值。复仇必须在格挡、躲闪或招架后使用。"
    if name == "Slam":
        return f"猛击敌人，造成武器伤害再加 {rec.s(1)} 点伤害。"
    if name == "Cleave":
        return f"横扫攻击，对目标及其最近的一个盟友造成武器伤害再加 {rec.s(1)} 点伤害。"
    if name == "Improved Challenging Shout":
        return f"使你的挑战怒吼冷却时间缩短 {abs(rec.s(1)) // 60} 分钟。"
    if name == "Stance Mastery":
        return f"切换姿态时保留最多 {rec.s(1)} 点怒气。"
    if name == "Sweeping Strikes":
        return "你的下一次近战武器攻击会击中附近的一个额外敌人。"
    if name == "Revenge Stun":
        return "使目标昏迷 5 秒。"
    if name == "Last Stand":
        return "激活后暂时使你的最大生命值提高 30%，持续 20 秒。效果结束后，临时生命值会被移除。"
    if name == "Berserker Rage":
        return "战士进入狂暴之怒，免疫恐惧、闷棍和瘫痪效果，并在受到伤害时产生额外怒气，持续 10 秒。"
    if name == "Mortal Strike":
        return f"一次凶狠的攻击，造成武器伤害再加 {rec.s(2)} 点伤害，并使目标受伤，受到的治疗效果降低 {abs(rec.s(1))}%，持续 10 秒。"
    if name == "Devastate":
        return f"破甲目标，造成破甲效果，并造成 50% 武器伤害再加 {rec.s(2)} 点额外伤害。目标身上的每层破甲效果都会提高该技能伤害。破甲效果最多可叠加 5 次。"
    if name == "Tactical Mastery":
        return f"切换姿态时额外保留最多 {rec.s(1)} 点怒气。在防御姿态下，嗜血和致死打击产生的威胁值大幅提高。"
    if name == "Anger Management":
        return "战斗中每 3 秒获得 1 点怒气。"
    if name == "Improved Heroic Strike":
        return f"使你的英勇打击消耗的怒气值降低 {max(1, rec.s(1) // 10)} 点。"
    if name == "Improved Charge":
        return f"使你的冲锋产生的怒气值提高 {max(1, rec.s(1) // 10)} 点。"
    if name == "Improved Rend":
        return f"使你的撕裂技能造成的流血伤害提高 {rec.s(1)}%。"
    if name == "Deflection":
        return f"使你的招架几率提高 {rec.s(1)}%。"
    if name == "Improved Overpower":
        return f"使你的压制技能的暴击几率提高 {rec.s(1)}%。"
    if name in ("Cruelty", "Precision"):
        return f"使你的{'近战和远程武器的命中几率' if name == 'Precision' else '近战暴击几率'}提高 {rec.s(1)}%。"
    if name == "Booming Voice":
        return f"使你的战斗怒吼、挫志怒吼和命令怒吼的作用范围与持续时间提高 {rec.s(1)}%。"
    if name == "Commanding Presence":
        return f"使你的战斗怒吼提供的攻击强度和命令怒吼提供的生命值提高 {rec.s(1)}%。"
    if name == "Unbridled Wrath":
        return f"你的近战攻击有几率额外产生 {max(1, rec.s(1) // 10)} 点怒气。"
    if name == "Improved Demoralizing Shout":
        return f"使你的挫志怒吼降低敌人近战攻击强度的效果提高 {rec.s(1)}%。"
    if name == "Improved Cleave":
        return f"使你的顺劈斩的额外伤害提高 {rec.s(1)}%。"
    if name == "Improved Execute":
        return f"使你的斩杀消耗的怒气值降低 {max(1, rec.s(1) // 10)} 点。"
    if name == "Improved Mortal Strike":
        seconds = abs(rec.s(1)) / 1000
        seconds_text = f"{seconds:g}"
        return f"使你的致死打击冷却时间缩短 {seconds_text} 秒，并使其造成的伤害提高 {rec.s(2)}%。"
    if name in ("Two-Handed Weapon Specialization", "One-Handed Weapon Specialization", "Dual Wield Specialization"):
        return f"使你使用对应武器造成的伤害提高 {rec.s(1)}%。"
    if name in ("Sword Specialization", "Mace Specialization", "Poleaxe Specialization"):
        return resolve_tokens(row.get("description_en") or rec.desc, rec, records)
    if name == "Flurry":
        return f"你的近战暴击之后，下 3 次近战攻击速度提高 {rec.s(1)}%。"
    if name == "Enrage":
        return f"你受到暴击后获得 {rec.s(1)}% 近战伤害加成，持续 12 秒，最多影响 12 次攻击。"
    if name == "Blood Craze":
        return f"你受到暴击后，在 6 秒内恢复总生命值的 {rec.s(1) * 6}%。"
    if name == "Bloodsurge":
        return f"你的英勇打击、嗜血和旋风斩命中时有 {rec.h()}% 的几率使下一个猛击在 5 秒内变为瞬发。"
    if name == "Furious Attacks":
        return f"你的普通近战攻击有几率使目标受到的所有治疗效果降低 {abs(records[56112].s(1))}%，持续 10 秒。该效果最多叠加 {records[56112].stack()} 次。"
    if name == "Rampage":
        rank = int((row.get("rank_en") or "Rank 1").split()[-1])
        ap = {1: 30, 2: records[30031].s(1), 3: records[30032].s(1)}.get(rank, rec.s(1))
        return f"战士进入暴怒状态，攻击强度提高 {ap} 点，且大多数成功的近战攻击会使攻击强度额外提高 {ap} 点。此效果最多叠加 5 次，持续 30 秒。此技能只能在造成暴击后使用。"
    if name == "Second Wind":
        tick_rage = max(1, rec.s(1) // 10)
        total_rage = tick_rage * 5
        total_health = rec.s(2) * 5
        return f"每当你受到昏迷或定身效果影响时，你会在 10 秒内获得 {total_rage} 点怒气，并恢复相当于总生命值 {total_health}% 的生命值。"
    if name == "Trauma":
        effect_id = 46856 if row.get("rank_en") == "Rank 1" else 46857
        return f"你的近战暴击使目标受到的流血效果提高 {records[effect_id].s(1)}%，持续 1 分钟。"
    if name == "Unrelenting Assault":
        damage_bonus = rec.s(2) if rec.s(2) > 0 else rec.s(3)
        reduction = 25 if row.get("rank_en") == "Rank 1" else 50
        return f"使你的压制和复仇冷却时间缩短 {abs(rec.s(1)) // 1000} 秒，且这两个技能造成的伤害提高 {damage_bonus}%。此外，如果你在玩家施法时对其使用压制，则其造成的魔法伤害和治疗效果降低 {reduction}%，持续 6 秒。"
    if name == "Wrecking Crew":
        effect_id = {1: 57518, 2: 57519, 3: 57520, 4: 57521, 5: 57522}.get(int((row.get("rank_en") or "Rank 1").split()[-1]), 57518)
        return f"你的近战暴击会使你进入激怒状态，造成的所有伤害提高 {records[effect_id].s(1)}%，持续 12 秒。此效果不与激怒叠加。"
    if name == "Intensify Rage":
        return f"使你的血性狂暴、狂暴之怒、鲁莽和死亡之愿冷却时间缩短 {abs(rec.s(1))}%。"
    if name == "Safeguard":
        effect_id = 46946 if row.get("rank_en") == "Rank 1" else 46947
        return f"使你援护目标受到的伤害降低 {abs(records[effect_id].s(1))}%，持续 6 秒。"
    if name == "Sword and Board":
        return f"使你的毁灭打击暴击几率提高 {rec.s(2)}%。当你的毁灭打击或复仇造成伤害时，有 {rec.h()}% 的几率刷新盾牌猛击的冷却时间，并使其在 5 秒内消耗降低 100%。"
    if name == "Taste for Blood":
        return f"每当你的撕裂造成伤害时，你有 {rec.h()}% 的几率在 9 秒内可以使用压制。1 次充能。该效果每 6 秒最多触发一次。"
    if name == "Vigilance":
        return f"将保护性目光集中在一个小队或团队成员身上，使其受到的伤害降低 {abs(rec.s(1))}%，并将其产生威胁值的 10% 转移给你。此外，该目标每次受到攻击时，你的嘲讽冷却时间都会刷新。持续 30 分钟。同一时间只能对一个目标生效。"
    if name == "Whirlwind":
        return f"你化作钢铁旋风，攻击 8 码范围内最多 {SPECIAL_N[1680]} 个敌人，对每个敌人造成双手近战武器的武器伤害。"
    if name == "Intimidating Shout":
        return f"战士发出怒吼，使 8 码范围内的敌人因恐惧而畏缩。最多 {SPECIAL_N[5246]} 个附近敌人会因恐惧逃跑，持续 8 秒。"
    if name == "Armored to the Teeth":
        armor = rec.s(1) * rec.s(2)
        return f"你每拥有 {armor} 点护甲值，攻击强度就提高 {rec.s(2)} 点。"
    if name == "Single-Minded Fury":
        return f"双持武器时移动速度提高 {records[150070].s(1)}%。你的近战自动攻击连续命中同一目标时，攻击速度提高 {records[150069].s(1)}%，最多叠加 {records[150069].stack()} 次，持续 6 秒。"
    if name == "Juggernaut":
        return f"你的冲锋现在可以在战斗中使用，但冷却时间延长 {records[64976].s(3) // 1000} 秒。冲锋后 10 秒内，你的下一个猛击或致死打击的暴击几率提高 {records[65156].s(1)}%。"
    return desc if desc else f"{nzh}。"


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    if row["name_en"] not in FORCE_GENERIC and CJK_RE.search(rec.desc) and "$" not in rec.desc and not re.search(r"[A-Za-z]{3,}", rec.desc):
        return cleanup(rec.desc)
    return cleanup(generic_desc(row, rec, records))


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    if name == "Battle Shout":
        return f"攻击强度提高 {rec.s(1)} 点。"
    if name == "Commanding Shout":
        return f"最大生命值提高 {rec.s(1)} 点。"
    if name == "Demoralizing Shout":
        return f"近战攻击强度降低 {abs(rec.s(1))} 点。"
    if name == "Thunder Clap":
        return f"攻击间隔延长 {abs(rec.s(2))}%。"
    if name == "Sunder Armor":
        return f"护甲降低 {abs(rec.s(1))} 点。"
    if name == "Rend":
        return f"每 3 秒造成 {rec.s(1)} 点流血伤害，另受武器伤害和攻击强度加成。"
    if name == "Mortal Strike":
        return f"受到的治疗效果降低 {abs(rec.s(1))}%。"
    if name == "Flurry":
        return f"攻击速度提高 {rec.s(1)}%。"
    if name == "Last Stand":
        return "最大生命值提高 30%。"
    if name == "Berserker Rage":
        return "免疫恐惧、闷棍和瘫痪效果。受到伤害时产生额外怒气。"
    if name == "Devastate":
        return "破甲效果。"
    if name == "Rampage":
        return "大多数近战命中会提高战士的攻击强度。"
    if name == "Vigilance":
        return f"受到的伤害降低 {abs(rec.s(1))}%，产生威胁值的 10% 转移给战士。"
    source = row.get("tooltip_zh") or row.get("tooltip_en") or rec.aura
    if CJK_RE.search(rec.aura) and "$" not in rec.aura and not re.search(r"[A-Za-z]{3,}", rec.aura):
        return cleanup(rec.aura)
    return resolve_tokens(source, rec, records)


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


def is_warrior(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & WARRIOR_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_warrior(row):
            continue
        rec = records[int(row["spell_id"])]
        before = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        row["name_zh"] = NAME_ZH.get(row["name_en"], rec.name if CJK_RE.search(rec.name) else row.get("name_zh", ""))
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
        if is_warrior(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or re.search(r"[A-Za-z]{3,}", row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority warrior rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"warrior spell ids synced: {len(updates)}")
    print(f"warrior zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:20]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:160])


if __name__ == "__main__":
    main()
