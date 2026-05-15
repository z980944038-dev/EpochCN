EpochCN:RegisterModule("Tooltip", function(E)
  if not EpochCNDB.tooltip then return end

  -- 性能优化：缓存频繁调用的全局函数为局部变量
  local strfind = string.find
  local strmatch = string.match
  local strgsub = string.gsub
  local getglobal = getglobal
  local type = type
  local tostring = tostring
  local pairs = pairs

  local function SetTooltipTitle(tooltip, title)
    if not tooltip or not title or title == "" then return end
    local name = tooltip:GetName()
    local titleLine = name and getglobal(name .. "TextLeft1")
    if titleLine and titleLine.SetText then
      titleLine:SetText(title)
    end
  end

  local function TranslateKnownTitle(tooltip)
    if not tooltip then return end
    local name = tooltip:GetName()
    local titleLine = name and getglobal(name .. "TextLeft1")
    if not titleLine or not titleLine.GetText then return end

    local title = titleLine:GetText()
    if not title or title == "" or string.match(title, "^%d+$") then return end

    local translated = (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[title])
      or (E.TranslateEnglishUnitName and E:TranslateEnglishUnitName(title))
      or (E.TranslateEnglishObjectName and E:TranslateEnglishObjectName(title))
    if translated and translated ~= title then
      SetTooltipTitle(tooltip, translated)
    end
  end

  local function AlreadyAdded(tooltip)
    local name = tooltip:GetName()
    if not name then return end

    for i = 1, tooltip:NumLines() do
      local line = getglobal(name .. "TextLeft" .. i)
      if line and line:GetText() then
        local text = line:GetText()
        if string.find(text, "EpochCN", 1, true) or string.find(text, "中文翻译：", 1, true) then
          return true
        end
      end
    end
  end

  local damageSchoolMap = {
    Fire = "火焰",
    Nature = "自然",
    Frost = "冰霜",
    Shadow = "暗影",
    Arcane = "奥术",
    Holy = "神圣",
    Physical = "物理",
  }

  local damageSchoolLowerMap = {
    fire = "火焰",
    nature = "自然",
    frost = "冰霜",
    shadow = "暗影",
    arcane = "奥术",
    holy = "神圣",
    physical = "物理",
  }

  local itemEffectNameMap = {
    ["Flaming Cannonball"] = "烈焰炮弹",
    ["Frost Arrow"] = "冰霜箭",
    ["Keeper's Sting"] = "守护者之刺",
    ["Searing Arrow"] = "灼热箭",
    ["a Frost Arrow"] = "冰霜箭",
    ["a Searing Arrow"] = "灼热箭",
  }

  local setNameMap = {
    ["The Gladiator"] = "角斗士",
    ["Savage Gladiator Helm"] = "野蛮角斗士头盔",
    ["Savage Gladiator Chain"] = "野蛮角斗士链甲",
    ["Savage Gladiator Leggings"] = "野蛮角斗士护腿",
    ["Savage Gladiator Greaves"] = "野蛮角斗士护胫",
    ["Savage Gladiator Grips"] = "野蛮角斗士护手",
    ["Beaststalker Armor"] = "野兽追猎者护甲",
    ["Beaststalker's Cap"] = "野兽追猎者之帽",
    ["Beaststalker's Tunic"] = "野兽追猎者外套",
    ["Beaststalker's Pants"] = "野兽追猎者短裤",
    ["Beaststalker's Gloves"] = "野兽追猎者手套",
    ["Beaststalker's Boots"] = "野兽追猎者长靴",
    ["Beaststalker's Mantle"] = "野兽追猎者衬肩",
    ["Beaststalker's Belt"] = "野兽追猎者腰带",
    ["Beaststalker's Bindings"] = "野兽追猎者护腕",
  }

  local staticTooltipLineMap = {
    ["Binds when picked up"] = "拾取后绑定",
    ["Binds when equipped"] = "装备后绑定",
    ["Binds when used"] = "使用后绑定",
    ["Random Enchantment"] = "随机附魔",
    ["Unique"] = "唯一",
    ["Unique-Equipped"] = "唯一装备",
    ["Item Level"] = "物品等级",
    ["Requires Level"] = "需要等级",
    ["Head"] = "头部",
    ["Neck"] = "颈部",
    ["Shoulder"] = "肩部",
    ["Back"] = "背部",
    ["Chest"] = "胸部",
    ["Wrist"] = "手腕",
    ["Hands"] = "手",
    ["Waist"] = "腰部",
    ["Legs"] = "腿部",
    ["Feet"] = "脚",
    ["Finger"] = "手指",
    ["Trinket"] = "饰品",
    ["One-Hand"] = "单手",
    ["Main Hand"] = "主手",
    ["Off Hand"] = "副手",
    ["Two-Hand"] = "双手",
    ["Ranged"] = "远程",
    ["Held In Off-hand"] = "副手物品",
    ["Shirt"] = "衬衣",
    ["Tabard"] = "战袍",
  }

  local spellNameOverrides = {
    ["Bear"] = "熊形态",
    ["Bear, Cat, or Travel Form"] = "熊形态、猎豹形态或旅行形态",
    ["Backstab"] = "背刺",
    ["Cat"] = "猎豹形态",
    ["Fade"] = "渐隐术",
    ["Holy Shock"] = "神圣震击",
    ["Immolate"] = "献祭",
    ["Kick"] = "脚踢",
    ["Lightning Bolt"] = "闪电箭",
    ["Maim"] = "割碎",
    ["Mutilate"] = "毁伤",
    ["Nature's Swiftness"] = "自然迅捷",
    ["Regrowth"] = "愈合",
    ["Shock"] = "震击",
    ["Shield Slam"] = "盾牌猛击",
    ["Sinister Strike"] = "邪恶攻击",
    ["Slice and Dice"] = "切割",
    ["Sprint"] = "疾跑",
    ["Starfire"] = "星火术",
    ["Stormstrike"] = "风暴打击",
    ["Swiftmend"] = "迅捷治愈",
    ["Thunder Clap"] = "雷霆一击",
    ["Traps"] = "陷阱",
    ["Travel Form"] = "旅行形态",
    ["Weakened Soul"] = "虚弱灵魂",
    ["Wrath"] = "愤怒",
  }

  local function HasCN(text)
    return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
  end

  local function HasAsciiLetters(text)
    return type(text) == "string" and string.find(text, "[A-Za-z]") ~= nil
  end

  local function NormalizeTooltipText(text)
    if type(text) ~= "string" then return "" end
    text = string.gsub(text, "|c%x%x%x%x%x%x%x%x", "")
    text = string.gsub(text, "|r", "")
    text = string.gsub(text, "\r", " ")
    text = string.gsub(text, "\n", " ")
    text = string.gsub(text, "%s+", " ")
    text = string.gsub(text, "^%s+", "")
    text = string.gsub(text, "%s+$", "")
    return text
  end

  local derivedSpellNameMap

  local function StripTrainingName(name)
    name = NormalizeTooltipText(name)
    name = strgsub(name, "^书卷：", "")
    name = strgsub(name, "^圣典：", "")
    name = strgsub(name, "^魔典：", "")
    name = strgsub(name, "^石板：", "")
    name = strgsub(name, "^宝典：", "")
    name = strgsub(name, "^手册：", "")
    name = strgsub(name, "雕文$", "")
    name = strgsub(name, "%s+[IVX]+$", "")
    return NormalizeTooltipText(name)
  end

  local function BuildDerivedSpellNameMap()
    if derivedSpellNameMap then return derivedSpellNameMap end

    derivedSpellNameMap = {}

    local glossaryText = EpochCN_Glossary and EpochCN_Glossary.text or {}
    for raw, localized in pairs(glossaryText) do
      if raw and localized and localized ~= "" and HasCN(localized) and not HasAsciiLetters(localized) then
        derivedSpellNameMap[raw] = localized
      end
    end

    local itemNameMap = EpochCN_ItemNameMap or {}
    for raw, localized in pairs(itemNameMap) do
      local spellName = strmatch(raw, "^Book of (.+)$")
      if not spellName then spellName = strmatch(raw, "^Codex:%s*(.+)$") end
      if not spellName then spellName = strmatch(raw, "^Codex of (.+)$") end
      if not spellName then spellName = strmatch(raw, "^Grimoire of (.+)$") end
      if not spellName then spellName = strmatch(raw, "^Tablet of (.+)$") end
      if not spellName then spellName = strmatch(raw, "^Tome of (.+)$") end
      if not spellName then spellName = strmatch(raw, "^Manual of (.+)$") end
      if not spellName then spellName = strmatch(raw, "^Handbook of (.+)$") end
      if spellName then
        spellName = NormalizeTooltipText(strgsub(spellName, "%s+[IVX]+$", ""))
      else
        spellName = strmatch(raw, "^Glyph of (.+)$")
      end

      if spellName then
        local translated = StripTrainingName(localized)
        if translated ~= "" and not HasAsciiLetters(translated) and not derivedSpellNameMap[spellName] then
          derivedSpellNameMap[spellName] = translated
        end
      end
    end

    for raw, localized in pairs(spellNameOverrides) do
      derivedSpellNameMap[raw] = localized
    end

    return derivedSpellNameMap
  end

  local function TranslateAbilityName(name)
    name = NormalizeTooltipText(name)
    name = strgsub(name, "[%.。]+$", "")
    local translated = BuildDerivedSpellNameMap()[name]
      or BuildDerivedSpellNameMap()[strgsub(name, "^%l", string.upper)]
      or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[name])
      or itemEffectNameMap[name]
    if translated and translated ~= "" then return translated end
    return name
  end

  local function JoinChineseList(values)
    local count = #values
    if count == 0 then return "" end
    if count == 1 then return values[1] end
    if count == 2 then return values[1] .. "和" .. values[2] end
    return table.concat(values, "、", 1, count - 1) .. "和" .. values[count]
  end

  local function TranslateAbilityList(text)
    text = NormalizeTooltipText(text)
    text = strgsub(text, ",%s+and%s+", ", ")
    text = strgsub(text, "%s+and%s+", ", ")

    local translated = {}
    for part in string.gmatch(text, "([^,]+)") do
      part = NormalizeTooltipText(part)
      if part ~= "" then
        table.insert(translated, TranslateAbilityName(part))
      end
    end

    if #translated == 0 then return text end
    return JoinChineseList(translated)
  end

  local function TranslateEffectName(name)
    name = NormalizeTooltipText(name)
    return TranslateAbilityName(name)
  end

  local function TranslateKnownObjectName(name)
    name = NormalizeTooltipText(name)
    local translated = (EpochCN_ItemNameMap and EpochCN_ItemNameMap[name])
      or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[name])
      or itemEffectNameMap[name]
    if translated and translated ~= name then return translated end

    translated = TranslateAbilityName(name)
    if translated ~= name then return translated end

    return (E.TranslateEnglishUnitName and E:TranslateEnglishUnitName(name)) or name
  end

  local mixedItemEffectLineMap = {
    ["A small satchel containing various trade goods."] = "一个装有各种贸易物资的小挎包。",
    ["An extremely potent alcoholic beverage."] = "一种效力极强的酒精饮料。",
    ["Allows the shaman to see elemental spirits."] = "使萨满祭司能够看见元素之灵。",
    ["Requires Argent Dawn - Revered"] = "需要银色黎明 - 崇敬",
    ["需要 Argent Dawn - Revered"] = "需要银色黎明 - 崇敬",
    ["Cure for the Touch of Zanzil."] = "赞吉尔之触的解药。",
  }

  local mixedItemEffectTargetMap = {
    ["Burning Exile"] = "炽燃流放者",
  }

  local function StripWrappedQuotes(text)
    if type(text) ~= "string" then return text end
    return (string.match(text, '^"(.-)"$')) or text
  end

  local function TranslateDurationText(duration)
    duration = NormalizeTooltipText(duration)
    local value = string.match(duration, "^(%d+) hrs?$")
    if value then return value .. "小时" end
    value = string.match(duration, "^(%d+) hours?$")
    if value then return value .. "小时" end
    value = string.match(duration, "^(%d+) mins?$")
    if value then return value .. "分钟" end
    value = string.match(duration, "^(%d+) minutes?$")
    if value then return value .. "分钟" end
    value = string.match(duration, "^(%d+) sec$")
    if value then return value .. "秒" end
    value = string.match(duration, "^(%d+) seconds?$")
    if value then return value .. "秒" end
    return duration
  end

  local function TranslateCooldownText(cooldown)
    cooldown = NormalizeTooltipText(cooldown)
    local value = string.match(cooldown, "^%((%d+) Sec Cooldown%)$")
    if value then return "（" .. value .. "秒冷却）" end
    value = string.match(cooldown, "^%((%d+) Min Cooldown%)$")
    if value then return "（" .. value .. "分钟冷却）" end
    value = string.match(cooldown, "^%((%d+) Hr Cooldown%)$")
    if value then return "（" .. value .. "小时冷却）" end
    return cooldown
  end

  local professionNameMap = {
    Alchemy = "炼金术",
    Blacksmithing = "锻造",
    Cooking = "烹饪",
    Enchanting = "附魔",
    Engineering = "工程学",
    FirstAid = "急救",
    ["First Aid"] = "急救",
    Fishing = "钓鱼",
    Herbalism = "草药学",
    Jewelcrafting = "珠宝加工",
    Leatherworking = "制皮",
    Mining = "采矿",
    Skinning = "剥皮",
    Tailoring = "裁缝",
  }

  local effectTermMap = {
    ["all primary stats"] = "所有主要属性",
    ["all stats"] = "所有属性",
    ["armor"] = "护甲",
    ["attack power"] = "攻击强度",
    ["block rating"] = "格挡等级",
    ["block value"] = "格挡值",
    ["critical strike"] = "爆击",
    ["critical strike rating"] = "爆击等级",
    ["critical strike chance"] = "爆击几率",
    ["chance to get a critical strike with all spells and attacks"] = "所有法术和攻击的爆击几率",
    ["chance to hit with all spells and attacks"] = "所有法术和攻击的命中几率",
    ["damage and healing done by magical spells and effects"] = "魔法法术和效果造成的伤害与治疗效果",
    ["damage dealt against other players"] = "对其他玩家造成的伤害",
    ["damage done by magical spells and effects"] = "魔法法术和效果造成的伤害",
    ["damage taken from other players"] = "受到其他玩家的伤害",
    ["defense"] = "防御",
    ["defense rating"] = "防御等级",
    ["dodge"] = "躲闪",
    ["dodge rating"] = "躲闪等级",
    ["expertise"] = "精准",
    ["expertise rating"] = "精准等级",
    ["haste rating"] = "急速等级",
    ["healing done by magical spells and effects"] = "魔法法术和效果的治疗效果",
    ["healing done by spells and effects"] = "法术和效果的治疗效果",
    ["hit rating"] = "命中等级",
    ["mana regen"] = "法力回复",
    ["mana regeneration"] = "法力回复",
    ["melee attack power"] = "近战攻击强度",
    ["melee haste"] = "近战急速",
    ["movement speed"] = "移动速度",
    ["parry"] = "招架",
    ["parry rating"] = "招架等级",
    ["ranged attack power"] = "远程攻击强度",
    ["ranged attack speed"] = "远程攻击速度",
    ["ranged haste"] = "远程急速",
    ["resilience rating"] = "韧性等级",
    ["run speed"] = "移动速度",
    ["shield block rating"] = "盾牌格挡等级",
    ["shield block value"] = "盾牌格挡值",
    ["spell critical strike rating"] = "法术爆击等级",
    ["spell critical strike chance"] = "法术爆击几率",
    ["spell damage and healing"] = "法术伤害与治疗效果",
    ["spell damage"] = "法术伤害",
    ["spell haste rating"] = "法术急速等级",
    ["spell hit rating"] = "法术命中等级",
    ["spell penetration"] = "法术穿透",
    ["spell power"] = "法术强度",
    ["stealth detection"] = "潜行侦测",
    ["weapon damage"] = "武器伤害",
  }

  local statNameMap = {
    Agility = "敏捷",
    Armor = "护甲",
    Intellect = "智力",
    Intelligence = "智力",
    Spirit = "精神",
    Stamina = "耐力",
    Strength = "力量",
  }

  local resistanceNameMap = {
    Arcane = "奥术抗性",
    Fire = "火焰抗性",
    Frost = "冰霜抗性",
    Nature = "自然抗性",
    Shadow = "暗影抗性",
    All = "所有抗性",
  }

  local function TranslateEffectTerm(term)
    term = NormalizeTooltipText(term)
    term = string.gsub(term, "^your%s+", "")
    term = string.gsub(term, "^the target's%s+", "")
    term = string.gsub(term, "^the player's%s+", "")
    term = string.gsub(term, "%s+", " ")

    if statNameMap[term] then return statNameMap[term] end
    if resistanceNameMap[term] then return resistanceNameMap[term] end

    local lower = string.lower(term)
    lower = string.gsub(lower, "^your%s+", "")
    lower = string.gsub(lower, "^the target's%s+", "")
    lower = string.gsub(lower, "^the player's%s+", "")
    return effectTermMap[lower]
  end

  local function TranslateSetName(name)
    name = NormalizeTooltipText(name)
    return setNameMap[name] or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[name]) or name
  end

  -- ========== 翻译结果缓存（LRU-style 大小限制，防止内存泄漏） ==========
  local itemEffectCache = {}
  local itemEffectCacheSize = 0
  local ITEM_EFFECT_CACHE_MAX = 512

  local function CacheGetEffect(text)
    return itemEffectCache[text]
  end

  local function CacheSetEffect(text, result)
    if itemEffectCache[text] ~= nil then return end  -- 已存在，跳过
    if itemEffectCacheSize >= ITEM_EFFECT_CACHE_MAX then
      -- 超出上限：清空缓存，避免迭代开销（物品 tooltip 不常变，代价极低）
      itemEffectCache = {}
      itemEffectCacheSize = 0
    end
    itemEffectCache[text] = result or false  -- false 表示"无翻译"
    itemEffectCacheSize = itemEffectCacheSize + 1
  end

  local function TranslateBonusText(text)
    text = NormalizeTooltipText(text)

    if staticTooltipLineMap[text] then return staticTooltipLineMap[text] end

    local label, number = string.match(text, "^(Item Level)%s+(%d+)$")
    if label and number then return staticTooltipLineMap[label] .. " " .. number end

    label, number = string.match(text, "^(Requires Level)%s+(%d+)$")
    if label and number then return staticTooltipLineMap[label] .. " " .. number end

    local profession, professionRank = string.match(text, "^Requires ([%a%s]+) %((%d+)%)$")
    if profession and professionRank then
      return "需要 " .. (professionNameMap[profession] or profession) .. " (" .. professionRank .. ")"
    end

    local genericTerm, genericAmount = string.match(text, "^Increases your (.-) by (%d+)%%%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. "%。" end
    end

    genericTerm, genericAmount = string.match(text, "^Increases (.-) by (%d+)%%%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. "%。" end
    end

    genericTerm, genericAmount = string.match(text, "^Improves your (.-) by (%d+)%%%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. "%。" end
    end

    genericTerm, genericAmount = string.match(text, "^Decreases your (.-) by (%d+)%%%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "降低 " .. genericAmount .. "%。" end
    end

    genericTerm, genericAmount = string.match(text, "^Increases your (.-) by (%d+)%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. " 点。" end
    end

    genericTerm, genericAmount = string.match(text, "^Increases (.-) by (%d+)%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. " 点。" end
    end

    genericTerm, genericAmount = string.match(text, "^Improves your (.-) by (%d+)%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "提高 " .. genericAmount .. " 点。" end
    end

    genericTerm, genericAmount = string.match(text, "^Increases (.-) by up to (%d+)%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "最多提高 " .. genericAmount .. " 点。" end
    end

    genericTerm, genericAmount = string.match(text, "^Increases your (.-) by up to (%d+)%.?$")
    if genericTerm and genericAmount then
      local cn = TranslateEffectTerm(genericTerm)
      if cn then return cn .. "最多提高 " .. genericAmount .. " 点。" end
    end

    -- ========== 基础属性 ==========
    local value = string.match(text, "%+(%d+) Strength")
    if value then return "+" .. value .. " 力量" end

    value = string.match(text, "%+(%d+) Agility")
    if value then return "+" .. value .. " 敏捷" end

    value = string.match(text, "%+(%d+) Stamina")
    if value then return "+" .. value .. " 耐力" end

    value = string.match(text, "%+(%d+) Intellect")
    if value then return "+" .. value .. " 智力" end

    value = string.match(text, "%+(%d+) Spirit")
    if value then return "+" .. value .. " 精神" end

    value = string.match(text, "%+(%d+) Armor")
    if value then return "+" .. value .. " 护甲" end

    value = string.match(text, "%+(%d+) Attack Power")
    if value then return "+" .. value .. " 攻击强度" end

    value = string.match(text, "%+(%d+) All Resistances")
    if value then return "+" .. value .. " 所有抗性" end

    value = string.match(text, "%+(%d+) Fire Resistance")
    if value then return "+" .. value .. " 火焰抗性" end

    value = string.match(text, "%+(%d+) Nature Resistance")
    if value then return "+" .. value .. " 自然抗性" end

    value = string.match(text, "%+(%d+) Frost Resistance")
    if value then return "+" .. value .. " 冰霜抗性" end

    value = string.match(text, "%+(%d+) Shadow Resistance")
    if value then return "+" .. value .. " 暗影抗性" end

    value = string.match(text, "%+(%d+) Arcane Resistance")
    if value then return "+" .. value .. " 奥术抗性" end

    -- ========== 治疗/法力药水（范围值） ==========
    -- "Restores 1050 to 1750 health." 或 "Restores 1050到1750 health."
    local lo, hi = string.match(text, "Restores (%d+) ?to ?(%d+) health")
    if not lo then lo, hi = string.match(text, "Restores (%d+)到(%d+) health") end
    if lo and hi then return "恢复 " .. lo .. " 到 " .. hi .. " 点生命值。" end

    lo, hi = string.match(text, "Restores (%d+) ?to ?(%d+) mana")
    if not lo then lo, hi = string.match(text, "Restores (%d+)到(%d+) mana") end
    if lo and hi then return "恢复 " .. lo .. " 到 " .. hi .. " 点法力值。" end

    -- "Restores 2934 mana over 30 sec." 或含中文"秒"
    local amt, dur = string.match(text, "Restores (%d+) mana over (%d+)")
    if amt and dur then return "在 " .. dur .. " 秒内恢复 " .. amt .. " 点法力值。" end

    amt, dur = string.match(text, "Restores (%d+) health over (%d+)")
    if amt and dur then return "在 " .. dur .. " 秒内恢复 " .. amt .. " 点生命值。" end

    -- 单值恢复 "Restores 500 health."
    value = string.match(text, "^Restores (%d+) health%.?$")
    if value then return "恢复 " .. value .. " 点生命值。" end

    value = string.match(text, "^Restores (%d+) mana%.?$")
    if value then return "恢复 " .. value .. " 点法力值。" end

    -- ========== 饮食相关 ==========
    if string.find(text, "Must remain seated while drinking", 1, true) then
      return "饮用时必须保持坐姿。"
    end
    if string.find(text, "Must remain seated while eating", 1, true) then
      return "进食时必须保持坐姿。"
    end

    -- ========== 冷却时间 ==========
    local duration = string.match(text, "%((%d+) [Mm]in cooldown%)")
    if duration then return "(" .. duration .. "分钟冷却)" end

    duration = string.match(text, "%((%d+) [Hh]our cooldown%)") or string.match(text, "%((%d+) Hr Cooldown%)")
    if duration then return "(" .. duration .. "小时冷却)" end

    duration = string.match(text, "%((%d+) [Ss]ec cooldown%)")
    if duration then return "(" .. duration .. "秒冷却)" end

    local dispelCooldown = string.match(text, "^Removes all movement impairing effects and all effects which cause loss of control of your character%.%s*(%b())$")
    if dispelCooldown then
      return "移除所有限制移动的效果，以及所有使你失去角色控制的效果。" .. TranslateCooldownText(dispelCooldown)
    end
    if text == "Removes all movement impairing effects and all effects which cause loss of control of your character." then
      return "移除所有限制移动的效果，以及所有使你失去角色控制的效果。"
    end

    -- ========== 战斗属性提升 ==========
    local attackPower, hit = string.match(text, "Increases your attack power by (%d+) and your chance to hit by (%d+)%%")
    if attackPower and hit then return "攻击强度提高 " .. attackPower .. " 点，命中几率提高 " .. hit .. "%。" end

    value = string.match(text, "Increased Defense %+?(%d+)")
    if value then return "防御等级提高 " .. value .. "。" end

    value = string.match(text, "Improves your chance to get a critical strike with melee and ranged attacks by (%d+)%%")
    if value then return "近战和远程攻击爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to get a critical strike by (%d+)%%")
    if value then return "爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to get a critical strike with spells by (%d+)%%")
    if value then return "法术爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to get a critical strike with all spells and attacks by (%d+)%%")
    if value then return "所有法术和攻击的爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Increases your chance to get a critical strike with spells by (%d+)%%")
    if value then return "法术爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to hit with melee and ranged attacks by (%d+)%%")
    if value then return "近战和远程攻击命中几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to hit with spells by (%d+)%%")
    if value then return "法术命中几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to hit with all spells and attacks by (%d+)%%")
    if value then return "所有法术和攻击的命中几率提高 " .. value .. "%。" end

    value = string.match(text, "Increases your chance to hit with spells by (%d+)%%")
    if value then return "法术命中几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to hit by (%d+)%%")
    if value then return "命中几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to dodge an attack by (%d+)%%")
    if value then return "躲闪几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to dodge or parry by (%d+)%%")
    if value then return "躲闪或招架几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to block attacks with a shield by (%d+)%%")
    if value then return "盾牌格挡几率提高 " .. value .. "%。" end

    value = string.match(text, "Reduces your chance to be dodged or parried by (%d+)%%")
    if value then return "你的攻击被躲闪或招架的几率降低 " .. value .. "%。" end

    value = string.match(text, "Increases your chance to parry an attack by (%d+)%%")
    if value then return "招架几率提高 " .. value .. "%。" end

    value = string.match(text, "Increases your chance to dodge an attack by (%d+)%%")
    if value then return "躲闪几率提高 " .. value .. "%。" end

    value = string.match(text, "Increases your chance to block attacks with a shield by (%d+)%%")
    if value then return "盾牌格挡几率提高 " .. value .. "%。" end

    local chance, mana = string.match(text, "Your normal ranged attacks have a (%d+)%% chance of restoring (%d+) mana")
    if chance and mana then return "你的普通远程攻击有 " .. chance .. "% 几率恢复 " .. mana .. " 点法力值。" end

    local spellcastMana, spellcastDuration = string.match(text, "^Chance on successful spellcast to restore (%d+) Mana over (%d+) sec%.?$")
    if spellcastMana and spellcastDuration then
      return "成功施法时有几率在 " .. spellcastDuration .. " 秒内恢复 " .. spellcastMana .. " 点法力值。"
    end

    -- ========== 炉石/传送 ==========
    if string.find(text, "Returns you to your home location", 1, true) then
      return "返回炉石绑定位置。"
    end

    if string.find(text, "Speak to an Innkeeper in a different place to change your home location", 1, true) then
      return "与其他地方的旅店老板交谈，可以改变你的炉石绑定位置。"
    end

    local zone = string.match(text, "Returns you to (.+)%.?$")
    if zone then return "返回" .. TranslateEffectName(zone) .. "。" end

    -- ========== 图腾 ==========
    if string.find(text, "Can count as an Air, Earth, Fire, and Water Totem", 1, true) then
      return "可视为空气、大地、火焰和水图腾。"
    end

    -- ========== 法术/治疗增益 ==========
    value = string.match(text, "Increases healing done by magical spells and effects by up to (%d+)")
    if value then return "魔法法术和效果的治疗量最多提高 " .. value .. " 点。" end

    value = string.match(text, "Increases healing done by spells and effects by up to (%d+)")
    if value then return "法术和效果的治疗量最多提高 " .. value .. " 点。" end

    value = string.match(text, "^Increases spell damage and healing by up to (%d+)%.?$")
    if value then return "法术伤害和治疗效果最多提高 " .. value .. " 点。" end

    value = string.match(text, "^Increases spell damage by up to (%d+)%.?$")
    if value then return "法术伤害最多提高 " .. value .. " 点。" end

    value = string.match(text, "^Increases damage and healing done by magical spells and effects by up to (%d+)%.?$")
    if value then return "魔法法术和效果造成的伤害与治疗量最多提高 " .. value .. " 点。" end

    value = string.match(text, "^Increases damage done by magical spells and effects by up to (%d+)%.?$")
    if value then return "魔法法术和效果造成的伤害最多提高 " .. value .. " 点。" end

    local spellDamage, healing = string.match(text, "^[Ss]pell damage done by up to (%d+) and healing done by up to (%d+) for all magical spells and effects%.?$")
    if not spellDamage then
      spellDamage, healing = string.match(text, "^Strengthening done by up to (%d+) and healing done by up to (%d+) for all magical spells and effects%.?$")
    end
    if spellDamage and healing then
      return "所有魔法法术和效果造成的伤害最多提高" .. spellDamage .. "点，治疗效果最多提高" .. healing .. "点。"
    end

    healing, spellDamage = string.match(text, "^Healing done by up to (%d+) and damage done by up to (%d+) for all magical spells and effects%.?$")
    if not healing then
      healing, spellDamage = string.match(text, "^Increases healing done by up to (%d+) and damage done by up to (%d+) for all magical spells and effects%.?$")
    end
    if healing and spellDamage then
      return "所有魔法法术和效果的治疗效果最多提高" .. healing .. "点，造成的伤害最多提高" .. spellDamage .. "点。"
    end

    spellDamage, healing = string.match(text, "^Increases damage done by up to (%d+) and healing done by up to (%d+) for all magical spells and effects%.?$")
    if spellDamage and healing then
      return "所有魔法法术和效果造成的伤害最多提高" .. spellDamage .. "点，治疗效果最多提高" .. healing .. "点。"
    end

    local schoolName, schoolAmount = string.match(text, "^Increases damage done by (%a+) spells and effects by up to (%d+)%.?$")
    if schoolName and schoolAmount then
      return (damageSchoolMap[schoolName] or schoolName) .. "法术和效果造成的伤害最多提高 " .. schoolAmount .. " 点。"
    end

    local attackPowerBonus, flaskDuration, cooldownSuffix = string.match(text, "^Increases melee and ranged attack power by (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.%s*(%b())$")
    if not attackPowerBonus then
      attackPowerBonus, flaskDuration = string.match(text, "^Increases melee and ranged attack power by (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.$")
    end
    if attackPowerBonus and flaskDuration then
      return "近战和远程攻击强度提高" .. attackPowerBonus .. "点，持续" .. TranslateDurationText(flaskDuration) .. "。算作战斗和守护药剂。此效果在死亡后仍然存在。" .. (cooldownSuffix and TranslateCooldownText(cooldownSuffix) or "")
    end

    local flaskSpellPower
    flaskSpellPower, flaskDuration, cooldownSuffix = string.match(text, "^Increases damage done by magical spells and effects by up to (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.%s*(%b())$")
    if not flaskSpellPower then
      flaskSpellPower, flaskDuration, cooldownSuffix = string.match(text, "^Increases damage done by magical spells effects by up to (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.%s*(%b())$")
    end
    if not flaskSpellPower then
      flaskSpellPower, flaskDuration = string.match(text, "^Increases damage done by magical spells and effects by up to (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.$")
    end
    if not flaskSpellPower then
      flaskSpellPower, flaskDuration = string.match(text, "^Increases damage done by magical spells effects by up to (%d+) for (.-)%. Counts as both a Battle and Guardian elixir%. This effect persists through death%.$")
    end
    if flaskSpellPower and flaskDuration then
      return "魔法法术和效果造成的伤害最多提高" .. flaskSpellPower .. "点，持续" .. TranslateDurationText(flaskDuration) .. "。算作战斗和守护药剂。此效果在死亡后仍然存在。" .. (cooldownSuffix and TranslateCooldownText(cooldownSuffix) or "")
    end

    local spellSchool, schoolBonus, elixirDuration, elixirCooldown = string.match(text, "^Increases spell (%a+) damage by up to (%d+) for (.-)%.? Battle Elixir%.?%s*(%b())$")
    if not spellSchool then
      spellSchool, schoolBonus, elixirDuration = string.match(text, "^Increases spell (%a+) damage by up to (%d+) for (.-)%.? Battle Elixir%.?$")
    end
    if spellSchool and schoolBonus and elixirDuration then
      return (damageSchoolLowerMap[spellSchool] or spellSchool) .. "法术伤害最多提高" .. schoolBonus .. "点，持续" .. TranslateDurationText(elixirDuration) .. "。战斗药剂。" .. (elixirCooldown and TranslateCooldownText(elixirCooldown) or "")
    end

    local spellPower, sizeDuration, sizeCooldown = string.match(text, "^Increases spell power by (%d+) and decreases size for (.-)%. Battle Elixir%.%s*(%b())$")
    if not spellPower then
      spellPower, sizeDuration = string.match(text, "^Increases spell power by (%d+) and decreases size for (.-)%. Battle Elixir%.$")
    end
    if spellPower and sizeDuration then
      return "法术强度提高" .. spellPower .. "点并缩小体型，持续" .. TranslateDurationText(sizeDuration) .. "。战斗药剂。" .. (sizeCooldown and TranslateCooldownText(sizeCooldown) or "")
    end

    -- 法术学派增益
    for school, cn in pairs(damageSchoolMap) do
      value = string.match(text, "Increases " .. school .. " spell damage by up to (%d+)")
      if value then return cn .. "法术伤害最多提高 " .. value .. " 点。" end
    end

    -- ========== 等级提升类 ==========
    value = string.match(text, "Improves spell critical strike rating by (%d+)")
    if value then return "法术爆击等级提高 " .. value .. "。" end

    value = string.match(text, "Improves critical strike rating by (%d+)")
    if value then return "爆击等级提高 " .. value .. "。" end

    value = string.match(text, "Improves hit rating by (%d+)")
    if value then return "命中等级提高 " .. value .. "。" end

    value = string.match(text, "Improves haste rating by (%d+)")
    if value then return "急速等级提高 " .. value .. "。" end

    value = string.match(text, "Improves spell hit rating by (%d+)")
    if value then return "法术命中等级提高 " .. value .. "。" end

    value = string.match(text, "Improves spell haste rating by (%d+)")
    if value then return "法术急速等级提高 " .. value .. "。" end

    value = string.match(text, "Increases defense rating by (%d+)")
    if value then return "防御等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your dodge rating by (%d+)")
    if value then return "躲闪等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your parry rating by (%d+)")
    if value then return "招架等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your block rating by (%d+)")
    if value then return "格挡等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your shield block rating by (%d+)")
    if value then return "盾牌格挡等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your resilience rating by (%d+)")
    if value then return "韧性等级提高 " .. value .. "。" end

    value = string.match(text, "Increases your expertise rating by (%d+)")
    if value then return "精准等级提高 " .. value .. "。" end

    value = string.match(text, "Increases armor penetration rating by (%d+)")
    if value then return "护甲穿透等级提高 " .. value .. "。" end

    value = string.match(text, "Increases attack power by (%d+)")
    if value then return "攻击强度提高 " .. value .. " 点。" end

    value = string.match(text, "Increases ranged attack power by (%d+)")
    if value then return "远程攻击强度提高 " .. value .. " 点。" end

    value = string.match(text, "Increases spell power by (%d+)")
    if value then return "法术强度提高 " .. value .. " 点。" end

    value = string.match(text, "Increases your armor penetration by (%d+)")
    if value then return "护甲穿透提高 " .. value .. " 点。" end

    local resistSchool, resistValue = string.match(text, "^Increases your resistance to (%a+) by (%d+)%.?$")
    if resistSchool and resistValue then
      return (resistanceNameMap[resistSchool] or (resistSchool .. "抗性")) .. "提高 " .. resistValue .. " 点。"
    end

    resistSchool, resistValue = string.match(text, "^Increases (%a+) resistance by (%d+)%.?$")
    if resistSchool and resistValue then
      return (resistanceNameMap[resistSchool] or (resistSchool .. "抗性")) .. "提高 " .. resistValue .. " 点。"
    end

    resistValue = string.match(text, "^Increases all resistances by (%d+)%.?$")
    if resistValue then return "所有抗性提高 " .. resistValue .. " 点。" end

    local resistSchoolA, resistSchoolB
    resistSchoolA, resistSchoolB, resistValue = string.match(text, "^Increases (%a+) and (%a+) resistance by (%d+)%.?$")
    if resistSchoolA and resistSchoolB and resistValue then
      return (damageSchoolLowerMap[string.lower(resistSchoolA)] or resistSchoolA) .. "和" .. (damageSchoolLowerMap[string.lower(resistSchoolB)] or resistSchoolB) .. "抗性提高 " .. resistValue .. " 点。"
    end

    local dualResistValue
    dualResistValue, resistSchoolA, resistSchoolB = string.match(text, "^%+(%d+) (%a+) and (%a+) Resistance%.?$")
    if dualResistValue and resistSchoolA and resistSchoolB then
      return (resistanceNameMap[resistSchoolA] or (resistSchoolA .. "抗性")) .. "和" .. (resistanceNameMap[resistSchoolB] or (resistSchoolB .. "抗性")) .. "提高 " .. dualResistValue .. " 点。"
    end

    value = string.match(text, "^Increases your maximum health by (%d+)%.?$")
      or string.match(text, "^Increases the player's maximum health by (%d+)%.?$")
    if value then return "生命值上限提高 " .. value .. " 点。" end

    value = string.match(text, "^Increases your maximum mana by (%d+)%.?$")
      or string.match(text, "^Increases the player's maximum mana by (%d+)%.?$")
    if value then return "法力值上限提高 " .. value .. " 点。" end

    local primaryStats, extraStamina = string.match(text, "^Increases your Primary Stats by (%d+) and Stamina by an additional (%d+) when in Arenas, Battlegrounds, and PvP Objectives%.?$")
    if primaryStats and extraStamina then
      return "在竞技场、战场和玩家对战目标区域中，主属性提高 " .. primaryStats .. " 点，额外获得 " .. extraStamina .. " 点耐力。"
    end

    local gainTerm, gainAmount, lossTerm, lossAmount, statDuration = string.match(text, "^Increases (%a+) by (%d+), but decreases (%a+) by (%d+) for (.-)%.?$")
    if gainTerm and gainAmount and lossTerm and lossAmount and statDuration then
      local gainName = TranslateEffectTerm(gainTerm) or gainTerm
      local lossName = TranslateEffectTerm(lossTerm) or lossTerm
      return gainName .. "提高 " .. gainAmount .. " 点，但" .. lossName .. "降低 " .. lossAmount .. " 点，持续" .. TranslateDurationText(statDuration) .. "。"
    end

    -- ========== 每5秒恢复 ==========
    value = string.match(text, "Restores (%d+) mana per 5 sec")
      or string.match(text, "Restores (%d+) mana every 5 sec")
      or string.match(text, "Restores (%d+) mana every 5 seconds")
      or string.match(text, "Restores (%d+) mana per 5 seconds")
    if value then return "每5秒恢复 " .. value .. " 点法力值。" end

    value = string.match(text, "Restores (%d+) health per 5 sec")
      or string.match(text, "Restores (%d+) health every 5 sec")
      or string.match(text, "Restores (%d+) health every 5 seconds")
      or string.match(text, "Restores (%d+) health per 5 seconds")
    if value then return "每5秒恢复 " .. value .. " 点生命值。" end

    -- ========== 伤害吸收 ==========
    lo, hi = string.match(text, "[Aa]bsorbs (%d+) ?to ?(%d+)")
    if not lo then lo, hi = string.match(text, "[Aa]bsorbs (%d+)到(%d+)") end
    if lo and hi then return "吸收 " .. lo .. " 到 " .. hi .. " 点伤害。" end

    value = string.match(text, "[Aa]bsorbs (%d+) damage")
    if value then return "吸收 " .. value .. " 点伤害。" end

    -- ========== 格挡值 ==========
    value = string.match(text, "Increases your shield block value by (%d+)")
    if value then return "盾牌格挡值提高 " .. value .. " 点。" end

    value = string.match(text, "Increases block value by (%d+)")
    if value then return "格挡值提高 " .. value .. " 点。" end

    -- ========== 法术穿透 ==========
    value = string.match(text, "Increases your spell penetration by (%d+)")
    if value then return "法术穿透提高 " .. value .. " 点。" end

    -- ========== 精准等级 / 专精值 ==========
    value = string.match(text, "Increases your expertise by (%d+)")
    if value then return "精准提高 " .. value .. " 点。" end

    -- ========== 近战/远程攻速 ==========
    value = string.match(text, "Increases melee haste by (%d+)%%")
    if value then return "近战攻击速度提高 " .. value .. "%。" end

    value = string.match(text, "Increases ranged haste by (%d+)%%")
    if value then return "远程攻击速度提高 " .. value .. "%。" end

    value = string.match(text, "^Improves your casting speed and causes periodic effects to occur more frequently with spells by ([%d%.]+)%%%.?$")
    if value then return "法术施放速度提高，且周期性法术效果触发频率提高 " .. value .. "%。" end

    value = string.match(text, "^Increases the effect that healing potions have on the wearer by (%d+)%%%. This effect does not stack%.?$")
    if value then return "你受到的治疗药水效果提高 " .. value .. "% 。该效果无法叠加。" end

    value = string.match(text, "^Increases the speed of your Ghost Wolf ability by ([%d%.]+)%%%.?$")
    if value then return "幽魂之狼的移动速度提高 " .. value .. "%。" end

    local spellName, spellSeconds = string.match(text, "^Reduces the casting time of your (.+) spell by ([%d%.]+) sec%.?$")
    if spellName and spellSeconds then
      return TranslateAbilityName(spellName) .. "的施法时间缩短 " .. spellSeconds .. " 秒。"
    end

    spellName, spellSeconds = string.match(text, "^The casting time on your (.+) spell is reduced by ([%d%.]+) sec%.?$")
    if spellName and spellSeconds then
      return TranslateAbilityName(spellName) .. "的施法时间缩短 " .. spellSeconds .. " 秒。"
    end

    local critSpell, critValue = string.match(text, "^Improves your chance to get a critical strike with all (.+) spells by (%d+)%%%.?$")
    if critSpell and critValue then
      return "所有" .. TranslateAbilityName(critSpell) .. "法术的爆击几率提高 " .. critValue .. "%。"
    end

    local petHeal = string.match(text, "^Causes your pet to be healed for ([%d%.]+)%% of the damage you deal%.?$")
    if petHeal then
      return "你的宠物恢复相当于你造成伤害 " .. petHeal .. "% 的生命值。"
    end

    local fadeDodge = string.match(text, "^Fade now also grants you a ([%d%.]+)%% chance to dodge attacks%.?$")
    if fadeDodge then
      return "渐隐术现在还会使你获得 " .. fadeDodge .. "% 的躲闪攻击几率。"
    end

    local moveSpeed, forms = string.match(text, "^Increases your movement speed by ([%d%.]+)%% while in (.+)%. Only active outdoors%.?$")
    if moveSpeed and forms then
      return "在" .. TranslateAbilityName(forms) .. "时，移动速度提高 " .. moveSpeed .. "% 。仅在室外生效。"
    end

    moveSpeed = string.match(text, "^Increases your movement speed by ([%d%.]+)%%%.?$")
    if moveSpeed then
      return "移动速度提高 " .. moveSpeed .. "% 。"
    end

    local firstSpell, nextSpell, reduction = string.match(text, "^Your (.+) casts have a chance to reduce the cast time on your next (.+) by ([%d%.]+) sec%.?$")
    if firstSpell and nextSpell and reduction then
      return "你的" .. TranslateAbilityName(firstSpell) .. "有几率使下一次" .. TranslateAbilityName(nextSpell) .. "的施法时间缩短 " .. reduction .. " 秒。"
    end

    local avoidInterrupt, castSpell = string.match(text, "^Gives you a ([%d%.]+)%% chance to avoid interruption caused by damage while casting (.+)%.?$")
    if avoidInterrupt and castSpell then
      return "当你施放" .. TranslateAbilityName(castSpell) .. "时，有 " .. avoidInterrupt .. "% 的几率避免因受到伤害而被打断。"
    end

    local spellEffect, sourceSpell, effectSeconds = string.match(text, "^Reduces the duration of the (.+) effect caused by your (.+) by ([%d%.]+) sec%.?$")
    if spellEffect and sourceSpell and effectSeconds then
      return TranslateAbilityName(sourceSpell) .. "造成的" .. TranslateAbilityName(spellEffect) .. "效果持续时间缩短 " .. effectSeconds .. " 秒。"
    end

    local manaSpell, manaCost = string.match(text, "^Reduces the mana cost of your (.+) spell by ([%d%.]+)%% of its base cost%.?$")
    if manaSpell and manaCost then
      return TranslateAbilityName(manaSpell) .. "的法力消耗降低其基础消耗的 " .. manaCost .. "% 。"
    end

    local cleanseSpell, cleanseHeal = string.match(text, "^Your (.+) spell also heals the target for ([%d%.]+)%.?$")
    if cleanseSpell and cleanseHeal then
      return "你的" .. TranslateAbilityName(cleanseSpell) .. "还会为目标恢复 " .. cleanseHeal .. " 点生命值。"
    end

    local dispelSpell, dispelChance = string.match(text, "^Reduces your chance that (.+) will be dispelled by ([%d%.]+)%%%.?$")
    if dispelSpell and dispelChance then
      return TranslateAbilityName(dispelSpell) .. "被驱散的几率降低 " .. dispelChance .. "% 。"
    end

    local healingSpell, healingBonus = string.match(text, "^Increases the effective spell power of your (.+) when used as a healing spell by ([%d%.]+)%%%.?$")
    if healingSpell and healingBonus then
      return TranslateAbilityName(healingSpell) .. "作为治疗法术使用时，受到的法术强度加成提高 " .. healingBonus .. "%。"
    end

    local energySpell, energyCost = string.match(text, "^Reduces the [Ee]nergy cost of your (.+) by ([%d%.]+)%.?$")
    if energySpell and energyCost then
      return TranslateAbilityName(energySpell) .. "的能量消耗降低 " .. energyCost .. " 点。"
    end

    local cooldownSpell, cooldownSeconds = string.match(text, "^Reduces the cooldown of your (.+) ability by ([%d%.]+) sec%.?$")
    if not cooldownSpell then
      cooldownSpell, cooldownSeconds = string.match(text, "^Reduces the cooldown of your (.+) by ([%d%.]+) sec%.?$")
    end
    if not cooldownSpell then
      cooldownSpell, cooldownSeconds = string.match(text, "^Reduces the cooldown of your (.+) by ([%d%.]+) seconds?%.?$")
    end
    if not cooldownSpell then
      cooldownSpell, cooldownSeconds = string.match(text, "^(.+)'s cooldown is reduced by ([%d%.]+) seconds?%.?$")
    end
    if cooldownSpell and cooldownSeconds then
      return TranslateAbilityName(cooldownSpell) .. "的冷却时间缩短 " .. cooldownSeconds .. " 秒。"
    end

    local durationSpell, durationSeconds = string.match(text, "^Increases the duration of your (.+) ability by ([%d%.]+) sec%.?$")
    if durationSpell and durationSeconds then
      return TranslateAbilityName(durationSpell) .. "的持续时间延长 " .. durationSeconds .. " 秒。"
    end

    value = string.match(text, "^Reduces the cast time of your Cyclone spell by ([%d%.]+) sec%.?$")
    if value then return "飓风术的施法时间缩短 " .. value .. " 秒。" end

    value = string.match(text, "^Increases ranged attack speed by ([%d%.]+)%%%.?$")
    if value then return "远程攻击速度提高 " .. value .. "% 。" end

    value = string.match(text, "^Reduces the cooldown of your Hammer of Justice by ([%d%.]+) sec%.?$")
    if value then return "制裁之锤的冷却时间缩短 " .. value .. " 秒。" end

    value = string.match(text, "^Reduces the pushback suffered from damaging attacks while casting Fear by (%d+)%%%.?$")
    if value then return "施放恐惧术时，受到伤害攻击造成的施法延迟降低 " .. value .. "%。" end

    value = string.match(text, "^Decreases the magical resistances of your spell targets by (%d+)%.?$")
    if value then return "你的法术目标的魔法抗性降低 " .. value .. " 点。" end

    value = string.match(text, "^Duration of incoming crowd control effects reduced by (%d+)%%%. Does not stack with similar effects%.?$")
    if value then return "你受到的控制效果持续时间缩短 " .. value .. "% 。该效果无法与同类效果叠加。" end

    local lossControlDuration, lossControlCooldown = string.match(text, "^Removes any loss of control effect with a duration of (%d+) seconds or more%. This effect can only occur once every (%d+) min%.?$")
    if not lossControlDuration then
      lossControlDuration, lossControlCooldown = string.match(text, "^Removes any loss of control effect with a duration of (%d+) seconds or more%. This effect can only occur once every (%d+) minute%.?$")
    end
    if lossControlDuration and lossControlCooldown then
      return "移除任意持续 " .. lossControlDuration .. " 秒或更久的失控效果。该效果每 " .. lossControlCooldown .. " 分钟只能触发一次。"
    end

    if text == "Allows underwater breathing." then
      return "允许在水下呼吸。"
    end

    if text == "Immune to Disarm." then
      return "免疫缴械。"
    end

    local professionName, professionBonus = string.match(text, "^([%a%s]+) %+(%d+)%.?$")
    if professionName and professionBonus and professionNameMap[professionName] then
      return professionNameMap[professionName] .. " +" .. professionBonus
    end

    -- ========== 暴击加成 ==========
    local critAbility, critChance = string.match(text, "^Increases the critical strike chance of (.+) by (%d+)%%%.?$")
    if critAbility and critChance then
      return TranslateAbilityList(critAbility) .. "的爆击几率提高 " .. critChance .. "%。"
    end

    -- ========== 被击中时 ==========
    value = string.match(text, "When struck in combat[,.]* has a (%d+)%% chance")
    if value then return "在战斗中被击中时，有 " .. value .. "% 几率触发效果。" end

    local chance2, effect2 = string.match(text, "When struck in combat[,.]* has a (%d+)%% chance of ([^%.]+)")
    if chance2 and effect2 then
      return "在战斗中被击中时，有 " .. chance2 .. "% 几率" .. effect2 .. "。"
    end

    local freezeDuration = string.match(text, "^When struck in combat has a chance of freezing the attacker in place for ([%d%.]+) sec%.?$")
      or string.match(text, "^When struck in combat has a chance of freezing the attacker in place for ([%d%.]+) seconds?%.?$")
    if freezeDuration then
      return "在战斗中被击中时，有几率将攻击者冻结在原地，持续 " .. freezeDuration .. " 秒。"
    end

    local shieldAmount = string.match(text, "^When struck in combat has a chance of shielding the wearer in a protective shield which will absorb ([%d%.]+) damage%.?$")
    if shieldAmount then
      return "在战斗中被击中时，有几率为穿戴者施加一个防护盾，可吸收 " .. shieldAmount .. " 点伤害。"
    end

    local fearDuration = string.match(text, "^When struck in combat has a chance of causing the attacker to flee in terror for ([%d%.]+) seconds?%.?$")
    if fearDuration then
      return "在战斗中被击中时，有几率使攻击者因恐惧而逃跑 " .. fearDuration .. " 秒。"
    end

    local manaGain, rageGain, energyGain = string.match(text, "^When struck in combat has a chance of returning ([%d%.]+) mana, ([%d%.]+) rage, or ([%d%.]+) energy to the wearer%.?$")
    if manaGain and rageGain and energyGain then
      return "在战斗中被击中时，有几率为穿戴者恢复 " .. manaGain .. " 点法力值、" .. rageGain .. " 点怒气或 " .. energyGain .. " 点能量。"
    end

    local procBonus, procDuration = string.match(text, "^Chance on spell cast to increase your damage and healing by up to ([%d%.]+) for ([%d%.]+) sec%.?$")
    if procBonus and procDuration then
      return "成功施法时有几率使你的伤害和治疗效果最多提高 " .. procBonus .. " 点，持续 " .. procDuration .. " 秒。"
    end

    procBonus, procDuration = string.match(text, "^Chance on melee attack to increase your damage and healing done by magical spells and effects by up to ([%d%.]+) for ([%d%.]+) sec%.?$")
    if procBonus and procDuration then
      return "近战攻击命中时有几率使魔法法术和效果造成的伤害与治疗效果最多提高 " .. procBonus .. " 点，持续 " .. procDuration .. " 秒。"
    end

    local healLo, healHi = string.match(text, "^Chance on melee attack to heal you for ([%d,]+) to ([%d,]+)%.?$")
    if healLo and healHi then
      return "近战攻击命中时有几率为你恢复 " .. healLo .. " 到 " .. healHi .. " 点生命值。"
    end

    local energyRestore = string.match(text, "^Chance on melee attack to restore ([%d%.]+) energy%.?$")
    if energyRestore then
      return "近战攻击命中时有几率恢复 " .. energyRestore .. " 点能量。"
    end

    local areaReduction = string.match(text, "^Reduces the damage you take from area of effect attacks by an additional ([%d%.]+)%%%.?$")
    if areaReduction then
      return "你受到的范围效果攻击伤害额外降低 " .. areaReduction .. "% 。"
    end

    local attackSpeedAbility, attackSpeedBonus = string.match(text, "^Increases the attack speed gained from (.+) by an additional ([%d%.]+)%%%.?$")
    if attackSpeedAbility and attackSpeedBonus then
      return TranslateAbilityName(attackSpeedAbility) .. "提供的攻击速度加成额外提高 " .. attackSpeedBonus .. "% 。"
    end

    local energyAbilityList, reducedEnergy = string.match(text, "^Reduces the [Ee]nergy cost of your (.+) abilities by ([%d%.]+)%.?$")
    if energyAbilityList and reducedEnergy then
      return TranslateAbilityList(energyAbilityList) .. "的能量消耗降低 " .. reducedEnergy .. " 点。"
    end

    local cooldownTarget, cooldownReduction = string.match(text, "^Reduces the cooldown on your (.+) by ([%d%.]+) sec%.?$")
    if cooldownTarget and cooldownReduction then
      return TranslateAbilityName(cooldownTarget) .. "的冷却时间缩短 " .. cooldownReduction .. " 秒。"
    end

    local shoutCost = string.match(text, "^All of your shout abilities cost ([%d%.]+) less rage%.?$")
    if shoutCost then
      return "你的所有怒吼技能消耗的怒气减少 " .. shoutCost .. " 点。"
    end

    local threatAbility, threatBonus = string.match(text, "^([%a][%a%s':%-%(%)]+) generates ([%d%.]+)%% more threat%.?$")
    if threatAbility and threatBonus then
      return TranslateAbilityName(threatAbility) .. "产生的威胁值提高 " .. threatBonus .. "%。"
    end

    threatAbility, threatBonus = string.match(text, "^([%a][%a%s':%-%(%)]+) generates ([%d%.]+)%% less threat%.?$")
    if threatAbility and threatBonus then
      return TranslateAbilityName(threatAbility) .. "产生的威胁值降低 " .. threatBonus .. "%。"
    end

    local levelAbility, levelBonus = string.match(text, "^(.+) gains an additional ([%d%.]+)%% of your current level%.?$")
    if levelAbility and levelBonus then
      return TranslateAbilityName(levelAbility) .. "额外获得相当于你当前等级 " .. levelBonus .. "% 的效果。"
    end

    local firelordBonus = string.match(text, "^While you are in an area touched by the Firelord, your attack power and spell damage is increased by ([%d%.]+)%.?$")
    if firelordBonus then
      return "当你身处火焰之王影响的区域时，攻击强度和法术伤害提高 " .. firelordBonus .. " 点。"
    end

    -- ========== 减少目标移速 ==========
    value = string.match(text, "Reduces target.s movement speed by (%d+)%%")
    if value then return "降低目标移动速度 " .. value .. "%。" end

    -- ========== 减少伤害 ==========
    value = string.match(text, "Reduces all damage taken by (%d+)%%")
    if value then return "受到的所有伤害降低 " .. value .. "%。" end

    value = string.match(text, "Reduces the damage taken from (%w+) effects by (%d+)%%")
    if value then return (damageSchoolMap[value] or value) .. "效果受到的伤害降低 " .. select(2, string.match(text, "Reduces the damage taken from (%w+) effects by (%d+)%%")) .. "%。" end

    -- ========== 宝石孔 ==========
    if string.find(text, "Red Socket", 1, true) and not string.find(text, "Blue", 1, true) and not string.find(text, "Yellow", 1, true) then
      return "红色宝石孔"
    end
    if string.find(text, "Blue Socket", 1, true) and not string.find(text, "Red", 1, true) and not string.find(text, "Yellow", 1, true) then
      return "蓝色宝石孔"
    end
    if string.find(text, "Yellow Socket", 1, true) and not string.find(text, "Red", 1, true) and not string.find(text, "Blue", 1, true) then
      return "黄色宝石孔"
    end
    if string.find(text, "Meta Socket", 1, true) then return "元宝石孔" end
    if string.find(text, "Prismatic Socket", 1, true) then return "棱彩宝石孔" end

    local socketBonus = string.match(text, "^Socket Bonus:%s*(.+)$")
    if socketBonus then
      local translated = TranslateBonusText(socketBonus)
      return "宝石孔加成：" .. (translated or socketBonus)
    end

    -- ========== 耐久度 ==========
    local cur, max = string.match(text, "Durability (%d+) / (%d+)")
    if cur and max then return "耐久度 " .. cur .. " / " .. max end

    -- ========== 绑定类型 ==========
    if text == "Binds when picked up" then return "拾取时绑定" end
    if text == "Binds when equipped" then return "装备时绑定" end
    if text == "Binds to account" then return "账号绑定" end
    if text == "Unique" then return "唯一" end

    -- ========== 武器伤害类型 ==========
    if text == "One-Hand" then return "单手" end
    if text == "Two-Hand" then return "双手" end
    if text == "Off Hand" then return "副手" end
    if text == "Main Hand" then return "主手" end
    if text == "Ranged" then return "远程" end
    if text == "Thrown" then return "投掷" end
    if text == "Gun" then return "枪" end
    if text == "Bow" then return "弓" end
    if text == "Crossbow" then return "弩" end
    if text == "Wand" then return "魔杖" end
    if text == "Sword" then return "剑" end
    if text == "Axe" then return "斧" end
    if text == "Mace" then return "锤" end
    if text == "Dagger" then return "匕首" end
    if text == "Fist Weapon" then return "拳套" end
    if text == "Polearm" then return "长柄武器" end
    if text == "Staff" then return "法杖" end
    if text == "Shield" then return "盾牌" end
    if text == "Held In Off-hand" then return "副手持握" end
    if text == "Relic" then return "圣器" end

    -- ========== 护甲类型 ==========
    if text == "Cloth" then return "布甲" end
    if text == "Leather" then return "皮甲" end
    if text == "Mail" then return "锁甲" end
    if text == "Plate" then return "板甲" end

    -- ========== 伤害范围 proc（兼容 X到Y 和 X to Y） ==========
    local effect, lo2, hi2, school2
    effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your ranged target with (.-) for (%d+) ?to ?(%d+) (.+) damage")
    if not effect then effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your ranged target with (.-) for (%d+)到(%d+) (.+) damage") end
    if not effect then effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your ranged target with (.-) for (%d+)到(%d+)点(.+)伤害") end
    if effect and lo2 and hi2 and school2 then
      school2 = string.gsub(school2, "%s+$", "")
      school2 = string.gsub(school2, "%.+$", "")
      return "有一定几率用" .. TranslateEffectName(effect) .. "打击你的远程目标，造成 " .. lo2 .. " 到 " .. hi2 .. " 点" .. (damageSchoolMap[school2] or school2) .. "伤害。"
    end

    effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your target with (.-) for (%d+) ?to ?(%d+) (.+) damage")
    if not effect then effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your target with (.-) for (%d+)到(%d+) (.+) damage") end
    if not effect then effect, lo2, hi2, school2 = string.match(text, "^Chance to strike your target with (.-) for (%d+)到(%d+)点(.+)伤害") end
    if effect and lo2 and hi2 and school2 then
      school2 = string.gsub(school2, "%s+$", "")
      school2 = string.gsub(school2, "%.+$", "")
      return "有一定几率用" .. TranslateEffectName(effect) .. "打击你的目标，造成 " .. lo2 .. " 到 " .. hi2 .. " 点" .. (damageSchoolMap[school2] or school2) .. "伤害。"
    end

    -- ========== 通用 "deals X to Y damage" ==========
    lo, hi, school2 = string.match(text, "deals (%d+) ?to ?(%d+) (.+) damage")
    if not lo then lo, hi, school2 = string.match(text, "deals (%d+)到(%d+) (.+) damage") end
    if lo and hi and school2 then
      school2 = string.gsub(school2, "%s+$", "")
      school2 = string.gsub(school2, "%.+$", "")
      return "造成 " .. lo .. " 到 " .. hi .. " 点" .. (damageSchoolMap[school2] or school2) .. "伤害。"
    end

    local schoolDamage = string.match(text, "^Smites an enemy for (%d+) (%a+) damage%.?$")
    local schoolName = string.match(text, "^Smites an enemy for %d+ (%a+) damage%.?$")
    if schoolDamage and schoolName then
      return "惩击敌人，造成 " .. schoolDamage .. " 点" .. (damageSchoolMap[schoolName] or schoolName) .. "伤害。"
    end

    local frostLo, frostHi, slowPct, frostDur = string.match(text, "^Launches a bolt of frost at the enemy causing (%d+) ?to ?(%d+) Frost damage and slowing movement speed by (%d+)%% for (%d+) sec%.?$")
    if not frostLo then
      frostLo, frostHi, slowPct, frostDur = string.match(text, "^Launches a bolt of frost at the enemy causing (%d+)到(%d+) Frost damage and slowing movement speed by (%d+)%% for (%d+) sec%.?$")
    end
    if frostLo and frostHi and slowPct and frostDur then
      return "向敌人射出一道冰霜箭，造成 " .. frostLo .. " 到 " .. frostHi .. " 点冰霜伤害，并使其移动速度降低 " .. slowPct .. "% ，持续 " .. frostDur .. " 秒。"
    end

    local fireLo, fireHi, extraDamage, extraDur = string.match(text, "^Hurls a fiery ball that causes (%d+) ?to ?(%d+) Fire damage and an additional (%d+) damage over (%d+) sec%.?$")
    if not fireLo then
      fireLo, fireHi, extraDamage, extraDur = string.match(text, "^Hurls a fiery ball that causes (%d+)到(%d+) Fire damage and an additional (%d+) damage over (%d+) sec%.?$")
    end
    if fireLo and fireHi and extraDamage and extraDur then
      return "掷出一颗火球，造成 " .. fireLo .. " 到 " .. fireHi .. " 点火焰伤害，并在 " .. extraDur .. " 秒内额外造成 " .. extraDamage .. " 点伤害。"
    end

    local poisonDamage, poisonTick, poisonDuration = string.match(text, "^Poisons target for (%d+) Nature damage every (%d+) sec for (%d+) sec%.?$")
    if poisonDamage and poisonTick and poisonDuration then
      return "使目标中毒，每 " .. poisonTick .. " 秒造成 " .. poisonDamage .. " 点自然伤害，持续 " .. poisonDuration .. " 秒。"
    end

    local shadowLo, shadowHi = string.match(text, "^Sends a shadowy bolt at the enemy causing (%d+) ?to ?(%d+) Shadow damage%.?$")
    if not shadowLo then
      shadowLo, shadowHi = string.match(text, "^Sends a shadowy bolt at the enemy causing (%d+)到(%d+) Shadow damage%.?$")
    end
    if shadowLo and shadowHi then
      return "向敌人发射一道暗影箭，造成 " .. shadowLo .. " 到 " .. shadowHi .. " 点暗影伤害。"
    end

    value = string.match(text, "^Sends a shadowy bolt at the enemy causing (%d+) Shadow damage%.?$")
    if value then return "向敌人发射一道暗影箭，造成 " .. value .. " 点暗影伤害。" end

    local inflictLo, inflictHi, inflictSchool = string.match(text, "^Inflicts (%d+) ?to ?(%d+) (%a+) damage to an enemy%.?$")
    if not inflictLo then
      inflictLo, inflictHi, inflictSchool = string.match(text, "^Inflicts (%d+)到(%d+) (%a+) damage to an enemy%.?$")
    end
    if inflictLo and inflictHi and inflictSchool then
      return "对敌人造成 " .. inflictLo .. " 到 " .. inflictHi .. " 点" .. (damageSchoolMap[inflictSchool] or inflictSchool) .. "伤害。"
    end

    local woundDamage = string.match(text, "^Wounds the target for (%d+) damage%.?$")
    if woundDamage then
      return "重创目标，造成 " .. woundDamage .. " 点伤害。"
    end

    local woundLo, woundHi, intellectLoss, woundDuration = string.match(text, "^Wounds the target for (%d+) ?to ?(%d+) damage and lowers Intellect of target by (%d+) for (%d+) sec%.?$")
    if not woundLo then
      woundLo, woundHi, intellectLoss, woundDuration = string.match(text, "^Wounds the target for (%d+)到(%d+) damage and lowers Intellect of target by (%d+) for (%d+) sec%.?$")
    end
    if woundLo and woundHi and intellectLoss and woundDuration then
      return "重创目标，造成 " .. woundLo .. " 到 " .. woundHi .. " 点伤害，并使目标智力降低 " .. intellectLoss .. " 点，持续 " .. woundDuration .. " 秒。"
    end

    value = string.match(text, "^Grants (%d+) extra attacks? on your next swing%.?$")
    if value then return "你的下一次攻击额外获得 " .. value .. " 次攻击。" end

    local crippleMove, crippleMelee, crippleRanged, crippleDuration = string.match(text, "^Cripples the target, reducing movement speed by (%d+)%%, increasing time between melee attacks by (%d+)%% and increasing time between ranged attacks by (%d+)%%%. Lasts (%d+) sec%.?$")
    if crippleMove and crippleMelee and crippleRanged and crippleDuration then
      return "使目标残废，移动速度降低 " .. crippleMove .. "% ，近战攻击间隔提高 " .. crippleMelee .. "% ，远程攻击间隔提高 " .. crippleRanged .. "% ，持续 " .. crippleDuration .. " 秒。"
    end

    local damageReduction, damageReductionDuration = string.match(text, "^Damage caused by the target is reduced by (%d+) for (%d+) min%.?$")
    if damageReduction and damageReductionDuration then
      return "目标造成的伤害降低 " .. damageReduction .. " 点，持续 " .. damageReductionDuration .. " 分钟。"
    end

    -- ========== 配方学习 ==========
    local recipeTarget = string.match(text, "^Teaches you how to make (.+)%.$")
    if not recipeTarget then recipeTarget = string.match(text, "^Teaches you how to make (.+)$") end
    if recipeTarget then
      local cn = TranslateKnownObjectName(recipeTarget)
      return "教你制作" .. cn .. "。"
    end

    local cookTarget = string.match(text, "^Teaches you how to cook (.+)%.$")
    if not cookTarget then cookTarget = string.match(text, "^Teaches you how to cook (.+)$") end
    if cookTarget then
      return "教你学会烹饪" .. TranslateKnownObjectName(cookTarget) .. "。"
    end

    if text == "Teaches you how to summon this mount." then
      return "教你学会召唤这种坐骑。"
    end

    local mountName = string.match(text, "^Summons and dismisses a rideable (.+)%. This mount increases speed depending on your Riding Skill%.?$")
    if mountName then
      return "召唤或解散一只可骑乘的" .. TranslateKnownObjectName(mountName) .. "。该坐骑的速度会根据你的骑术等级提高。"
    end

    if text == "Change the school of magic that this wand fires." then
      return "改变这根魔杖发射的魔法学派。"
    end

    if text == "Places all five of the Khans' gems in the Amulet of Spirits." then
      return "将五枚可汗宝石全部放入灵魂护符中。"
    end

    local dummyDuration = string.match(text, "^Drops a target dummy on the ground that attracts nearby monsters to attack it%. Lasts for (%d+) seconds or until killed%.?$")
    if dummyDuration then
      return "在地上放下一个假人，吸引附近怪物攻击它。持续 " .. dummyDuration .. " 秒或直到被摧毁。"
    end

    local siphonCooldown = string.match(text, "^Siphon energy from a weakened elemental%. %((%d+) Sec Cooldown%)$")
    if siphonCooldown then
      return "从一个虚弱的元素身上吸取能量。（" .. siphonCooldown .. "秒冷却）"
    end

    local bindingCooldown = string.match(text, "^Call forth a terrible force, binding it to an elemental form%. %((%d+) Min Cooldown%)$")
    if bindingCooldown then
      return "召唤一股可怕的力量，将其束缚为元素形态。（" .. bindingCooldown .. "分钟冷却）"
    end

    -- ========== 其他常见静态文本 ==========
    if string.find(text, "Soulbound", 1, true) then return "灵魂绑定" end
    if string.find(text, "Quest Item", 1, true) then return "任务物品" end
    if text == "Conjured Item" then return "魔法制造" end
    if text == "Right Click to Open" then return "右键点击打开" end
    if text == "Right-Click to Open" then return "右键点击打开" end
  end

  local function HasEquipPrefix(text)
    return string.find(text, "Equip", 1, true) or string.find(text, "装备", 1, true)
  end

  local function HasUsePrefix(text)
    return string.find(text, "Use", 1, true) or string.find(text, "使用", 1, true)
  end

  -- 内部实现（不含缓存，供包装函数调用）
  local function TranslateItemEffectTextImpl(clean)
    local setIndex = string.match(clean, "%((%d+)%)")
    local earlyBonus = TranslateBonusText(clean)
    if earlyBonus then
      if setIndex then
        return "(" .. setIndex .. ") 套装：" .. earlyBonus
      elseif HasUsePrefix(clean) then
        return "使用：" .. earlyBonus
      elseif HasEquipPrefix(clean) then
        return "装备：" .. earlyBonus
      end
    end

    local plainSetBonus = string.match(clean, "^Set[:：]%s*(.+)$")
    if not plainSetBonus then
      plainSetBonus = string.match(clean, "^套装[:：]%s*(.+)$")
    end
    if plainSetBonus then
      local translatedPlainSet = TranslateBonusText(plainSetBonus)
      if translatedPlainSet then
        return "套装：" .. translatedPlainSet
      end
    end

    local prefix = ""
    local rest
    rest = string.match(clean, "^Equip[:：]%s*(.+)$")
    if rest then
      prefix = "装备："
      clean = NormalizeTooltipText(rest)
    else
      rest = string.match(clean, "^装备[:：]%s*(.+)$")
    end
    if rest and prefix == "" then
      prefix = "装备："
      clean = NormalizeTooltipText(rest)
    elseif prefix == "" then
      rest = string.match(clean, "^Use[:：]%s*(.+)$")
    end
    if rest and prefix == "" then
      prefix = "使用："
      clean = NormalizeTooltipText(rest)
    elseif prefix == "" then
      rest = string.match(clean, "^使用[:：]%s*(.+)$")
    end
    if rest and prefix == "" then
      prefix = "使用："
      clean = NormalizeTooltipText(rest)
    elseif prefix == "" then
      rest = string.match(clean, "^Chance on hit[:：]%s*(.+)$")
    end
    if rest and prefix == "" then
      prefix = "击中时可能："
      clean = NormalizeTooltipText(rest)
    end

    local setName, setCount = string.match(clean, "^(.-) %((%d+/%d+)%)$")
    if setName and setCount then
      local translatedSet = TranslateSetName(setName)
      if translatedSet ~= setName then
        return translatedSet .. " (" .. setCount .. ")"
      end
    end

    local setIndex, setBonus = string.match(clean, "^%((%d+)%)%s*套装[:：]%s*(.+)$")
    if not setIndex then
      setIndex, setBonus = string.match(clean, "^%((%d+)%)%s*Set[:：]%s*(.+)$")
    end
    if setIndex and setBonus then
      local translatedBonus = TranslateBonusText(setBonus)
      if translatedBonus then
        return "(" .. setIndex .. ") 套装：" .. translatedBonus
      end
    end

    local translatedSetItem = TranslateSetName(clean)
    if translatedSetItem ~= clean then
      return translatedSetItem
    end

    local effect, amount, school = string.match(clean, "^Chance to strike your ranged target with (.-) for (%d+)%s*%[?%d*%]?%s*(%a+) damage%.?$")
    if effect and amount and school then
      return prefix .. "有一定几率用" .. TranslateEffectName(effect) .. "打击你的远程目标，造成" .. amount .. "点" .. (damageSchoolMap[school] or school) .. "伤害。"
    end

    effect, amount, school = string.match(clean, "^Chance to strike your target with (.-) for (%d+)%s*%[?%d*%]?%s*(%a+) damage%.?$")
    if effect and amount and school then
      return prefix .. "有一定几率用" .. TranslateEffectName(effect) .. "打击你的目标，造成" .. amount .. "点" .. (damageSchoolMap[school] or school) .. "伤害。"
    end

    local translatedBonus = TranslateBonusText(clean)
    if translatedBonus then
      return prefix .. translatedBonus
    end

    local translatedMixed = mixedItemEffectLineMap[clean]
    if translatedMixed then
      return prefix .. translatedMixed
    end

    local amount, duration = string.match(clean, "^Decrease the armor of the target by (%d+) for (%d+) sec%. While affected, the target cannot stealth or turn invisible%.?$")
    if not amount then
      amount, duration = string.match(clean, "^Decrease the 护甲 of the target by (%d+) for (%d+)秒%. While affected, the target cannot stealth or turn invisible%.?$")
    end
    if amount and duration then
      return prefix .. "使目标的护甲降低 " .. amount .. " 点，持续 " .. duration .. "秒。在效果持续期间，目标无法潜行或隐形。"
    end

    local minutes = string.match(clean, "^Allows the drinker to breathe water for (%d+) min%.?$")
    if not minutes then
      minutes = string.match(clean, "^Allows the 饮用者 to breathe water for (%d+)分钟%.?$")
    end
    if minutes then
      return prefix .. "使饮用者可以在水下呼吸，持续 " .. minutes .. "分钟。"
    end

    local health = string.match(clean, "^Instantly restores (%d+) life%.?$") or string.match(clean, "^Instantly restores (%d+) health%.?$")
    if health then
      return prefix .. "立即恢复 " .. health .. " 点生命值。"
    end

    local banishTarget, banishCooldown = string.match(clean, "^Banishes%s+(.+)%s*%((%d+)%s*[Ss]ec%s*[Cc]ooldown%)$")
    if banishTarget and banishCooldown then
      local normalizedTarget = string.gsub(banishTarget, "^[Aa]n?%s+", "")
      local translatedTarget = TranslateEffectName(normalizedTarget)
      if translatedTarget == normalizedTarget then
        translatedTarget = mixedItemEffectTargetMap[normalizedTarget] or normalizedTarget
      end
      if normalizedTarget ~= banishTarget then
        return prefix .. "放逐一名" .. translatedTarget .. "。（" .. banishCooldown .. "秒冷却）"
      end
      return prefix .. "放逐" .. translatedTarget .. "。（" .. banishCooldown .. "秒冷却）"
    end

    local translated = clean
    -- 动词前缀
    translated = string.gsub(translated, "^Chance to ", "有一定几率")
    translated = string.gsub(translated, "^Increases ", "提高")
    translated = string.gsub(translated, "^Improves ", "提高")
    translated = string.gsub(translated, "^Restores ", "恢复")
    translated = string.gsub(translated, "^Gives ", "给予")
    translated = string.gsub(translated, "^Heals ", "治疗")
    translated = string.gsub(translated, "^Absorbs ", "吸收")
    translated = string.gsub(translated, "^Deals ", "造成")
    -- 伤害学派
    translated = string.gsub(translated, " Fire damage", "点火焰伤害")
    translated = string.gsub(translated, " Nature damage", "点自然伤害")
    translated = string.gsub(translated, " Frost damage", "点冰霜伤害")
    translated = string.gsub(translated, " Shadow damage", "点暗影伤害")
    translated = string.gsub(translated, " Arcane damage", "点奥术伤害")
    translated = string.gsub(translated, " Holy damage", "点神圣伤害")
    translated = string.gsub(translated, " Physical damage", "点物理伤害")
    translated = string.gsub(translated, " damage", "点伤害")
    -- 资源关键词
    translated = string.gsub(translated, " health%.", "点生命值。")
    translated = string.gsub(translated, " health$", "点生命值")
    translated = string.gsub(translated, " health ", "点生命值 ")
    translated = string.gsub(translated, " mana%.", "点法力值。")
    translated = string.gsub(translated, " mana$", "点法力值")
    translated = string.gsub(translated, " mana ", "点法力值 ")
    -- 时间
    translated = string.gsub(translated, " over (%d+) sec%.", "，持续%1秒。")
    translated = string.gsub(translated, " over (%d+) sec$", "，持续%1秒")
    translated = string.gsub(translated, " for (%d+) sec%.", "，持续%1秒。")
    translated = string.gsub(translated, " for (%d+) sec$", "，持续%1秒")
    translated = string.gsub(translated, "(%d+) sec%.", "%1秒。")
    translated = string.gsub(translated, "(%d+) sec ", "%1秒 ")
    translated = string.gsub(translated, "(%d+) sec$", "%1秒")
    -- 数值连接
    translated = string.gsub(translated, "(%d+) to (%d+)", "%1到%2")

    if translated ~= clean and not HasAsciiLetters(translated) then
      return prefix .. translated
    end
  end

  -- 外层缓存包装（所有代码路径均覆盖，避免重复 string 操作）
  local function TranslateItemEffectText(text, itemData)
    if not text or text == "" then return end

    local clean = NormalizeTooltipText(text)
    local pendingExact
    if itemData and itemData[5] then
      local exact = itemData[5][clean]
      if exact and not HasAsciiLetters(exact) then return exact end
      pendingExact = exact
    end

    if EpochCN_TooltipLineData then
      local exact = EpochCN_TooltipLineData[clean]
      if exact then return exact end
    end

    local cached = CacheGetEffect(text)
    if cached ~= nil then return cached or nil end

    if not HasAsciiLetters(clean) then
      CacheSetEffect(text, false)
      return
    end

    local result = TranslateItemEffectTextImpl(clean)
    if result then
      if pendingExact and HasAsciiLetters(result) and not HasAsciiLetters(pendingExact) then
        result = pendingExact
      end
    elseif pendingExact then
      result = pendingExact
    end
    CacheSetEffect(text, result)
    return result
  end

  local function TranslateMixedItemText(text, itemData)
    if type(text) ~= "string" or text == "" or not HasAsciiLetters(text) then return text end

    local changed
    local lines = {}
    for line in string.gmatch(text .. "\n", "(.-)\n") do
      local translated = TranslateItemEffectText(line, itemData)
      if not translated or translated == line then
        local unquoted = StripWrappedQuotes(line)
        if unquoted ~= line then
          local unquotedTranslated = TranslateItemEffectText(unquoted, itemData)
          if unquotedTranslated and unquotedTranslated ~= unquoted then
            translated = unquotedTranslated
          end
        end
      end

      if translated and translated ~= line then
        changed = true
        table.insert(lines, translated)
      else
        table.insert(lines, line)
      end
    end

    if changed then
      return table.concat(lines, "\n")
    end

    return text
  end

  local function TranslateItemEffectLines(tooltip, itemData)
    if not tooltip or not tooltip.GetName or not tooltip.NumLines then return end
    local name = tooltip:GetName()
    if not name then return end

    local changed
    for i = 2, tooltip:NumLines() do
      local line = getglobal(name .. "TextLeft" .. i)
      if line and line.GetText and line.SetText then
        local text = line:GetText()
        local translated = TranslateItemEffectText(text, itemData)
        if (not translated or HasAsciiLetters(translated)) and HasAsciiLetters(text) then
          local mixedTranslated = TranslateMixedItemText(translated or text, itemData)
          if mixedTranslated and mixedTranslated ~= (translated or text) then
            translated = mixedTranslated
          end
        end
        if translated and translated ~= text then
          line:SetText(translated)
          changed = true
        end
      end
    end

    return changed
  end

  local function TranslateTooltipLine(tooltip, index)
    if not tooltip or not tooltip.GetName or not index then return end
    local name = tooltip:GetName()
    if not name then return end
    local line = getglobal(name .. "TextLeft" .. index)
    if line and line.GetText and line.SetText then
      local text = line:GetText()
      local translated = TranslateItemEffectText(text)
      if (not translated or HasAsciiLetters(translated)) and HasAsciiLetters(text) then
        local mixedTranslated = TranslateMixedItemText(translated or text)
        if mixedTranslated and mixedTranslated ~= (translated or text) then
          translated = mixedTranslated
        end
      end
      if translated and translated ~= text then
        line:SetText(translated)
        return true
      end
    end
  end

  local function HookTooltipLineWriters(tooltip)
    if not tooltip or tooltip.EpochCNLineWritersHooked then return end
    if not tooltip.AddLine and not tooltip.AddDoubleLine then return end

    tooltip.EpochCNLineWritersHooked = true

    local function GetLineWriterItemData(self)
      if not self or not self.EpochCNItemData or not self.GetItem then return end
      local _, link = self:GetItem()
      if link then return self.EpochCNItemData end
    end

    local function IsLineHookUnsafe(self)
      local owner = self and self.GetOwner and self:GetOwner()
      local name = owner and owner.GetName and owner:GetName()
      if not name then return end

      return string.find(name, "^SpellButton")
        or string.find(name, "^ActionButton")
        or string.find(name, "^MultiBar")
        or string.find(name, "^BonusActionButton")
        or string.find(name, "^PetActionButton")
        or string.find(name, "^ShapeshiftButton")
        or string.find(name, "^PossessButton")
        or string.find(name, "^MultiCast")
        or string.find(name, "^VehicleMenuBarActionButton")
    end

    local rawAddLine = tooltip.AddLine
    if rawAddLine then
      tooltip.AddLine = function(self, text, r, g, b, wrap)
        if text and not self.EpochCNTranslatingLine and not IsLineHookUnsafe(self) then
          self.EpochCNTranslatingLine = true
          local translated = TranslateItemEffectText(text, GetLineWriterItemData(self))
          self.EpochCNTranslatingLine = nil
          if translated then text = translated end
        end
        return rawAddLine(self, text, r, g, b, wrap)
      end
    end

    local rawAddDoubleLine = tooltip.AddDoubleLine
    if rawAddDoubleLine then
      tooltip.AddDoubleLine = function(self, leftText, rightText, lr, lg, lb, rr, rg, rb)
        if not self.EpochCNTranslatingLine and not IsLineHookUnsafe(self) then
          self.EpochCNTranslatingLine = true
          local itemData = GetLineWriterItemData(self)
          local translatedLeft = TranslateItemEffectText(leftText, itemData)
          local translatedRight = TranslateItemEffectText(rightText, itemData)
          self.EpochCNTranslatingLine = nil
          if translatedLeft then leftText = translatedLeft end
          if translatedRight then rightText = translatedRight end
        end
        return rawAddDoubleLine(self, leftText, rightText, lr, lg, lb, rr, rg, rb)
      end
    end
  end

  function E:DumpTooltipLines(tooltip)
    tooltip = tooltip or GameTooltip
    if not tooltip or not tooltip.GetName or not tooltip.NumLines then
      self:Print("没有可读取的 Tooltip。")
      return
    end

    local name = tooltip:GetName()
    if not name then
      self:Print("当前 Tooltip 没有名称。")
      return
    end

    self:Print("Tooltip 行数：" .. tostring(tooltip:NumLines()))
    for i = 1, tooltip:NumLines() do
      local left = getglobal(name .. "TextLeft" .. i)
      local right = getglobal(name .. "TextRight" .. i)
      local leftText = left and left.GetText and left:GetText()
      local rightText = right and right.GetText and right:GetText()
      local translated = TranslateItemEffectText(leftText)
      self:Print(i .. " L=" .. tostring(leftText))
      if translated then self:Print(i .. " T=" .. tostring(translated)) end
      if rightText then self:Print(i .. " R=" .. tostring(rightText)) end
    end
  end

  local function IsUnsafeTooltipOwner(tooltip)
    local owner = tooltip and tooltip.GetOwner and tooltip:GetOwner()
    local name = owner and owner.GetName and owner:GetName()
    if not name then return end

    return string.find(name, "^SpellButton")
      or string.find(name, "^ActionButton")
      or string.find(name, "^MultiBar")
      or string.find(name, "^BonusActionButton")
      or string.find(name, "^PetActionButton")
      or string.find(name, "^ShapeshiftButton")
      or string.find(name, "^PossessButton")
      or string.find(name, "^MultiCast")
      or string.find(name, "^VehicleMenuBarActionButton")
  end

  -- 清理 SpellData 中未解析的 DBC 公式 token，避免在 Tooltip 中显示乱码
  local function SanitizeSpellDesc(text)
    if not text or text == "" then return text end
    -- 移除 ${...} 花括号公式块
    text = string.gsub(text, "%$%b{}", "")
    -- 移除 $(...} 混合括号公式块
    text = string.gsub(text, "%$%(.-}", "")
    -- 移除 $(...) 圆括号公式块
    text = string.gsub(text, "%$%b()", "")
    -- 移除 $lxxx:yyy; 条件复数形式
    text = string.gsub(text, "%$l[^;]*;", "")
    -- 移除 $/10;s2 除法引用格式
    text = string.gsub(text, "%$/[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $*15;s1 乘法引用格式
    text = string.gsub(text, "%$%*[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $SpellID+token 引用，如 "$42208m1"、"$27026o2"、"$7922d"
    text = string.gsub(text, "%$%d+[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $RAP、$AP 等变量引用
    text = string.gsub(text, "%$RAP", "")
    text = string.gsub(text, "%$AP", "")
    -- 移除其它变量引用，如 $SPH、$rap、$HND
    text = string.gsub(text, "%$[A-Za-z_]+%d*", "")
    -- 移除标准单字母 token：$s1 $d $o1 $n $a1 $m1 等
    text = string.gsub(text, "%$[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除孤立 $，避免公式被部分清洗后残留
    text = string.gsub(text, "%$", "")
    -- 移除 $z $c $g
    text = string.gsub(text, "%$[zZcCgG]", "")
    -- 移除残留的非 $ 前缀公式碎片
    text = string.gsub(text, "%d%d%d%d+m%d+/[%-%d%.]*", "")
    text = string.gsub(text, "m%d+/[%-%d%.]+", "")
    text = string.gsub(text, "/%d*%.?%d*;s%d+", "")
    text = string.gsub(text, "/%d+;%d+[A-Za-z]%d*", "")
    text = string.gsub(text, "/%d+;[A-Za-z]%d*", "")
    text = string.gsub(text, "/%d+;", "")
    text = string.gsub(text, "<[^>]+>", "")
    text = string.gsub(text, "%?[A-Za-z]%d+%[([^%]]*)%]%[[^%]]*%]", "%1")
    text = string.gsub(text, "0%-m%d+/[%d%.]+", "")
    text = string.gsub(text, "%d%d%d%d%d+s%d+", "")
    text = string.gsub(text, "%d%d%d%d%d+d", "")
    text = string.gsub(text, "%d%d%d%d+a%d+", "")
    -- 修复孤立百分号
    text = string.gsub(text, "([^%d])%%([，。、])", "%1%2")
    text = string.gsub(text, "([^%d])%%$", "%1")
    -- 清理多余空格
    text = string.gsub(text, "%s+", " ")
    text = string.gsub(text, "^%s", "")
    text = string.gsub(text, "%s$", "")
    return text
  end


  local function AddTranslation(tooltip, title, description, source)
    if not title or AlreadyAdded(tooltip) then return end

    tooltip:AddLine(" ")
    if EpochCNDB.showDesignTag then
      tooltip:AddLine("|cff33ffccEpochCN|r |cffcccccc" .. E.designLabel .. "|r", 0.2, 1, 0.8)
    else
      tooltip:AddLine("|cff33ffccEpochCN|r", 0.2, 1, 0.8)
    end
    tooltip:AddLine(title, 1, 0.92, 0.45)
    if description and description ~= "" then
      tooltip:AddLine(SanitizeSpellDesc(description), 0.92, 0.92, 0.92, true)
    end
    if EpochCNDB.showSource and source and source ~= "" then
      tooltip:AddLine("来源: " .. source, 0.55, 0.55, 0.55)
    end
  end

  local function AddItemDetails(tooltip, link)
    if not link or not GetItemInfo then return end

    local _, _, _, itemLevel, itemMinLevel, itemType, itemSubType, _, itemEquipLoc = GetItemInfo(link)
    local stats = GetItemStats and GetItemStats(link)
    local hasDetails = false

    if (itemType == "Armor" or itemType == "Weapon") and TPCN_GlobalData then
      local subtype = TPCN_GlobalData[itemSubType]
      local equipLoc = TPCN_GlobalData[itemEquipLoc]
      if subtype or equipLoc then
        tooltip:AddDoubleLine(subtype or itemSubType or "", equipLoc or "", 1, 1, 1, 1, 1, 1)
        hasDetails = true
      end
    end

    if stats and TPCN_ItemStatsOrder then
      for _, stat in ipairs(TPCN_ItemStatsOrder) do
        if stat.id and stat.val and stats[stat.id] then
          tooltip:AddLine("+" .. stat.val .. " " .. stats[stat.id], 1, 1, 0.5, true)
          hasDetails = true
        end
      end
    end

    if itemLevel and itemLevel > 0 then
      tooltip:AddLine("物品等级：" .. itemLevel, 1, 1, 1, true)
      hasDetails = true
    end

    if itemMinLevel and itemMinLevel > 0 then
      tooltip:AddLine("需要等级：" .. itemMinLevel, 1, 1, 1, true)
      hasDetails = true
    end

    return hasDetails
  end

  local function AddItemTranslation(tooltip, link, data)
    if AlreadyAdded(tooltip) then return end

    if data and data[1] then
      SetTooltipTitle(tooltip, data[1])
    end

    local hasContent = data and data[1]
    if not hasContent then
      local _, _, _, itemLevel, itemMinLevel, itemType, itemSubType, _, itemEquipLoc = GetItemInfo and GetItemInfo(link)
      hasContent = itemLevel or itemMinLevel or itemType == "Armor" or itemType == "Weapon" or (TPCN_GlobalData and (TPCN_GlobalData[itemSubType] or TPCN_GlobalData[itemEquipLoc]))
    end
    if not hasContent then return end

    tooltip:AddLine(" ")
    if EpochCNDB.showDesignTag then
      tooltip:AddLine("|cff33ffccEpochCN|r |cffcccccc" .. E.designLabel .. "|r", 0.2, 1, 0.8)
    else
      tooltip:AddLine("|cff33ffccEpochCN|r", 0.2, 1, 0.8)
    end
    if data and data[1] then
      tooltip:AddLine(data[1], 1, 0.92, 0.45)
    end
    AddItemDetails(tooltip, link)
    if data and data[2] and data[2] ~= "" then
      tooltip:AddLine(TranslateMixedItemText(data[2], data), 0.92, 0.92, 0.92, true)
    end
    if EpochCNDB.showSource and data and data[3] and data[3] ~= "" then
      tooltip:AddLine("来源: " .. data[3], 0.55, 0.55, 0.55)
    end
  end

  local function GetTooltipItemData(tooltip)
    if not tooltip or not tooltip.GetItem then return end
    local _, link = tooltip:GetItem()
    if not link then return end

    local id = string.match(link, "Hitem:(%d+):")
    return E:GetItemData(id), link
  end

  local function TranslateItem(tooltip)
    local data, link = GetTooltipItemData(tooltip)
    if not link then return end
    tooltip.EpochCNItemData = data

    if data and data[1] then
      SetTooltipTitle(tooltip, data[1])
    else
      TranslateKnownTitle(tooltip)
    end
    TranslateItemEffectLines(tooltip, data)
    if data and EpochCNDB.appendTooltip then
      AddItemTranslation(tooltip, link, data)
    end
  end

  local function TranslateSpell(tooltip)
    tooltip.EpochCNItemData = nil
    -- 法术书按钮仅追加翻译文本，不修改原有 tooltip，安全无污染。
    -- 动作条按钮由 IsLineHookUnsafe 单独保护。
    if not tooltip.GetSpell then return end

    local name, _, id = tooltip:GetSpell()
    local data = E:GetSpellData(id) or (E.GetSpellDataByName and E:GetSpellDataByName(name))
    if data then AddTranslation(tooltip, data[1], data[2], data[3]) end
  end

  local function TranslateSpellID(tooltip, id)
    if IsUnsafeTooltipOwner(tooltip) then return end
    local data = E:GetSpellData(id)
    if data then AddTranslation(tooltip, data[1], data[2], data[3]) end
  end

  local function ExtractSpellID(link)
    if not link then return end
    return string.match(link, "Hspell:(%d+)") or string.match(link, "Htalent:(%d+)")
  end

  local function TranslateUnit(tooltip)
    tooltip.EpochCNItemData = nil
    local _, unit = tooltip:GetUnit()
    if not unit or not UnitGUID then return end

    local guid = UnitGUID(unit)
    if not guid then return end

    local unitID
    if GetCreatureIDFromUnit then
      unitID = GetCreatureIDFromUnit(unit)
    else
      unitID = tonumber(string.sub(guid, 8, 12), 16)
    end

    local data = E:GetUnitData(unitID)
    local englishName = UnitName(unit)
    if data then
      E:RegisterEnglishUnitName(englishName, data[1])
      SetTooltipTitle(tooltip, data[1])
      AddTranslation(tooltip, data[1], data[2], data[3])
      SetTooltipTitle(tooltip, data[1])
    elseif englishName and E.TranslateEnglishUnitName then
      local translated = E:TranslateEnglishUnitName(englishName)
      if translated and translated ~= englishName then
        E:RegisterEnglishUnitName(englishName, translated)
        SetTooltipTitle(tooltip, translated)
      end
    end
  end

  if GameTooltip then
    HookTooltipLineWriters(GameTooltip)
    GameTooltip:HookScript("OnTooltipSetItem", TranslateItem)
    GameTooltip:HookScript("OnTooltipSetUnit", TranslateUnit)
    -- OnShow 仅处理非物品/非单位的杂项 tooltip（如游戏对象）
    -- 物品翻译由 OnTooltipSetItem 处理，单位翻译由 OnTooltipSetUnit 处理
    GameTooltip:HookScript("OnShow", function(self)
      TranslateKnownTitle(self)
    end)
    if GameTooltip.HookScript then
      GameTooltip:HookScript("OnTooltipSetSpell", TranslateSpell)
    end

    -- Do not replace GameTooltip methods; doing so can taint protected spell/action paths.
  end

  if ItemRefTooltip then
    HookTooltipLineWriters(ItemRefTooltip)
    ItemRefTooltip:HookScript("OnTooltipSetItem", TranslateItem)
    -- OnShow 仅补充标题翻译；物品效果行由 OnTooltipSetItem 处理
    ItemRefTooltip:HookScript("OnShow", function(self)
      TranslateKnownTitle(self)
    end)

    -- Do not replace ItemRefTooltip methods; keep item translation on normal tooltip scripts.
  end

  for _, tooltipName in pairs({
    "ShoppingTooltip1",
    "ShoppingTooltip2",
    "ItemRefShoppingTooltip1",
    "ItemRefShoppingTooltip2",
  }) do
    local tooltip = getglobal(tooltipName)
    if tooltip and tooltip.HookScript then
      HookTooltipLineWriters(tooltip)
      tooltip:HookScript("OnTooltipSetItem", TranslateItem)
      -- OnShow 仅补充标题翻译；物品效果行由 OnTooltipSetItem 处理
      tooltip:HookScript("OnShow", function(self)
        TranslateKnownTitle(self)
      end)
    end
  end

  -- 绿字翻译需要同时覆盖 AddLine/AddDoubleLine：
  -- 拍卖行、比较框和部分 Epoch 自定义 tooltip 会在 OnTooltipSetItem 之后继续追加效果行。
  -- 这里只 hook 已知物品 tooltip，且翻译函数带缓存，避免恢复旧版全局扫描造成卡顿。
end)
