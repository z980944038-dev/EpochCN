#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WoW 3.3.5 Description Translation - Pattern-based batch translator
Handles mount, enchant, pet summon, and other pattern-based descriptions.
"""
import re

# ============================================================
# Pattern-based translation rules
# ============================================================

def translate_mount(desc):
    """Translate mount summon descriptions"""
    # Pattern: "Summons and dismisses a rideable XXX. This mount increases speed depending on your Riding Skill."
    m = re.match(r"Summons and dismisses (?:a rideable |an? )?(.+?)\.\s*(?:This mount increases speed depending on your Riding Skill\.)?$", desc)
    if m:
        mount_name = m.group(1).strip().rstrip('.')
        return f"召唤并解散{mount_name}。根据你的骑术技能提高速度。"
    
    # Pattern: "Summons a XXX, which serves as a mount for the caster. Speed is increased by $s2%. This mount increases speed depending on your Riding Skill."
    m = re.match(r"Summons (?:a |an )?(.+?),?\s*which serves as a mount(?:\s*for the caster)?\.?\s*Speed is increased by (\$s\d+)%\.?\s*(?:This mount increases speed depending on your Riding Skill\.)?$", desc)
    if m:
        mount_name = m.group(1).strip()
        speed_var = m.group(2)
        return f"召唤{mount_name}作为坐骑。速度提高{speed_var}%。根据你的骑术技能提高速度。"
    
    # Pattern: "Summons and dismisses a rideable XXX.   This mount increases speed depending on your Riding Skill."
    m = re.match(r"Summons and dismisses (?:a rideable |an? )?(.+?)\.\s+This mount increases speed depending on your Riding Skill\.$", desc)
    if m:
        mount_name = m.group(1).strip()
        return f"召唤并解散{mount_name}。根据你的骑术技能提高速度。"
    
    return None


def translate_enchant(desc):
    """Translate permanent enchant descriptions"""
    # Pattern: "Permanently enchant(s) a/an XXX to increase/give YYY by ZZZ."
    m = re.match(r"Permanently enchants? (?:a |an )?(.+?) to (.+)\.$", desc)
    if m:
        target = m.group(1).strip()
        effect = m.group(2).strip()
        target_zh = translate_enchant_target(target)
        effect_zh = translate_enchant_effect(effect)
        return f"永久附魔{target_zh}，使其{effect_zh}。"
    return None


def translate_enchant_target(target):
    """Translate enchant target"""
    targets = {
        "melee weapon": "一把近战武器",
        "weapon": "一把武器",
        "shield": "一面盾牌",
        "cloak": "一件披风",
        "chest": "一件胸甲",
        "boots": "一双靴子",
        "bracers": "一副护腕",
        "gloves": "一副手套",
        "ring": "一枚戒指",
        "2H weapon": "一把双手武器",
        "two-handed weapon": "一把双手武器",
        "head or leg slot item": "一件头部或腿部装备",
        "piece of chest armor": "一件胸甲",
    }
    for en, zh in targets.items():
        if en.lower() in target.lower():
            return zh
    return target


def translate_enchant_effect(effect):
    """Translate enchant effect text"""
    # Common patterns
    effect = re.sub(r"increase (?:the )?Frost spell power by (\d+)", r"冰霜法术强度提高\1", effect)
    effect = re.sub(r"increase (?:the )?Fire spell power by (\d+)", r"火焰法术强度提高\1", effect)
    effect = re.sub(r"increase (?:the )?Shadow spell power by (\d+)", r"暗影法术强度提高\1", effect)
    effect = re.sub(r"increase spell power by (\d+)", r"法术强度提高\1", effect)
    effect = re.sub(r"increase Strength by (\d+)", r"力量提高\1", effect)
    effect = re.sub(r"increase Agility by (\d+)", r"敏捷提高\1", effect)
    effect = re.sub(r"increase Stamina by (\d+)", r"耐力提高\1", effect)
    effect = re.sub(r"increase Intellect by (\d+)", r"智力提高\1", effect)
    effect = re.sub(r"increase Spirit by (\d+)", r"精神提高\1", effect)
    effect = re.sub(r"increase attack power by (\d+)", r"攻击强度提高\1", effect)
    effect = re.sub(r"increase haste rating by (\d+)", r"急速等级提高\1", effect)
    effect = re.sub(r"increase critical strike rating by (\d+)", r"暴击等级提高\1", effect)
    effect = re.sub(r"increase hit rating by (\d+)", r"命中等级提高\1", effect)
    effect = re.sub(r"increase defense rating by (\d+)", r"防御等级提高\1", effect)
    effect = re.sub(r"increase resilience rating by (\d+)", r"韧性等级提高\1", effect)
    effect = re.sub(r"increase armor penetration rating by (\d+)", r"护甲穿透等级提高\1", effect)
    effect = re.sub(r"increase expertise rating by (\d+)", r"精准等级提高\1", effect)
    effect = re.sub(r"restore (\d+) mana every 5 seconds", r"每5秒恢复\1点法力值", effect)
    effect = re.sub(r"restore (\d+) mana per 5 sec", r"每5秒恢复\1点法力值", effect)
    effect = re.sub(r"increase the effects of your healing spells by (\d+) and your spell damage by (\d+)", r"治疗法术效果提高\1，法术伤害提高\2", effect)
    effect = re.sub(r"increase healing done by spells and effects by up to (\d+)", r"法术和效果的治疗量最多提高\1", effect)
    effect = re.sub(r"increase spell damage by up to (\d+)", r"法术伤害最多提高\1", effect)
    effect = re.sub(r"increase damage and healing done by magical spells and effects by up to (\d+)", r"法术和效果造成的伤害和治疗量最多提高\1", effect)
    effect = re.sub(r"give a chance to restore (\d+) mana on spellcast", r"施法时有几率恢复\1点法力值", effect)
    effect = re.sub(r"sometimes increase your spell power by (\d+) for (\d+) secs", r"有时使你的法术强度提高\1，持续\2秒", effect)
    effect = re.sub(r"sometimes increase your attack power by (\d+) for (\d+) secs", r"有时使你的攻击强度提高\1，持续\2秒", effect)
    effect = re.sub(r"increase armor by (\d+)", r"护甲提高\1", effect)
    effect = re.sub(r"increase dodge rating by (\d+)", r"躲闪等级提高\1", effect)
    effect = re.sub(r"increase parry rating by (\d+)", r"招架等级提高\1", effect)
    effect = re.sub(r"increase block rating by (\d+)", r"格挡等级提高\1", effect)
    effect = re.sub(r"increase block value by (\d+)", r"格挡值提高\1", effect)
    effect = re.sub(r"add (\d+) damage", r"增加\1点伤害", effect)
    effect = re.sub(r"have a chance of disarming your attacker on a successful block", r"成功格挡时有几率缴械攻击者", effect)
    effect = re.sub(r"increase Nature resistance by (\d+)", r"自然抗性提高\1", effect)
    effect = re.sub(r"increase Fire resistance by (\d+)", r"火焰抗性提高\1", effect)
    effect = re.sub(r"increase Shadow resistance by (\d+)", r"暗影抗性提高\1", effect)
    effect = re.sub(r"increase Frost resistance by (\d+)", r"冰霜抗性提高\1", effect)
    effect = re.sub(r"increase Arcane resistance by (\d+)", r"奥术抗性提高\1", effect)
    effect = re.sub(r"increase all resistances by (\d+)", r"所有抗性提高\1", effect)
    effect = re.sub(r"increase all stats by (\d+)", r"所有属性提高\1", effect)
    effect = re.sub(r"increase run speed", r"提高移动速度", effect)
    effect = re.sub(r"increase mount speed by (\d+)%", r"骑乘速度提高\1%", effect)
    effect = re.sub(r"reduce threat from all spells and attacks by (\d+)%", r"所有法术和攻击的威胁值降低\1%", effect)
    effect = re.sub(r"occasionally heal the wearer for (\d+)", r"偶尔治疗佩戴者\1点生命值", effect)
    effect = re.sub(r"grant minor speed and (\d+) Stamina", r"略微提高移动速度并使耐力提高\1", effect)
    return effect


def translate_pet_summon(desc):
    """Translate Right Click pet summon descriptions"""
    m = re.match(r"Right Click to summon and dismiss your (.+)\.$", desc)
    if m:
        pet_name = m.group(1).strip()
        return f"右键点击召唤或解散你的{pet_name}。"
    return None


# Run the pattern-based translation
if __name__ == "__main__":
    master = '/Users/macos/Documents/汉化补丁/SpellTranslation/spell_english_spellbook_priority.tsv'
    with open(master, 'r', encoding='utf-8') as f:
        header = next(f).rstrip('\n').split('\t')
        rows = []
        for line in f:
            cols = line.rstrip('\n').split('\t')
            while len(cols) < 12:
                cols.append('')
            rows.append(cols[:12])

    # Collect unique pending descriptions
    unique_pending = {}
    for r in rows:
        desc_en = r[5].strip()
        desc_zh = r[9].strip()
        if desc_en and not desc_zh:
            if desc_en not in unique_pending:
                unique_pending[desc_en] = None

    print(f"Total unique pending descriptions: {len(unique_pending)}")

    # Apply pattern-based translations
    translated = 0
    for desc_en in list(unique_pending.keys()):
        zh = translate_mount(desc_en)
        if zh:
            unique_pending[desc_en] = zh
            translated += 1
            continue
        zh = translate_enchant(desc_en)
        if zh:
            unique_pending[desc_en] = zh
            translated += 1
            continue
        zh = translate_pet_summon(desc_en)
        if zh:
            unique_pending[desc_en] = zh
            translated += 1
            continue

    print(f"Pattern-translated: {translated}")
    print(f"Still need manual translation: {len(unique_pending) - translated}")

    # Write pattern-translated to TSV
    output = '/Users/macos/Documents/汉化补丁/SpellTranslation/trans_desc_patterns.tsv'
    with open(output, 'w', encoding='utf-8') as f:
        f.write("description_en\tdescription_zh\n")
        for en, zh in unique_pending.items():
            if zh:
                f.write(f"{en.replace(chr(9), ' ')}\t{zh.replace(chr(9), ' ')}\n")
    print(f"Written pattern translations to {output}")

    # Write remaining to a file for manual translation
    remaining_output = '/Users/macos/Documents/汉化补丁/SpellTranslation/pending_desc_remaining.tsv'
    with open(remaining_output, 'w', encoding='utf-8') as f:
        f.write("description_en\n")
        for en, zh in unique_pending.items():
            if not zh:
                f.write(f"{en.replace(chr(9), ' ')}\n")
    print(f"Written remaining to {remaining_output}")
