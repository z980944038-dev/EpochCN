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

HUNTER_SKILLS = {"50", "51", "163"}

NAME_ZH = {
    "Aimed Shot": "瞄准射击",
    "Animal Handler": "动物管理员",
    "Arcane Shot": "奥术射击",
    "Aspect Mastery": "守护掌握",
    "Aspect of the Beast": "野兽守护",
    "Aspect of the Cheetah": "猎豹守护",
    "Aspect of the Dragonhawk": "龙鹰守护",
    "Aspect of the Hawk": "雄鹰守护",
    "Aspect of the Monkey": "灵猴守护",
    "Aspect of the Pack": "豹群守护",
    "Aspect of the Viper": "蝰蛇守护",
    "Aspect of the Wild": "野性守护",
    "Auto Shot": "自动射击",
    "Barrage": "弹幕",
    "Beast Lore": "野兽知识",
    "Beast Mastery": "野兽掌握",
    "Bestial Discipline": "野兽戒律",
    "Bestial Wrath": "狂野怒火",
    "Black Arrow": "黑箭",
    "Call Pet": "召唤宠物",
    "Call Stabled Pet": "召唤兽栏宠物",
    "Careful Aim": "精确瞄准",
    "Catlike Reflexes": "猎豹反射",
    "Chimera Shot": "奇美拉射击",
    "Clever Traps": "灵巧陷阱",
    "Cobra Strikes": "眼镜蛇打击",
    "Combat Experience": "作战经验",
    "Concussive Barrage": "震荡弹幕",
    "Concussive Shot": "震荡射击",
    "Counterattack": "反击",
    "Deflection": "偏斜",
    "Deterrence": "威慑",
    "Disengage": "逃脱",
    "Dismiss Pet": "解散宠物",
    "Distracting Shot": "扰乱射击",
    "Eagle Eye": "鹰眼术",
    "Efficiency": "效率",
    "Endurance Training": "耐久训练",
    "Entrapment": "诱捕",
    "Expose Weakness": "破甲虚弱",
    "Explosive Shot": "爆炸射击",
    "Explosive Trap": "爆炸陷阱",
    "Explosive Trap Effect": "爆炸陷阱效果",
    "Feed Pet": "喂养宠物",
    "Feign Death": "假死",
    "Ferocious Inspiration": "凶猛灵感",
    "Ferocity": "凶暴",
    "Flare": "照明弹",
    "Focused Aim": "专注瞄准",
    "Focused Fire": "集中火力",
    "Freezing Arrow": "冰冻箭",
    "Freezing Arrow Effect": "冰冻箭效果",
    "Freezing Trap": "冰冻陷阱",
    "Frenzy": "狂乱",
    "Frost Trap": "冰霜陷阱",
    "Go for the Throat": "直取要害",
    "Hawk Eye": "鹰眼",
    "Humanoid Slaying": "人型生物杀手",
    "Hunter vs. Wild": "荒野猎手",
    "Hunter's Mark": "猎人印记",
    "Hunting Party": "狩猎小队",
    "Immolation Trap": "献祭陷阱",
    "Immolation Trap Effect": "献祭陷阱效果",
    "Improved Arcane Shot": "强化奥术射击",
    "Improved Aspect of the Hawk": "强化雄鹰守护",
    "Improved Aspect of the Monkey": "强化灵猴守护",
    "Improved Barrage": "强化弹幕",
    "Improved Concussive Shot": "强化震荡射击",
    "Improved Feign Death": "强化假死",
    "Improved Hunter's Mark": "强化猎人印记",
    "Improved Mend Pet": "强化治疗宠物",
    "Improved Revive Pet": "强化复活宠物",
    "Improved Steady Shot": "强化稳固射击",
    "Improved Stings": "强化钉刺",
    "Improved Tracking": "强化追踪",
    "Improved Wing Clip": "强化摔绊",
    "Increased Pet Talent": "宠物天赋点数提高",
    "Intimidation": "胁迫",
    "Invigoration": "鼓舞",
    "Kill Command": "杀戮命令",
    "Kill Shot": "杀戮射击",
    "Killer Instinct": "杀戮本能",
    "Kindred Spirits": "志趣相投",
    "Lethal Shots": "夺命射击",
    "Lightning Reflexes": "闪电反射",
    "Lock and Load": "荷枪实弹",
    "Longevity": "长寿",
    "Marked for Death": "死亡标记",
    "Master Marksman": "狙击高手",
    "Master Tactician": "战术大师",
    "Master's Call": "主人的召唤",
    "Melee Specialization": "近战专精",
    "Mend Pet": "治疗宠物",
    "Misdirection": "误导",
    "Monster Slaying": "怪物杀手",
    "Mongoose Bite": "猫鼬撕咬",
    "Mortal Shots": "致死射击",
    "Multi-Shot": "多重射击",
    "Noxious Stings": "毒性钉刺",
    "Pathfinding": "寻路",
    "Piercing Shots": "穿刺射击",
    "Point of No Escape": "无路可逃",
    "Ranged Weapon Specialization": "远程武器专精",
    "Rapid Fire": "急速射击",
    "Rapid Killing": "疾速杀戮",
    "Rapid Recuperation": "急速恢复",
    "Rapid Recuperation Effect": "急速恢复效果",
    "Raptor Strike": "猛禽一击",
    "Readiness": "准备就绪",
    "Resourcefulness": "足智多谋",
    "Revive Pet": "复活宠物",
    "Savage Strikes": "野蛮打击",
    "Scare Beast": "恐吓野兽",
    "Scorpid Sting": "蝎毒钉刺",
    "Scatter Shot": "驱散射击",
    "Serpent Sting": "毒蛇钉刺",
    "Serpent's Swiftness": "毒蛇迅捷",
    "Silencing Shot": "沉默射击",
    "Snake Trap": "毒蛇陷阱",
    "Sniper Training": "狙击训练",
    "Spirit Bond": "灵魂联结",
    "Steady Shot": "稳固射击",
    "Surefooted": "稳固",
    "Survival Instincts": "生存本能",
    "Survivalist": "生存专家",
    "Survival of the Fittest": "适者生存",
    "T.N.T.": "爆破专家",
    "Tame Beast": "驯服野兽",
    "The Beast Within": "野兽之心",
    "Thick Hide": "厚皮",
    "Thrill of the Hunt": "狩猎刺激",
    "Track Beasts": "追踪野兽",
    "Track Demons": "追踪恶魔",
    "Track Dragonkin": "追踪龙类",
    "Track Elementals": "追踪元素生物",
    "Track Giants": "追踪巨人",
    "Track Hidden": "追踪隐藏生物",
    "Track Humanoids": "追踪人型生物",
    "Track Undead": "追踪亡灵",
    "Trap Mastery": "陷阱掌握",
    "Tranquilizing Shot": "宁神射击",
    "Trueshot Aura": "强击光环",
    "Unleashed Fury": "狂怒释放",
    "Viper Sting": "蝰蛇钉刺",
    "Volley": "乱射",
    "Wild Quiver": "狂野箭袋",
    "Wild Quiver Auto Shot": "狂野箭袋自动射击",
    "Wing Clip": "摔绊",
    "Wyvern Sting": "翼龙钉刺",
}

