#!/usr/bin/env python3
"""Generate exact green tooltip line translations from the EpochHead snapshot."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "SourceData" / "EpochHead" / "items" / "items.json"
OUT = ROOT / "Data" / "TooltipLineData.lua"
ITEM_GENERATOR = ROOT / "Tools" / "generate_epoch_items.py"
OVERRIDES = ROOT / "Tools" / "tooltip_line_overrides.json"
EFFECT_LINE_RE = re.compile(r"^(?:Equip|Use|Chance on hit|Set):|^\(\d+\)\s*Set:", re.I)


spec = importlib.util.spec_from_file_location("generate_epoch_items", ITEM_GENERATOR)
items_gen = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(items_gen)


SCHOOL = {
    "Arcane": "奥术",
    "Fire": "火焰",
    "Frost": "冰霜",
    "Holy": "神圣",
    "Nature": "自然",
    "Shadow": "暗影",
    "Physical": "物理",
}

CREATURE = {
    "Beasts": "野兽",
    "Demons": "恶魔",
    "Dragonkin": "龙类",
    "Elementals": "元素生物",
    "Humanoids": "人型生物",
    "Undead": "亡灵",
}

STAT = {
    "Agility": "敏捷",
    "Armor": "护甲",
    "Attack Power": "攻击强度",
    "all resistances": "所有抗性",
    "all stats": "所有属性",
    "block rating": "格挡等级",
    "damage": "伤害",
    "damage to beasts": "对野兽的伤害",
    "damage to elementals": "对元素生物的伤害",
    "Defense": "防御",
    "defense rating": "防御等级",
    "fishing skill": "钓鱼技能",
    "frost resistance": "冰霜抗性",
    "Frost spell power": "冰霜法术强度",
    "health": "生命值",
    "herbalism skill": "草药学技能",
    "Intellect": "智力",
    "its damage": "伤害",
    "its damage to beasts": "对野兽的伤害",
    "its damage to elementals": "对元素生物的伤害",
    "mana": "法力值",
    "mining skill": "采矿技能",
    "shadow resistance": "暗影抗性",
    "skinning skill": "剥皮技能",
    "spell power": "法术强度",
    "Spirit": "精神",
    "Stamina": "耐力",
    "Strength": "力量",
}

SLOTS = {
    "bracers": "护腕",
    "chest armor": "胸甲",
    "gloves": "手套",
    "a cloak": "披风",
    "a melee weapon": "近战武器",
    "a shield": "盾牌",
    "a two-handed melee weapon": "双手近战武器",
}

PET_SKILLS = {
    "Felguard Anguish": "恶魔卫士痛楚",
    "Felguard Cleave": "恶魔卫士顺劈斩",
    "Felguard Demonic Frenzy": "恶魔卫士恶魔狂乱",
    "Felguard Intercept": "恶魔卫士拦截",
    "Felhunter Devour Magic": "地狱猎犬吞噬魔法",
    "Felhunter Paranoia": "地狱猎犬多疑",
    "Felhunter Shadow Bite": "地狱猎犬暗影撕咬",
    "Felhunter Spell Lock": "地狱猎犬法术封锁",
    "Felhunter Tainted Blood": "地狱猎犬污浊之血",
    "Gift of the Wild": "野性赐福",
    "Imp Blood Pact": "小鬼血之契印",
    "Imp Fire Shield": "小鬼火焰之盾",
    "Imp Firebolt": "小鬼火焰箭",
    "Imp Phase Shift": "小鬼相位变换",
    "Succubus Lash of Pain": "魅魔痛苦鞭笞",
    "Succubus Lesser Invisibility": "魅魔次级隐形术",
    "Succubus Seduction": "魅魔魅惑",
    "Succubus Soothing Kiss": "魅魔安抚之吻",
    "Voidwalker Consume Shadows": "虚空行者吞噬暗影",
    "Voidwalker Sacrifice": "虚空行者牺牲",
    "Voidwalker Suffering": "虚空行者受难",
    "Voidwalker Torment": "虚空行者折磨",
}

ABILITY = {
    "Barkskin": "树皮术",
    "Chain Lightning": "闪电链",
    "Cleanse": "清洁术",
    "Consecration": "奉献",
    "Crusader Strike": "十字军打击",
    "Deadly Throw": "致命投掷",
    "Devotion Aura": "虔诚光环",
    "Drain Soul": "吸取灵魂",
    "Earth Elemental Totem": "土元素图腾",
    "Earth Shock": "大地震击",
    "Exorcism": "驱邪术",
    "Fear": "恐惧术",
    "Flash of Light": "圣光闪现",
    "Flame Shock": "烈焰震击",
    "Frost Shock": "冰霜震击",
    "Hammer of Justice": "制裁之锤",
    "Healing Stream Totem": "治疗之泉图腾",
    "Holy Wrath": "神圣愤怒",
    "Hurricane": "飓风",
    "Innervate": "激活",
    "Lesser Healing Wave": "次级治疗波",
    "Maul": "槌击",
    "Mind Blast": "心灵震爆",
    "Moonfire": "月火术",
    "Multi-Shot": "多重射击",
    "Polymorph": "变形术",
    "Psychic Scream": "心灵尖啸",
    "Rake": "扫击",
    "Reincarnation": "复生",
    "Rejuvenation": "回春术",
    "Seal": "圣印",
    "Shadow Bolt": "暗影箭",
    "Shadow Word: Death": "暗言术：灭",
    "Shadowfiend": "暗影魔",
    "Shock": "震击",
    "Swipe": "横扫",
    "Tiger's Fury": "猛虎之怒",
}

LINE_OVERRIDES = {
    "Use: (null)": "使用：无效果。",
    "Chance on hit: A burst of energy fills the caster, increasing his damage by 10 and armor by 150 for 15 sec.": "击中时可能：一股能量充盈施法者，使其伤害提高 10 点、护甲提高 150 点，持续 15 秒。",
    "Chance on hit: Blasts a target for 60 Fire damage and increases damage done to target by Fire damage by 10 for 30 sec.": "击中时可能：轰击目标，造成 60 点火焰伤害，并使目标受到的火焰伤害提高 10 点，持续 30 秒。",
    "Chance on hit: Blasts nearby enemies with thunder increasing the time between their attacks by 11% for 10 sec and doing 7 Nature damage to them. Will affect up to 4 targets.": "击中时可能：用雷霆轰击附近敌人，使其攻击间隔延长 11%，持续 10 秒，并造成 7 点自然伤害。最多影响 4 个目标。",
    "Chance on hit: Calls forth an Emerald Dragon Whelp to protect you in battle for a short period of time.": "击中时可能：召唤一只翡翠雏龙，在短时间内保护你作战。",
    "Chance on hit: Causes the target to bleed for 3 damage every 2 sec for 12 sec. Stacks up to 25 times.": "击中时可能：使目标流血，每 2 秒造成 3 点伤害，持续 12 秒。最多叠加 25 次。",
    "Chance on hit: Conjures a sudden burst of water, dealing 137 to 159 Frost damage to your target and protecting yourself with a bubble that absorbs 675 damage for 3 sec.": "击中时可能：召出一阵水流，对目标造成 137 到 159 点冰霜伤害，并用气泡保护自己，吸收 675 点伤害，持续 3 秒。",
    "Chance on hit: Corrosive acid that deals 7 Nature damage every 3 sec and lowers target's armor by 50 for 30 sec.": "击中时可能：腐蚀性酸液每 3 秒造成 7 点自然伤害，并使目标护甲降低 50 点，持续 30 秒。",
    "Chance on hit: Cripples the target, reducing movement speed by 40%, increasing time between melee attacks by 45% and increasing time between ranged attacks by 45%. Lasts 20 sec.": "击中时可能：重创目标，使其移动速度降低 40%，近战和远程攻击间隔延长 45%，持续 20 秒。",
    "Chance on hit: Drain either health or mana from your target. If the target has no mana, only health is drained.": "击中时可能：从目标身上吸取生命值或法力值。如果目标没有法力值，则只吸取生命值。",
    "Chance on hit: Enemy is inflicted with the Bleakwood Curse that reduces their magic resistances by 25. Can be applied up to 3 times.": "击中时可能：使敌人受到荒木诅咒，魔法抗性降低 25 点。最多叠加 3 次。",
    "Chance on hit: Instantly shocks the target with concussive force, causing 65 to 69 Nature damage. It also interrupts spellcasting and prevents any spell in that school from being cast for 2 sec.": "击中时可能：立即以震荡力量冲击目标，造成 65 到 69 点自然伤害，并打断施法，使其 2 秒内无法施放同系法术。",
    "Chance on hit: Reduce your threat to the current target making them less likely to attack you.": "击中时可能：降低你对当前目标的威胁值，使其不太可能攻击你。",
    "Chance on hit: Summons the infernal spirit of Shahram.": "击中时可能：召唤沙赫拉姆的地狱火之魂。",
    "Chance on hit: The chomper chomps the target, chomping their movement speed by 40% for 8 sec.": "击中时可能：咬击目标，使其移动速度降低 40%，持续 8 秒。",
    "Equip: Allows you to fish in lava and magma.": "装备：允许你在熔岩和岩浆中钓鱼。",
    "Equip: Chance to gain additional Dragon Scales when skinning Dragons.": "装备：剥取龙类时有几率获得额外的龙鳞。",
    "Equip: Herbalism +5.": "装备：草药学 +5。",
    "Equip: Impress others with your fashion sense.": "装备：用你的时尚品味给别人留下深刻印象。",
    "Equip: Mining +2": "装备：采矿 +2。",
    "Equip: Mining +3": "装备：采矿 +3。",
    "Equip: Mining +5.": "装备：采矿 +5。",
    "Equip: Nearby Gahz'ridian appears on the minimap.": "装备：附近的加兹瑞迪安会显示在小地图上。",
    "Equip: Nearby elven gems appear on the minimap.": "装备：附近的精灵宝石会显示在小地图上。",
    "Equip: Protects the wearer from being fully engulfed by Shadow Flame.": "装备：保护穿戴者免于被暗影烈焰完全吞噬。",
    "Equip: Protects the wearer from the Mark of Kazzak.": "装备：保护穿戴者免受卡扎克印记影响。",
    "Equip: Reduces damage from falling.": "装备：降低坠落伤害。",
    "Equip: Run speed increased slightly.": "装备：奔跑速度略微提高。",
    "Equip: Skinning +10.": "装备：剥皮 +10。",
    "Equip: This item appears to be cursed.": "装备：这件物品似乎被诅咒了。",
    "Equip: This weapon will never lose durability.": "装备：这把武器永远不会损失耐久度。",
    "Set: Every time your Hurricane spell deals damage its cooldown is reduced by 0.5 sec.": "套装：每当你的飓风造成伤害时，其冷却时间缩短 0.5 秒。",
    "Set: Increases the critical strike chance of your Shock spells by 3%.": "套装：你的震击法术爆击几率提高 3%。",
    "Set: Increases the damage dealt by your Priest periodic effects by 2%.": "套装：你的牧师周期性效果造成的伤害提高 2%。",
    "Set: Increases the damage done by your Shadow Bolt and Drain Soul by 3%.": "套装：你的暗影箭和吸取灵魂造成的伤害提高 3%。",
    "Set: Increases your spell damage by 1 for every 150 armor you have.": "套装：你每拥有 150 点护甲，法术伤害提高 1 点。",
    "Set: Killing a target with Shadow Word: Death now also decreases the cooldown of Shadowfiend by 30 seconds.": "套装：使用暗言术：灭杀死目标时，还会使暗影魔的冷却时间缩短 30 秒。",
    "Set: Reduces the cooldown of Earth Elemental Totem by 7 minutes.": "套装：土元素图腾的冷却时间缩短 7 分钟。",
    "Set: Using Innervate on another target also grants you Innervate at 15% effectiveness.": "套装：对其他目标使用激活时，你也会获得效果为 15% 的激活。",
}

_tooltip_overrides: dict[str, str] | None = None


def load_tooltip_overrides() -> dict[str, str]:
    global _tooltip_overrides
    if _tooltip_overrides is None:
        if OVERRIDES.exists():
            data = json.loads(OVERRIDES.read_text(encoding="utf-8"))
            _tooltip_overrides = {str(raw).strip(): str(cn).strip() for raw, cn in data.items() if raw and cn}
        else:
            _tooltip_overrides = {}
    return _tooltip_overrides

PROFESSION = {
    "Cook": "厨师",
    "Expert Cook": "高级厨师",
    "Expert Fisherman": "高级钓鱼",
    "expert in first aid": "高级急救",
}

RECIPE_PREFIXES = (
    "食谱：",
    "公式：",
    "图样：",
    "结构图：",
    "设计图：",
    "手册：",
    "教程",
    "秘典：",
    "宝典：",
    "魔典：",
    "石板：",
    "书卷：",
)


def has_ascii_letters(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text or ""))


def iter_effect_lines(item: dict) -> list[str]:
    """Return all lines that can appear as green/effect tooltip text in game."""
    lines: list[str] = []
    seen: set[str] = set()

    for raw in item.get("green") or []:
        raw = str(raw or "").strip()
        if raw and raw not in seen:
            seen.add(raw)
            lines.append(raw)

    for row in item.get("tooltip") or []:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("text") or "").strip()
        if not raw or raw in seen:
            continue
        color = str(row.get("color") or "")
        if color == "green" or EFFECT_LINE_RE.search(raw):
            seen.add(raw)
            lines.append(raw)

    return lines


def lua_escape(text: str) -> str:
    return items_gen.lua_escape(text)


def finish(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    text = text.replace(" %", "%")
    text = text.replace(" 。", "。")
    if text and not re.search(r"[。！？）]$", text):
        text += "。"
    return text


def cn_school(name: str) -> str:
    return SCHOOL.get(name, name)


def cn_stat(name: str) -> str:
    key = (name or "").strip()
    return STAT.get(key) or STAT.get(key.lower()) or items_gen.consumables.replace_terms(key)


def cn_ability(name: str) -> str:
    key = re.sub(r"\s+spell$", "", (name or "").strip())
    return ABILITY.get(key) or PET_SKILLS.get(key) or items_gen.translate_spell_name(key, {})


def cn_ability_list(value: str) -> str:
    value = re.sub(r",\s+and\s+", ", ", (value or "").strip())
    value = re.sub(r"\s+and\s+", ", ", value)
    parts = [cn_ability(part.strip()) for part in value.split(",") if part.strip()]
    if not parts or any(has_ascii_letters(part) for part in parts):
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]}和{parts[1]}"
    return "、".join(parts[:-1]) + f"和{parts[-1]}"


def strip_recipe_prefix(name: str) -> str:
    name = name or ""
    for prefix in RECIPE_PREFIXES:
        if name.startswith(prefix):
            return name[len(prefix):].strip()
    return name.strip()


def context_item_name(item: dict, existing_items: dict, name_map: dict, objective_names: dict) -> str:
    item_id = int(item["id"])
    base = existing_items.get(item_id)
    if base and items_gen.has_cn(base[0]) and not has_ascii_letters(base[0]):
        return base[0]
    en_name = item.get("name") or ""
    mapped = name_map.get(en_name)
    if mapped and items_gen.has_cn(mapped) and not has_ascii_letters(mapped):
        return mapped
    translated = items_gen.translate_item_name(en_name, existing_items, objective_names)
    if translated and items_gen.has_cn(translated) and not has_ascii_letters(translated):
        return translated
    return ""


def translate_teaches(line: str, item: dict, cn_name: str) -> str:
    if line == "Use: Teaches you the fine art of fish finding.":
        return "使用：教你学会寻找鱼点的精妙技艺。"

    if line == "Use: Teaches you how to be an Expert Cook, allowing a maximum of 225 cooking skill.":
        return "使用：教你成为高级厨师，使烹饪技能上限提高到225。"
    if line == "Use: Teaches you how to be an Expert Fisherman, allowing a maximum of 225 fishing skill.":
        return "使用：教你成为高级钓鱼者，使钓鱼技能上限提高到225。"
    if line == "Use: Teaches you how to be an expert in first aid, allowing a maximum of 225 first aid skill.":
        return "使用：教你成为高级急救医师，使急救技能上限提高到225。"

    match = re.match(r"^Use: Teaches you how to permanently enchant (.+?) to increase (.+?) by ([\d,]+)(?:\. Requires a level (\d+) or higher item)?\.$", line, re.I)
    if match:
        slot = SLOTS.get(match.group(1).lower(), items_gen.consumables.replace_terms(match.group(1)))
        stat = cn_stat(match.group(2))
        extra = f"需要等级 {match.group(4)} 或更高的物品。" if match.group(4) else ""
        return f"使用：教你学会永久性地为{slot}附魔，使{stat}提高 {match.group(3)} 点。{extra}"

    match = re.match(r"^Use: Teaches you how to permanently enchant (.+?) to restore ([\d,]+) mana every 5 seconds\.$", line, re.I)
    if match:
        slot = SLOTS.get(match.group(1).lower(), items_gen.consumables.replace_terms(match.group(1)))
        return f"使用：教你学会永久性地为{slot}附魔，使其每5秒恢复 {match.group(2)} 点法力值。"

    match = re.match(r"^Use: Teaches you how to (.+?)\.$", line)
    if match and cn_name:
        target = strip_recipe_prefix(cn_name)
        if target and not has_ascii_letters(target):
            return f"使用：教你学会制作{target}。"

    match = re.match(r"^Use: Teaches (.+?)(?: \(Rank (\d+)\))?\.$", line)
    if match:
        spell = PET_SKILLS.get(match.group(1)) or items_gen.translate_spell_name(match.group(1), {})
        if not has_ascii_letters(spell):
            rank = f"（等级 {match.group(2)}）" if match.group(2) else ""
            return f"使用：教你学会{spell}{rank}。"

    return ""


def translate_effect_with_prefix(line: str) -> str:
    if line in LINE_OVERRIDES:
        return LINE_OVERRIDES[line]

    prefix = ""
    body = line
    for raw, cn in [
        ("Equip: ", "装备："),
        ("Use: ", "使用："),
        ("Chance on hit: ", "击中时可能："),
        ("Set: ", "套装："),
    ]:
        if body.startswith(raw):
            prefix = cn
            body = body[len(raw):]
            break

    match = re.match(r"^\+([\d,]+) ranged Attack Power\.?$", body, re.I)
    if match:
        return f"{prefix}远程攻击强度提高 {match.group(1)} 点。"

    match = re.match(r"^\+([\d,]+) Attack Power when fighting (Beasts|Demons|Dragonkin|Elementals|Humanoids|Undead)\.?(.*)$", body, re.I)
    if match:
        extra = "同时允许你代表银色黎明收集天灾石。" if "Scourgestones" in match.group(3) else ""
        return f"{prefix}与{CREATURE[match.group(2)]}作战时，攻击强度提高 {match.group(1)} 点。{extra}"

    match = re.match(r"^Attack Power increased by ([\d,]+) when fighting (Beasts|Demons|Dragonkin|Elementals|Humanoids|Undead)\.?$", body, re.I)
    if match:
        return f"{prefix}与{CREATURE[match.group(2)]}作战时，攻击强度提高 {match.group(1)} 点。"

    match = re.match(r"^Blasts a target for ([\d,]+)(?: to ([\d,]+))? (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage\.?$", body, re.I)
    if match:
        amount = f"{match.group(1)} 到 {match.group(2)}" if match.group(2) else match.group(1)
        return f"{prefix}轰击目标，造成 {amount} 点{cn_school(match.group(3))}伤害。"

    match = re.match(r"^Blasts up to ([\d,]+) targets for ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage\.?$", body, re.I)
    if match:
        return f"{prefix}轰击最多 {match.group(1)} 个目标，造成 {match.group(2)} 到 {match.group(3)} 点{cn_school(match.group(4))}伤害。"

    match = re.match(r"^Chance to strike your (melee|ranged) target with (?:a |an )?(.+?) for ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage\.?$", body, re.I)
    if match:
        proc = items_gen.translate_proc_name(match.group(2))
        if not has_ascii_letters(proc):
            kind = "近战" if match.group(1).lower() == "melee" else "远程"
            return f"{prefix}有几率用{proc}打击你的{kind}目标，造成 {match.group(3)} 到 {match.group(4)} 点{cn_school(match.group(5))}伤害。"

    match = re.match(r"^Smites an enemy for ([\d,]+)(?: to ([\d,]+))?(?: (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical))? damage\.?$", body, re.I)
    if match:
        amount = f"{match.group(1)} 到 {match.group(2)}" if match.group(2) else match.group(1)
        school = f"{cn_school(match.group(3))}" if match.group(3) else ""
        return f"{prefix}惩击敌人，造成 {amount} 点{school}伤害。"

    match = re.match(r"^(?:Deals|Inflicts|Wounds the target for|Delivers a fatal wound for|Sends a shadowy bolt at the enemy causing|Instantly lightning shocks the target for) ([\d,]+)(?: to ([\d,]+))?(?: (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical))? damage\.?$", body, re.I)
    if match:
        amount = f"{match.group(1)} 到 {match.group(2)}" if match.group(2) else match.group(1)
        school = f"{cn_school(match.group(3))}" if match.group(3) else ""
        return f"{prefix}造成 {amount} 点{school}伤害。"

    match = re.match(r"^Hurls a fiery ball that causes ([\d,]+)(?: to ([\d,]+))? Fire damage and an additional ([\d,]+) damage over ([\d,]+) sec\.?$", body, re.I)
    if match:
        amount = f"{match.group(1)} 到 {match.group(2)}" if match.group(2) else match.group(1)
        return f"{prefix}掷出一团火球，造成 {amount} 点火焰伤害，并在 {match.group(4)} 秒内额外造成 {match.group(3)} 点伤害。"

    match = re.match(r"^Corrupts the target, causing ([\d,]+) damage over ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}腐蚀目标，在 {match.group(2)} 秒内造成 {match.group(1)} 点伤害。"

    match = re.match(r"^Deals ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage every ([\d,]+) sec for ([\d,]+) sec\.?(.*)$", body, re.I)
    if match:
        extra = "所有造成的伤害随后会转移给施法者。" if "transferred to the caster" in match.group(5) else ""
        return f"{prefix}每 {match.group(3)} 秒造成 {match.group(1)} 点{cn_school(match.group(2))}伤害，持续 {match.group(4)} 秒。{extra}"

    match = re.match(r"^Inflicts (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage(?: to an enemy)? every ([\d,]+) sec\.? for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}每 {match.group(2)} 秒造成{cn_school(match.group(1))}伤害，持续 {match.group(3)} 秒。"

    match = re.match(r"^Inflicts ([\d,]+) to ([\d,]+) (Arcane|Fire|Frost|Holy|Nature|Shadow|Physical) damage to an enemy every ([\d,]+) sec\.? for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}对敌人每 {match.group(4)} 秒造成 {match.group(1)} 到 {match.group(2)} 点{cn_school(match.group(3))}伤害，持续 {match.group(5)} 秒。"

    match = re.match(r"^Poisons target for ([\d,]+) Nature damage every ([\d,]+) sec for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}使目标中毒，每 {match.group(2)} 秒造成 {match.group(1)} 点自然伤害，持续 {match.group(3)} 秒。"

    match = re.match(r"^Burns the enemy for ([\d,]+) damage over ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}灼烧敌人，在 {match.group(2)} 秒内造成 {match.group(1)} 点伤害。"

    match = re.match(r"^Grants (?:(\d+) |an? )extra attacks? on your next swing\.?$", body, re.I)
    if match:
        amount = match.group(1) or "1"
        return f"{prefix}你的下一次攻击额外获得 {amount} 次攻击。"

    match = re.match(r"^Stuns target for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}击昏目标，持续 {match.group(1)} 秒。"

    match = re.match(r"^Knocks target silly for ([\d,]+) sec(?: and increases Strength by ([\d,]+) for ([\d,]+) sec)?\.?$", body, re.I)
    if match:
        extra = f"并使力量提高 {match.group(2)} 点，持续 {match.group(3)} 秒。" if match.group(2) else ""
        return f"{prefix}将目标击晕，持续 {match.group(1)} 秒。{extra}"

    match = re.match(r"^Disarm target's weapon for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}缴械目标的武器，持续 {match.group(1)} 秒。"

    match = re.match(r"^Restores ([\d,]+) mana\.?$", body, re.I)
    if match:
        return f"{prefix}恢复 {match.group(1)} 点法力值。"

    match = re.match(r"^Defense \+([\d,]+) for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}防御提高 {match.group(1)} 点，持续 {match.group(2)} 秒。"

    match = re.match(r"^Increases Attack Power against (Beasts|Demons|Dragonkin|Elementals|Humanoids|Undead) by ([\d,]+) for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}对{CREATURE[match.group(1)]}的攻击强度提高 {match.group(2)} 点，持续 {match.group(3)} 秒。"

    match = re.match(r"^Increases damage done by ([\d,]+) and attack speed by ([\d,]+)% for ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}造成的伤害提高 {match.group(1)} 点，攻击速度提高 {match.group(2)}%，持续 {match.group(3)} 秒。"

    match = re.match(r"^Increases damage done by magical spells and effects by up to ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}魔法法术和效果造成的伤害最多提高 {match.group(1)} 点。"

    match = re.match(r"^Increases damage done to (Humanoids|Undead) by magical spells and effects by up to ([\d,]+)\.?(.*)$", body, re.I)
    if match:
        extra = "同时允许你代表银色黎明收集天灾石。" if "Scourgestones" in match.group(3) else ""
        return f"{prefix}对{CREATURE[match.group(1)]}的魔法法术和效果伤害最多提高 {match.group(2)} 点。{extra}"

    match = re.match(r"^Increases (?:the )?damage (?:done|dealt) by (?:your )?(.+?) by (?:up to )?([\d,]+)(%)?\.?$", body, re.I)
    if match:
        ability = cn_ability_list(match.group(1)) or cn_ability(match.group(1))
        if not has_ascii_letters(ability):
            unit = "%" if match.group(3) else " 点"
            return f"{prefix}{ability}造成的伤害提高 {match.group(2)}{unit}。"

    match = re.match(r"^Increases healing done by (.+?) by (?:up to )?([\d,]+)\.?$", body, re.I)
    if match:
        ability = cn_ability(match.group(1))
        if not has_ascii_letters(ability):
            return f"{prefix}{ability}的治疗效果最多提高 {match.group(2)} 点。"

    match = re.match(r"^Reduces the (cooldown|mana cost|energy cost|rage cost) of (?:your )?(.+?) by ([\d.]+) (sec|seconds|minutes)?\.?$", body, re.I)
    if match:
        ability = cn_ability_list(match.group(2)) or cn_ability(match.group(2))
        if not has_ascii_letters(ability):
            kind = {"cooldown": "冷却时间", "mana cost": "法力消耗", "energy cost": "能量消耗", "rage cost": "怒气消耗"}[match.group(1).lower()]
            unit = " 秒" if (match.group(4) or "").lower().startswith("sec") else (" 分钟" if (match.group(4) or "").lower().startswith("min") else " 点")
            return f"{prefix}{ability}的{kind}降低 {match.group(3)}{unit}。"

    match = re.match(r"^Improves (critical strike|hit|resilience) rating by ([\d,]+)\.?$", body, re.I)
    if match:
        stat = {"critical strike": "爆击等级", "hit": "命中等级", "resilience": "韧性等级"}[match.group(1).lower()]
        return f"{prefix}{stat}提高 {match.group(2)} 点。"

    match = re.match(r"^Increases (mount|swim) speed by ([\d,]+)%\.?$", body, re.I)
    if match:
        kind = "坐骑速度" if match.group(1).lower() == "mount" else "游泳速度"
        return f"{prefix}{kind}提高 {match.group(2)}%。"

    match = re.match(r"^Increases the block value of your shield by ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}你的盾牌格挡值提高 {match.group(1)} 点。"

    match = re.match(r"^All attacks are guaranteed to land and will be critical strikes for the next ([\d,]+) sec\.?$", body, re.I)
    if match:
        return f"{prefix}接下来 {match.group(1)} 秒内，所有攻击必定命中并造成爆击。"

    match = re.match(r"^Allows underwater breathing\.?$", body, re.I)
    if match:
        return f"{prefix}允许在水下呼吸。"

    match = re.match(r"^Begins taming an? (.+?) to be your companion for ([\d,]+) (?:min|minutes)\. If you lose the beast's attention for any reason, the taming process will fail\.$", body, re.I)
    if match:
        target = "野兽"
        return f"{prefix}开始驯服一只{target}作为你的伙伴，持续 {match.group(2)} 分钟。如果你因任何原因失去野兽的注意，驯服过程就会失败。"

    match = re.match(r"^Increases maximum (health|mana) by ([\d,]+) for ([\d,]+) hr\.?$", body, re.I)
    if match:
        stat = "生命值" if match.group(1).lower() == "health" else "法力值"
        return f"{prefix}{stat}上限提高 {match.group(2)} 点，持续 {match.group(3)} 小时。"

    match = re.match(r"^Increases (Spirit|Stamina|Agility|Intellect|Strength|Rage|armor) by ([\d,]+) for ([\d,]+) (?:min|minutes|hr|hours)\.?$", body, re.I)
    if match:
        stat = cn_stat(match.group(1))
        unit = "小时" if "hr" in body.lower() or "hour" in body.lower() else "分钟"
        return f"{prefix}{stat}提高 {match.group(2)} 点，持续 {match.group(3)} {unit}。"

    match = re.match(r"^Increases Spell Damage by up to ([\d,]+) for ([\d,]+) min\.?$", body, re.I)
    if match:
        return f"{prefix}法术伤害最多提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。"

    match = re.match(r"^Increases Spell Healing by up to ([\d,]+) for ([\d,]+) min\.?$", body, re.I)
    if match:
        return f"{prefix}法术治疗效果最多提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。"

    match = re.match(r"^Increases spell (fire|frost|nature|shadow|arcane|holy) damage by up to ([\d,]+) for ([\d,]+) min\.?$", body, re.I)
    if match:
        return f"{prefix}{cn_school(match.group(1).title())}法术伤害最多提高 {match.group(2)} 点，持续 {match.group(3)} 分钟。"

    match = re.match(r"^Restores ([\d,]+) to ([\d,]+) (health|mana)\.?$", body, re.I)
    if match:
        stat = "生命值" if match.group(3).lower() == "health" else "法力值"
        return f"{prefix}恢复 {match.group(1)} 到 {match.group(2)} 点{stat}。"

    match = re.match(r"^Absorbs ([\d,]+)(?: to ([\d,]+))? (fire|frost|magical) damage\. Lasts ([\d,]+) min\.?(?: \(([\d,]+) Min Cooldown\))?$", body, re.I)
    if match:
        amount = f"{match.group(1)} 到 {match.group(2)}" if match.group(2) else match.group(1)
        school = {"fire": "火焰", "frost": "冰霜", "magical": "魔法"}[match.group(3).lower()]
        cd = f"（{match.group(5)}分钟冷却）" if match.group(5) else ""
        return f"{prefix}吸收 {amount} 点{school}伤害。持续 {match.group(4)} 分钟。{cd}"

    match = re.match(r"^Attach a lure to your equipped fishing pole, increasing Fishing by ([\d,]+) for ([\d,]+) min\. \(([\d,]+) Min Cooldown\)$", body, re.I)
    if match:
        return f"{prefix}在你装备的鱼竿上装上鱼饵，使钓鱼技能提高 {match.group(1)} 点，持续 {match.group(2)} 分钟。（{match.group(3)}分钟冷却）"

    match = re.match(r"^Attaches a permanent scope to a bow(?:, crossbow,)? or gun that increases its (damage|chance to hit) by ([\d,]+)(%)?\.?(?:nnAttaching this scope to a ranged weapon causes it to become soulbound\.)?(?: \(([\d,]+) Sec Cooldown\))?$", body, re.I)
    if match:
        attr = "伤害" if match.group(1).lower() == "damage" else "命中几率"
        unit = "%" if match.group(3) else " 点"
        bind = "将此瞄准镜装到远程武器上会使其变为灵魂绑定。" if "soulbound" in body.lower() else ""
        cd = f"（{match.group(4)}秒冷却）" if match.group(4) else ""
        return f"{prefix}为弓或枪械装上永久性瞄准镜，使其{attr}提高 {match.group(2)}{unit}。{bind}{cd}"

    match = re.match(r"^Permanently adds ([\d,]+) (?:to )?(.+?) to (.+?)\.?$", body, re.I)
    if match:
        stat = cn_stat(match.group(2))
        target = items_gen.consumables.replace_terms(match.group(3))
        if not has_ascii_letters(stat + target):
            return f"{prefix}永久性地为{target}增加 {match.group(1)} 点{stat}。"

    match = re.match(r"^Permanently embed an armor crystal into your chestpiece, increasing maximum health by ([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}将护甲水晶永久嵌入你的胸甲，使生命值上限提高 {match.group(1)} 点。"

    match = re.match(r"^Dispels all harmful magic effects from yourself\.?$", body, re.I)
    if match:
        return f"{prefix}驱散你身上的所有有害魔法效果。"

    match = re.match(r"^Immune to Disarm\.?$", body, re.I)
    if match:
        return f"{prefix}免疫缴械。"

    match = re.match(r"^Increased Fishing \+([\d,]+)\.?$", body, re.I)
    if match:
        return f"{prefix}钓鱼技能提高 {match.group(1)} 点。"

    return ""


def translate_contextual(line: str, item: dict, cn_name: str, objective_names: dict) -> str:
    exact = load_tooltip_overrides().get(line)
    if exact and not has_ascii_letters(exact):
        return exact

    numbered_set = re.match(r"^\((\d+)\)\s*Set:\s*(.+)$", line, re.I)
    if numbered_set:
        unnumbered = "Set: " + numbered_set.group(2).strip()
        base_set = items_gen.translate_tooltip_line(unnumbered, objective_names)
        if base_set and not has_ascii_letters(base_set):
            return f"({numbered_set.group(1)}) {base_set}"
        custom_set = translate_effect_with_prefix(unnumbered)
        if custom_set and not has_ascii_letters(custom_set):
            return f"({numbered_set.group(1)}) {finish(custom_set)}"

    base = items_gen.translate_tooltip_line(line, objective_names)
    if base and not has_ascii_letters(base):
        return base

    if line.startswith("Use: Teaches"):
        taught = translate_teaches(line, item, cn_name)
        if taught and not has_ascii_letters(taught):
            return finish(taught)

    custom = translate_effect_with_prefix(line)
    if custom and not has_ascii_letters(custom):
        return finish(custom)

    return ""


def main() -> None:
    items = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    existing_items = items_gen.load_item_data()
    name_map = items_gen.load_name_map()
    objective_names = items_gen.consumables.load_objective_names()

    translations: dict[str, str] = {}
    owners: dict[str, int] = {}
    for item in sorted(items, key=lambda row: int(row["id"])):
        cn_name = context_item_name(item, existing_items, name_map, objective_names)
        for raw in iter_effect_lines(item):
            raw = (raw or "").strip()
            if not raw or raw in translations:
                continue
            translated = translate_contextual(raw, item, cn_name, objective_names)
            if translated and not has_ascii_letters(translated):
                translations[raw] = translated
                owners[raw] = int(item["id"])

    all_green = sorted({line.strip() for item in items for line in iter_effect_lines(item) if line and line.strip()})
    missing = [line for line in all_green if line not in translations]

    lines = [
        "-- Generated by Tools/generate_tooltip_lines.py.",
        "-- Source: SourceData/EpochHead/items/items.json green tooltip lines.",
        "function LoadEpochCNTooltipLineData()",
        "  EpochCN_TooltipLineData = {",
    ]
    for raw in sorted(translations):
        lines.append(f'    ["{lua_escape(raw)}"] = "{lua_escape(translations[raw])}",')
    lines.extend(["  }", "end", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")

    audit = ROOT / "Tools" / "TOOLTIP_GREEN_COVERAGE.md"
    audit_lines = [
        "# Tooltip Green-Line Coverage",
        "",
        f"- Unique green lines: {len(all_green)}",
        f"- Exact Chinese translations: {len(translations)}",
        f"- Remaining lines needing manual review: {len(missing)}",
        "",
        "## Remaining Samples",
        "",
    ]
    for line in missing[:300]:
        audit_lines.append(f"- `{line}`")
    audit.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT}")
    print(f"unique_green={len(all_green)} translated={len(translations)} missing={len(missing)}")
    print(f"wrote {audit}")


if __name__ == "__main__":
    main()
