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

PRIEST_SKILLS = {"56", "78", "613"}
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")

NAME_ZH = {
    "Absolution": "赦免", "Abolish Disease": "驱除疾病", "Aspiration": "志向",
    "Binding Heal": "联结治疗", "Blackout": "昏厥", "Bless Water": "祝福之水",
    "Blessed Healing": "神圣治疗", "Blessed Recovery": "神圣恢复",
    "Blessed Resilience": "神圣韧性", "Body and Soul": "身心合一",
    "Borrowed Time": "借来的时光", "Circle of Healing": "治疗之环",
    "Clearcasting": "节能施法", "Cure Disease": "祛病术", "Darkness": "黑暗",
    "Desperate Prayer": "绝望祷言", "Devouring Plague": "噬灵瘟疫",
    "Dispersion": "消散", "Dispel Magic": "驱散魔法", "Divine Aegis": "神圣庇护",
    "Divine Fury": "神圣之怒", "Divine Hymn": "神圣赞美诗",
    "Divine Providence": "神圣眷顾", "Divine Spirit": "神圣之灵",
    "Empowered Healing": "强化治疗", "Empowered Renew": "强化恢复",
    "Enlightenment": "启迪", "Fade": "渐隐术", "Fear Ward": "防护恐惧结界",
    "Flash Heal": "快速治疗", "Focused Casting": "专注施法",
    "Focused Mind": "专注意志", "Focused Power": "专注之力",
    "Focused Will": "坚定意志", "Force of Will": "意志之力",
    "Glyph of Dispel Magic": "驱散魔法雕文",
    "Glyph of Power Word: Shield": "真言术：盾雕文",
    "Glyph of Prayer of Healing": "治疗祷言雕文", "Grace": "优雅",
    "Greater Heal": "强效治疗术", "Guardian Spirit": "守护之魂",
    "Heal": "治疗术", "Healing Prayers": "治疗祷言",
    "Holy Concentration": "神圣专注", "Holy Fire": "神圣之火",
    "Holy Focus": "神圣专注", "Holy Nova": "神圣新星",
    "Holy Reach": "神圣延伸", "Holy Specialization": "神圣专精",
    "Hymn of Hope": "希望圣歌", "Improved Devouring Plague": "强化噬灵瘟疫",
    "Improved Divine Spirit": "强化神圣之灵", "Improved Fade": "强化渐隐术",
    "Improved Flash Heal": "强化快速治疗", "Improved Healing": "强化治疗术",
    "Improved Inner Fire": "强化心灵之火", "Improved Mana Burn": "强化法力燃烧",
    "Improved Mind Blast": "强化心灵震爆",
    "Improved Power Word: Fortitude": "强化真言术：韧",
    "Improved Power Word: Shield": "强化真言术：盾",
    "Improved Psychic Scream": "强化心灵尖啸",
    "Improved Renew": "强化恢复", "Improved Shadow Word: Pain": "强化暗言术：痛",
    "Improved Shadowform": "强化暗影形态",
    "Improved Vampiric Embrace": "强化吸血鬼的拥抱",
    "Inner Fire": "心灵之火", "Inner Focus": "心灵专注", "Inspiration": "灵感",
    "Lesser Heal": "次级治疗术", "Levitate": "漂浮术", "Lightwell": "光明之泉",
    "Lightwell Renew": "光明之泉恢复", "Mana Burn": "法力燃烧",
    "Martyrdom": "殉难", "Mass Dispel": "群体驱散", "Meditation": "冥想",
    "Mental Agility": "精神敏锐", "Mental Strength": "心灵之力",
    "Mind Blast": "心灵震爆", "Mind Control": "精神控制",
    "Mind Flay": "精神鞭笞", "Mind Sear": "精神灼烧",
    "Mind Soothe": "安抚心灵", "Mind Vision": "心灵视界",
    "Misery": "悲惨", "Pain and Suffering": "痛苦与折磨",
    "Pain Suppression": "痛苦压制", "Penance": "苦修",
    "Power Infusion": "能量灌注", "Power Word: Barrier": "真言术：障",
    "Power Word: Fortitude": "真言术：韧", "Power Word: Shield": "真言术：盾",
    "Prayer of Fortitude": "坚韧祷言", "Prayer of Healing": "治疗祷言",
    "Prayer of Mending": "愈合祷言", "Prayer of Shadow Protection": "暗影防护祷言",
    "Prayer of Spirit": "精神祷言", "Psychic Horror": "心灵恐惧",
    "Psychic Scream": "心灵尖啸", "Rapture": "狂喜", "Reflective Shield": "反射护盾",
    "Renew": "恢复", "Renewed Hope": "新生希望", "Resurrection": "复活术",
    "Searing Light": "灼热之光", "Serendipity": "好运", "Shackle Undead": "束缚亡灵",
    "Shadow Affinity": "暗影亲和", "Shadow Focus": "暗影集中",
    "Shadow Power": "暗影之力", "Shadow Protection": "暗影防护",
    "Shadow Reach": "暗影延伸", "Shadow Resilience": "暗影韧性",
    "Shadow Weaving": "暗影交织", "Shadow Word: Death": "暗言术：灭",
    "Shadow Word: Pain": "暗言术：痛", "Shadowfiend": "暗影魔",
    "Shadowform": "暗影形态", "Silence": "沉默", "Silent Resolve": "无声消退",
    "Smite": "惩击", "Soul Warding": "灵魂护盾", "Spell Warding": "法术屏障",
    "Spirit Tap": "精神分流", "Spirit of Redemption": "救赎之魂",
    "Spiritual Guidance": "精神指引", "Spiritual Healing": "精神治疗",
    "Surge of Light": "圣光涌动", "Test of Faith": "信仰试炼",
    "Twin Disciplines": "双生戒律", "Twisted Faith": "扭曲信仰",
    "Unbreakable Will": "坚定意志", "Vampiric Embrace": "吸血鬼的拥抱",
    "Vampiric Touch": "吸血鬼之触", "Wand Specialization": "魔杖专精",
}