TERM_FIXES = [
    ("Hunter's Mark", "猎人印记"),
    ("Arcane Shot", "奥术射击"),
    ("Aimed Shot", "瞄准射击"),
    ("Multi-Shot", "多重射击"),
    ("Serpent Sting", "毒蛇钉刺"),
    ("Viper Sting", "蝰蛇钉刺"),
    ("Scorpid Sting", "蝎毒钉刺"),
    ("Wyvern Sting", "翼龙钉刺"),
    ("Raptor Strike", "猛禽一击"),
    ("Mongoose Bite", "猫鼬撕咬"),
    ("Wing Clip", "摔绊"),
    ("Mend Pet", "治疗宠物"),
    ("Revive Pet", "复活宠物"),
    ("Dismiss Pet", "解散宠物"),
    ("Feign Death", "假死"),
    ("Immolation Trap", "献祭陷阱"),
    ("Explosive Trap", "爆炸陷阱"),
    ("Freezing Trap", "冰冻陷阱"),
    ("Frost Trap", "冰霜陷阱"),
    ("Snake Trap", "毒蛇陷阱"),
    ("Aspect of the Hawk", "雄鹰守护"),
    ("Aspect of the Monkey", "灵猴守护"),
    ("Aspect of the Cheetah", "猎豹守护"),
    ("Aspect of the Pack", "豹群守护"),
    ("Aspect of the Beast", "野兽守护"),
    ("Aspect of the Viper", "蝰蛇守护"),
    ("Aspect of the Dragonhawk", "龙鹰守护"),
    ("Aspect of the Wild", "野性守护"),
    ("Steady Shot", "稳固射击"),
    ("Kill Shot", "杀戮射击"),
    ("Explosive Shot", "爆炸射击"),
    ("Black Arrow", "黑箭"),
    ("Chimera Shot", "奇美拉射击"),
    ("Explosive Trap Effect", "爆炸陷阱效果"),
    ("Immolation Trap Effect", "献祭陷阱效果"),
    ("Nature damage", "自然伤害"),
    ("Fire damage", "火焰伤害"),
    ("Arcane damage", "奥术伤害"),
    ("Shadow damage", "暗影伤害"),
    ("ranged attack power", "远程攻击强度"),
    ("Ranged Attack Power", "远程攻击强度"),
    ("attack power", "攻击强度"),
    ("Attack Power", "攻击强度"),
    ("critical strike", "暴击"),
    ("Critical Strike", "暴击"),
    ("critical", "暴击"),
    ("Crit", "暴击"),
    ("damage", "伤害"),
    ("Damage", "伤害"),
    ("mana", "法力值"),
    ("Mana", "法力值"),
    ("threat", "威胁值"),
    ("Threat", "威胁值"),
    ("cooldown", "冷却时间"),
    ("Cooldown", "冷却时间"),
    ("Health", "生命值"),
    ("health", "生命值"),
    ("Stamina", "耐力"),
    ("Agility", "敏捷"),
    ("Intellect", "智力"),
    ("Spirit", "精神"),
    ("Strength", "力量"),
    ("Armor", "护甲"),
    ("armor", "护甲"),
    ("爆击", "暴击"),
    ("蛰刺", "钉刺"),
]

DURATION_BY_ID = {
    3355: "10秒",
    14308: "15秒",
    14309: "20秒",
    13797: "15秒",
    14298: "15秒",
    14299: "15秒",
    14300: "15秒",
    14301: "15秒",
    13810: "30秒",
    13812: "20秒",
    14314: "20秒",
    14315: "20秒",
    27025: "20秒",
    49064: "20秒",
    49065: "20秒",
    19185: "5秒",
    19229: "5秒",
    19574: "18秒",
    19577: "3秒",
    19578: "5秒",
    19579: "10秒",
    19580: "15秒",
    19581: "20秒",
    19582: "25秒",
    19583: "30秒",
    20337: "30秒",
    19386: "12秒",
    24131: "12秒",
    24132: "12秒",
    24133: "12秒",
    24134: "12秒",
    24135: "12秒",
    27068: "12秒",
    27069: "12秒",
    49009: "12秒",
    49010: "12秒",
    49011: "12秒",
    49012: "12秒",
    60053: "5秒",
    61846: "直到取消",
    61847: "直到取消",
}

DURATION_BY_NAME = {
    "Mend Pet": "15秒",
    "Eyes of the Beast": "1分钟",
    "Hunter's Mark": "5分钟",
    "Freezing Trap": "1分钟",
    "Freezing Arrow": "1分钟",
    "Flare": "20秒",
    "Serpent Sting": "15秒",
    "Viper Sting": "8秒",
    "Scorpid Sting": "20秒",
    "Wyvern Sting": "12秒",
    "Immolation Trap": "1分钟",
    "Explosive Trap": "1分钟",
    "Frost Trap": "1分钟",
    "Snake Trap": "1分钟",
    "Volley": "6秒",
    "Rapid Fire": "15秒",
    "Wing Clip": "10秒",
    "Concussive Shot": "4秒",
    "Aspect of the Pack": "直到取消",
    "Aspect of the Cheetah": "直到取消",
    "Aspect of the Hawk": "直到取消",
    "Aspect of the Monkey": "直到取消",
    "Aspect of the Beast": "直到取消",
    "Aspect of the Viper": "直到取消",
    "Aspect of the Dragonhawk": "直到取消",
    "Aspect of the Wild": "直到取消",
    "Feign Death": "6分钟",
    "Eagle Eye": "1分钟",
    "Scare Beast": "20秒",
    "Bestial Wrath": "18秒",
    "The Beast Within": "18秒",
    "Deterrence": "5秒",
    "Rapid Recuperation Effect": "6秒",
    "Misdirection": "30秒",
    "Master's Call": "4秒",
}

RADIUS_BY_NAME = {
    "Flare": 10,
    "Volley": 8,
    "Frost Trap": 10,
    "Explosive Trap": 10,
    "Aspect of the Pack": 40,
    "Aspect of the Wild": 40,
    "Trueshot Aura": 45,
}

SPECIAL_N = {
    2643: 3,
    14288: 3,
    14289: 3,
    14290: 3,
    25294: 3,
    27021: 3,
    49047: 3,
    49048: 3,
    49065: 10,
}

FORCE_GENERIC = set(NAME_ZH)
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


def rank_zh(rank: str) -> str:
    if not rank:
        return ""
    match = re.fullmatch(r"Rank (\d+)", rank)
    if match:
        return f"等级 {match.group(1)}"
    if rank == "Passive":
        return "被动"
    if rank == "Racial Passive":
        return "种族被动"
    return rank.replace("Rank", "等级").replace("Passive", "被动")


def duration(rec: SpellRec) -> str:
    return DURATION_BY_ID.get(rec.id) or DURATION_BY_NAME.get(rec.name) or ""


