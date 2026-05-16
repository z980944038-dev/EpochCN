# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import os
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
PRIORITY = ROOT / "SpellTranslation" / "spell_english_spellbook_priority.tsv"
FULL = ROOT / "SpellTranslation" / "spell_english_full_for_translation.tsv"
DBC = Path(os.environ.get("EPOCHCN_SPELL_DBC", BASE / "overlay" / "DBFilesClient" / "Spell.dbc"))
ROGUE_SKILLS = {"38", "39", "253"}

NAME_ZH = {
    "Adrenaline Rush": "冲动", "Aggression": "侵犯", "Ambush": "伏击", "Backstab": "背刺",
    "Blade Flurry": "剑刃乱舞", "Blade Twisting": "剑刃扭转", "Blind": "致盲", "Blood Spatter": "溅血",
    "Camouflage": "伪装", "Cheap Shot": "偷袭", "Cheat Death": "欺诈死亡", "Cloak of Shadows": "暗影斗篷",
    "Cold Blood": "冷血", "Combat Potency": "战斗潜能", "Cut to the Chase": "穷追猛砍", "Dagger Specialization": "匕首专精",
    "Deadened Nerves": "麻痹神经", "Deadliness": "致命", "Deadly Brew": "致命酿造", "Deadly Throw": "致命投掷",
    "Deflection": "偏斜", "Detect Traps": "侦测陷阱", "Dirty Deeds": "卑鄙", "Dirty Tricks": "卑鄙伎俩",
    "Disarm Trap": "解除陷阱", "Dismantle": "卸除武装", "Distract": "扰乱", "Dual Wield Specialization": "双武器专精",
    "Elusiveness": "飘忽不定", "Endurance": "耐久", "Enveloping Shadows": "笼罩之影", "Envenom": "毒伤",
    "Evasion": "闪避", "Eviscerate": "剔骨", "Expose Armor": "破甲", "Fan of Knives": "刀扇",
    "Feint": "佯攻", "Filthy Tricks": "卑鄙把戏", "Find Weakness": "寻找弱点", "Fist Weapon Specialization": "拳套专精",
    "Fleet Footed": "健步如飞", "Focused Attacks": "专注攻击", "Garrote": "锁喉", "Ghostly Strike": "鬼魅攻击",
    "Gouge": "凿击", "Heightened Senses": "敏锐感知", "Hemorrhage": "出血", "Honor Among Thieves": "盗亦有道",
    "Hunger For Blood": "血之饥渴", "Improved Ambush": "强化伏击", "Improved Eviscerate": "强化剔骨", "Improved Expose Armor": "强化破甲",
    "Improved Gouge": "强化凿击", "Improved Kick": "强化踢击", "Improved Kidney Shot": "强化肾击", "Improved Poisons": "强化药膏",
    "Improved Sinister Strike": "强化影袭", "Improved Slice and Dice": "强化切割", "Improved Sprint": "强化疾跑", "Initiative": "先发制人",
    "Intuition": "直觉", "Kick": "踢击", "Kidney Shot": "肾击", "Killing Spree": "杀戮盛宴",
    "Lethality": "致命偷袭", "Lightning Reflexes": "闪电反射", "Mace Specialization": "锤类武器专精", "Malice": "恶意",
    "Master of Deception": "欺诈高手", "Master of Subtlety": "敏锐大师", "Master Poisoner": "药膏大师", "Murder": "谋杀",
    "Mutilate": "毁伤", "Nerves of Steel": "钢铁意志", "Opportunity": "伺机而动", "Overkill": "过度杀戮",
    "Overkill - aura remove spell": "过度杀戮 - 移除光环法术", "Pick Pocket": "偷窃", "Precision": "精准", "Premeditation": "预谋",
    "Preparation": "伺机待发", "Prey on the Weak": "欺凌弱小", "Puncturing Wounds": "穿刺之伤", "Quick Recovery": "快速恢复",
    "Redirect": "转移", "Relentless Strikes": "无情打击", "Relentless Strikes Effect": "无情打击效果", "Remorseless Attacks": "冷酷攻击",
    "Riposte": "还击", "Rogue Passive (DND)": "盗贼被动（DND）", "Rupture": "割裂", "Ruthlessness": "无情",
    "Safe Fall": "安全降落", "Sap": "闷棍", "Savage Combat": "野蛮战斗", "Seal Fate": "封印命运",
    "Serrated Blades": "锯齿利刃", "Setup": "预备", "Shadow Dance": "暗影之舞", "Shadowstep": "暗影步",
    "Shiv": "毒刃", "Sinister Calling": "邪恶召唤", "Sinister Strike": "影袭", "Slaughter from the Shadows": "暗影杀戮",
    "Sleight of Hand": "手法娴熟", "Slice and Dice": "切割", "Sprint": "疾跑", "Stealth": "潜行",
    "Surprise Attacks": "奇袭", "Sword Specialization": "剑类武器专精", "Throwing Specialization": "投掷专精", "Tricks of the Trade": "嫁祸诀窍",
    "Turn the Tables": "扭转局势", "Unfair Advantage": "不公平优势", "Vanish": "消失", "Vanished": "已消失",
    "Vigor": "精力", "Vile Poisons": "恶性药膏", "Vitality": "活力", "Waylay": "埋伏", "Weapon Expertise": "武器专家",
}