TERM_FIXES = [
    ("Priest", "牧师"), ("priest", "牧师"), ("Holy", "神圣"), ("Discipline", "戒律"),
    ("Shadow", "暗影"), ("Power Word: Shield", "真言术：盾"),
    ("Power Word: Fortitude", "真言术：韧"), ("Power Word: Barrier", "真言术：障"),
    ("Shadow Word: Pain", "暗言术：痛"), ("Shadow Word: Death", "暗言术：灭"),
    ("Renew", "恢复"), ("Smite", "惩击"), ("Flash Heal", "快速治疗"),
    ("Greater Heal", "强效治疗术"), ("Lesser Heal", "次级治疗术"), ("Heal", "治疗术"),
    ("Prayer of Healing", "治疗祷言"), ("Prayer of Mending", "愈合祷言"),
    ("Mind Blast", "心灵震爆"), ("Mind Flay", "精神鞭笞"), ("Mind Sear", "精神灼烧"),
    ("Devouring Plague", "噬灵瘟疫"), ("Vampiric Touch", "吸血鬼之触"),
    ("Vampiric Embrace", "吸血鬼的拥抱"), ("Shadowfiend", "暗影魔"),
    ("spell power", "法术强度"), ("Spell Power", "法术强度"), ("damage", "伤害"),
    ("Damage", "伤害"), ("healing", "治疗"), ("Healing", "治疗"), ("health", "生命值"),
    ("Health", "生命值"), ("mana", "法力值"), ("Mana", "法力值"), ("armor", "护甲"),
    ("Armor", "护甲"), ("Spirit", "精神"), ("Stamina", "耐力"), ("Intellect", "智力"),
    ("resistance", "抗性"), ("Shadow", "暗影"), ("Holy", "神圣"), ("critical strike", "暴击"),
    ("critical", "暴击"), ("haste", "急速"), ("threat", "威胁值"), ("cooldown", "冷却时间"),
    ("stun", "昏迷"), ("Stun", "昏迷"), ("Fear", "恐惧"), ("Silence", "沉默"),
    ("Disease", "疾病"), ("disease", "疾病"), ("Humanoid", "人型生物"),
    ("Undead", "亡灵"), ("movement speed", "移动速度"), ("party and raid", "小队和团队"),
    ("party or raid", "小队或团队"), ("friendly target", "友方目标"), ("friendly", "友方"),
    ("enemy", "敌人"), ("enemies", "敌人"), ("caster", "施法者"), ("yards", "码"),
    ("yard", "码"), ("seconds", "秒"), ("sec.", "秒"), ("爆击", "暴击"),
]

DURATION_BY_NAME = {
    "Abolish Disease": "20秒", "Blessed Healing": "6秒", "Blessed Recovery": "6秒",
    "Blessed Resilience": "6秒", "Borrowed Time": "6秒", "Body and Soul": "4秒",
    "Clearcasting": "15秒", "Devouring Plague": "24秒", "Dispersion": "6秒",
    "Divine Aegis": "12秒", "Divine Hymn": "8秒", "Divine Spirit": "30分钟",
    "Fade": "10秒", "Fear Ward": "3分钟", "Focused Casting": "6秒",
    "Focused Will": "8秒", "Grace": "15秒", "Guardian Spirit": "10秒",
    "Holy Fire": "7秒", "Hymn of Hope": "8秒", "Inner Fire": "30分钟",
    "Levitate": "10分钟", "Lightwell": "3分钟", "Lightwell Renew": "6秒",
    "Mind Control": "1分钟", "Mind Flay": "3秒", "Mind Sear": "5秒",
    "Mind Soothe": "15秒", "Mind Vision": "1分钟", "Pain Suppression": "8秒",
    "Power Infusion": "15秒", "Power Word: Barrier": "10秒",
    "Power Word: Fortitude": "30分钟", "Power Word: Shield": "30秒",
    "Prayer of Fortitude": "1小时", "Prayer of Mending": "30秒",
    "Prayer of Shadow Protection": "1小时", "Prayer of Spirit": "1小时",
    "Psychic Horror": "3秒", "Psychic Scream": "8秒", "Renew": "15秒",
    "Renewed Hope": "20秒", "Shadow Protection": "10分钟",
    "Shadow Weaving": "15秒", "Shadow Word: Pain": "18秒",
    "Shadowfiend": "15秒", "Shadowform": "直到取消", "Shackle Undead": "50秒",
    "Silence": "5秒", "Spirit of Redemption": "15秒", "Spirit Tap": "15秒",
    "Vampiric Embrace": "1分钟", "Vampiric Touch": "15秒",
    "光井": "3分钟", "动力注入": "15秒", "吸血鬼之拥": "1分钟",
    "心灵鞭笞": "3秒", "沉默": "5秒", "疼痛抑制": "8秒",
    "吸血鬼之触": "15秒", "真言术：屏障": "10秒",
}