def radius(rec: SpellRec, index: int = 1) -> str:
    return str(RADIUS_BY_NAME.get(rec.name, 0) or rec.s(index))


def over_time(rec: SpellRec, n: int, source_text: str) -> str:
    if rec.name in ("Serpent Sting", "Black Arrow"):
        return str(rec.s(n) * 5)
    if rec.name in ("Immolation Trap Effect",):
        return str(rec.s(n) * 5)
    if rec.name in ("Explosive Trap Effect",):
        return str(rec.s(n) * 10)
    if rec.name == "Mend Pet":
        return str(rec.s(n) * 5)
    seconds = rec.amp_sec(n)
    dur = duration(rec)
    match = re.search(r"(\d+)", dur)
    if seconds and match:
        return str(rec.s(n) * int(match.group(1)) // seconds)
    return str(rec.s(n))


def replace_formulas(text: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    def val(spell_id: int, index: int, maxv: bool = False) -> int:
        target = records.get(spell_id)
        if not target:
            return 0
        return target.maxv(index) if maxv else target.s(index)

    text = re.sub(
        r"\$\{\$RAP\*0\.1\+\$(\d+)?m(\d+)\*5\}",
        lambda m: f"{val(int(m.group(1) or rec.id), int(m.group(2))) * 5}点加远程攻击强度10%",
        text,
    )
    text = re.sub(
        r"\$\{\$RAP\*0\.1\+\$(\d+)m(\d+)\}",
        lambda m: f"{val(int(m.group(1)), int(m.group(2)))}点加远程攻击强度10%",
        text,
    )
    text = re.sub(
        r"\$\{\$RAP\*0\.1\+\$(\d+)M(\d+)\}",
        lambda m: f"{val(int(m.group(1)), int(m.group(2)), True)}点加远程攻击强度10%",
        text,
    )
    text = re.sub(
        r"\$\{\$rap\*0\.15\+\$m(\d+)\}",
        lambda m: f"{rec.s(int(m.group(1)))}点加远程攻击强度15%",
        text,
    )
    text = re.sub(
        r"\$\{\$AP\*0\.2\+\$m(\d+)\}",
        lambda m: f"{rec.s(int(m.group(1)))}点加攻击强度20%",
        text,
    )
    text = re.sub(
        r"\$\{\$m(\d+)\+\$RAP\*0\.2\}",
        lambda m: f"{rec.s(int(m.group(1)))}点加远程攻击强度20%",
        text,
    )
    text = re.sub(
        r"\$\{\$m(\d+)\+\$RAP\*0\.4\}",
        lambda m: f"{rec.s(int(m.group(1)))}点加远程攻击强度40%",
        text,
    )
    text = re.sub(r"\$\{\$m(\d+)/10\}", lambda m: str(int(rec.s(int(m.group(1))) / 10)), text)
    text = re.sub(r"\$\{\$m(\d+)\*4\}", lambda m: str(rec.s(int(m.group(1))) * 4), text)
    text = re.sub(
        r"\$\{\$(\d+)m(\d+)\+\(\$m(\d+)\*30\)\}",
        lambda m: str(val(int(m.group(1)), int(m.group(2))) + rec.s(int(m.group(3))) * 30),
        text,
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
    text = re.sub(r"\$g([^:;]*):([^;]*);", lambda m: m.group(1) or m.group(2) or "", text)
    text = text.replace("$<threat>", "10")

    def ref_value(spell_id: int, token: str, number: str = "") -> str:
        target = records.get(spell_id)
        if not target:
            return ""
        index = int(number or "1")
        token = token.lower()
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
        if token in ("n", "i", "x"):
            return str(SPECIAL_N.get(spell_id, target.stack() or target.s(index) or 1))
        if token == "u":
            return str(target.stack() or SPECIAL_N.get(spell_id, target.s(index) or 1))
        return ""

    text = re.sub(
        r"\$/(\d+);(\d+)([A-Za-z])(\d*)",
        lambda m: str(int(int(ref_value(int(m.group(2)), m.group(3), m.group(4)) or 0) / int(m.group(1)))),
        text,
    )
    text = re.sub(
        r"\$/(\d+);([A-Za-z])(\d*)",
        lambda m: str(int(int(ref_value(rec.id, m.group(2), m.group(3)) or 0) / int(m.group(1)))),
        text,
    )
    text = re.sub(
        r"\$([0-9]+)([A-Za-z])(\d*)",
        lambda m: ref_value(int(m.group(1)), m.group(2), m.group(3)),
        text,
    )
    text = re.sub(r"\$s(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$m(\d*)", lambda m: str(rec.s(int(m.group(1) or "1"))), text, flags=re.I)
    text = re.sub(r"\$o(\d*)", lambda m: over_time(rec, int(m.group(1) or "1"), source_text), text, flags=re.I)
    text = re.sub(r"\$t(\d*)", lambda m: str(rec.amp_sec(int(m.group(1) or "1")) or 1), text, flags=re.I)
    text = re.sub(r"\$a(\d*)", lambda m: radius(rec, int(m.group(1) or "1")), text, flags=re.I)
    text = re.sub(r"\$x(\d*)", lambda _: str(SPECIAL_N.get(rec.id, rec.stack() or 1)), text, flags=re.I)
    text = text.replace("$d", duration(rec)).replace("$D", duration(rec))
    text = text.replace("$h", str(rec.h())).replace("$H", str(rec.h()))
    text = re.sub(r"\$[niu]", lambda _: str(rec.stack() or SPECIAL_N.get(rec.id, 1)), text, flags=re.I)
    text = re.sub(r"\$\*[\d.]+;[A-Za-z]\d*", "", text)
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
    for old, new in NAME_ZH.items():
        text = text.replace(old, new)
    text = text.replace("降低-", "降低").replace("提高-", "降低").replace("减少-", "减少")
    text = text.replace("有一定几率", "有几率")
    text = text.replace("他:她;", "")
    text = re.sub(r" +([，。；：、])", r"\1", text)
    text = re.sub(r"([（(]) +", r"\1", text)
    text = re.sub(r" +([）)])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.replace(" .", "。").replace(". ", "。").replace(".", "。")
    text = re.sub(r"(\d+)。(\d+)", r"\1.\2", text)
    text = text.replace(" ,", "，").replace(",", "，")
    return text.strip()


def rank_num(row: dict[str, str]) -> int:
    match = re.search(r"(\d+)", row.get("rank_en", ""))
    return int(match.group(1)) if match else 1


def generic_desc(row: dict[str, str], rec: SpellRec, records: dict[int, SpellRec]) -> str:
    name = row["name_en"]
    desc_en = row.get("description_en") or rec.desc
    desc = resolve_tokens(desc_en, rec, records)
    rank = rank_num(row)

    if name == "Auto Shot":
        return "自动射击目标，直到取消。"
    if name == "Call Pet":
        return "召唤你的宠物到身边。"
    if name == "Call Stabled Pet":
        return "召唤你兽栏中的宠物。"
    if name == "Revive Pet":
        return f"复活你的宠物，使其以 {rec.s(1)}% 的基础生命值重回战斗。"
    if name == "Mend Pet":
        return f"在 15 秒内为你的宠物恢复 {over_time(rec, 1, desc_en)} 点生命值。"
    if name == "Eyes of the Beast":
        return "直接控制你的宠物，并从它的视角观察世界，持续 1 分钟。"
    if name == "Beast Lore":
        return "收集目标野兽的信息，显示其伤害、生命值、护甲和抗性，以及饮食偏好。"
    if name.startswith("Track "):
        target = NAME_ZH.get(name, name).replace("追踪", "")
        return f"在小地图上显示附近{target}的位置。"
    if name == "Dismiss Pet":
        return f"解散你的宠物。解散宠物会使其快乐值降低 {abs(rec.s(1)) // 1000 if abs(rec.s(1)) >= 1000 else abs(rec.s(1))} 点。"
    if name == "Tame Beast":
        return f"开始驯服一只野兽作为你的伙伴。在 20 秒驯服期间，你的护甲值降低 {abs(records.get(1515, rec).s(3))}%。如果你失去野兽的注意力，驯服会失败。"
    if name == "Feed Pet":
        return "用食物喂养你的宠物，使其恢复生命值并提高快乐值。"
    if name == "Flare":
        return "照亮目标区域，使 10 码范围内所有潜行和隐形的敌人显形，持续 20 秒。"
    if name == "Eagle Eye":
        return "拉近猎人的视野。只能在户外使用，持续 1 分钟。"
    if name == "Feign Death":
        return "假装死亡，可能欺骗敌人使其忽略你，最多持续 6 分钟。"
    if name == "Disengage":
        return "在战斗中尝试脱离目标，降低威胁值并向后跃开。必须站在地面上。"
    if name == "Readiness":
        return "激活后，立即结束你其它猎人技能的冷却时间。"
    if name == "Rapid Fire":
        return f"使远程攻击速度提高 {rec.s(1)}%，持续 15 秒。"
    if name == "Concussive Shot":
        return f"使目标眩晕，移动速度降低 {abs(rec.s(1))}%，持续 4 秒。"
    if name == "Distracting Shot":
        return "扰乱目标，造成威胁值。等级越高效果越强。"
    if name == "Scare Beast":
        return f"恐吓一只野兽，使其因恐惧逃跑，最多持续 {duration(rec) or '20秒'}。伤害可能打断该效果。同一时间只能恐吓一只野兽。"
    if name == "Tranquilizing Shot":
        return "尝试从敌方目标身上移除 1 个狂乱效果。"
    if name == "Misdirection":
        return "将你接下来 30 秒内造成的威胁值转移给目标小队或团队成员，从下一次攻击开始生效，最多持续 4 秒。"
    if name == "Master's Call":
        return "你的宠物协助一个友方目标，移除并免疫所有移动限制效果，持续 4 秒。"

    if name == "Raptor Strike":
        return f"一次强力攻击，使近战伤害提高 {rec.s(1)} 点。"
    if name == "Wing Clip":
        return f"造成 {rec.s(2)} 点伤害，并使敌方目标移动速度降低 {abs(rec.s(1))}%，持续 10 秒。"
    if name == "Mongoose Bite":
        return f"反击敌人，造成 {rec.s(1)} 点加攻击强度 20% 的伤害。只能在你躲闪后使用。"
    if name == "Counterattack":
        return f"招架后可用的反击，造成 {rec.s(1)} 点伤害，并使目标无法移动，持续 5 秒。"
    if name == "Arcane Shot":
        dispel = f"，并驱散 {rec.s(1)} 个魔法效果" if rec.s(1) > 1 and rank >= 6 else ""
        amount = rec.s(2) if rank >= 6 else rec.s(1)
        return f"一次瞬发射击，造成 {amount} 点加远程攻击强度 15% 的奥术伤害{dispel}。"
    if name == "Serpent Sting":
        total = rec.s(1) * 5
        return f"钉刺目标，在 15 秒内造成 {total} 点加远程攻击强度 10% 的自然伤害。每个猎人在同一目标身上只能激活一种钉刺。"
    if name == "Viper Sting":
        return f"钉刺目标，在 8 秒内吸取 {over_time(rec, 1, desc_en)} 点法力值。每个猎人在同一目标身上只能激活一种钉刺。"
    if name == "Scorpid Sting":
        return f"钉刺目标，使其近战和远程攻击命中几率降低 {abs(rec.s(1))}%，持续 20 秒。每个猎人在同一目标身上只能激活一种钉刺。"
    if name == "Aimed Shot":
        return f"一次瞄准射击，造成远程武器伤害再加 {rec.s(1)} 点伤害，并使目标受到的治疗效果降低 50%，持续 10 秒。"
    if name == "Multi-Shot":
        extra = f"，并造成额外 {rec.s(1)} 点伤害" if rec.s(1) > 1 else ""
        return f"发射多枚弹药，最多击中 {SPECIAL_N.get(rec.id, 3)} 个目标{extra}。"
    if name == "Volley":
        effect_id = {1: 42243, 2: 42244, 3: 42245, 4: 42234, 5: 58431, 6: 58434}.get(rank, 42243)
        dmg = records.get(effect_id, rec).s(1)
        return f"向目标区域持续射出大量弹药，持续 6 秒，每秒对 8 码范围内的敌方目标造成 {dmg} 点奥术伤害。"
    if name == "Steady Shot":
        return f"一次稳定射击，造成 {rec.s(1)} 点加远程攻击强度 20% 的伤害。若目标受到眩晕效果影响，额外造成 {rec.s(2)} 点伤害。"
    if name == "Kill Shot":
        return f"尝试终结受伤目标，造成 {rec.s(1)} 点加远程攻击强度 40% 的伤害。只能对生命值低于 20% 的敌人使用。"
    if name == "Kill Command":
        return f"下达杀戮命令，使你的宠物立即攻击并造成 {rec.s(1)} 点额外伤害。只能在猎人对目标造成暴击后使用。"
    if name == "Silencing Shot":
        return f"射击敌人，造成 {rec.s(1)}% 武器伤害并使其沉默 3 秒。"
    if name == "Chimera Shot":
        return "造成 125% 武器伤害，并根据目标身上的钉刺刷新或触发额外效果。"
    if name == "Explosive Shot":
        return f"发射爆炸弹药，对目标造成 {rec.s(1)} 点火焰伤害，并在接下来 2 秒内每秒额外造成一次火焰伤害。"
    if name == "Black Arrow":
        return f"向目标射出黑箭，使你对其造成的所有伤害提高 {rec.s(2)}%，并在 15 秒内造成 {rec.s(1) * 5} 点加远程攻击强度 10% 的暗影伤害。黑箭与陷阱类法术共用冷却时间。"

    if name == "Freezing Trap":
        freeze = {1: "10秒", 2: "15秒", 3: "20秒"}.get(rank, "20秒")
        return f"放置冰霜陷阱，冻结第一个靠近的敌人，使其无法行动，最多持续 {freeze}。任何伤害都会打破冰冻。陷阱存在 1 分钟。同一时间只能激活一个陷阱。"
    if name == "Freezing Arrow":
        return "发射冰冻箭，在目标位置放置冰冻陷阱。第一个靠近的敌人会被冻结，最多持续 20 秒。任何伤害都会打破冰冻。同一时间只能激活一个陷阱。"
    if name == "Frost Trap":
        return "放置冰霜陷阱，第一个敌人靠近时生成冰霜区域，持续 30 秒。区域内 10 码范围的所有敌人移动速度降低 60%。陷阱存在 1 分钟。同一时间只能激活一个陷阱。"
    if name == "Immolation Trap":
        effect_id = {1: 13797, 2: 14298, 3: 14299, 4: 14300, 5: 14301, 6: 27024, 7: 49053, 8: 49054, 9: 60192, 10: 60202, 11: 60210}.get(rank, 13797)
        eff = records.get(effect_id, rec)
        return f"放置火焰陷阱，使第一个靠近的敌人在 15 秒内受到 {eff.s(1) * 5} 点加远程攻击强度 10% 的火焰伤害。陷阱存在 1 分钟。同一时间只能激活一个陷阱。"
    if name == "Immolation Trap Effect":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点火焰伤害。"
    if name == "Explosive Trap":
        effect_id = {1: 13812, 2: 14314, 3: 14315, 4: 27025, 5: 49064, 6: 49065}.get(rank, 13812)
        eff = records.get(effect_id, rec)
        return f"放置火焰陷阱，敌人靠近时爆炸，对 10 码范围内所有敌人造成 {eff.s(1)} 到 {eff.maxv(1)} 点加远程攻击强度 10% 的火焰伤害，并在 20 秒内额外造成 {eff.s(2) * 10} 点火焰伤害。陷阱存在 1 分钟。同一时间只能激活一个陷阱。"
    if name == "Explosive Trap Effect":
        return f"每 {rec.amp_sec(2) or 2} 秒造成 {rec.s(2)} 点火焰伤害。"
    if name == "Snake Trap":
        return "放置毒蛇陷阱，第一个敌人靠近时会召唤多条毒蛇攻击目标。陷阱存在 1 分钟。同一时间只能激活一个陷阱。"
    if name == "Wyvern Sting":
        dot = {1: 24131, 2: 24134, 3: 24135, 4: 27069, 5: 49009, 6: 49010}.get(rank, rec.id)
        effect = records.get(dot, rec)
        tick = effect.s(1) if effect.s(1) > 1 else rec.s(1)
        return f"射出带刺箭矢，使目标沉睡，最多持续 12 秒。任何伤害都会取消沉睡。当目标醒来时，钉刺会在 12 秒内造成 {tick * 6} 点自然伤害。每个猎人同一目标只能激活一种钉刺。"

    if name == "Aspect of the Hawk":
        return f"猎人获得雄鹰守护，远程攻击强度提高 {rec.s(1)} 点。同一时间只能激活一种守护。"
    if name == "Aspect of the Monkey":
        return f"猎人获得灵猴守护，躲闪几率提高 {rec.s(1)}%。同一时间只能激活一种守护。"
    if name == "Aspect of the Cheetah":
        return f"猎人获得猎豹守护，移动速度提高 {rec.s(1)}%。如果猎人受到攻击，会眩晕 4 秒。同一时间只能激活一种守护。"
    if name == "Aspect of the Pack":
        return f"猎人和 40 码范围内的小队及团队成员获得豹群守护，移动速度提高 {rec.s(1)}%。如果受到攻击，会眩晕 4 秒。同一时间只能激活一种守护。"
    if name == "Aspect of the Beast":
        return "猎人获得野兽守护，无法被追踪。同一时间只能激活一种守护。"
    if name == "Aspect of the Viper":
        return "猎人获得蝰蛇守护，每 5 秒恢复法力值，恢复量随智力、等级和当前法力值缺口提高。同一时间只能激活一种守护。"
    if name == "Aspect of the Dragonhawk":
        dodge = rec.s(3) if rec.s(2) <= 1 else rec.s(2)
        return f"猎人获得龙鹰守护，远程攻击强度提高 {rec.s(1)} 点，躲闪几率提高 {dodge}%。同一时间只能激活一种守护。"
    if name == "Aspect of the Wild":
        return f"猎人与 40 码范围内的小队及团队成员获得野性守护，自然抗性提高 {rec.s(1)} 点。同一时间只能激活一种守护。"
    if name == "Trueshot Aura":
        return f"使 45 码范围内所有小队和团队成员的攻击强度提高 {rec.s(1)} 点。"
    if name == "Bestial Wrath":
        return f"使你的宠物进入狂怒状态，造成的伤害提高 {rec.s(1)}%，持续 18 秒。狂怒期间宠物不会感到怜悯、懊悔或恐惧，除非被杀死，否则无法停止。"
    if name == "Intimidation":
        return "命令你的宠物胁迫目标，在下一次成功近战攻击时造成大量威胁值并使目标昏迷 3 秒。"
    if name == "Deterrence":
        return "激活后使你的招架几率提高 100%，远程和法术攻击未命中你的几率提高 100%，持续 5 秒。"
    if name == "Scatter Shot":
        return "短程射击，造成 50% 武器伤害并使目标迷惑 4 秒。任何伤害都会取消该效果。使用后会停止你的攻击。"

    simple = simple_talent_desc(name, rec, row, records)
    if simple:
        return simple

    if CJK_RE.search(desc) and not re.search(r"[A-Za-z]{3,}", desc):
        return desc
    return f"{NAME_ZH.get(name, name)}。"


def simple_talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rank = rank_num(row)
    if name == "Improved Aspect of the Hawk":
        return f"当雄鹰守护或龙鹰守护激活时，你的普通远程攻击有 10% 几率使远程攻击速度提高 {rec.s(1)}%，持续 12 秒。"
    if name == "Endurance Training":
        return f"使你的宠物总生命值提高 {rec.s(1)}%，你的总生命值提高 {rec.s(2)}%。"
    if name == "Focused Fire":
        return f"当你的宠物存活时，你造成的所有伤害提高 {rec.s(1)}%。你的杀戮命令暴击几率提高 {rec.s(2)}%。"
    if name == "Thick Hide":
        return f"使你的宠物护甲提高 {rec.s(1)}%，你从装备获得的护甲值提高 {rec.s(2)}%。"
    if name == "Improved Revive Pet":
        return f"使你的复活宠物施法时间缩短 {abs(rec.s(1)) // 1000} 秒，法力消耗降低 {abs(rec.s(2))}%，宠物复活后的生命值提高 {rec.s(3)}%。"
    if name == "Pathfinding":
        return f"使你的猎豹守护和豹群守护提供的速度加成提高 {rec.s(1)}%，骑乘速度提高 {rec.s(2)}%。"
    if name == "Aspect Mastery":
        return "使蝰蛇守护的法力恢复惩罚降低，灵猴守护和龙鹰守护的躲闪加成提高，雄鹰守护和龙鹰守护的攻击强度加成提高。"
    if name == "Unleashed Fury":
        return f"使你的宠物造成的伤害提高 {rec.s(1)}%。"
    if name == "Improved Mend Pet":
        return f"使治疗宠物的法力消耗降低 {abs(rec.s(1))}%，并有 {rec.s(2)}% 几率每跳驱散宠物身上的 1 个诅咒、疾病、魔法或中毒效果。"
    if name == "Ferocity":
        return f"使你的宠物暴击几率提高 {rec.s(1)}%。"
    if name == "Spirit Bond":
        return f"当你的宠物激活时，你和宠物每 10 秒恢复总生命值的 {rec.s(1)}%，并使你受到的治疗效果提高 {rec.s(2)}%。"
    if name == "Intimidation":
        return "命令你的宠物胁迫目标，在下一次成功近战攻击时造成大量威胁值并使目标昏迷 3 秒。"
    if name == "Bestial Discipline":
        return f"使你的宠物集中值回复速度提高 {rec.s(1)}%。"
    if name == "Animal Handler":
        return f"使你的宠物攻击强度提高 {rec.s(1)}%，并使你的召唤宠物冷却时间缩短 {abs(rec.s(2))} 秒。"
    if name == "Frenzy":
        return f"你的宠物造成暴击后，有 {rec.s(1)}% 几率使其攻击速度提高 30%，持续 8 秒。"
    if name == "Ferocious Inspiration":
        return f"你的宠物造成暴击后，所有小队和团队成员造成的所有伤害提高 {rec.s(1)}%，持续 10 秒。"
    if name == "Catlike Reflexes":
        return f"使你的躲闪几率提高 {rec.s(1)}%，并使宠物躲闪几率提高 {rec.s(2)}%。"
    if name == "Serpent's Swiftness":
        return f"使你的远程攻击速度提高 {rec.s(1)}%，宠物近战攻击速度提高 {rec.s(2)}%。"
    if name == "The Beast Within":
        return "当你的宠物在狂野怒火影响下时，你也会进入狂怒状态，造成的伤害提高 10%，所有法术法力消耗降低 20%，持续 18 秒。"
    if name == "Cobra Strikes":
        return f"你的奥术射击、稳固射击和杀戮射击造成暴击后，有 {rec.h()}% 几率使宠物接下来 2 次特殊攻击必定暴击。"
    if name == "Kindred Spirits":
        return f"使你和宠物造成的伤害提高 {rec.s(1)}%，并使你的宠物移动速度提高 {rec.s(2)}%。"
    if name == "Beast Mastery":
        return "你掌握野兽训练，获得 4 点额外宠物天赋点数，并可以驯服奇异野兽。"
    if name == "Increased Pet Talent":
        return f"使你的宠物获得 {rec.s(1)} 点额外天赋点数。"

    if name == "Lethal Shots":
        return f"使你的远程武器暴击几率提高 {rec.s(1)}%。"
    if name == "Improved Hunter's Mark":
        return f"使你的猎人印记提供的远程攻击强度加成提高 {rec.s(1)}%，并使猎人印记无法被驱散。"
    if name == "Efficiency":
        return f"使你的射击和钉刺技能法力消耗降低 {abs(rec.s(1))}%。"
    if name == "Go for the Throat":
        return f"你的远程自动攻击暴击后，使你的宠物获得 {rec.s(1)} 点集中值。"
    if name == "Improved Arcane Shot":
        return f"使你的奥术射击冷却时间缩短 {abs(rec.s(1)) / 1000:g} 秒。"
    if name == "Aimed Shot":
        return generic_desc(row, rec, records)
    if name == "Rapid Killing":
        return f"使你的急速射击冷却时间缩短 {rank} 分钟。此外，杀死能提供经验或荣誉值的敌人后，你的下一次瞄准射击、奥术射击或奇美拉射击伤害提高 {rec.s(1)}%，持续 20 秒。"
    if name == "Improved Stings":
        return f"使你的毒蛇钉刺和翼龙钉刺造成的伤害提高 {rec.s(1)}%，蝰蛇钉刺吸取的法力值提高 {rec.s(2)}%，并使你的钉刺被驱散的几率降低 {rec.s(3)}%。"
    if name == "Mortal Shots":
        return f"使你的远程技能暴击伤害加成提高 {rec.s(1)}%。"
    if name == "Concussive Barrage":
        if rec.id == 35101:
            return "目标眩晕，持续 4 秒。"
        return f"你的奇美拉射击和多重射击命中目标后，有 {rec.h()}% 几率使目标眩晕 4 秒。"
    if name == "Barrage":
        return f"使你的多重射击、瞄准射击和乱射伤害提高 {rec.s(1)}%。"
    if name == "Combat Experience":
        return f"使你的敏捷和智力提高 {rec.s(1)}%。"
    if name == "Ranged Weapon Specialization":
        return f"使你的远程武器伤害提高 {rec.s(1)}%。"
    if name == "Careful Aim":
        return f"使你的远程攻击强度提高，数值相当于你智力总值的 {rec.s(1)}%。"
    if name == "Piercing Shots":
        return f"你的瞄准射击、稳固射击和奇美拉射击暴击后，会使目标在 8 秒内流血，造成相当于该次伤害 {rec.s(1)}% 的伤害。"
    if name == "Trueshot Aura":
        return generic_desc(row, rec, records)
    if name == "Improved Barrage":
        return f"使你的多重射击和瞄准射击暴击几率提高 {rec.s(1)}%，乱射受到伤害打断的几率降低 {rec.s(2)}%。"
    if name == "Master Marksman":
        return f"使你的远程暴击几率提高 {rec.s(1)}%，并使稳固射击、瞄准射击和奇美拉射击的法力消耗降低 {abs(rec.s(2))}%。"
    if name == "Rapid Recuperation":
        return f"急速射击影响期间，每 3 秒恢复 {rec.s(1)}% 法力值；获得疾速杀戮效果后，每 2 秒恢复 {rec.s(2)}% 法力值，持续 6 秒。"
    if name == "Wild Quiver":
        return f"你的远程自动攻击有 {rec.h()}% 几率发射额外一箭，造成 {rec.s(1)}% 武器伤害。"
    if name == "Silencing Shot":
        return generic_desc(row, rec, records)
    if name == "Improved Steady Shot":
        return f"你的稳固射击命中后有 {rec.h()}% 几率使下一次瞄准射击、奥术射击或奇美拉射击造成的伤害提高 {rec.s(1)}%，法力消耗降低 {abs(rec.s(2))}%。"
    if name == "Marked for Death":
        return f"使你的射击和宠物特殊技能伤害提高 {rec.s(1)}%，并使瞄准射击、奥术射击、杀戮射击和奇美拉射击对被猎人印记标记目标的暴击伤害加成提高 {rec.s(2)}%。"
    if name == "Chimera Shot":
        return generic_desc(row, rec, records)

    if name == "Improved Tracking":
        return f"当你追踪野兽、恶魔、龙类、元素、巨人、人型生物或亡灵时，对这些类型目标造成的所有伤害提高 {rec.s(1)}%。"
    if name == "Hawk Eye":
        return f"使你的远程武器射程提高 {rec.s(1)} 码。"
    if name == "Savage Strikes":
        return f"使猛禽一击和猫鼬撕咬的暴击几率提高 {rec.s(1)}%。"
    if name == "Surefooted":
        return f"使你的移动限制效果持续时间缩短 {abs(rec.s(1))}%，并使命中几率提高 {rec.s(2)}%。"
    if name == "Entrapment":
        if rec.id == 19185:
            return "目标无法移动，持续 5 秒。"
        return f"使你的献祭陷阱、冰霜陷阱、爆炸陷阱和毒蛇陷阱有 {rec.h()}% 几率诱捕目标，使其无法移动，持续 5 秒。"
    if name == "Trap Mastery":
        return f"使你的冰霜陷阱和冰冻陷阱被抵抗的几率降低 {abs(rec.s(1))}%，献祭陷阱、爆炸陷阱和黑箭造成的周期性伤害提高 {rec.s(2)}%。"
    if name == "Survival Instincts":
        return f"使你受到的所有伤害降低 {abs(rec.s(1))}%，并使奥术射击、稳固射击和爆炸射击的暴击几率提高 {rec.s(2)}%。"
    if name == "Survivalist":
        return f"使你的总生命值提高 {rec.s(1)}%。"
    if name == "Deflection":
        return f"使你的招架几率提高 {rec.s(1)}%。"
    if name == "Survival of the Fittest":
        return f"使你的所有属性提高 {rec.s(1)}%，并使你被暴击的几率降低 {abs(rec.s(2))}%。"
    if name == "T.N.T.":
        return f"使你的爆炸射击、爆炸陷阱、黑箭和献祭陷阱伤害提高 {rec.s(2)}%。"
    if name == "Lock and Load":
        return f"你的冰冻陷阱、冰冻箭和冰霜陷阱触发时有 {rec.h()}% 几率，使接下来 2 次奥术射击或爆炸射击不触发冷却、不消耗法力且不消耗弹药。"
    if name == "Resourcefulness":
        return f"使所有陷阱和黑箭的法力消耗降低 {abs(rec.s(1))}%，冷却时间缩短 {abs(rec.s(2)) // 1000} 秒。"
    if name == "Killer Instinct":
        return f"使所有攻击的暴击几率提高 {rec.s(1)}%。"
    if name == "Noxious Stings":
        return f"如果你的毒蛇钉刺在目标身上，你对其造成的所有伤害提高 {rec.s(1)}%；你的翼龙钉刺被驱散时也会使驱散者沉睡 {rec.s(2)} 秒。"
    if name == "Point of No Escape":
        return f"对受到你的冰冻陷阱、冰冻箭或冰霜陷阱影响的目标，你的所有攻击暴击几率提高 {rec.s(1)}%。"
    if name == "Thrill of the Hunt":
        return f"你的爆炸射击、奥术射击、瞄准射击和黑箭造成暴击时，有 {rec.h()}% 几率返还该技能基础法力消耗的 40%。"
    if name == "Counterattack":
        return generic_desc(row, rec, records)
    if name == "Lightning Reflexes":
        return f"使你的敏捷提高 {rec.s(1)}%。"
    if name == "Expose Weakness":
        if rec.id == 34501:
            return "所有攻击者对该目标获得攻击强度加成。"
        return f"你的远程暴击有 {rec.h()}% 几率使你的攻击强度提高，数值相当于你敏捷的 25%，持续 7 秒。"
    if name == "Hunting Party":
        return f"使你的敏捷总值提高 {rec.s(1)}%。你的奥术射击、爆炸射击和稳固射击暴击后，有 {rec.h()}% 几率使最多 10 名小队或团队成员每秒恢复 1% 最大法力值，持续 15 秒。"
    if name == "Sniper Training":
        return f"站定 6 秒后，你的杀戮射击、瞄准射击、稳固射击和爆炸射击伤害提高 {rec.s(1)}%，持续 15 秒。杀戮射击的暴击几率提高 {rec.s(2)}%。"
    if name == "Hunter vs. Wild":
        return f"使你和宠物的攻击强度与远程攻击强度提高，数值相当于你总耐力的 {rec.s(1)}%。"
    if name == "Black Arrow":
        return generic_desc(row, rec, records)
    if name == "Master Tactician":
        return f"你的远程攻击命中后有 6% 几率使所有攻击的暴击几率提高 {rec.s(1)}%，持续 8 秒。"
    if name == "Rapid Recuperation Effect":
        return "每 3 秒恢复 1% 法力值。"
    if name == "Wild Quiver Auto Shot":
        return "向目标发射额外一箭，造成 80% 武器伤害。"
    if name == "Freezing Arrow Effect":
        return "目标被冻结，无法行动。"

    if name == "Monster Slaying":
        return f"对野兽、巨人和龙类目标造成的所有伤害提高 {rec.s(1)}%，对这些目标造成的暴击伤害额外提高 {rec.s(2)}%。"
    if name == "Humanoid Slaying":
        return f"对人型生物目标造成的所有伤害提高 {rec.s(1)}%，对这些目标造成的暴击伤害额外提高 {rec.s(2)}%。"
    if name == "Melee Specialization":
        return f"使猛禽一击、猫鼬撕咬、反击和摔绊造成的伤害提高 {rec.s(1)}%。"
    if name == "Improved Concussive Shot":
        return f"你的震荡射击有 {rec.h()}% 几率使目标昏迷 3 秒。"
    if name == "Improved Wing Clip":
        return f"你的摔绊有 {rec.h()}% 几率使目标无法移动，持续 5 秒。"
    if name == "Improved Aspect of the Monkey":
        return f"使你的灵猴守护提供的躲闪几率加成提高 {rec.s(1)}%。"
    if name == "Clever Traps":
        return f"使你的冰冻陷阱和冰霜陷阱效果持续时间提高 {rec.s(1)}%，献祭陷阱和爆炸陷阱效果伤害提高 {rec.s(2)}%，毒蛇陷阱召唤的毒蛇数量提高 {rec.s(2)}%。"
    if name == "Improved Feign Death":
        return f"使你的假死被抵抗的几率降低 {abs(rec.s(1))}%。"
    if name == "Focused Aim":
        return f"使你的稳固射击施法时因受到伤害而损失的施法时间缩短 {abs(rec.s(1))}%，并使命中几率提高 {rec.s(2)}%。"
    if name == "Invigoration":
        return f"当你的宠物特殊技能造成暴击时，你有 {rec.s(1)}% 几率立即恢复 {records[53398].s(1)}% 法力值。"
    if name == "Longevity":
        return f"使你的狂野怒火、胁迫和宠物特殊技能冷却时间缩短 {abs(rec.s(1))}%。"

    return ""


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    if name == "Auto Shot":
        return "正在射击目标。"
    if name == "Eyes of the Beast":
        return "正在直接控制宠物。"
    if name == "Beast Lore":
        return "已显示野兽信息。"
    if name.startswith("Track "):
        return f"正在{NAME_ZH.get(name, name)}。"
    if name == "Tame Beast":
        return "正在驯服宠物。"
    if name == "Flare":
        return "潜行和隐形单位会被显形。"
    if name == "Scare Beast":
        return "被恐惧。"
    if name == "Feign Death":
        return "正在假死。"
    if name == "Aspect of the Cheetah":
        return f"移动速度提高 {rec.s(1)}%。受到攻击时会眩晕。"
    if name == "Aspect of the Pack":
        return f"移动速度提高 {rec.s(1)}%。受到攻击时会眩晕。"
    if name == "Aspect of the Beast":
        return "无法被追踪。"
    if name == "Aspect of the Viper":
        return "正在恢复法力值。"
    if name == "Immolation Trap":
        effect_id = {1: 13797, 2: 14298, 3: 14299, 4: 14300, 5: 14301, 6: 27024, 7: 49053, 8: 49054, 9: 60192, 10: 60202, 11: 60210}.get(rank_num(row), rec.id)
        eff = records.get(effect_id, rec)
        return f"每 {eff.amp_sec(1) or 3} 秒造成 {eff.s(1)} 点火焰伤害。"
    if name == "Immolation Trap Effect":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点火焰伤害。"
    if name == "Explosive Trap Effect":
        return f"每 {rec.amp_sec(2) or 2} 秒造成 {rec.s(2)} 点火焰伤害。"
    if name == "Black Arrow":
        return f"受到的所有伤害提高 {rec.s(2)}%，每 {rec.amp_sec(1) or 3} 秒受到 {rec.s(1)} 点暗影伤害。"
    if name == "Entrapment":
        return "无法移动。"
    if name == "Deterrence":
        return "躲闪和招架几率提高。"
    if name == "Counterattack":
        return "无法移动。"
    if name == "Wyvern Sting":
        if rec.s(1) > 1 and rec.amp_sec(1):
            return f"每 {rec.amp_sec(1)} 秒造成 {rec.s(1)} 点自然伤害。"
        return "正在沉睡。"
    if name == "Aimed Shot":
        return "受到的治疗效果降低 50%。"
    if name == "Scatter Shot":
        return "迷惑。"
    if name == "Trueshot Aura":
        return f"攻击强度提高 {rec.s(1)} 点。"
    if name == "Bestial Wrath":
        return "激怒。"
    if name == "Intimidation":
        return "被胁迫。"
    if name == "Spirit Bond":
        return f"每 10 秒恢复总生命值的 {rec.s(1)}%。"
    if name == "The Beast Within":
        return "激怒。"
    if name == "Misdirection":
        return "正在转移威胁值。"
    if name == "Silencing Shot":
        return "沉默。"
    if name == "Expose Weakness":
        return "所有攻击者对该目标获得攻击强度加成。"
    if name == "Master Tactician":
        return f"所有攻击的暴击几率提高 {rec.s(1)}%。"
    if name == "Rapid Killing":
        return f"下一次瞄准射击、奥术射击或奇美拉射击伤害提高 {rec.s(1)}%。"
    if name == "Concussive Barrage":
        return "眩晕。"
    if name == "Improved Steady Shot":
        return f"瞄准射击、奥术射击或奇美拉射击造成的伤害提高 {rec.s(1)}%，法力消耗降低 {abs(rec.s(2))}%。"
    if name == "Rapid Recuperation Effect":
        return "每 3 秒恢复 1% 法力值。"
    if name == "Wild Quiver Auto Shot":
        return "向目标发射额外一箭，造成 80% 武器伤害。"
    if name == "Lock and Load":
        return "接下来的奥术射击或爆炸射击不触发冷却时间、不消耗法力值，也不消耗弹药。"
    if name == "Explosive Shot":
        return "每秒受到火焰伤害。"
    if name == "Freezing Arrow Effect":
        return "被冻结。"
    if name == "Call Stabled Pet":
        return "选择一个兽栏中的宠物来替换当前宠物。"
    if name == "Mend Pet":
        return f"每 {rec.amp_sec(1) or 3} 秒恢复 {rec.s(1)} 点生命值。"
    if name == "Serpent Sting":
        return f"每 {rec.amp_sec(1) or 3} 秒造成 {rec.s(1)} 点自然伤害。"
    if name == "Viper Sting":
        return f"每 {rec.amp_sec(1) or 2} 秒吸取 {rec.s(1)} 点法力值。"
    if name == "Scorpid Sting":
        return f"近战和远程攻击命中几率降低 {abs(rec.s(1))}%。"
    if name == "Wing Clip":
        return f"移动速度降低 {abs(rec.s(1))}%。"
    if name == "Concussive Shot":
        return f"移动速度降低 {abs(rec.s(1))}%。"
    if name == "Rapid Fire":
        return f"远程攻击速度提高 {rec.s(1)}%。"
    if name == "Aspect of the Hawk":
        return f"远程攻击强度提高 {rec.s(1)} 点。"
    if name == "Aspect of the Monkey":
        return f"躲闪几率提高 {rec.s(1)}%。"
    if name == "Aspect of the Dragonhawk":
        dodge = rec.s(3) if rec.s(2) <= 1 else rec.s(2)
        return f"远程攻击强度提高 {rec.s(1)} 点，躲闪几率提高 {dodge}%。"
    if name == "Aspect of the Wild":
        return f"自然抗性提高 {rec.s(1)} 点。"
    if name == "Hunter's Mark":
        mark = mark_values(row, rec, records)
        return f"所有攻击者对该目标的远程攻击强度提高 {mark[0]} 点，每次远程攻击命中后额外提高 {mark[1]} 点，最高 {mark[2]} 点。"
    source = row.get("tooltip_en") or rec.aura
    return resolve_tokens(source, rec, records)


def mark_values(row: dict[str, str], rec: SpellRec, records: dict[int, SpellRec]) -> tuple[int, int, int]:
    linked = {1: 84535, 2: 84536, 3: 84537, 4: 84538, 5: 53338}.get(rank_num(row), rec.id)
    target = records.get(linked, rec)
    base = target.s(2)
    step = rec.s(2)
    if rec.id in (1130, 14323, 14324, 14325):
        step = rec.s(2)
    if step <= 1:
        step = max(1, base // 10)
    return base, step, base + step * 30


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    name = row["name_en"]
    if name == "Hunter's Mark":
        base, step, cap = mark_values(row, rec, records)
        return f"在目标身上施加猎人印记，使所有攻击者对该目标的远程攻击强度提高 {base} 点。每次被远程攻击命中后，远程攻击强度额外提高 {step} 点，最高 {cap} 点。此外，猎人始终可以看见该目标，即使目标潜行或隐形；目标也会显示在小地图上。持续 5 分钟。"
    return cleanup(generic_desc(row, rec, records))


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


def is_hunter(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & HUNTER_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_hunter(row):
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
        if is_hunter(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or re.search(r"[A-Za-z]{3,}", row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority hunter rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"hunter spell ids synced: {len(updates)}")
    print(f"hunter zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:30]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