TERM_FIXES = [
    ("邪恶打击", "影袭"), ("肾上腺素激增", "冲动"), ("冲刺", "疾跑"), ("偏转", "偏斜"),
    ("双持专精", "双武器专精"), ("拳套武器专精", "拳套专精"), ("爆击", "暴击"), ("格挡几率", "招架几率"),
    ("敏捷性", "敏捷"), ("再生率", "回复速度"), ("您的", "你的"), ("潜行者", "盗贼"),
    ("能力", "技能"), ("点。 奖励", "点。奖励"), ("。 此外", "。此外"), ("对手", "敌人"),
]
TOKEN_RE = re.compile(r"\$\{[^{}]*\}|\$\?[^\s，。；:：]*|\$<[^>]+>|\$[A-Za-z_]*\d*|\$/[^\s，。；:：]*|\$\*[^\s，。；:：]*|\$")
CJK_RE = re.compile(r"[\u3400-\u9fff]")


def signed(value: int) -> int:
    return value if value < 2**31 else value - 2**32


def cleanup(text: str) -> str:
    text = TOKEN_RE.sub("", text or "")
    for old, new in TERM_FIXES:
        text = text.replace(old, new)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r" +([，。；：])", r"\1", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()


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
        return signed(self.values[80 + n - 1]) + signed(self.values[74 + n - 1])

    def b(self, n: int) -> float:
        return struct.unpack("f", struct.pack("I", self.values[119 + n - 1]))[0]

    def amp_sec(self, n: int) -> int:
        amp = signed(self.values[98 + n - 1])
        return int(amp / 1000) if amp > 0 else 0


def load_spell_dbc() -> dict[int, SpellRec]:
    data = DBC.read_bytes()
    magic, record_count, field_count, record_size, string_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise RuntimeError("Spell.dbc is not WDBC")
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


def parse_point_seconds(desc: str) -> str:
    pairs = re.findall(r"(\d+)\s+points?\s*:\s*(\d+)\s+seconds", desc or "")
    return "\\n".join(f"   {p}点：{s}秒" for p, s in pairs)


def parse_rupture(desc: str) -> str:
    pairs = re.findall(r"(\d+)\s+points?\s*:\s*(\d+)\s+damage\s+over\s+(\d+)\s+secs", desc or "")
    return "\\n".join(f"   {p}点：{sec}秒内造成{dmg}点伤害" for p, dmg, sec in pairs)


def parse_slice(desc: str) -> str:
    lines = []
    for line in (desc or "").splitlines():
        match = re.search(r"(\d+)\s+points?\s*:\s*(.*) seconds", line)
        if not match:
            continue
        values = re.findall(r"\[(\d+)\]", match.group(2))
        if values:
            lines.append(f"   {match.group(1)}点：{values[-1]}秒")
    return "\\n".join(lines)


def eviscerate_table(rec: SpellRec) -> str:
    base_min = rec.s(1)
    base_max = max(base_min, rec.maxv(1))
    per = rec.b(1)
    lines = []
    for points in range(1, 6):
        low = int(round(base_min + per * points))
        high = int(round(base_max + per * points))
        lines.append(f"   {points}点：{low}-{high}点伤害，另受攻击强度加成")
    return "\\n".join(lines)


def deadly_throw_table(rec: SpellRec) -> str:
    base_min = rec.s(1)
    base_max = max(base_min, rec.maxv(1))
    per = rec.b(1) if rec.b(1) > 0 else 1
    lines = []
    for points in range(1, 6):
        low = int(round(base_min + per * points))
        high = int(round(base_max + per * points))
        lines.append(f"   {points}点：投掷武器伤害再加{low}-{high}点伤害")
    return "\\n".join(lines)


def envenom_table(rec: SpellRec) -> str:
    base = max(1, rec.s(2))
    return "\\n".join(f"   {doses}层：约{base * doses}点毒药伤害，另受攻击强度加成" for doses in range(1, 6))


def concrete_dbc_desc(rec: SpellRec | None) -> str | None:
    if rec and rec.desc and CJK_RE.search(rec.desc) and "$" not in rec.desc:
        return cleanup(rec.desc)
    return None


