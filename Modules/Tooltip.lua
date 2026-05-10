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
    if not tooltip or not EpochCN_ObjectiveNameData then return end
    local name = tooltip:GetName()
    local titleLine = name and getglobal(name .. "TextLeft1")
    if not titleLine or not titleLine.GetText then return end

    local title = titleLine:GetText()
    if not title or title == "" or string.match(title, "^%d+$") then return end

    local translated = EpochCN_ObjectiveNameData[title]
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
    ["Keeper's Sting"] = "守护者之刺",
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

  local function TranslateEffectName(name)
    name = NormalizeTooltipText(name)
    return itemEffectNameMap[name] or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[name]) or name
  end

  local function TranslateKnownObjectName(name)
    name = NormalizeTooltipText(name)
    return (EpochCN_ItemNameMap and EpochCN_ItemNameMap[name])
      or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[name])
      or itemEffectNameMap[name]
      or name
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
    value = string.match(text, "Restores (%d+) health")
    if value then return "恢复 " .. value .. " 点生命值。" end

    value = string.match(text, "Restores (%d+) mana")
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

    -- ========== 战斗属性提升 ==========
    local attackPower, hit = string.match(text, "Increases your attack power by (%d+) and your chance to hit by (%d+)%%")
    if attackPower and hit then return "攻击强度提高 " .. attackPower .. " 点，命中几率提高 " .. hit .. "%。" end

    value = string.match(text, "Increased Defense %+?(%d+)")
    if value then return "防御等级提高 " .. value .. "。" end

    value = string.match(text, "Improves your chance to get a critical strike with melee and ranged attacks by (%d+)%%")
    if value then return "近战和远程攻击爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to get a critical strike by (%d+)%%")
    if value then return "爆击几率提高 " .. value .. "%。" end

    value = string.match(text, "Improves your chance to hit with melee and ranged attacks by (%d+)%%")
    if value then return "近战和远程攻击命中几率提高 " .. value .. "%。" end

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
    value = string.match(text, "Increases healing done by spells and effects by up to (%d+)")
    if value then return "法术和效果的治疗量最多提高 " .. value .. " 点。" end

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

    -- ========== 每5秒恢复 ==========
    value = string.match(text, "Restores (%d+) mana per 5 sec")
    if value then return "每5秒恢复 " .. value .. " 点法力值。" end

    value = string.match(text, "Restores (%d+) health per 5 sec")
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

    -- ========== 暴击加成 ==========
    value = string.match(text, "Increases the critical strike chance of (%w+) by (%d+)%%")
    if value then return value .. " 的爆击几率提高 " .. select(2, string.match(text, "Increases the critical strike chance of (%w+) by (%d+)%%")) .. "%。" end

    -- ========== 被击中时 ==========
    value = string.match(text, "When struck in combat[,.]* has a (%d+)%% chance")
    if value then return "在战斗中被击中时，有 " .. value .. "% 几率触发效果。" end

    local chance2, effect2 = string.match(text, "When struck in combat[,.]* has a (%d+)%% chance of ([^%.]+)")
    if chance2 and effect2 then
      return "在战斗中被击中时，有 " .. chance2 .. "% 几率" .. effect2 .. "。"
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

    -- ========== 配方学习 ==========
    local recipeTarget = string.match(text, "^Teaches you how to make (.+)%.$")
    if not recipeTarget then recipeTarget = string.match(text, "^Teaches you how to make (.+)$") end
    if recipeTarget then
      local cn = TranslateKnownObjectName(recipeTarget)
      return "教你制作" .. cn .. "。"
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

    if translated ~= clean then
      return prefix .. translated
    end

    if prefix ~= "" then
      local result = prefix .. clean
      CacheSetEffect(text, result)
      return result
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
          local translated = TranslateItemEffectText(text)
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
          local translatedLeft = TranslateItemEffectText(leftText)
          local translatedRight = TranslateItemEffectText(rightText)
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
    -- 移除 法术ID前缀+m/除数 组合，如 "54928m1/1000"、"1144440m2/-1000.2"
    text = string.gsub(text, "%d%d%d%d+m%d+/[%-%d%.]*", "")
    -- 移除独立的 mX/除数 公式，如 "m1/1000"、"m2/1000.1"
    text = string.gsub(text, "m%d+/[%-%d%.]+", "")
    -- 移除 /除数;sX 条件引用，如 "/1000;s1"、"/1000;s2"
    text = string.gsub(text, "/%d*%.?%d*;s%d+", "")
    -- 移除 0-mX/除数 范围公式，如 "0-m1/1000.2"
    text = string.gsub(text, "0%-m%d+/[%d%.]+", "")
    -- 移除 5位以上法术ID+sX 的法术引用，如 "34082s2"（5位数字+s+数字）
    text = string.gsub(text, "%d%d%d%d%d+s%d+", "")
    -- 移除 dX 持续时间引用 token，如 "1165156d秒" 中的数字前缀
    text = string.gsub(text, "%d%d%d%d%d+d", "")
    -- 移除 aX 范围引用，如 "5729a1"
    text = string.gsub(text, "%d%d%d%d+a%d+", "")
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
      tooltip:AddLine(data[2], 0.92, 0.92, 0.92, true)
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

    if data and data[1] then
      SetTooltipTitle(tooltip, data[1])
    else
      TranslateKnownTitle(tooltip)
    end
    TranslateItemEffectLines(tooltip, data)
  end

  local function TranslateSpell(tooltip)
    if IsUnsafeTooltipOwner(tooltip) then return end
    if not tooltip.GetSpell then return end

    local _, _, id = tooltip:GetSpell()
    local data = E:GetSpellData(id)
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
    if data then
      E:RegisterEnglishUnitName(UnitName(unit), data[1])
      SetTooltipTitle(tooltip, data[1])
      AddTranslation(tooltip, data[1], data[2], data[3])
      SetTooltipTitle(tooltip, data[1])
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
