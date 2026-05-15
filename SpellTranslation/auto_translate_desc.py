#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WoW 3.3.5 Description Auto-Translator
Uses pattern matching and term dictionaries to translate spell descriptions.
Outputs a TSV file with translations.
"""
import re
import sys

# ============================================================
# Term Dictionary - WoW specific terms
# ============================================================
TERMS = {
    # Damage types
    "Holy damage": "神圣伤害",
    "Shadow damage": "暗影伤害",
    "Fire damage": "火焰伤害",
    "Frost damage": "冰霜伤害",
    "Nature damage": "自然伤害",
    "Arcane damage": "奥术伤害",
    "Physical damage": "物理伤害",
    "physical damage": "物理伤害",
    # Stats
    "attack power": "攻击强度",
    "Attack Power": "攻击强度",
    "spell power": "法术强度",
    "Spell Power": "法术强度",
    "spell damage": "法术伤害",
    "Spell Damage": "法术伤害",
    "melee attack power": "近战攻击强度",
    "ranged attack power": "远程攻击强度",
    # Attributes
    "Strength": "力量",
    "Agility": "敏捷",
    "Stamina": "耐力",
    "Intellect": "智力",
    "Spirit": "精神",
    # Resistances
    "Fire resistance": "火焰抗性",
    "Frost resistance": "冰霜抗性",
    "Nature resistance": "自然抗性",
    "Shadow resistance": "暗影抗性",
    "Arcane resistance": "奥术抗性",
    # Classes
    "Paladin": "圣骑士",
    "Warrior": "战士",
    "Mage": "法师",
    "Warlock": "术士",
    "Priest": "牧师",
    "Rogue": "盗贼",
    "Hunter": "猎人",
    "Shaman": "萨满",
    "Druid": "德鲁伊",
    "Death Knight": "死亡骑士",
    # Pets/Demons
    "Imp": "小鬼",
    "Voidwalker": "虚空行者",
    "Succubus": "魅魔",
    "Felhunter": "地狱猎犬",
    "Felguard": "恶魔卫士",
    # Common terms
    "combo point": "连击点",
    "combo points": "连击点",
    "critical strike": "暴击",
    "critical hit": "暴击",
    "mana": "法力值",
    "health": "生命值",
    "rage": "怒气",
    "energy": "能量",
    "runic power": "符文能量",
    "threat": "威胁值",
    "armor": "护甲",
    "dodge": "躲闪",
    "parry": "招架",
    "block": "格挡",
    "stealth": "潜行",
    "Stealth": "潜行",
    "stealthed": "潜行",
    "Stealthed": "潜行",
}


def load_pending():
    """Load all pending descriptions from the master file"""
    master = '/Users/macos/Documents/汉化补丁/SpellTranslation/spell_english_spellbook_priority.tsv'
    with open(master, 'r', encoding='utf-8') as f:
        header = next(f).rstrip('\n').split('\t')
        rows = []
        for line in f:
            cols = line.rstrip('\n').split('\t')
            while len(cols) < 12:
                cols.append('')
            rows.append(cols[:12])

    pending = {}
    for r in rows:
        desc_en = r[5].strip()
        desc_zh = r[9].strip()
        if desc_en and not desc_zh:
            if desc_en not in pending:
                pending[desc_en] = None
    return pending


def write_translations(translations, output_path):
    """Write translations to TSV"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("description_en\tdescription_zh\n")
        for en, zh in translations.items():
            if zh:
                en_clean = en.replace('\t', ' ')
                zh_clean = zh.replace('\t', ' ')
                f.write(f"{en_clean}\t{zh_clean}\n")
    count = sum(1 for v in translations.values() if v)
    print(f"Written {count} translations to {output_path}")


if __name__ == "__main__":
    pending = load_pending()
    print(f"Total pending: {len(pending)}")
    
    # Import the manual dict
    sys.path.insert(0, '/Users/macos/Documents/汉化补丁/SpellTranslation')
    from desc_dict import DESC_ZH as manual_dict
    
    translated = {}
    
    # Apply manual translations first
    for en in pending:
        if en in manual_dict:
            translated[en] = manual_dict[en]
    
    print(f"After manual dict: {len(translated)}")
    print(f"Still pending: {len(pending) - len(translated)}")
    
    # Write what we have
    write_translations(translated, '/Users/macos/Documents/汉化补丁/SpellTranslation/trans_desc_batch1.tsv')