def concrete_dbc_tip(rec: SpellRec | None) -> str | None:
    if rec and rec.aura and CJK_RE.search(rec.aura) and "$" not in rec.aura:
        return cleanup(rec.aura)
    return None


def generic_desc(name: str, rec: SpellRec, desc: str) -> str:
    if name == "Pick Pocket": return "偷取目标的财物。"
    if name == "Distract": return f"投掷干扰物，吸引附近怪物的注意力，持续{max(rec.s(1), 10)}秒。不会打破潜行。"
    if name == "Kick": return f"快速踢击敌人，造成{rec.s(2)}点伤害，并打断施法，使其在5秒内无法施放同系法术。"
    if name == "Gouge": return f"造成{rec.s(1)}点伤害，使敌人瘫痪4秒，并停止你的自动攻击。目标必须面对你。任何伤害都会使目标恢复神志。奖励1个连击点。"
    if name == "Stealth": return f"允许盗贼潜行，但移动速度降低{abs(rec.s(3))}%。持续直到取消。"
    if name == "Cheap Shot": return "使目标昏迷4秒。必须在潜行状态下发动。奖励2个连击点。"
    if name == "Disarm Trap": return "潜行接近陷阱以解除它。不要靠得太近，否则陷阱会被触发。"
    if name == "Vanish": return "使盗贼从视野中消失，进入强化潜行模式10秒，并解除移动限制效果。"
    if name == "Safe Fall": return "降低坠落造成的伤害。"
    if name == "Detect Traps": return "大幅提高侦测陷阱的几率。"
    if name == "Sprint": return f"使盗贼的移动速度提高{rec.s(1)}%，持续15秒。不会打破潜行。"
    if name == "Evasion":
        if rec.s(2) < 0:
            return f"使盗贼的躲闪几率提高{rec.s(1)}%，远程攻击命中你的几率降低{abs(rec.s(2))}%，持续15秒。"
        return f"使盗贼的躲闪几率提高{rec.s(1)}%，持续15秒。"
    if name == "Shiv": return "立即使用副手武器攻击，并自动将副手武器上的药膏施加到目标身上。慢速武器消耗更多能量。奖励1个连击点。"
    if name == "Backstab":
        match = re.search(r"plus (\d+)", desc or "")
        plus = int(match.group(1)) if match else int(round(rec.s(1) * 1.5))
        return f"背刺目标，造成{rec.s(2)}%武器伤害再加{plus}点额外伤害。必须在目标背后发动。主手必须装备匕首。奖励1个连击点。"
    if name == "Ambush":
        match = re.search(r"plus (\d+)", desc or "")
        plus = int(match.group(1)) if match else rec.s(1)
        return f"伏击目标，造成{rec.s(2)}%武器伤害再加{plus}点额外伤害。必须在潜行状态下并位于目标背后发动。主手必须装备匕首。奖励1个连击点。"
    if name == "Sinister Strike": return f"立即发动攻击，造成普通武器伤害再加{rec.s(1)}点额外伤害。奖励1个连击点。"
    if name == "Eviscerate": return "终结技，根据连击点数造成直接伤害：\\n" + eviscerate_table(rec)
    if name == "Rupture":
        table = parse_rupture(desc)
        return "终结技，造成持续流血伤害，伤害受攻击强度加成。持续时间和总伤害随连击点数增加：\\n" + table if table else "终结技，造成持续流血伤害，伤害受攻击强度加成。连击点数越多，持续时间和总伤害越高。"
    if name == "Garrote":
        tick = rec.s(1)
        amp = rec.amp_sec(1) or 3
        total = tick * 6
        silence = "并使其沉默3秒，" if "silencing" in (desc or "") else ""
        return f"锁喉敌人，{silence}每{amp}秒造成{tick}点流血伤害，18秒共造成{total}点伤害，另受攻击强度加成。必须在潜行状态下并位于目标背后发动。奖励1个连击点。"
    if name == "Kidney Shot": return "终结技，使目标昏迷。持续时间随连击点数增加：\\n" + parse_point_seconds(desc)
    if name == "Expose Armor": return f"终结技，暴露目标弱点，使其护甲降低{abs(rec.s(1))}点。对已经被破甲的目标再次使用会延长破甲持续时间，最多延长至60秒。持续时间随连击点数增加：\\n" + parse_point_seconds(desc)
    if name == "Slice and Dice": return f"终结技，使近战攻击速度提高{rec.s(2)}%。持续时间随连击点数增加：\\n{parse_slice(desc)}\\n受强化切割等效果影响时，持续时间会进一步延长。"
    if name == "Deadly Throw": return f"终结技，使目标移动速度降低{abs(rec.s(2))}%，持续6秒，并造成投掷武器伤害。伤害随连击点数增加：\\n{deadly_throw_table(rec)}"
    if name == "Envenom": return "终结技，消耗目标身上的致命药膏层数并立即造成毒药伤害。每个连击点消耗一层，消耗层数越多伤害越高，并短暂提高你施加药膏的几率：\\n" + envenom_table(rec)
    if name == "Hemorrhage":
        dagger = "；装备匕首时武器伤害比例更高" if "dagger is equipped" in (desc or "") else ""
        return f"立即发动攻击，造成{rec.s(2)}%武器伤害{dagger}，并使目标出血，使其受到的物理伤害最多提高{rec.s(3)}点。持续10次充能或15秒。奖励1个连击点。"
    if name == "Ghostly Strike": return f"发动一次攻击，造成{rec.s(1)}%武器伤害，并使你的躲闪几率提高{rec.s(2)}%，持续7秒。奖励1个连击点。"
    if name == "Feint": return f"进行佯攻，不造成伤害，但会降低{abs(rec.s(1))}点威胁值，使敌人更不愿攻击你。"
    if name == "Riposte": return f"招架敌人的攻击后可用。造成{rec.s(1)}%武器伤害，并缴械目标6秒。"
    if name == "Dismantle": return "缴械敌人，移除其携带的武器、盾牌和其他装备，持续10秒。"
    return cleanup(desc) if CJK_RE.search(cleanup(desc)) and "$" not in cleanup(desc) else f"{NAME_ZH.get(name, name)}的盗贼技能效果。"


