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

WARLOCK_SKILLS = {"354", "355", "593"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")

NAME_ZH = {
    "Amplify Bane": "灾祸增效",
    "Aftermath": "清算",
    "Atrocity": "暴行",
    "Backdraft": "爆燃",
    "Backlash": "反冲",
    "Bane": "灾祸",
    "Bane of Agony": "痛苦灾祸",
    "Bane of Doom": "厄运灾祸",
    "Bane of Exhaustion": "疲劳灾祸",
    "Bane of Tongues": "语言灾祸",
    "Banish": "放逐术",
    "Cataclysm": "灾变",
    "Challenging Howl": "挑战嚎叫",
    "Chaos Bolt": "混乱之箭",
    "Chaos Bolt Passive": "混乱之箭被动",
    "Conflagrate": "燃烧",
    "Contagion": "传染",
    "Corruption": "腐蚀术",
    "Create Firestone": "制造火焰石",
    "Create Healthstone": "制造治疗石",
    "Create Soulstone": "制造灵魂石",
    "Create Soulwell": "制造灵魂之井",
    "Create Spellstone": "制造法术石",
    "Curse of Agony": "痛苦诅咒",
    "Curse of Doom Effect": "厄运诅咒效果",
    "Curse of Idiocy": "痴呆诅咒",
    "Curse of Recklessness": "鲁莽诅咒",
    "Curse of the Elements": "元素诅咒",
    "Curse of Tongues": "语言诅咒",
    "Curse of Weakness": "虚弱诅咒",
    "Dark Pact": "黑暗契约",
    "Death Coil": "死亡缠绕",
    "Death's Embrace": "死亡之拥",
    "Decimation": "灭杀",
    "Demon Armor": "恶魔护甲",
    "Demon Charge": "恶魔冲锋",
    "Demon Portal": "恶魔传送门",
    "Demon Skin": "恶魔皮肤",
    "Demonic Aegis": "恶魔庇护",
    "Demonic Circle: Summon": "恶魔法阵：召唤",
    "Demonic Circle: Teleport": "恶魔法阵：传送",
    "Demonic Empowerment": "恶魔增效",
    "Demonic Embrace": "恶魔之拥",
    "Demonic Immolate": "恶魔献祭",
    "Demonic Knowledge": "恶魔知识",
    "Demonic Pact": "恶魔契约",
    "Demonic Resilience": "恶魔韧性",
    "Demonic Sacrifice": "恶魔牺牲",
    "Demonic Tactics": "恶魔战术",
    "Destructive Reach": "毁灭延伸",
    "Detect Invisibility": "侦测隐形",
    "Devastation": "毁灭",
    "Drain Life": "吸取生命",
    "Drain Mana": "吸取法力",
    "Drain Soul": "吸取灵魂",
    "Emberstorm": "灰烬风暴",
    "Empowered Corruption": "腐蚀增效",
    "Empowered Imp": "小鬼增效",
    "Enslave Demon": "奴役恶魔",
    "Eradication": "根除",
    "Everlasting Affliction": "持久痛苦",
    "Eye of Kilrogg": "基尔罗格之眼",
    "Fear": "恐惧术",
    "Fel Armor": "邪甲术",
    "Fel Concentration": "恶魔专注",
    "Fel Domination": "恶魔支配",
    "Fel Intellect": "恶魔智力",
    "Fel Stamina": "恶魔耐力",
    "Fel Synergy": "恶魔协同",
    "Fire and Brimstone": "硫磺烈火",
    "Grim Reach": "无情延伸",
    "Haunt": "鬼影缠身",
    "Health Funnel": "生命通道",
    "Hellfire": "地狱烈焰",
    "Hellfire Effect": "地狱烈焰效果",
    "Howl of Terror": "恐惧嚎叫",
    "Immolate": "献祭",
    "Immolation": "献祭",
    "Immolation Aura": "献祭光环",
    "Improved Bane of Agony": "强化痛苦灾祸",
    "Improved Corruption": "强化腐蚀术",
    "Improved Curse of Weakness": "强化虚弱诅咒",
    "Improved Demonic Tactics": "强化恶魔战术",
    "Improved Drain Soul": "强化吸取灵魂",
    "Improved Enslave Demon": "强化奴役恶魔",
    "Improved Fear": "强化恐惧术",
    "Improved Felhunter": "强化地狱猎犬",
    "Improved Firebolt": "强化火焰箭",
    "Improved Health Funnel": "强化生命通道",
    "Improved Healthstone": "强化治疗石",
    "Improved Howl of Terror": "强化恐惧嚎叫",
    "Improved Immolate": "强化献祭",
    "Improved Imp": "强化小鬼",
    "Improved Lash of Pain": "强化剧痛鞭笞",
    "Improved Life Tap": "强化生命分流",
    "Improved Searing Pain": "强化灼热之痛",
    "Improved Shadow Bite": "强化暗影撕咬",
    "Improved Shadow Bolt": "强化暗影箭",
    "Improved Soul Leech": "强化灵魂汲取",
    "Improved Succubus": "强化魅魔",
    "Improved Voidwalker": "强化虚空行者",
    "Incinerate": "烧尽",
    "Inferno": "地狱火",
    "Intensity": "强烈",
    "Kindling Soul": "燃魂",
    "Life Tap": "生命分流",
    "Malediction": "诅咒增幅",
    "Mana Feed": "法力喂食",
    "Master Conjuror": "魔石大师",
    "Master Demonologist": "恶魔学识大师",
    "Master Summoner": "召唤大师",
    "Metamorphosis": "恶魔变形",
    "Molten Core": "熔火之心",
    "Molten Skin": "熔火皮肤",
    "Nemesis": "复仇女神",
    "Nether Protection": "虚空防护",
    "Nightfall": "夜幕",
    "Pandemic": "恶疾",
    "Pyroclasm": "火焰冲撞",
    "Rain of Fire": "火焰之雨",
    "Ritual of Doom": "末日仪式",
    "Ritual of Doom Effect": "末日仪式效果",
    "Ritual of Souls": "灵魂仪式",
    "Ritual of Summoning": "召唤仪式",
    "Ruin": "毁灭",
    "Searing Pain": "灼热之痛",
    "Seed of Corruption": "腐蚀之种",
    "Sense Demons": "感知恶魔",
    "Shadow and Flame": "暗影与烈焰",
    "Shadow Bolt": "暗影箭",
    "Shadow Cleave": "暗影顺劈",
    "Shadow Embrace": "暗影之拥",
    "Shadow Mastery": "暗影掌握",
    "Shadow Ward": "防护暗影结界",
    "Shadowburn": "暗影灼烧",
    "Shadowflame": "暗影烈焰",
    "Shadowfury": "暗影之怒",
    "Siphon Life": "生命虹吸",
    "Soul Fire": "灵魂之火",
    "Soul Leech": "灵魂汲取",
    "Soul Link": "灵魂链接",
    "Soul Pact": "灵魂契约",
    "Soul Siphon": "灵魂虹吸",
    "Soulshatter": "灵魂碎裂",
    "Sudden Fear": "骤然恐惧",
    "Summon Dreadsteed": "召唤恐惧战马",
    "Summon Felguard": "召唤恶魔卫士",
    "Summon Felhunter": "召唤地狱猎犬",
    "Summon Felsteed": "召唤地狱战马",
    "Summon Imp": "召唤小鬼",
    "Summon Succubus": "召唤魅魔",
    "Summon Voidwalker": "召唤虚空行者",
    "Suppression": "镇压",
    "Torture": "折磨",
    "Unending Breath": "魔息术",
    "Unholy Power": "邪恶强化",
    "Unstable Affliction": "痛苦无常",
    "zzOldImproved Demonic Tactics": "旧版强化恶魔战术",
}

TERM_FIXES = [
    ("Imp", "小鬼"), ("Voidwalker", "虚空行者"), ("Succubus", "魅魔"), ("Felhunter", "地狱猎犬"),
    ("Felguard", "恶魔卫士"), ("Doomguard", "末日守卫"), ("Infernal", "地狱火"),
    ("Warlock", "术士"), ("Demon", "恶魔"), ("demon", "恶魔"), ("Demons", "恶魔"),
    ("Shadow damage-over-time", "暗影持续伤害"), ("damage-over-time", "持续伤害"),
    ("Shadow", "暗影"), ("Fire", "火焰"), ("Frost", "冰霜"), ("Nature", "自然"),
    ("Arcane", "奥术"), ("Holy", "神圣"), ("damage", "伤害"), ("Damage", "伤害"),
    ("health", "生命值"), ("Health", "生命值"), ("mana", "法力值"), ("Mana", "法力值"),
    ("armor", "护甲"), ("Armor", "护甲"), ("Spirit", "精神"), ("Intellect", "智力"),
    ("Stamina", "耐力"), ("resistance", "抗性"), ("resistances", "抗性"),
    ("spell power", "法术强度"), ("Spell Damage", "法术伤害"), ("Spell damage", "法术伤害"),
    ("critical strike", "暴击"), ("critical hit", "暴击"), ("critical", "暴击"),
    ("threat", "威胁值"), ("cooldown", "冷却时间"), ("casting time", "施法时间"),
    ("cast time", "施法时间"), ("movement speed", "移动速度"), ("melee attack power", "近战攻击强度"),
    ("nearby enemies", "附近敌人"), ("party or raid", "小队或团队"), ("Soul Shard", "灵魂碎片"),
    ("Corruption", "腐蚀术"), ("Immolate", "献祭"), ("Shadow Bolt", "暗影箭"),
    ("Incinerate", "烧尽"), ("Soul Fire", "灵魂之火"), ("Searing Pain", "灼热之痛"),
    ("Conflagrate", "燃烧"), ("Drain Life", "吸取生命"), ("Drain Mana", "吸取法力"),
    ("Drain Soul", "吸取灵魂"), ("Life Tap", "生命分流"), ("Fear", "恐惧术"),
    ("Bane of Agony", "痛苦灾祸"), ("Bane of Doom", "厄运灾祸"), ("Bane of Exhaustion", "疲劳灾祸"),
    ("Bane of Tongues", "语言灾祸"), ("Curse of Weakness", "虚弱诅咒"),
    ("Curse of the Elements", "元素诅咒"), ("Seed of Corruption", "腐蚀之种"),
    ("Unstable Affliction", "痛苦无常"), ("Haunt", "鬼影缠身"), ("Shadowburn", "暗影灼烧"),
    ("Hellfire", "地狱烈焰"), ("Rain of Fire", "火焰之雨"), ("Healthstone", "治疗石"),
    ("Firestone", "火焰石"), ("Spellstone", "法术石"), ("Soulstone", "灵魂石"),
    ("爆击", "暴击"), ("$ghimself:herself;", "自身"), ("healed", "治疗"),
]

DURATION_BY_NAME = {
    "Amplify Bane": "30秒", "Bane of Agony": "24秒", "Bane of Doom": "1分钟",
    "Bane of Exhaustion": "12秒", "Bane of Tongues": "30秒", "Banish": "30秒",
    "Corruption": "18秒", "Curse of Agony": "24秒", "Curse of Idiocy": "30秒",
    "Curse of Recklessness": "2分钟", "Curse of the Elements": "5分钟",
    "Curse of Tongues": "30秒", "Curse of Weakness": "2分钟",
    "Death Coil": "3秒", "Demon Armor": "30分钟", "Demon Portal": "15秒",
    "Demon Skin": "30分钟", "Demonic Circle: Summon": "6分钟",
    "Detect Invisibility": "10分钟", "Drain Life": "5秒", "Drain Mana": "5秒",
    "Drain Soul": "15秒", "Enslave Demon": "5分钟", "Fear": "20秒", "Fel Armor": "30分钟",
    "Haunt": "12秒", "Health Funnel": "10秒", "Hellfire": "15秒", "Howl of Terror": "8秒",
    "Immolate": "15秒", "Immolation": "15秒", "Immolation Aura": "15秒",
    "Inferno": "5分钟", "Metamorphosis": "30秒", "Rain of Fire": "8秒",
    "Shadow Ward": "30秒", "Seed of Corruption": "18秒", "Siphon Life": "30秒",
    "Soul Link": "直到取消", "Unending Breath": "10分钟", "Unstable Affliction": "15秒",
}

RADIUS_BY_NAME = {
    "Hellfire": 10, "Howl of Terror": 10, "Inferno": 10, "Rain of Fire": 8, "Ritual of Souls": 0,
    "Seed of Corruption": 15, "Shadow Cleave": 5, "Shadowflame": 10, "Shadowfury": 8,
    "Soulshatter": 50, "Challenging Howl": 10,
}

TALENT_NAMES = {
    "Aftermath", "Backdraft", "Backlash", "Bane", "Cataclysm", "Contagion", "Dark Pact",
    "Death's Embrace", "Decimation", "Demonic Aegis", "Demonic Embrace", "Demonic Knowledge",
    "Demonic Pact", "Demonic Resilience", "Demonic Tactics", "Destructive Reach",
    "Devastation", "Emberstorm", "Empowered Corruption", "Empowered Imp", "Eradication",
    "Everlasting Affliction", "Fel Concentration", "Fel Intellect", "Fel Stamina", "Fel Synergy",
    "Fire and Brimstone", "Grim Reach", "Improved Bane of Agony", "Improved Corruption",
    "Improved Curse of Weakness", "Improved Demonic Tactics", "Improved Drain Soul",
    "Improved Enslave Demon", "Improved Fear", "Improved Felhunter", "Improved Firebolt",
    "Improved Health Funnel", "Improved Healthstone", "Improved Howl of Terror",
    "Improved Immolate", "Improved Imp", "Improved Lash of Pain", "Improved Life Tap",
    "Improved Searing Pain", "Improved Shadow Bite", "Improved Shadow Bolt",
    "Improved Soul Leech", "Improved Succubus", "Improved Voidwalker", "Intensity",
    "Kindling Soul", "Malediction", "Mana Feed", "Master Conjuror", "Master Demonologist",
    "Master Summoner", "Molten Core", "Molten Skin", "Nemesis", "Nether Protection",
    "Nightfall", "Pandemic", "Pyroclasm", "Ruin", "Shadow and Flame", "Shadow Embrace",
    "Shadow Mastery", "Soul Leech", "Soul Siphon", "Suppression", "Torture", "Unholy Power",
    "zzOldImproved Demonic Tactics", "Chaos Bolt Passive",
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
    return rank.replace("Rank", "等级").replace("Summon", "召唤").replace("Demon", "恶魔").replace("Passive", "被动")


def duration(rec: SpellRec) -> str:
    return DURATION_BY_NAME.get(rec.name, "")


def duration_seconds(rec: SpellRec, fallback: int = 1) -> int:
    text = duration(rec)
    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    value = int(match.group(1))
    if "分钟" in text:
        return value * 60
    return value


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 3
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
    if token == "q":
        return str(target.q(index))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 1)
    return ""


def resolve_tokens(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if not text:
        return ""
    text = text.replace("$D", duration(rec)).replace("$d", duration(rec)).replace("$e", "1")
    text = re.sub(r"\$\{\$(\d+)m(\d+)\*4\}", lambda m: str(records[int(m.group(1))].s(int(m.group(2))) * 4), text)
    text = re.sub(r"\$\{\$(\d+)m(\d+)\*8\}", lambda m: str(records[int(m.group(1))].s(int(m.group(2))) * 8), text)
    text = re.sub(r"\$\{\$m(\d+)\*4\}", lambda m: str(rec.s(int(m.group(1))) * 4), text)
    text = re.sub(r"\$\{\$m(\d+)\*8\}", lambda m: str(rec.s(int(m.group(1))) * 8), text)
    text = re.sub(r"\$\{\$m(\d+)\+\$SPI\*1\.5\}", lambda m: f"{rec.s(int(m.group(1)))} 点加精神值的 150%", text)
    text = re.sub(r"\$\{\$m(\d+)\*\$<mult>\+\$SPS\*\.5\*\$<mult>\}", lambda m: f"{rec.s(int(m.group(1)))} 点加法术强度的 50%", text)
    text = re.sub(r"\$\{\$m(\d+)/-1000\}", lambda m: str(abs(rec.s(int(m.group(1)))) / 1000), text)
    text = re.sub(r"\$\{\$m(\d+)\*\$<mult>\}", lambda m: str(rec.s(int(m.group(1)))), text)
    text = re.sub(r"\$\{\$M(\d+)\*\$<mult>\}", lambda m: str(rec.maxv(int(m.group(1)))), text)
    text = re.sub(r"\$\*([0-9]+);([sm])(\d*)", lambda m: str(int(m.group(1)) * int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0)), text, flags=re.I)
    text = re.sub(r"\$/(\d+);(\d+)([A-Za-z])(\d*)", lambda m: f"{int(int(ref_value(int(m.group(2)), m.group(3), m.group(4), records, rec) or 0) / int(m.group(1))):g}", text)
    text = re.sub(r"\$/(\d+);([A-Za-z])(\d*)", lambda m: f"{int(int(ref_value(rec.id, m.group(2), m.group(3), records, rec) or 0) / int(m.group(1))):g}", text)
    text = re.sub(r"\$(\d+)([A-Za-z])(\d*)", lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3), records, rec), text)
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: str(over_time(rec, int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)", lambda _: str(RADIUS_BY_NAME.get(rec.name, 10)), text, flags=re.I)
    text = re.sub(r"\$q(\d*)", lambda m: str(rec.q(int(m.group(1) or "1"))), text, flags=re.I)
    text = text.replace("$h", str(rec.h())).replace("$H", str(rec.h()))
    return cleanup(text)


def ref_rec_from_text(text: str, records: dict[int, SpellRec], fallback: SpellRec) -> SpellRec:
    match = re.search(r"\$(\d+)[smo]", text or "")
    return records.get(int(match.group(1)), fallback) if match else fallback


def seed_records(text: str, records: dict[int, SpellRec], rec: SpellRec) -> tuple[SpellRec, SpellRec]:
    dot_match = re.search(r"causing\s+\$(\d+)o1", text or "", flags=re.I)
    dot_rec = records.get(int(dot_match.group(1)), rec) if dot_match else rec
    explosion_match = re.search(r"(?:inflict|deals)\s+\$(\d+)s1", text or "", flags=re.I)
    explosion_rec = records.get(int(explosion_match.group(1)), rec) if explosion_match else rec
    return dot_rec, explosion_rec


def damage_range(rec: SpellRec, n: int = 1) -> str:
    lo, hi = rec.s(n), rec.maxv(n)
    return f"{lo} 到 {hi}" if hi != lo else str(lo)


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    desc_en = row.get("description_en") or rec.desc

    if name == "Shadow Bolt":
        return f"向敌人发射暗影箭，造成 {damage_range(rec)} 点暗影伤害。"
    if name == "Searing Pain":
        return f"灼烧敌方目标，造成 {damage_range(rec)} 点火焰伤害，并产生大量威胁值。"
    if name == "Soul Fire":
        return f"燃烧敌人的灵魂，造成 {damage_range(rec)} 点火焰伤害。"
    if name == "Shadowburn":
        return f"立即冲击目标，造成 {rec.s(2)} 点暗影伤害。如果目标在 5 秒内死于暗影灼烧并可提供经验值或荣誉，施法者获得一块灵魂碎片。"
    if name == "Incinerate":
        return f"对目标造成 {damage_range(rec)} 点火焰伤害。如果目标受到献祭影响，则额外造成 {rec.s(1) // 4} 点火焰伤害。"
    if name == "Conflagrate":
        return f"点燃已受到你的献祭影响的目标，造成 {damage_range(rec)} 点火焰伤害，并消耗献祭效果。"
    if name == "Chaos Bolt":
        return f"向敌人发射混乱之箭，造成 {damage_range(rec)} 点火焰伤害。混乱之箭无法被抵抗，并会穿透所有吸收效果。"
    if name == "Death Coil":
        return f"使敌方目标因恐惧逃跑 {duration(rec)}，并造成 {damage_range(rec)} 点暗影伤害。施法者恢复等同于伤害量 100% 的生命值。"

    if name == "Corruption":
        return f"腐蚀目标，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害。"
    if name in ("Bane of Agony", "Curse of Agony"):
        return f"使目标痛苦不堪，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害。伤害开始较低，随后逐渐增强。同一术士对同一目标只能激活一个{'灾祸' if name.startswith('Bane') else '诅咒'}。"
    if name == "Immolate":
        return f"灼烧敌人，造成 {rec.s(2)} 点火焰伤害，并在 {duration(rec)} 内额外造成 {over_time(rec, 1)} 点火焰伤害。"
    if name == "Bane of Doom":
        return f"用迫近的厄运诅咒目标，在 {duration(rec)} 后造成 {rec.s(1)} 点暗影伤害。如果目标死于该伤害，有几率召唤一名末日守卫。不能对玩家施放。"
    if name == "Drain Life":
        return f"每 {rec.amp_sec(1) or 1} 秒从目标身上转移 {rec.s(1)} 点生命值给施法者，持续 {duration(rec)}。"
    if name == "Drain Mana":
        return f"每 {rec.amp_sec(1) or 1} 秒从目标身上转移 {rec.s(1)} 点法力值给施法者，持续 {duration(rec)}。"
    if name == "Drain Soul":
        return f"吸取目标的灵魂，在 {duration(rec)} 内造成 {over_time(rec, 2)} 点暗影伤害；根据目标已损失生命值，伤害最多提高 40%。如果目标在引导期间死亡且可提供经验值或荣誉，施法者获得一块灵魂碎片。"
    if name == "Siphon Life":
        tick = rec.amp_sec(1) or 3
        return f"每 {tick} 秒对目标造成 {rec.s(2)} 点伤害，并将 {rec.s(1)} 点生命值转移给施法者，持续 {duration(rec)}。"
    if name == "Unstable Affliction":
        return f"暗影能量缓慢摧毁目标，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害。如果痛苦无常被驱散，会对驱散者造成 {rec.s(1) * 9} 点伤害并沉默 {duration(records.get(31117, rec)) or '5秒'}。"
    if name == "Seed of Corruption":
        dot_rec, explosion = seed_records(desc_en, records, rec)
        return f"在敌方目标体内埋下恶魔之种，在 {duration(dot_rec)} 内造成 {over_time(dot_rec, 1)} 点暗影伤害。当目标承受 {dot_rec.s(2)} 点总伤害或死亡时，种子爆炸，对目标周围 {RADIUS_BY_NAME['Seed of Corruption']} 码内所有其他敌人造成 {explosion.s(1)} 点暗影伤害。同一术士对同一目标只能激活一个腐蚀术效果。"
    if name == "Haunt":
        return f"向目标释放幽魂，造成 {damage_range(rec)} 点暗影伤害，并使你在目标身上的暗影持续伤害提高 {rec.s(3)}%，持续 {duration(rec)}。鬼影缠身结束或被驱散时，幽魂返回并为你恢复相当于其造成伤害 {rec.s(2)}% 的生命值。"
    if name == "Rain of Fire":
        eff = ref_rec_from_text(desc_en + " " + row.get("tooltip_en", ""), records, rec)
        return f"召唤火焰之雨灼烧目标区域的敌人，在 {duration(rec)} 内造成 {eff.s(1) * 4} 点火焰伤害。该持续伤害可以暴击。"
    if name == "Hellfire":
        eff = ref_rec_from_text(desc_en, records, rec)
        return f"点燃施法者周围区域，每 {rec.amp_sec(2) or 1} 秒对自身造成 {rec.s(2)} 点火焰伤害，并对附近所有敌人造成 {eff.s(1)} 点火焰伤害，持续 {duration(rec)}。"
    if name == "Hellfire Effect":
        return f"每秒受到 {rec.s(1)} 点火焰伤害。"
    if name == "Shadowflame":
        dot = records.get(47960, rec)
        return f"施法者前方锥形范围内的目标受到 {rec.s(1)} 点暗影伤害，并在 {duration(dot)} 内额外受到 {over_time(dot, 1)} 点火焰伤害。"
    if name == "Shadowfury":
        return f"释放暗影之怒，造成 {damage_range(rec)} 点暗影伤害，并使 {RADIUS_BY_NAME['Shadowfury']} 码范围内所有敌人昏迷 {duration(rec)}。"
    if name == "Shadow Cleave":
        return f"对一个敌方目标及其附近盟友造成 {damage_range(rec)} 点暗影伤害，最多影响 {rec.stack() or rec.s(1)} 个目标。"
    if name == "Immolation" or name == "Immolation Aura":
        eff = records.get(20153, records.get(50590, rec))
        return f"点燃附近敌人，每 {rec.amp_sec(1) or 1} 秒造成 {eff.s(1)} 点火焰伤害，持续 {duration(rec)}。"
    if name == "Demonic Immolate":
        return "恶魔形态下强化献祭效果，使附近敌人持续受到火焰伤害。"

    if name == "Curse of Weakness":
        extra = f"，护甲值降低 {abs(rec.s(2))}%" if abs(rec.s(2)) > 1 else ""
        return f"使目标近战攻击强度降低 {abs(rec.s(1))} 点{extra}，持续 {duration(rec)}。同一术士对同一目标只能激活一个诅咒。"
    if name == "Curse of the Elements":
        return f"诅咒目标 {duration(rec)}，使其奥术、火焰、冰霜、自然和暗影抗性降低 {abs(rec.s(1))} 点，并使其受到的魔法伤害提高 {rec.s(2)}%。同一术士对同一目标只能激活一个诅咒。"
    if name in ("Bane of Tongues", "Curse of Tongues"):
        kind = "灾祸" if name.startswith("Bane") else "诅咒"
        return f"迫使目标说恶魔语，使所有法术的施法时间延长 {abs(rec.s(1))}%，持续 {duration(rec)}。同一术士对同一目标只能激活一个{kind}。"
    if name == "Curse of Recklessness":
        return f"用鲁莽诅咒目标，使其近战攻击强度提高 {rec.s(1)} 点，但护甲降低 {abs(rec.s(2))} 点，持续 {duration(rec)}。被诅咒的敌人不会逃跑，并会忽略恐惧和惊骇效果。同一术士对同一目标只能激活一个诅咒。"
    if name == "Curse of Idiocy":
        amount = abs(rec.s(1))
        total = amount * 15
        return f"用痴呆诅咒目标，每 {rec.amp_sec(3) or 2} 秒使其智力和精神降低 {amount} 点，直到各自总计降低 {total} 点。同一术士对同一目标只能激活一个诅咒。"
    if name == "Bane of Exhaustion":
        return f"使目标移动速度降低 {abs(rec.s(1))}%，持续 {duration(rec)}。同一术士对同一目标只能激活一个灾祸。"
    if name == "Amplify Bane":
        return f"使你的下一个厄运灾祸或痛苦灾祸效果提高 {rec.s(1)}%，下一个疲劳灾祸额外提高 {abs(rec.s(2))}%，下一个语言灾祸额外提高 {abs(rec.s(3))}%，持续 {DURATION_BY_NAME['Amplify Bane']}。"

    if name == "Demon Skin":
        return f"保护施法者，使护甲提高 {rec.s(1)} 点，并每 5 秒恢复 {rec.s(2)} 点生命值，持续 {duration(rec)}。"
    if name == "Demon Armor":
        if "health generated" in desc_en:
            return f"保护施法者，使护甲提高 {rec.s(1)} 点，并使通过法术和效果获得的生命值提高 {rec.s(2)}%，持续 {duration(rec)}。同一时间只能激活一种护甲法术。"
        return f"保护施法者，使护甲提高 {rec.s(1)} 点，暗影抗性提高 {rec.s(2)} 点，并每 5 秒恢复 {rec.s(3)} 点生命值，持续 {duration(rec)}。同一时间只能激活一种护甲法术。"
    if name == "Fel Armor":
        if rec.s(2) > 1:
            return f"邪能环绕施法者，使法术强度提高 {rec.s(3)} 点并额外提高相当于精神 {rec.s(1)}% 的数值，每 5 秒恢复最大生命值的 {rec.s(2)}%，持续 {duration(rec)}。同一时间只能激活一种护甲法术。"
        return f"邪能环绕施法者，使通过法术和效果获得的生命值提高 {rec.s(1)}%，法术伤害最多提高 {rec.s(3)} 点，持续 {duration(rec)}。同一时间只能激活一种护甲法术。"
    if name == "Shadow Ward":
        return f"吸收 {rec.s(1)} 点暗影伤害，持续 {duration(rec)}。"
    if name == "Detect Invisibility":
        return f"使友方目标能够侦测次级隐形，持续 {duration(rec)}。"
    if name == "Unending Breath":
        return f"使目标能够在水下呼吸，持续 {duration(rec)}。"
    if name == "Sense Demons":
        return "在小地图上显示附近所有恶魔的位置，直到取消。同一时间只能激活一种追踪形式。"
    if name == "Eye of Kilrogg":
        return "召唤一只基尔罗格之眼，并将你的视觉与它绑定。该眼移动迅速，但非常脆弱。"
    if name == "Fear":
        return f"使敌人恐惧逃跑，最多持续 {duration(rec)}。造成伤害可能打断该效果。同一时间只能恐惧 1 个目标。"
    if name == "Howl of Terror":
        return f"发出嚎叫，使 {RADIUS_BY_NAME['Howl of Terror']} 码范围内最多 {rec.stack() or rec.s(1)} 个敌人因恐惧逃跑，持续 {duration(rec)}。造成伤害可能打断该效果。"
    if name == "Banish":
        return f"放逐敌方目标，使其无法行动但处于无敌状态，最多持续 {duration(rec)}。同一时间只能放逐一个目标。只能对恶魔和元素生物使用。"
    if name == "Enslave Demon":
        return f"奴役最高 {rec.s(1)} 级的目标恶魔，迫使其服从你的命令。被奴役时，恶魔攻击间隔延长 {abs(rec.s(2))}%，施法速度降低 {abs(rec.s(3))}%，最多持续 {duration(rec)}。反复奴役同一恶魔会更难成功。"
    if name == "Soulshatter":
        return f"使 {RADIUS_BY_NAME['Soulshatter']} 码范围内所有敌人对你的威胁值降低 {abs(rec.s(1))}%。"
    if name == "Life Tap":
        if row["spell_id"] == "57946":
            return f"将 {rec.s(1)} 点加精神值 150% 的生命值转化为 {rec.s(1)} 点加法术强度 50% 的法力值。法术强度会提高返还的法力值。"
        return f"将 {rec.s(1)} 点生命值转化为 {rec.s(1)} 点法力值。"
    if name == "Health Funnel":
        return f"只要施法者保持引导，每秒将 {rec.s(1)} 点生命值输送给施法者的宠物，持续 {duration(rec)}。"
    if name == "Dark Pact":
        return f"吸取宠物 {rec.s(1)} 点法力值，并将 100% 法力值返还给你。"

    if name == "Create Healthstone":
        amount = linked_amount(desc_en, records, rec)
        return f"制造一块治疗石，使用后可立即恢复 {amount} 点生命值。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Create Soulstone":
        eff = ref_rec_from_text(desc_en, records, rec)
        return f"制造一块灵魂石。灵魂石可以储存一个目标的灵魂；如果目标在灵魂被储存期间死亡，将能以 {abs(eff.s(1))} 点生命值和 {abs(eff.q(1))} 点法力值复活。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Create Firestone":
        hit = linked_amount(desc_en, records, rec)
        bonus = second_linked_amount(desc_en, records, rec)
        return f"制造一块火焰石，可为主手武器附魔，使每次攻击有几率额外造成 {hit} 点火焰伤害。装备火焰石还会使火焰法术伤害提高 {bonus} 点。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Create Spellstone":
        return "制造一块法术石，使用后可驱散施法者身上的所有有害魔法效果。\n\n制造出的物品在离线超过 15 分钟后会消失。"
    if name == "Create Soulwell" or name == "Ritual of Souls":
        return "开始一个制造灵魂之井的仪式。团队成员可以点击灵魂之井获得治疗石。灵魂之井持续 3 分钟或可使用 10 次。需要施法者和另外 2 名小队成员共同完成仪式。"
    if name == "Ritual of Summoning":
        return "开始召唤仪式，将一名目标小队或团队成员召唤到施法者身边。需要施法者和另外 2 名小队成员共同完成仪式。"
    if name == "Ritual of Doom":
        return "开始末日仪式，牺牲一名随机参与者来召唤末日守卫。末日守卫必须立刻被奴役，否则会攻击仪式参与者。需要施法者和另外 4 名小队成员共同完成仪式。"
    if name in ("Ritual of Doom Effect", "Curse of Doom Effect"):
        return "召唤一名末日守卫。"

    if name.startswith("Summon "):
        pet = NAME_ZH.get(name, name).replace("召唤", "")
        if name in ("Summon Felsteed", "Summon Dreadsteed"):
            speed = rec.s(2) if rec.s(2) > 1 else 100
            return f"召唤{pet}作为施法者的坐骑。移动速度提高 {speed}%，实际速度取决于你的骑术技能。"
        return f"召唤一名{pet}听从术士的命令。"
    if name == "Inferno":
        return "从扭曲虚空召唤陨石，对区域内所有敌方目标造成火焰伤害并使其昏迷。一个地狱火从陨坑中升起，在施法者命令下作战 5 分钟。"
    if name == "Demonic Circle: Summon":
        return f"在脚下召唤一个恶魔法阵，持续 {duration(rec)}。同一时间只能激活一个恶魔法阵。"
    if name == "Demonic Circle: Teleport":
        return "将你传送到自己的恶魔法阵，并移除所有诱捕效果。"
    if name == "Metamorphosis":
        return "你变身为恶魔，持续 30 秒。该形态使来自物品的护甲加成提高 600%，伤害提高 20%，被近战攻击暴击的几率降低 6%，昏迷和诱捕效果持续时间缩短 50%。你还会获得一些独特的恶魔技能。冷却时间 3 分钟。"
    if name == "Demon Charge":
        return "向敌人冲锋，使其昏迷 3 秒。"
    if name == "Challenging Howl":
        return f"嘲讽 {RADIUS_BY_NAME['Challenging Howl']} 码范围内所有敌人，持续 {duration(rec)}。"
    if name == "Demon Portal":
        return f"撕开通往扭曲虚空的传送门，持续 {duration(rec)}，周期性释放受你控制的恶魔。这些恶魔不会取代你当前激活的恶魔，最后召唤出的恶魔必定是恶魔卫士，并会使你当前目标昏迷。"
    if name == "Soul Pact":
        return f"与一名小队或团队成员的灵魂缔结契约。若目标在契约期间死亡，你获得 1 块灵魂碎片，法术伤害提高 {records.get(84703, rec).s(1)} 点，持续 {duration(records.get(84703, rec)) or '15秒'}。"

    talent = talent_desc(name, rec, row, records)
    if talent:
        return talent

    resolved = resolve_tokens(desc_en, rec, records)
    if CJK_RE.search(resolved) and not re.search(r"[A-Za-z]{3,}", resolved):
        return resolved
    return f"{NAME_ZH.get(name, name)}：获得第 {rank_num(row)} 级术士效果。"


def linked_amount(text: str, records: dict[int, SpellRec], rec: SpellRec) -> int:
    match = re.search(r"\$(\d+)s1", text or "")
    return records.get(int(match.group(1)), rec).s(1) if match else rec.s(1)


def second_linked_amount(text: str, records: dict[int, SpellRec], rec: SpellRec) -> int:
    matches = re.findall(r"\$(\d+)s1", text or "")
    if len(matches) > 1:
        return records.get(int(matches[1]), rec).s(1)
    return rec.s(1)


def pct(value: int) -> int:
    return abs(value)


def chance(rec: SpellRec) -> int:
    return rec.h() if 0 < rec.h() <= 100 else abs(rec.s(1))


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    if name == "Cataclysm":
        return f"使你的毁灭系法术法力消耗降低 {pct(rec.s(1))}%。"
    if name == "Fel Concentration":
        return f"使你在引导吸取生命、吸取法力或吸取灵魂时，有 {rec.s(1)}% 几率避免因受到伤害而被打断。"
    if name == "Bane":
        return f"使你的暗影箭和献祭施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒，灵魂之火施法时间缩短 {abs(rec.s(2)) / 1000:g} 秒。"
    if name == "Improved Shadow Bolt":
        eff = records.get(17794, rec)
        return f"你的暗影箭暴击会使目标受到的暗影伤害提高 {eff.s(1)}%，直到受到 4 次非周期性伤害为止，最多持续 {duration(eff) or '12秒'}。"
    if name == "Soul Siphon":
        return f"目标身上每有一种独立的痛苦系效果，你的吸取生命和吸取灵魂吸取量额外提高 {rec.s(1)}%，最多提高 {rec.s(2)}%。"
    if name == "Improved Corruption":
        return f"使你的腐蚀术施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒，腐蚀之种施法时间缩短 {abs(rec.s(2)) / 1000:g} 秒。"
    if name == "Improved Immolate":
        return f"使你的献祭初始伤害提高 {rec.s(1)}%。"
    if name == "Destructive Reach":
        return f"使你的毁灭系法术射程提高 {rec.s(1)}%，并使毁灭系法术造成的威胁值降低 {abs(rec.s(2))}%。"
    if name == "Improved Searing Pain":
        return f"使你的灼热之痛暴击几率提高 {rec.s(1)}%。"
    if name == "Emberstorm":
        return f"使你的火焰法术伤害提高 {rec.s(1)}%，并使烧尽的施法时间缩短 {rec.s(2)}%。"
    if name == "Ruin":
        return f"使你的毁灭系法术暴击伤害加成提高 {rec.s(1)}%。"
    if name == "Pyroclasm":
        return f"使你的火焰之雨、地狱烈焰和灵魂之火有 26% 几率使目标昏迷 {duration(records.get(18093, rec)) or '3秒'}。"
    if name == "Nightfall":
        return f"你的腐蚀术、吸取生命和腐蚀之种对敌人造成伤害后，有 {chance(rec)}% 几率使你进入暗影冥思状态，使下一次暗影箭的施法时间缩短 100%。"
    if name == "Aftermath":
        return f"你的毁灭系法术有 {chance(rec)}% 几率使目标眩晕，持续 {duration(records.get(18118, rec)) or '5秒'}。"
    if name == "Improved Firebolt":
        return f"使你的小鬼火焰箭施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒，法力消耗降低 {pct(rec.s(2))}%。小鬼火焰箭暴击时，你有 {rec.s(3)}% 几率获得小鬼之火，使下一个单体火焰法术的初始伤害提高。"
    if name == "Improved Lash of Pain":
        return f"使你的魅魔剧痛鞭笞冷却时间缩短 {abs(rec.s(1)) / 1000:g} 秒。"
    if name == "Devastation":
        return f"使你的毁灭系法术暴击几率提高 {rec.s(1)}%。"
    if name == "Intensity":
        return f"使你在施放或引导任何毁灭系法术时，有 {rec.s(1)}% 几率抵抗因受到伤害而造成的打断。"
    if name == "Suppression":
        return f"使敌人抵抗你的痛苦系法术的几率降低 {pct(rec.s(1))}%。"
    if name == "Improved Curse of Weakness":
        return f"使你的虚弱诅咒效果提高 {rec.s(1)}%。"
    if name == "Improved Life Tap":
        return f"使你的生命分流获得的法力值提高 {rec.s(1)}%。"
    if name == "Improved Drain Soul":
        return f"如果目标在你吸取其灵魂时被你杀死，则返还你最大法力值的 {rec.s(3)}%；吸取灵魂伤害提高 {rec.s(1)}%。此外，你的痛苦系法术产生的威胁值降低 {pct(rec.s(2))}%。"
    if name == "Grim Reach":
        return f"使你的痛苦系法术射程提高 {rec.s(1)}%。"
    if name == "Shadow Mastery":
        return f"使你的暗影法术造成的伤害或吸取的生命值提高 {rec.s(1)}%。"
    if name == "Improved Healthstone":
        return f"使你的治疗石恢复的生命值提高 {rec.s(1)}%。"
    if name == "Improved Imp":
        return f"使你的小鬼火焰箭、火焰之盾和血之契印效果提高 {rec.s(1)}%。"
    if name == "Demonic Embrace":
        return f"使你的总耐力提高 {rec.s(1)}%，但总精神降低 {abs(rec.s(2))}%。"
    if name == "Improved Health Funnel":
        return f"使你的生命通道传输的生命值提高 {rec.s(1)}%，初始生命值消耗降低 {abs(rec.s(2))}%。"
    if name == "Improved Voidwalker":
        return f"使你的虚空行者折磨、吞噬暗影、牺牲和受难技能效果提高 {rec.s(1)}%。"
    if name == "Fel Domination":
        return f"你的下一个小鬼、虚空行者、魅魔、地狱猎犬或恶魔卫士召唤法术施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒，法力消耗降低 {abs(rec.s(2))}%。"
    if name == "Master Summoner":
        return f"使你的小鬼、虚空行者、魅魔、地狱猎犬和恶魔卫士召唤法术施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒，法力消耗降低 {abs(rec.s(2))}%。"
    if name == "Fel Intellect":
        return f"使你的小鬼、虚空行者、魅魔、地狱猎犬和恶魔卫士智力提高 {rec.s(1)}%，并使你的最大法力值提高 {rec.s(2)}%。"
    if name == "Fel Stamina":
        return f"使你的小鬼、虚空行者、魅魔、地狱猎犬和恶魔卫士耐力提高 {rec.s(1)}%，并使你的最大生命值提高 {rec.s(2)}%。"
    if name == "Improved Succubus":
        return f"使你的魅魔剧痛鞭笞和安抚之吻效果提高 {rec.s(1)}%，诱惑和次级隐形持续时间延长 {rec.s(2)}%。"
    if name == "Master Conjuror":
        return f"使制造魔石的施法时间缩短 {abs(rec.s(2)) / 1000:g} 秒。火焰石和火焰石效果的火焰伤害加成提高 {rec.s(1)}%。法术石使用时还会提供吸收效果，并提高从灵魂石复活获得的生命值。"
    if name == "Unholy Power":
        return f"使你的虚空行者、魅魔、地狱猎犬和恶魔卫士近战攻击伤害，以及小鬼火焰箭伤害提高 {rec.s(1)}%。"
    if name == "Demonic Sacrifice":
        return "牺牲你召唤的恶魔，获得持续 30 分钟的效果。召唤任何恶魔都会取消该效果。\n\n小鬼：火焰伤害提高。\n\n虚空行者：周期性恢复生命值。\n\n魅魔：暗影伤害提高。\n\n地狱猎犬：周期性恢复法力值。\n\n恶魔卫士：暗影和火焰伤害提高。"
    if name == "Improved Enslave Demon":
        return f"使你的奴役恶魔造成的攻击速度和施法速度惩罚降低 {rec.s(1)}%，被抵抗几率降低 {rec.s(3)}%。"
    if name == "Improved Bane of Agony":
        return f"使你的痛苦灾祸伤害提高 {rec.s(1)}%。"
    if name == "Soul Link":
        eff = records.get(25228, rec)
        return f"激活后，施法者承受的所有伤害有 {eff.s(2)}% 由你的小鬼、虚空行者、魅魔、地狱猎犬、恶魔卫士或被奴役的恶魔承担。该伤害无法被阻止。此外，恶魔和主人造成的伤害提高 {eff.s(1)}%。"
    if name == "Improved Howl of Terror":
        return f"使你的恐惧嚎叫施法时间缩短 {abs(rec.s(1)) / 1000:g} 秒。"
    if name == "Contagion":
        return f"使痛苦灾祸、厄运灾祸、生命虹吸、腐蚀术和腐蚀之种伤害提高 {rec.s(1)}%，并使你的痛苦系法术被驱散的几率额外降低 {rec.s(3)}%。"
    if name == "Demonic Aegis":
        return f"使你的恶魔护甲和邪甲术效果提高 {rec.s(1)}%。"
    if name == "Demonic Tactics":
        return f"使你和你召唤的恶魔近战与法术暴击几率提高 {rec.s(1)}%。"
    if name == "Shadow and Flame":
        return f"你的暗影箭和烧尽额外获得相当于你法术伤害加成 {rec.s(1)}% 的效果。"
    if name == "Soul Leech":
        return f"你的暗影箭、暗影灼烧、灵魂之火、烧尽、灼热之痛和燃烧有 {chance(rec)}% 几率返还相当于造成伤害 {rec.s(1)}% 的生命值。"
    if name == "Nether Protection":
        return f"被暗影或火焰法术击中后，你有 {chance(rec)}% 几率免疫暗影和火焰法术，持续 {duration(records.get(30300, rec)) or '4秒'}。"
    if name == "Demonic Resilience":
        return f"使你被近战和法术暴击的几率降低 {abs(rec.s(1))}%，并使你召唤的恶魔受到的所有伤害降低 {abs(rec.s(2))}%。"
    if name == "Mana Feed":
        return f"当你通过吸取法力或生命分流获得法力值时，你的宠物获得你所获得法力值的 {rec.s(1)}%。"
    if name == "Empowered Corruption":
        return f"你的腐蚀术额外获得相当于法术伤害加成 {rec.s(1) * 6}% 的效果，并使腐蚀之种触发爆炸所需伤害降低 {abs(rec.s(2))}%。"
    if name == "Shadow Embrace":
        eff = records.get(32386, rec)
        return f"你的腐蚀术、痛苦灾祸、生命虹吸和腐蚀之种还会触发暗影之拥效果，使目标造成的物理伤害降低 {max(abs(rec.s(1)), abs(eff.s(1)))}%。"
    if name == "Malediction":
        return f"使你的元素诅咒伤害加成效果额外提高 {rec.s(1)}%。"
    if name == "Backlash":
        return f"使你的法术暴击几率额外提高 {rec.s(2)}%，并使你在受到物理攻击命中时有 {chance(rec)}% 几率让下一个暗影箭或烧尽的施法时间缩短 100%。该效果持续 {duration(records.get(34936, rec)) or '8秒'}，且每 8 秒只能触发一次。"
    if name == "Demonic Knowledge":
        return f"使你的法术伤害提高，数值相当于当前激活恶魔耐力与智力总和的 {rec.s(1)}%。"
    if name == "Demonic Empowerment":
        return "强化术士召唤的恶魔。\n\n小鬼：法术暴击几率提高。\n\n虚空行者：生命值和威胁值提高。\n\n魅魔：解除所有昏迷和移动限制效果。\n\n地狱猎犬：攻击速度提高。\n\n恶魔卫士：攻击速度提高并免疫昏迷和移动限制效果。"
    if name == "Eradication":
        return f"当你的腐蚀术造成伤害时，有 {chance(rec)}% 几率使施法速度提高 {records.get(64368, rec).s(1)}%，持续 {duration(records.get(64368, rec)) or '10秒'}。"
    if name == "Death's Embrace":
        return f"当你的生命值不高于 20% 时，吸取生命的吸取量提高 {rec.s(1)}%；当目标生命值不高于 35% 时，你的暗影法术伤害提高 {rec.s(2)}%。"
    if name == "Everlasting Affliction":
        return f"你的腐蚀术和痛苦无常额外获得相当于法术伤害加成 {rec.s(2)}% 的效果；你的吸取生命、吸取灵魂、暗影箭和鬼影缠身有 {chance(rec)}% 几率重置目标身上腐蚀术的持续时间。"
    if name == "Atrocity":
        return "毁灭周围区域，使 15 码范围内所有目标受到腐蚀术（等级 8）。此外，你的腐蚀术持续时间结束时会对目标造成 434 点暗影伤害。"
    if name == "Empowered Imp":
        return f"使你的小鬼造成的伤害提高 {rec.s(1)}%；你的小鬼造成暴击时，有 {rec.s(2)}% 几率使你下一个法术的暴击几率提高 {records.get(47283, rec).s(1)}%，持续 {duration(records.get(47283, rec)) or '8秒'}。"
    if name == "Fel Synergy":
        return f"你的法术造成伤害后，有 {chance(rec)}% 几率为宠物恢复相当于该法术伤害 {rec.s(1)}% 的生命值。"
    if name == "Demonic Pact":
        return f"使你的法术伤害提高 {rec.s(3)}%。你的宠物造成暴击后，会为小队或团队成员施加恶魔契约，使其法术强度提高，数值相当于你法术伤害的 {rec.s(1)}%，持续 {duration(records.get(48090, rec)) or '45秒'}。该效果有 {records.get(53646, rec).s(2)} 秒冷却时间。不会影响被奴役的恶魔。"
    if name == "Molten Core":
        return f"使你的献祭持续时间延长 {abs(rec.s(2)) / 1000:g} 秒；当你的腐蚀术造成伤害时，有 {chance(rec)}% 几率获得熔火之心，使你接下来 3 次烧尽或灵魂之火获得强化，持续 {duration(records.get(47383, rec)) or '15秒'}。"
    if name == "Backdraft":
        return f"施放燃烧后，你接下来 3 个毁灭系法术的施法时间和公共冷却时间缩短 {abs(records.get(54274, rec).s(1))}%，持续 {duration(records.get(54274, rec)) or '15秒'}。"
    if name == "Kindling Soul":
        return f"你的法术伤害提高，数值相当于精神的 {rec.s(2)}%；你的法术暴击会使精神提高 {records.get(47426, rec).s(1)}%，持续 10 秒。"
    if name == "Torture":
        return "当你的暗影法术造成暴击后，下一个灼热之痛或献祭有几率变为瞬发。该效果有 20 秒冷却时间。"
    if name == "Fire and Brimstone":
        return f"使你的烧尽和混乱之箭对受到你献祭影响的目标造成的伤害提高 {rec.s(1)}%，并使燃烧的暴击几率提高 {rec.s(2)}%。"
    if name == "Improved Fear":
        return f"你的恐惧术效果结束时会使目标陷入噩梦，使其移动速度降低 {abs(records.get(60946, rec).s(1))}%，持续 {duration(records.get(60946, rec)) or '5秒'}。"
    if name == "Sudden Fear":
        return "你的下一个恐惧术变为瞬发。"
    if name == "Improved Felhunter":
        return f"你的地狱猎犬每次用暗影撕咬命中时恢复最大法力值的 4%，该技能冷却时间缩短 {abs(rec.s(1)) / 1000:g} 秒。此外，地狱猎犬的恶魔智力效果提高 {rec.s(2)}%。"
    if name == "Improved Soul Leech":
        return f"你的灵魂汲取效果还会为你和召唤的恶魔恢复最大法力值的 {rec.s(1)}%，并有 {rec.s(2)}% 几率使最多 10 名小队或团队成员获得每 5 秒恢复最大法力值 1% 的效果，持续 {duration(records.get(57669, rec)) or '15秒'}。"
    if name == "Improved Demonic Tactics":
        return f"使你召唤的恶魔暴击几率提高，数值相当于你暴击几率的 {rec.s(1)}%。"
    if name == "Pandemic":
        return f"使你的腐蚀术和痛苦无常周期性伤害可以暴击，暴击时伤害提高 {rec.s(1)}%，并使鬼影缠身的暴击伤害加成提高 {rec.s(2)}%。"
    if name == "Nemesis":
        return f"使你的恶魔增效、恶魔变形和恶魔支配冷却时间缩短 {abs(rec.s(1))}%。"
    if name == "Decimation":
        return f"当你用暗影箭、烧尽或灵魂之火命中生命值不高于 {rec.s(2)}% 的目标时，灵魂之火施法时间缩短 {rec.s(1)}%，持续 {duration(records.get(63165, rec)) or '10秒'}。在灭杀效果下施放灵魂之火不消耗灵魂碎片。"
    if name == "Molten Skin":
        return f"使你受到的所有伤害降低 {abs(rec.s(1))}%。"
    if name == "Improved Shadow Bite":
        return "你的地狱猎犬每次用暗影撕咬命中时恢复最大法力值的 5%。"
    if name == "Master Demonologist":
        if row.get("description_en"):
            rank = rank_num(row)
            imp = abs(records.get(23759 + max(0, rank - 1), rec).s(1))
            void = abs(records.get(23760 if rank == 1 else 23840 + rank, rec).s(1))
            succ = records.get(23761 if rank == 1 else 23832 + rank, rec).s(1)
            felguard = records.get(35701 + rank, rec)
            return f"只要召唤的恶魔存活，术士和恶魔都会获得对应效果。\n\n小鬼：造成的威胁值降低 {imp}%。\n\n虚空行者：受到的物理伤害降低 {void}%。\n\n魅魔：造成的所有伤害提高 {succ}%。\n\n地狱猎犬：所有抗性按等级提高，每级提高 {rank / 5:g} 点。\n\n恶魔卫士：造成的所有伤害提高 {felguard.s(1)}%，所有抗性按等级提高，每级提高 {rank / 10:g} 点。"
        tip = row.get("tooltip_en", "")
        if "threat" in tip:
            return f"造成的威胁值降低 {abs(rec.s(1))}%。"
        if "physical" in tip:
            return f"受到的物理伤害降低 {abs(rec.s(1))}%。"
        if "damage caused" in tip and "resistance" not in tip:
            return f"造成的所有伤害提高 {rec.s(1)}%。"
        if "resistance" in tip and "damage" in tip:
            return f"造成的所有伤害提高 {rec.s(1)}%，所有魔法抗性提高 {rec.s(2)} 点。"
        if "resistance" in tip:
            return f"所有魔法抗性提高 {rec.s(1)} 点。"
    if name == "zzOldImproved Demonic Tactics" or name == "Chaos Bolt Passive":
        return f"{NAME_ZH[name]}。"
    return ""


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    if name in ("Corruption", "Bane of Agony", "Curse of Agony", "Unstable Affliction"):
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点暗影伤害。"
    if name == "Immolate":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点火焰伤害。"
    if name == "Drain Life":
        return f"每 {rec.amp_sec(1) or 1} 秒吸取 {rec.s(1)} 点生命值给施法者。"
    if name == "Drain Mana":
        return f"每 {rec.amp_sec(1) or 1} 秒吸取 {rec.s(1)} 点法力值给施法者。"
    if name == "Drain Soul":
        return f"每 {rec.amp_sec(2) or 3} 秒造成 {rec.s(2)} 点暗影伤害。"
    if name == "Siphon Life":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(2)} 点伤害，并吸取 {rec.s(1)} 点生命值给施法者。"
    if name == "Rain of Fire":
        eff = ref_rec_from_text(row.get("tooltip_en", "") + row.get("description_en", ""), records, rec)
        return f"每 {eff.amp_sec(1) or 2} 秒造成 {eff.s(1)} 点火焰伤害。"
    if name == "Hellfire":
        return "对自身和附近所有敌人造成火焰伤害。"
    if name == "Curse of Weakness":
        return f"近战攻击强度降低 {abs(rec.s(1))} 点。"
    if name == "Curse of the Elements":
        return f"奥术、火焰、冰霜、自然和暗影抗性降低 {abs(rec.s(1))} 点，受到的魔法伤害提高 {rec.s(2)}%。"
    if name in ("Bane of Tongues", "Curse of Tongues"):
        return f"正在说恶魔语，施法时间延长 {abs(rec.s(1))}%。"
    if name == "Curse of Recklessness":
        return f"近战攻击强度提高 {rec.s(1)} 点，护甲降低 {abs(rec.s(2))} 点；目标不会逃跑并会忽略恐惧和惊骇效果。"
    if name == "Bane of Exhaustion":
        return f"移动速度降低 {abs(rec.s(1))}%。"
    if name == "Demon Skin":
        return f"护甲提高 {rec.s(1)} 点，每 5 秒恢复 {rec.s(2)} 点生命值。"
    if name == "Demon Armor":
        if "health generated" in (row.get("description_en") or ""):
            return f"护甲提高 {rec.s(1)} 点，通过法术和效果获得的生命值提高 {rec.s(2)}%。"
        return f"护甲提高 {rec.s(1)} 点，暗影抗性提高 {rec.s(2)} 点，每 5 秒恢复 {rec.s(3)} 点生命值。"
    if name == "Fel Armor":
        if rec.s(2) > 1:
            return f"法术强度提高 {rec.s(3)} 点并额外提高精神的 {rec.s(1)}%，每 5 秒恢复最大生命值的 {rec.s(2)}%。"
        return f"通过法术和效果获得的生命值提高 {rec.s(1)}%，法术伤害最多提高 {rec.s(3)} 点。"
    if name == "Shadow Ward":
        return f"吸收 {rec.s(1)} 点暗影伤害。"
    if name == "Death Coil":
        return "惊骇。"
    if name == "Fear":
        return "恐惧。"
    if name == "Howl of Terror":
        return "因恐惧逃跑。"
    if name == "Banish":
        return "无敌，但无法行动。"
    if name == "Enslave Demon":
        return "被奴役。"
    if name == "Metamorphosis":
        return "恶魔形态：护甲、伤害提高，被近战暴击几率降低，昏迷和诱捕持续时间缩短。"
    if name == "Haunt":
        return f"受到的暗影持续伤害提高 {rec.s(3)}%。"
    if name == "Seed of Corruption":
        dot_rec, _ = seed_records(row.get("description_en", "") or rec.desc, records, rec)
        return f"每 {dot_rec.amp_sec(1) or 3} 秒造成 {dot_rec.s(1)} 点暗影伤害。受到 {dot_rec.s(2)} 点总伤害或死亡后爆炸。"
    if name == "Shadowfury":
        return "昏迷。"
    if name == "Demonic Circle: Summon":
        return "已召唤恶魔法阵。"
    if name == "Demonic Circle: Teleport":
        return "传送到恶魔法阵。"
    if name == "Soul Pact":
        return "与附近术士灵魂相连。"
    if name == "Master Demonologist":
        return ""
    if name in TALENT_NAMES:
        return ""

    source = row.get("tooltip_en") or rec.aura
    tip = resolve_tokens(source, rec, records)
    if CJK_RE.search(tip) and not re.search(r"[A-Za-z]{3,}", tip):
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


def is_warlock(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & WARLOCK_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_warlock(row):
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
        if is_warlock(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or re.search(r"[A-Za-z]{3,}", row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority warlock rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"warlock spell ids synced: {len(updates)}")
    print(f"warlock zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:30]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