ID_DURATION = {
    6788: "15秒", 10872: "20秒", 14743: "6秒", 14893: "15秒", 15258: "15秒",
    15269: "3秒", 15271: "15秒", 27813: "6秒", 27817: "6秒", 27818: "6秒",
    27827: "15秒", 27873: "6秒", 33143: "6秒", 33151: "10秒", 34754: "15秒",
    41635: "30秒", 44416: "8秒", 45237: "8秒", 47585: "6秒", 47753: "12秒",
    47930: "15秒", 48045: "5秒", 60069: "1秒", 63853: "12秒", 63944: "20秒",
    64058: "10秒", 64128: "4秒", 64844: "8秒", 64904: "8秒", 55680: "6秒",
    70772: "6秒",
}

RADIUS_BY_NAME = {
    "Circle of Healing": 15, "Divine Hymn": 40, "Holy Nova": 10, "Hymn of Hope": 40,
    "Mass Dispel": 15, "Mind Sear": 10, "Prayer of Healing": 30, "Power Word: Barrier": 10,
    "Psychic Scream": 8,
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
    return DURATION_BY_NAME.get(rec.name, DURATION_BY_NAME.get(NAME_ZH.get(rec.name, ""), "持续时间"))


def duration_seconds(rec: SpellRec, fallback: int = 1) -> int:
    text = duration(rec)
    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    value = int(match.group(1))
    if "小时" in text:
        return value * 3600
    if "分钟" in text:
        return value * 60
    return value


def over_time(rec: SpellRec, n: int, ticks: int | None = None) -> int:
    if ticks is None:
        seconds = rec.amp_sec(n) or 3
        ticks = max(1, duration_seconds(rec, seconds) // seconds)
    return rec.s(n) * ticks


def positive(value: int) -> int:
    return abs(value)


def ms(value: int) -> str:
    return f"{abs(value) / 1000:g}"


def chance(rec: SpellRec, fallback: int = 100) -> int:
    return rec.h() if 0 <= rec.h() <= 100 else fallback


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
        return str(RADIUS_BY_NAME.get(target.name) or target.s(index) or 30)
    if token == "q":
        return str(abs(target.q(index)))
    if token in ("u", "n", "i", "x"):
        return str(target.stack() or target.s(index) or 1)
    if token == "h":
        return str(chance(target))
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
    text = re.sub(r"(伤害|治疗|恢复|吸收|拥有|以|为)-(\d)", r"\1\2", text)
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
    text = text.replace("$h1", str(chance(rec))).replace("$h", str(chance(rec))).replace("$H", str(chance(rec)))
    return cleanup(text)


def ability_desc(name: str, rec: SpellRec, records: dict[int, SpellRec]) -> str:
    if name == "Power Word: Shield":
        return f"为友方目标施加护盾，吸收 {rec.s(1)} 点伤害，持续 {duration(rec)}。护盾存在时，受到伤害不会打断施法。目标获得护盾后，在 {duration(records.get(6788, rec))} 内无法再次获得真言术：盾。"
    if name == "Renew":
        return f"在 {duration(rec)} 内为目标恢复 {over_time(rec, 1)} 点生命值。"
    if name == "Mind Soothe":
        return f"安抚目标，使其攻击你的范围缩小 {positive(rec.s(1))} 码。只影响指定等级或以下的人型生物，持续 {duration(rec)}。"
    if name == "Dispel Magic":
        return f"驱散目标身上的魔法，移除友方目标身上 {rec.s(1)} 个有害法术，或敌方目标身上 {rec.s(1)} 个有益法术。"
    if name == "Cure Disease":
        return f"移除友方目标身上的 {rec.s(1)} 个疾病效果。"
    if name == "Abolish Disease":
        return f"尝试移除目标身上的 {rec.s(2)} 个疾病效果，并在 {duration(rec)} 内每 {rec.amp_sec(1) or 5} 秒额外尝试移除 {records.get(10872, rec).s(1)} 个疾病效果。"
    if name == "Smite":
        return f"惩击敌人，造成 {rec.s(1)} 点神圣伤害。"
    if name == "Fade":
        return f"渐隐，使敌人在 {duration(rec)} 内不太可能攻击你。"
    if name == "Inner Fire":
        parts = [f"护甲提高 {rec.s(1)} 点"]
        if rec.s(2) > 1:
            parts.append(f"法术强度提高 {rec.s(2)} 点")
        return f"神圣能量充满施法者，使{'，'.join(parts)}。每次受到近战或远程伤害会移除一层效果，持续 {duration(rec)}，或直到 {rec.stack() or 20} 层效果耗尽。"
    if name == "Shadow Word: Pain":
        return f"黑暗咒语，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害。"
    if name == "Prayer of Healing":
        return f"强大的祷言，为 {RADIUS_BY_NAME['Prayer of Healing']} 码内的小队成员恢复 {rec.s(1)} 点生命值。"
    if name == "Mind Control":
        return f"控制最高 {rec.s(1)} 级的人型生物心智，但使其攻击间隔延长 {positive(rec.s(3))}%。最多持续 {duration(rec)}。"
    if name == "Shadow Protection":
        return f"使目标的暗影抗性提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Power Word: Fortitude":
        return f"为目标注入力量，使耐力提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Levitate":
        return f"使施法者漂浮在离地数尺的位置。漂浮时坠落速度降低，并可以在水面上行走，持续 {duration(rec)}。受到伤害会取消效果。"
    if name == "Resurrection":
        return f"使死亡玩家复活，并使其拥有 {rec.s(1)} 点生命值和 {abs(rec.q(1))} 点法力值。无法在战斗中施放。"
    if name in {"Lesser Heal", "Heal", "Greater Heal", "Flash Heal", "Desperate Prayer"}:
        target = "施法者" if name == "Desperate Prayer" else "友方目标"
        return f"为{target}恢复 {rec.s(1)} 点生命值。"
    if name == "Binding Heal":
        return f"为一个友方目标和施法者各恢复 {rec.s(1)} 点生命值，产生较低威胁值。"
    if name == "Mind Vision":
        return f"使施法者透过目标的眼睛观察世界，持续 {duration(rec)}。"
    if name == "Devouring Plague":
        return f"使目标感染疾病，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害。噬灵瘟疫造成的伤害会治疗施法者。"
    if name == "Fear Ward":
        return f"守护友方目标，使下一次作用于目标的恐惧效果失败并消耗结界，持续 {duration(rec)}。"
    if name == "Lightwell Renew":
        return f"在 {duration(rec)} 内为目标恢复 {over_time(rec, 1)} 点生命值。"
    if name == "Mind Blast":
        return f"冲击目标，造成 {rec.s(1)} 点暗影伤害。"
    if name == "Psychic Scream":
        return f"施法者发出心灵尖啸，使 {RADIUS_BY_NAME['Psychic Scream']} 码内最多 {rec.q(1)} 个敌人逃跑，持续 {duration(rec)}。造成伤害可能打断效果。"
    if name == "Mana Burn":
        return f"摧毁目标 {rec.s(1)} 点法力值，并按摧毁法力值的 50% 对其造成暗影伤害。"
    if name == "Shackle Undead":
        return f"束缚亡灵敌人，最多持续 {duration(rec)}。被束缚的单位无法移动、攻击或施法，任何伤害都会解除效果。同一时间只能束缚一个目标。"
    if name == "Power Infusion":
        return f"为目标注入能量，使施法速度提高 {rec.s(1)}%，所有法术的法力值消耗降低 {positive(rec.s(2))}%，持续 {duration(rec)}。"
    if name == "Divine Spirit":
        return f"神圣力量注入目标，使精神提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Holy Fire":
        return f"以神圣火焰吞噬敌人，造成 {rec.s(1)} 点神圣伤害，并在 {duration(rec)} 内额外造成 {over_time(rec, 2)} 点神圣伤害。"
    if name == "Holy Nova":
        heal = records.get(23455, rec).s(1)
        return f"在施法者周围爆发神圣之光，对 {RADIUS_BY_NAME['Holy Nova']} 码内敌人造成 {rec.s(1)} 点神圣伤害，并为 {RADIUS_BY_NAME['Holy Nova']} 码内小队成员恢复 {heal} 点生命值。这些效果不会产生威胁值。"
    if name == "Vampiric Embrace":
        return f"以暗影能量感染目标，使你对其造成的单体暗影法术伤害有 {rec.s(1)}% 转化为小队成员的治疗，持续 {duration(rec)}。"
    if name == "Mind Flay":
        if rec.id == 58381:
            base = records.get(48156, rec)
            return f"以暗影能量攻击目标心智，在 {duration(base)} 内造成 {base.s(3) * 3} 点暗影伤害，并使其移动速度降低 {positive(base.s(2))}%。必须引导。"
        return f"以暗影能量攻击目标心智，在 {duration(rec)} 内造成 {over_time(rec, 1)} 点暗影伤害，并使其移动速度降低 {positive(rec.s(2))}%。必须引导。"
    if name == "Shadowform":
        return f"进入暗影形态，使你的暗影伤害提高 {rec.s(2)}%，受到的物理伤害降低 {positive(rec.s(3))}%。该形态下不能施放神圣法术。"
    if name == "Silence":
        return f"使目标沉默，无法施法，持续 {duration(rec)}。"
    if name == "Spirit of Redemption":
        return f"总精神提高 {records.get(20711, rec).s(2)}%。死亡时，牧师化为救赎之魂，持续 {duration(records.get(27827, rec))}。救赎之魂期间无法移动、攻击、被攻击或成为任何法术目标，但可以免费施放治疗法术。效果结束后牧师死亡。"
    if name == "Prayer of Fortitude":
        return f"为小队和团队成员注入力量，使耐力提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Prayer of Spirit":
        return f"为小队和团队成员注入力量，使精神提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Prayer of Shadow Protection":
        return f"为小队和团队成员注入力量，使暗影抗性提高 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name == "Lightwell":
        return f"制造一口神圣光明之泉，持续 {duration(rec)}。团队或小队成员可点击光明之泉，在 {duration(records.get(27873, rec))} 内恢复 {over_time(records.get(27873, rec), 1)} 点生命值。受到直接伤害会取消该治疗效果。光明之泉拥有 {rec.q(1)} 次使用次数。"
    if name == "Mass Dispel":
        return f"驱散 {RADIUS_BY_NAME['Mass Dispel']} 码范围内的魔法，最多从每个友方目标身上移除 {rec.s(1)} 个有害法术，并从每个敌方目标身上移除 {rec.s(1)} 个有益法术。可移除通常无法驱散的强力魔法效果。"
    if name == "Shadow Word: Death":
        return f"以黑暗束缚之语冲击目标，造成 {rec.s(1)} 点暗影伤害。如果目标未被暗言术：灭杀死，施法者会受到等量伤害。"
    if name == "Prayer of Mending":
        if rec.s(1) <= 0:
            return f"愈合祷言治疗后跳转到附近的小队或团队成员身上，持续 {duration(records.get(41635, rec))}。"
        return f"在目标身上放置法术，使其下一次受到伤害时恢复 {rec.s(1)} 点生命值。治疗发生后，愈合祷言会跳转到 {rec.s(3)} 码内的一个小队或团队成员身上，最多跳转 {rec.s(2)} 次，持续 {duration(records.get(41635, rec))}。"
    if name == "Shadowfiend":
        return f"制造暗影魔攻击目标。暗影魔造成伤害时，施法者获得法力值。持续 {duration(rec)}。"
    if name == "Circle of Healing":
        return f"治疗友方目标及其周围 {RADIUS_BY_NAME['Circle of Healing']} 码内的小队成员，恢复 {rec.s(1)} 点生命值。"
    if name == "Penance":
        damage_by_rank = {1: 47666, 2: 52998, 3: 52999, 4: 53000}
        heal_by_rank = {1: 47750, 2: 52983, 3: 52984, 4: 52985}
        rank_match = re.search(r"(\d+)", rec.rank or "")
        rank = int(rank_match.group(1)) if rank_match else 1
        for known_id, known_rank in {
            47666: 1, 47750: 1, 47757: 1, 47758: 1,
            52983: 2, 52986: 2, 52998: 2, 53001: 2, 53005: 2,
            52984: 3, 52987: 3, 52999: 3, 53002: 3, 53006: 3,
            52985: 4, 52988: 4, 53000: 4, 53003: 4, 53007: 4,
        }.items():
            if rec.id == known_id:
                rank = known_rank
                break
        heal = records.get(heal_by_rank.get(rank, 47750), rec)
        dmg = records.get(damage_by_rank.get(rank, 47666), rec)
        return f"向目标发射神圣光芒。对敌方目标立即造成 {dmg.s(1)} 点神圣伤害，并每 1 秒再次造成一次伤害，持续 2 秒；对友方目标立即恢复 {heal.s(1)} 点生命值，并每 1 秒再次治疗一次，持续 2 秒。"
    if name == "Dispersion":
        return f"化为纯粹暗影能量，使受到的所有伤害降低 {positive(records.get(47585, rec).s(1))}%。期间无法攻击或施法，但每 {records.get(60069, rec).amp_sec(1) or 1} 秒恢复 {records.get(60069, rec).s(1)}% 法力值。持续 {duration(rec)}。可在昏迷、恐惧或沉默时施放，并解除移动限制和移动速度降低效果。"
    if name == "Guardian Spirit":
        return f"召唤守护之魂守护友方目标，使目标受到的治疗效果提高 {rec.s(1)}%，并在目标即将死亡时牺牲自身使其恢复最大生命值的 {rec.s(2)}%。持续 {duration(rec)}。"
    if name == "Mind Sear":
        pulse = records.get(49821, rec)
        return f"在敌方目标周围引发暗影爆炸，每 1 秒对其 {RADIUS_BY_NAME['Mind Sear']} 码内所有敌人造成 {pulse.s(1)} 点暗影伤害，持续 {duration(records.get(48045, rec))}。必须引导。"
    if name == "Vampiric Touch":
        return f"在 {duration(rec)} 内对目标造成 {over_time(rec, 2)} 点暗影伤害，并使所有小队成员获得法力值，数值相当于你造成的暗影法术伤害的 {rec.s(1)}%。"
    if name == "Divine Hymn":
        heal = records.get(64844, rec)
        return f"每 {rec.amp_sec(1) or 2} 秒为 {RADIUS_BY_NAME['Divine Hymn']} 码内生命值最低的 {rec.s(2)} 个友方小队或团队目标恢复 {heal.s(1)} 点生命值，并使其受到的治疗效果提高 {heal.s(2)}%，持续 {duration(rec)}。必须引导。"
    if name == "Hymn of Hope":
        mana = records.get(64904, rec)
        return f"每 {rec.amp_sec(1) or 2} 秒为 {RADIUS_BY_NAME['Hymn of Hope']} 码内法力值最低的 {rec.s(2)} 个友方小队或团队目标恢复 {mana.s(1)}% 法力值，并使其最大法力值提高 {mana.s(2)}%，持续 {duration(rec)}。必须引导。"
    if name == "Psychic Horror":
        return f"恐吓目标，使其因恐惧而颤抖 {duration(rec)}，并缴械 {duration(records.get(64058, rec))}。"
    if name == "Blessed Healing":
        return f"在 {duration(rec)} 内为目标持续恢复生命值。"
    if name == "Bless Water":
        return "向清水注入力量，将其转化为弱效圣水。"
    if name == "Power Word: Barrier":
        return f"在施法者周围创造屏障，为屏障内所有小队和团队成员吸收伤害，总量最多 {rec.s(1)} 点，持续 {duration(rec)}。"
    if name.startswith("Glyph of "):
        return talent_desc(name, rec, {}, records)
    return ""


def talent_desc(name: str, rec: SpellRec, row: dict[str, str], records: dict[int, SpellRec]) -> str:
    table = {
        "Mental Agility": f"使你的瞬发法术法力值消耗降低 {positive(rec.s(1))}%。",
        "Meditation": f"使你在施法时仍保持 {rec.s(1)}% 的法力恢复。",
        "Unbreakable Will": f"使你抵抗昏迷、恐惧和沉默效果的几率额外提高 {rec.s(1)}%。",
        "Silent Resolve": f"使你的神圣和戒律法术产生的威胁值降低 {positive(rec.s(1))}%，并使你的法术被驱散的几率降低 {rec.s(2)}%。",
        "Wand Specialization": f"使你的魔杖伤害提高 {rec.s(1)}%。",
        "Martyrdom": f"受到近战或远程暴击后，有 {chance(rec, 50)}% 几率获得专注施法效果，持续 {duration(records.get(14743, rec))}，并使你抵抗施法打断的几率提高 {records.get(14743, rec).s(2)}%。",
        "Focused Casting": f"施放后，受到伤害不会延长施法时间，持续 {duration(rec)}。",
        "Improved Inner Fire": f"使心灵之火提供的护甲加成提高 {rec.s(1)}%，并使其可承受的攻击次数增加 {rec.s(2)} 次。",
        "Improved Power Word: Shield": f"使真言术：盾吸收的伤害提高 {rec.s(1)}%。",
        "Improved Power Word: Fortitude": f"使真言术：韧和坚韧祷言的效果提高 {rec.s(1)}%。",
        "Improved Mana Burn": f"使法力燃烧的施法时间缩短 {ms(rec.s(1))} 秒。",
        "Inner Focus": f"激活后，下一个法术的法力值消耗降低 {positive(rec.s(1))}%，暴击几率提高 {rec.s(2)}%。",
        "Holy Specialization": f"使你的神圣法术暴击几率提高 {rec.s(1)}%。",
        "Inspiration": f"你的快速治疗、治疗术、强效治疗术、联结治疗、苦修、愈合祷言或治疗之环造成暴击后，使目标护甲提高 {records.get(14893, rec).s(1)}%，持续 {duration(records.get(14893, rec))}。",
        "Spiritual Healing": f"使你的治疗法术效果提高 {rec.s(1)}%。",
        "Spiritual Guidance": f"使法术伤害和治疗效果提高，最多相当于你的总精神值的 {rec.s(1)}%。",
        "Improved Renew": f"使恢复的治疗量提高 {rec.s(1)}%。",
        "Searing Light": f"使惩击和神圣之火造成的伤害提高 {rec.s(1)}%。",
        "Shadow Resilience": f"使你被所有法术暴击的几率降低 {positive(rec.s(1))}%。",
        "Healing Prayers": f"使治疗祷言和愈合祷言的法力值消耗降低 {positive(rec.s(1))}%。",
        "Improved Healing": f"使次级治疗术、治疗术和强效治疗术的法力值消耗降低 {positive(rec.s(1))}%。",
        "Holy Focus": f"使你施放任何神圣法术时有 {rec.s(1)}% 几率避免因受到伤害而被打断。",
        "Shadow Weaving": f"你的暗影伤害法术有 {rec.s(1)}% 几率使目标易受暗影伤害，受到的暗影伤害提高 {records.get(15258, rec).s(1)}%。最多叠加 {records.get(15258, rec).stack() or 5} 次，持续 {duration(records.get(15258, rec))}。",
        "Darkness": f"使你的暗影法术伤害提高 {rec.s(1)}%。",
        "Shadow Focus": f"使目标抵抗你的暗影法术的几率降低 {rec.s(1)}%。",
        "Blackout": f"你的暗影伤害法术有 {chance(rec, 2)}% 几率使目标昏迷 {duration(records.get(15269, rec))}。",
        "Spirit Tap": f"你杀死可获得经验值或荣誉值的目标后，有 {chance(rec, 20)}% 几率使精神提高 {records.get(15271, rec).s(1)}%，施法时的法力恢复提高 {records.get(15271, rec).s(2)}%，持续 {duration(records.get(15271, rec))}。",
        "Shadow Affinity": f"使你的暗影法术产生的威胁值降低 {positive(rec.s(1))}%。",
        "Improved Mind Blast": f"使心灵震爆的冷却时间缩短 {ms(rec.s(1))} 秒。",
        "Improved Fade": f"使渐隐术的冷却时间缩短 {ms(rec.s(1))} 秒。",
        "Improved Shadow Word: Pain": f"使暗言术：痛的时长延长 {ms(rec.s(1))} 秒。",
        "Improved Psychic Scream": f"使心灵尖啸的冷却时间缩短 {ms(rec.s(1))} 秒。",
        "Shadow Reach": f"使你的攻击性暗影法术射程延长 {rec.s(1)}%。",
        "Divine Fury": f"使惩击、神圣之火、治疗术和强效治疗术的施法时间缩短 {ms(rec.s(1))} 秒。",
        "Force of Will": f"使你的法术伤害提高 {rec.s(2)}%，攻击性法术暴击几率提高 {rec.s(1)}%。",
        "Mental Strength": f"使你的最大法力值提高 {rec.s(1)}%。",
        "Holy Reach": f"使惩击和神圣之火的射程，以及治疗祷言、神圣新星、神圣赞美诗和治疗之环的作用半径提高 {rec.s(1)}%。",
        "Blessed Recovery": f"受到近战或远程暴击后，在 {duration(records.get(27813, rec))} 内恢复相当于所受伤害 {rec.s(1)}% 的生命值。",
        "Improved Vampiric Embrace": f"使吸血鬼的拥抱的治疗比例额外提高 {rec.s(1)}%。",
        "Spell Warding": f"使你受到的所有法术伤害降低 {positive(rec.s(1))}%。",
        "Blessed Resilience": f"受到暴击后有 {chance(rec, 20)}% 几率在 {duration(records.get(33143, rec))} 内免疫再次被暴击。",
        "Surge of Light": f"你的法术暴击有 {chance(rec, 25)}% 几率使下一次惩击或快速治疗变为瞬发、法力值消耗降低 {positive(records.get(33151, rec).s(1))}%，但无法造成暴击。效果持续 {duration(records.get(33151, rec))}。",
        "Empowered Healing": f"强效治疗术额外获得治疗加成 {rec.s(1)}% 的收益，快速治疗和联结治疗额外获得 {rec.s(2)}% 的收益。",
        "Absolution": f"使驱散魔法、祛病术、驱除疾病和群体驱散的法力值消耗降低 {positive(rec.s(1))}%。",
        "Improved Divine Spirit": f"使神圣之灵和精神祷言的效果提高 {rec.s(3)}%，并使目标获得相当于其精神值 {rec.s(1)}% 的法术强度。",
        "Focused Power": f"使心灵震爆、群体驱散和伤害性神圣法术的暴击几率提高 {rec.s(2)}%，并使群体驱散的施法时间缩短 {ms(rec.s(1))} 秒。",
        "Misery": f"暗言术：痛、精神鞭笞和吸血鬼之触还会使目标受到法术命中的几率提高 {rec.s(1) // 100}%，并使你的法术获得相当于精神值 {rec.s(2) // 100}% 的额外伤害加成。",
        "Reflective Shield": f"使真言术：盾吸收伤害的 {rec.s(1)}% 反射给攻击者。该伤害不会产生威胁值。",
        "Pain Suppression": f"立即使友方目标的威胁值降低 {positive(records.get(44416, rec).s(1))}%，受到的所有伤害降低 {positive(rec.s(1))}%，抵抗驱散机制的几率提高 {rec.s(2)}%，持续 {duration(rec)}。",
        "Focused Mind": f"使心灵震爆、精神控制和精神鞭笞的法力值消耗降低 {positive(rec.s(1))}%。",
        "Shadow Power": f"使心灵震爆和暗言术：灭的暴击几率提高 {rec.s(1)}%。",
        "Holy Concentration": f"施放快速治疗、联结治疗或强效治疗术后，有 {chance(rec, 2)}% 几率进入节能施法状态，使下一次快速治疗、联结治疗或强效治疗术的法力值消耗降低 {positive(records.get(34754, rec).s(1))}%。",
        "Clearcasting": f"使下一次快速治疗、联结治疗或强效治疗术的法力值消耗降低 {positive(rec.s(1))}%。",
        "Enlightenment": f"使你的总耐力、智力和精神提高 {rec.s(1)}%。",
        "Focused Will": f"受到暴击后，你获得坚定意志效果，受到的所有伤害降低，受到的治疗效果提高。持续 {duration(records.get(45237, rec))}。",
        "Aspiration": f"使心灵专注、能量灌注、痛苦压制和苦修的冷却时间缩短 {positive(rec.s(1))}%。",
        "Divine Aegis": f"治疗法术暴击会在目标身上产生保护护盾，吸收相当于治疗量 {rec.s(1)}% 的伤害，持续 {duration(records.get(47753, rec))}。",
        "Grace": f"快速治疗、强效治疗术和苦修有 {chance(rec, 50)}% 几率祝福目标，使其受到你的治疗效果提高 {rec.s(1)}%。最多叠加 {rec.stack() or 3} 次，持续 {duration(records.get(47930, rec))}。",
        "Rapture": f"你的真言术：盾被完全吸收或驱散时，立即恢复总法力值的 {rec.s(1)}%，目标获得 {rec.s(2)}% 的法力值、{rec.s(2) / 10:g} 点怒气、{rec.s(2)} 点能量或 {rec.s(2) / 10:g} 点符文能量。该效果每 {duration(records.get(63853, rec))} 最多触发一次。",
        "Test of Faith": f"对生命值不高于 50% 的友方目标治疗效果提高 {rec.s(1)}%。",
        "Divine Providence": f"使治疗之环、联结治疗、神圣新星、愈合祷言、神圣赞美诗和苦修的治疗效果提高 {rec.s(1)}%，并使愈合祷言的冷却时间缩短 {positive(rec.s(3))} 秒。",
        "Improved Shadowform": f"渐隐术现在有 {rec.s(1)}% 几率移除所有移动限制效果，暗影形态下施法时因受到伤害而损失的施法或引导时间降低 {rec.s(2)}%。",
        "Twisted Faith": f"使你的法术强度提高，数值相当于总精神值的 {rec.s(1)}%，并使你的精神鞭笞和心灵震爆对受暗言术：痛影响的目标造成的伤害提高 {rec.s(2)}%。",
        "Pain and Suffering": f"精神鞭笞有 {chance(rec, 33)}% 几率刷新目标身上暗言术：痛的时长，并使你受到的所有伤害降低 {positive(rec.s(2))}%。",
        "Twin Disciplines": f"使你的瞬发法术造成的伤害和治疗效果提高 {rec.s(1)}%。",
        "Borrowed Time": f"施放真言术：盾后，你的下一个法术急速提高 {rec.s(1)}%，并使真言术：盾吸收的伤害额外提高，数值相当于你的法术强度的 {rec.s(2)}%。",
        "Glyph of Dispel Magic": f"你的驱散魔法在友方目标身上成功驱散时，还会为目标恢复最大生命值的 {rec.s(1)}%。",
        "Glyph of Power Word: Shield": f"你的真言术：盾还会立即治疗目标，数值相当于吸收量的 {records.get(55672, rec).s(1)}%。",
        "Glyph of Prayer of Healing": f"你的治疗祷言还会在接下来的 {duration(records.get(55680, rec))} 内额外治疗目标，数值相当于初始治疗量的 {records.get(55680, rec).s(1)}%。",
        "Renewed Hope": f"使快速治疗、强效治疗术和苦修对受虚弱灵魂影响目标的暴击几率提高 {rec.s(1)}%，并在你施放真言术：盾后使所有小队或团队成员受到的所有伤害降低 {rec.s(3)}%，持续 {duration(records.get(63944, rec))}。",
        "Improved Flash Heal": f"使快速治疗的法力值消耗降低 {positive(rec.s(2))}%，并使快速治疗对生命值不高于 50% 的友方目标暴击几率提高 {rec.s(1)}%。",
        "Empowered Renew": f"恢复额外获得治疗加成 {rec.s(1)}% 的收益，并且施放恢复时会立即治疗目标，数值相当于持续治疗总量的 {rec.s(2)}%。",
        "Soul Warding": f"使真言术：盾的冷却时间缩短 {ms(rec.s(1))} 秒，并使真言术：盾的法力值消耗降低 {positive(rec.s(2))}%。",
        "Improved Devouring Plague": f"使噬灵瘟疫的周期性伤害提高 {rec.s(1)}%，并在施放噬灵瘟疫时立即造成相当于周期性总伤害 {rec.s(2)}% 的伤害。",
        "Serendipity": f"当你使用联结治疗或快速治疗进行治疗时，使下一次强效治疗术或治疗祷言的施法时间缩短、法力值消耗降低。最多叠加 {rec.stack() or 3} 次。",
        "Body and Soul": f"你施放真言术：盾时，使目标移动速度提高 {rec.s(1)}%，持续 {duration(records.get(64128, rec))}；施放驱除疾病时，有 {rec.s(2)}% 几率额外移除目标身上的 1 个中毒效果。",
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


def is_priest(row: dict[str, str]) -> bool:
    skill_ids = set((row.get("skill_line_ids") or "").split(","))
    return bool(skill_ids & PRIEST_SKILLS) or (row.get("name_en") == "Devouring Plague" and "792" in skill_ids)


def process_rows(rows: list[dict[str, str]], records: dict[int, SpellRec]) -> tuple[dict[str, dict[str, str]], int]:
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_priest(row):
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
        if is_priest(row)
        and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", "")
             or ASCII_WORD_RE.search(row.get("description_zh", "") + " " + row.get("tooltip_zh", "") + " " + row.get("name_zh", "")))
    ]
    print(f"priority priest rows changed: {changed}")
    print(f"full rows changed directly: {full_changed}")
    print(f"priest spell ids synced: {len(full_updates)}")
    print(f"priest zh rows still containing $ or English words: {len(bad)}")
    for row in bad[:40]:
        print(row["spell_id"], row["name_en"], row["name_zh"], row.get("description_zh", "")[:180], row.get("tooltip_zh", "")[:120])


if __name__ == "__main__":
    main()