def desc_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    return concrete_dbc_desc(rec) or cleanup(generic_desc(row["name_en"], rec, rec.desc or row.get("description_en", "")))


def tip_for(row: dict[str, str], records: dict[int, SpellRec]) -> str:
    rec = records[int(row["spell_id"])]
    concrete = concrete_dbc_tip(rec)
    if concrete:
        return concrete
    en = row.get("tooltip_en", "") or rec.aura
    mapping = {
        "Stunned.": "昏迷。", "Incapacitated.": "瘫痪。", "Sapped.": "已被闷棍。",
        "Disoriented.": "迷惑。", "Improved stealth.": "强化潜行。", "Disarmed.": "被缴械。",
        "Dazed.": "眩晕。", "Finishing move that causes damage per combo point.": "终结技，根据连击点数造成伤害。",
    }
    if en in mapping:
        return mapping[en]
    if "Movement speed increased" in en: return f"移动速度提高{rec.s(1)}%。"
    if "Movement slowed" in en: return f"移动速度降低{abs(rec.s(2)) if row['name_en'] == 'Deadly Throw' else abs(rec.s(3))}%。"
    if "Melee attack speed increased" in en: return f"近战攻击速度提高{rec.s(2)}%。"
    if "Armor decreased" in en: return f"护甲降低{abs(rec.s(1))}点。"
    if "damage every" in en and row["name_en"] == "Garrote": return f"每{rec.amp_sec(1) or 3}秒造成{rec.s(1)}点伤害。"
    if "Causes damage every" in en: return "周期性造成伤害。"
    if "Increases damage taken" in en: return f"受到的物理伤害提高{rec.s(3)}点。"
    if "Energy regeneration increased" in en: return f"能量回复速度提高{rec.s(1)}%。"
    if "Dodge chance" in en or "dodge chance" in en: return f"躲闪几率提高{rec.s(1)}%。"
    if "Critical strike chance" in en: return "下一个攻击性技能的暴击几率提高。"
    if "chance to resist spells" in en: return "抵抗法术的几率提高。"
    return cleanup(en)


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


def is_rogue(row: dict[str, str]) -> bool:
    return bool(set((row.get("skill_line_ids") or "").split(",")) & ROGUE_SKILLS)


def main() -> None:
    records = load_spell_dbc()
    fields, rows = read_tsv(PRIORITY)
    updates: dict[str, dict[str, str]] = {}
    changed = 0
    for row in rows:
        if not is_rogue(row):
            continue
        before = tuple(row.get(key, "") for key in ("name_zh", "rank_zh", "description_zh", "tooltip_zh"))
        row["name_zh"] = NAME_ZH.get(row["name_en"], row.get("name_zh", ""))
        row["rank_zh"] = rank_zh(row.get("rank_en", ""))
        row["description_zh"] = cleanup(desc_for(row, records))
        row["tooltip_zh"] = cleanup(tip_for(row, records))
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
        if is_rogue(row) and ("$" in row.get("description_zh", "") or "$" in row.get("tooltip_zh", ""))
    ]
    print(f"priority rogue rows changed: {changed}")
    print(f"full rows synced: {full_changed}")
    print(f"rogue spell ids synced: {len(updates)}")
    print(f"rogue zh rows still containing $: {len(bad)}")


if __name__ == "__main__":
    main()
