EpochCN:RegisterModule("AuctionHouse", function(E)
  if not EpochCNDB.auctionHouse then return end

  local auctionTerms = {
    -- Auction tabs/buttons
    AUCTIONS = "拍卖",
    BIDS = "竞标",
    BROWSE = "浏览",
    SEARCH = "搜索",
    RESET = "重置",
    BID = "竞标",
    BUYOUT = "一口价",
    CLOSE = "关闭",
    CANCEL_AUCTION = "取消拍卖",
    CREATE_AUCTION = "开始拍卖",
    CURRENT_BID = "当前价格",
    AUCTION_CREATOR = "出售者",
    AUCTION_TIME_LEFT1 = "短",
    AUCTION_TIME_LEFT2 = "中",
    AUCTION_TIME_LEFT3 = "长",
    AUCTION_TIME_LEFT4 = "非常长",

    -- Top-level auction categories. Blizzard_AuctionUI builds the filter tree
    -- from these constants, so changing them before the UI loads keeps clicks usable.
    ITEM_CLASS_WEAPON = "武器",
    ITEM_CLASS_ARMOR = "护甲",
    ITEM_CLASS_CONTAINER = "容器",
    ITEM_CLASS_CONSUMABLE = "消耗品",
    ITEM_CLASS_GLYPH = "雕文",
    ITEM_CLASS_TRADEGOODS = "商品",
    ITEM_CLASS_PROJECTILE = "弹药",
    ITEM_CLASS_QUIVER = "箭袋",
    ITEM_CLASS_RECIPE = "配方",
    ITEM_CLASS_GEM = "宝石",
    ITEM_CLASS_MISCELLANEOUS = "其他",
    ITEM_CLASS_QUESTITEM = "任务",

    -- Weapon subclasses
    ITEM_SUBCLASS_WEAPON_AXE1H = "单手斧",
    ITEM_SUBCLASS_WEAPON_AXE2H = "双手斧",
    ITEM_SUBCLASS_WEAPON_BOW = "弓",
    ITEM_SUBCLASS_WEAPON_CROSSBOW = "弩",
    ITEM_SUBCLASS_WEAPON_DAGGER = "匕首",
    ITEM_SUBCLASS_WEAPON_FISHINGPOLE = "鱼竿",
    ITEM_SUBCLASS_WEAPON_FIST = "拳套武器",
    ITEM_SUBCLASS_WEAPON_GUN = "枪械",
    ITEM_SUBCLASS_WEAPON_MACE1H = "单手锤",
    ITEM_SUBCLASS_WEAPON_MACE2H = "双手锤",
    ITEM_SUBCLASS_WEAPON_MISCELLANEOUS = "其他",
    ITEM_SUBCLASS_WEAPON_POLEARM = "长柄武器",
    ITEM_SUBCLASS_WEAPON_STAFF = "法杖",
    ITEM_SUBCLASS_WEAPON_SWORD1H = "单手剑",
    ITEM_SUBCLASS_WEAPON_SWORD2H = "双手剑",
    ITEM_SUBCLASS_WEAPON_THROWN = "投掷武器",
    ITEM_SUBCLASS_WEAPON_WAND = "魔杖",

    -- Armor subclasses
    ITEM_SUBCLASS_ARMOR_CLOTH = "布甲",
    ITEM_SUBCLASS_ARMOR_LEATHER = "皮甲",
    ITEM_SUBCLASS_ARMOR_MAIL = "锁甲",
    ITEM_SUBCLASS_ARMOR_PLATE = "板甲",
    ITEM_SUBCLASS_ARMOR_SHIELD = "盾牌",
    ITEM_SUBCLASS_ARMOR_LIBRAM = "圣物",
    ITEM_SUBCLASS_ARMOR_IDOL = "神像",
    ITEM_SUBCLASS_ARMOR_TOTEM = "图腾",
    ITEM_SUBCLASS_ARMOR_SIGIL = "魔印",
    ITEM_SUBCLASS_ARMOR_MISCELLANEOUS = "其他",

    -- Container subclasses
    ITEM_SUBCLASS_CONTAINER_BAG = "背包",
    ITEM_SUBCLASS_CONTAINER_SOUL_BAG = "灵魂袋",
    ITEM_SUBCLASS_CONTAINER_HERB_BAG = "草药袋",
    ITEM_SUBCLASS_CONTAINER_ENCHANTING_BAG = "附魔材料袋",
    ITEM_SUBCLASS_CONTAINER_ENGINEERING_BAG = "工程学材料袋",
    ITEM_SUBCLASS_CONTAINER_GEM_BAG = "宝石袋",
    ITEM_SUBCLASS_CONTAINER_MINING_BAG = "矿石袋",
    ITEM_SUBCLASS_CONTAINER_LEATHERWORKING_BAG = "制皮材料袋",
    ITEM_SUBCLASS_CONTAINER_INSCRIPTION_BAG = "铭文包",

    -- Consumable subclasses
    ITEM_SUBCLASS_CONSUMABLE_FOOD_DRINK = "食物和饮料",
    ITEM_SUBCLASS_CONSUMABLE_POTION = "药水",
    ITEM_SUBCLASS_CONSUMABLE_ELIXIR = "药剂",
    ITEM_SUBCLASS_CONSUMABLE_FLASK = "合剂",
    ITEM_SUBCLASS_CONSUMABLE_BANDAGE = "绷带",
    ITEM_SUBCLASS_CONSUMABLE_ITEM_ENHANCEMENT = "物品强化",
    ITEM_SUBCLASS_CONSUMABLE_SCROLL = "卷轴",
    ITEM_SUBCLASS_CONSUMABLE_OTHER = "其他",
    ITEM_SUBCLASS_CONSUMABLE_CONSUMABLE = "消耗品",

    -- Trade goods subclasses
    ITEM_SUBCLASS_TRADE_GOODS_ELEMENTAL = "元素",
    ITEM_SUBCLASS_TRADE_GOODS_CLOTH = "布料",
    ITEM_SUBCLASS_TRADE_GOODS_LEATHER = "皮革",
    ITEM_SUBCLASS_TRADE_GOODS_METAL_STONE = "金属和矿石",
    ITEM_SUBCLASS_TRADE_GOODS_MEAT = "肉类",
    ITEM_SUBCLASS_TRADE_GOODS_HERB = "草药",
    ITEM_SUBCLASS_TRADE_GOODS_ENCHANTING = "附魔",
    ITEM_SUBCLASS_TRADE_GOODS_JEWELCRAFTING = "珠宝加工",
    ITEM_SUBCLASS_TRADE_GOODS_PARTS = "零件",
    ITEM_SUBCLASS_TRADE_GOODS_DEVICES = "装置",
    ITEM_SUBCLASS_TRADE_GOODS_EXPLOSIVES = "爆炸物",
    ITEM_SUBCLASS_TRADE_GOODS_MATERIALS = "材料",
    ITEM_SUBCLASS_TRADE_GOODS_ARMOR_ENCHANTMENT = "护甲附魔",
    ITEM_SUBCLASS_TRADE_GOODS_WEAPON_ENCHANTMENT = "武器附魔",
    ITEM_SUBCLASS_TRADE_GOODS_OTHER = "其他",

    -- Projectile/quiver/recipe/gem/glyph/misc subclasses
    ITEM_SUBCLASS_ARROW = "箭",
    ITEM_SUBCLASS_BULLET = "子弹",
    ITEM_SUBCLASS_QUIVER = "箭袋",
    ITEM_SUBCLASS_AMMO_POUCH = "弹药袋",
    ITEM_SUBCLASS_GLYPH_WARRIOR = "战士雕文",
    ITEM_SUBCLASS_GLYPH_PALADIN = "圣骑士雕文",
    ITEM_SUBCLASS_GLYPH_HUNTER = "猎人雕文",
    ITEM_SUBCLASS_GLYPH_ROGUE = "潜行者雕文",
    ITEM_SUBCLASS_GLYPH_PRIEST = "牧师雕文",
    ITEM_SUBCLASS_GLYPH_DEATHKNIGHT = "死亡骑士雕文",
    ITEM_SUBCLASS_GLYPH_SHAMAN = "萨满祭司雕文",
    ITEM_SUBCLASS_GLYPH_MAGE = "法师雕文",
    ITEM_SUBCLASS_GLYPH_WARLOCK = "术士雕文",
    ITEM_SUBCLASS_GLYPH_DRUID = "德鲁伊雕文",
    ITEM_SUBCLASS_RECIPE_BOOK = "书籍",
    ITEM_SUBCLASS_RECIPE_LEATHERWORKING = "制皮",
    ITEM_SUBCLASS_RECIPE_TAILORING = "裁缝",
    ITEM_SUBCLASS_RECIPE_ENGINEERING = "工程学",
    ITEM_SUBCLASS_RECIPE_BLACKSMITHING = "锻造",
    ITEM_SUBCLASS_RECIPE_COOKING = "烹饪",
    ITEM_SUBCLASS_RECIPE_ALCHEMY = "炼金术",
    ITEM_SUBCLASS_RECIPE_FIRST_AID = "急救",
    ITEM_SUBCLASS_RECIPE_ENCHANTING = "附魔",
    ITEM_SUBCLASS_RECIPE_FISHING = "钓鱼",
    ITEM_SUBCLASS_RECIPE_JEWELCRAFTING = "珠宝加工",
    ITEM_SUBCLASS_RECIPE_INSCRIPTION = "铭文",
    ITEM_SUBCLASS_GEM_RED = "红色",
    ITEM_SUBCLASS_GEM_BLUE = "蓝色",
    ITEM_SUBCLASS_GEM_YELLOW = "黄色",
    ITEM_SUBCLASS_GEM_PURPLE = "紫色",
    ITEM_SUBCLASS_GEM_GREEN = "绿色",
    ITEM_SUBCLASS_GEM_ORANGE = "橙色",
    ITEM_SUBCLASS_GEM_META = "多彩",
    ITEM_SUBCLASS_GEM_SIMPLE = "简易",
    ITEM_SUBCLASS_GEM_PRISMATIC = "棱彩",
    ITEM_SUBCLASS_MISCELLANEOUS_MOUNT = "坐骑",
    ITEM_SUBCLASS_MISCELLANEOUS_COMPANION_PET = "小宠物",
    ITEM_SUBCLASS_MISCELLANEOUS_HOLIDAY = "节日",
    ITEM_SUBCLASS_MISCELLANEOUS_OTHER = "其他",
  }

  local textMap = {
    ["All"] = "全部",
    ["Search"] = "搜索",
    ["Reset"] = "重置",
    ["Bid"] = "竞标",
    ["Buyout"] = "一口价",
    ["Close"] = "关闭",
    ["Cancel Auction"] = "取消拍卖",
    ["Create Auction"] = "开始拍卖",
    ["Current Bid"] = "当前价格",
    ["Seller"] = "出售者",
    ["Time Left"] = "剩余时间",
    ["Item"] = "物品",
    ["Level"] = "等级",
    ["Rarity"] = "品质",
    ["Duration"] = "持续时间",
    ["Stack Size"] = "堆叠数量",
    ["Number of Stacks"] = "堆叠组数",
    ["Weapon"] = "武器",
    ["Armor"] = "护甲",
    ["Container"] = "容器",
    ["Consumable"] = "消耗品",
    ["Glyph"] = "雕文",
    ["Trade Goods"] = "商品",
    ["Projectile"] = "弹药",
    ["Quiver"] = "箭袋",
    ["Recipe"] = "配方",
    ["Gem"] = "宝石",
    ["Miscellaneous"] = "其他",
    ["Quest"] = "任务",
    ["One-Handed Axes"] = "单手斧",
    ["Two-Handed Axes"] = "双手斧",
    ["Bows"] = "弓",
    ["Crossbows"] = "弩",
    ["Daggers"] = "匕首",
    ["Fishing Poles"] = "鱼竿",
    ["Fist Weapons"] = "拳套武器",
    ["Guns"] = "枪械",
    ["One-Handed Maces"] = "单手锤",
    ["Two-Handed Maces"] = "双手锤",
    ["Polearms"] = "长柄武器",
    ["Staves"] = "法杖",
    ["One-Handed Swords"] = "单手剑",
    ["Two-Handed Swords"] = "双手剑",
    ["Thrown"] = "投掷武器",
    ["Wands"] = "魔杖",
    ["Cloth"] = "布甲",
    ["Leather"] = "皮甲",
    ["Mail"] = "锁甲",
    ["Plate"] = "板甲",
    ["Shields"] = "盾牌",
    ["Idols"] = "神像",
    ["Totems"] = "图腾",
    ["Librams"] = "圣契",
    ["Sigils"] = "魔印",
    ["Bag"] = "背包",
    ["Soul Bag"] = "灵魂袋",
    ["Herb Bag"] = "草药袋",
    ["Enchanting Bag"] = "附魔材料袋",
    ["Engineering Bag"] = "工程学材料袋",
    ["Gem Bag"] = "宝石袋",
    ["Mining Bag"] = "矿石袋",
    ["Leatherworking Bag"] = "制皮材料袋",
    ["Inscription Bag"] = "铭文包",
    ["Food & Drink"] = "食物和饮料",
    ["Potion"] = "药水",
    ["Elixir"] = "药剂",
    ["Flask"] = "合剂",
    ["Bandage"] = "绷带",
    ["Item Enhancement"] = "物品强化",
    ["Scroll"] = "卷轴",
    ["Other"] = "其他",
    ["Elemental"] = "元素",
    ["Metal & Stone"] = "金属和矿石",
    ["Meat"] = "肉类",
    ["Herb"] = "草药",
    ["Enchanting"] = "附魔",
    ["Jewelcrafting"] = "珠宝加工",
    ["Parts"] = "零件",
    ["Devices"] = "装置",
    ["Explosives"] = "爆炸物",
    ["Materials"] = "材料",
    ["Armor Enchantment"] = "护甲附魔",
    ["Weapon Enchantment"] = "武器附魔",
    ["Arrow"] = "箭",
    ["Bullet"] = "子弹",
    ["Ammo Pouch"] = "弹药袋",
    ["Warrior"] = "战士",
    ["Paladin"] = "圣骑士",
    ["Hunter"] = "猎人",
    ["Rogue"] = "潜行者",
    ["Priest"] = "牧师",
    ["Death Knight"] = "死亡骑士",
    ["Shaman"] = "萨满祭司",
    ["Mage"] = "法师",
    ["Warlock"] = "术士",
    ["Druid"] = "德鲁伊",
    ["Book"] = "书籍",
    ["Leatherworking"] = "制皮",
    ["Tailoring"] = "裁缝",
    ["Engineering"] = "工程学",
    ["Blacksmithing"] = "锻造",
    ["Cooking"] = "烹饪",
    ["Alchemy"] = "炼金术",
    ["First Aid"] = "急救",
    ["Fishing"] = "钓鱼",
    ["Inscription"] = "铭文",
    ["Red"] = "红色",
    ["Blue"] = "蓝色",
    ["Yellow"] = "黄色",
    ["Purple"] = "紫色",
    ["Green"] = "绿色",
    ["Orange"] = "橙色",
    ["Meta"] = "多彩",
    ["Simple"] = "简易",
    ["Prismatic"] = "棱彩",
    ["Mount"] = "坐骑",
    ["Companion Pets"] = "小宠物",
    ["Holiday"] = "节日",
  }

  for key, value in pairs(auctionTerms) do
    local raw = getglobal(key)
    if type(raw) == "string" and raw ~= "" then
      textMap[raw] = value
    end
    textMap[value] = value
  end

  if TPCN_GlobalData then
    for raw, localized in pairs(TPCN_GlobalData) do
      if type(raw) == "string" and type(localized) == "string" then
        textMap[raw] = localized
      end
    end
  end

  local itemNameMap = {}
  local itemReverseMap = {}
  local auctionSearchCache = {}
  local itemNameBuilt = false
  local randomAffixMap = {
    ["of the Monkey"] = "灵猴",
    ["of the Eagle"] = "雄鹰",
    ["of the Bear"] = "野熊",
    ["of the Whale"] = "鲸鱼",
    ["of the Owl"] = "夜枭",
    ["of the Gorilla"] = "猩猩",
    ["of the Falcon"] = "猎鹰",
    ["of the Boar"] = "野猪",
    ["of the Wolf"] = "孤狼",
    ["of the Tiger"] = "猛虎",
    ["of Spirit"] = "精神",
    ["of Stamina"] = "耐力",
    ["of Strength"] = "力量",
    ["of Agility"] = "敏捷",
    ["of Intellect"] = "智力",
    ["of Power"] = "能量",
    ["of Spell Power"] = "法术能量",
    ["of Defense"] = "防御",
    ["of Regeneration"] = "回复",
    ["of Eluding"] = "躲闪",
    ["of Concentration"] = "专注",
    ["of Arcane Protection"] = "奥术防护",
    ["of Fire Protection"] = "火焰防护",
    ["of Frost Protection"] = "冰霜防护",
    ["of Nature Protection"] = "自然防护",
    ["of Shadow Protection"] = "暗影防护",
    ["of Arcane Resistance"] = "奥术抗性",
    ["of Fire Resistance"] = "火焰抗性",
    ["of Frost Resistance"] = "冰霜抗性",
    ["of Nature Resistance"] = "自然抗性",
    ["of Shadow Resistance"] = "暗影抗性",
    ["of the Sorcerer"] = "巫师",
    ["of the Physician"] = "医师",
    ["of the Prophet"] = "先知",
    ["of the Invoker"] = "唤魔者",
    ["of the Bandit"] = "强盗",
    ["of the Beast"] = "野兽",
    ["of the Hierophant"] = "圣者",
    ["of the Soldier"] = "士兵",
    ["of the Elder"] = "长者",
    ["of the Champion"] = "勇士",
    ["of Blocking"] = "格挡",
    ["of the Grove"] = "林地",
    ["of the Hunt"] = "狩猎",
    ["of the Mind"] = "心智",
    ["of the Crusade"] = "远征",
    ["of the Vision"] = "洞察",
    ["of the Ancestor"] = "先祖",
    ["of the Nightmare"] = "梦魇",
    ["of the Battle"] = "战斗",
    ["of the Shadow"] = "暗影",
    ["of the Sun"] = "太阳",
    ["of the Moon"] = "月亮",
    ["of the Wild"] = "荒野",
    ["of Magic"] = "魔法",
    ["of the Knight"] = "骑士",
    ["of the Seer"] = "预言者",
    ["of the Foreseer"] = "先见者",
    ["of the Thief"] = "盗贼",
    ["of the Necromancer"] = "通灵师",
    ["of the Marksman"] = "神射手",
    ["of the Squire"] = "侍从",
    ["of Restoration"] = "恢复",
    ["of Speed"] = "速度",
    ["of Toughness"] = "坚韧",
    ["of Proficiency"] = "熟练",
    ["of Beast Slaying"] = "野兽杀手",
    ["of Retaliation"] = "反击",
    ["of Critical Strike"] = "爆击",
    ["of Marksmanship"] = "射击",
    ["of Arcane Wrath"] = "奥术之怒",
    ["of Shadow Wrath"] = "暗影之怒",
    ["of Fiery Wrath"] = "火焰之怒",
    ["of Holy Wrath"] = "神圣之怒",
    ["of Frozen Wrath"] = "冰霜之怒",
    ["of Nature's Wrath"] = "自然之怒",
    ["of Healing"] = "治疗",
    ["of Sorcery"] = "巫术",
    ["of Striking"] = "打击",
  }

  local function HasCN(text)
    return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
  end

  local function NormalizeText(text)
    if type(text) ~= "string" then return "" end
    text = string.gsub(text, "|c%x%x%x%x%x%x%x%x", "")
    text = string.gsub(text, "|r", "")
    text = string.gsub(text, '\\"', '"')
    text = string.gsub(text, "\\'", "'")
    text = string.gsub(text, "\\", "")
    text = string.gsub(text, "^%s+", "")
    text = string.gsub(text, "%s+$", "")
    return text
  end

  local function AddItemName(english, chinese)
    english = NormalizeText(english)
    chinese = NormalizeText(chinese)
    if english == "" or chinese == "" or english == chinese then return end
    itemNameMap[english] = chinese
    itemReverseMap[chinese] = english
  end

  local function BuildItemNameMap()
    if itemNameBuilt then return end
    itemNameBuilt = true

    if EpochCN_ObjectiveNameData then
      for english, chinese in pairs(EpochCN_ObjectiveNameData) do
        AddItemName(english, chinese)
      end
    end

    if EpochCN_Overrides and EpochCN_Overrides.englishItems then
      for english, chinese in pairs(EpochCN_Overrides.englishItems) do
        AddItemName(english, chinese)
      end
    end
  end

  local function TokenizeEnglish(text, counts)
    for token in string.gmatch(text or "", "[A-Za-z][A-Za-z%-']+") do
      if string.len(token) > 2 then
        counts[token] = (counts[token] or 0) + 1
      end
    end
  end

  local function FindEnglishSearchTerm(chinese)
    chinese = NormalizeText(chinese)
    if chinese == "" or not HasCN(chinese) then return chinese end

    BuildItemNameMap()
    if auctionSearchCache[chinese] then return auctionSearchCache[chinese] end

    local exact = itemReverseMap[chinese]
    if exact then
      auctionSearchCache[chinese] = exact
      return exact
    end

    local counts = {}
    local firstMatch
    local matchCount = 0
    for english, localized in pairs(itemNameMap) do
      if string.find(localized, chinese, 1, true) then
        firstMatch = firstMatch or english
        matchCount = matchCount + 1
        TokenizeEnglish(english, counts)
      end
    end

    local bestToken, bestCount
    for token, count in pairs(counts) do
      if not bestCount or count > bestCount or (count == bestCount and string.len(token) < string.len(bestToken)) then
        bestToken, bestCount = token, count
      end
    end

    local result = bestToken or firstMatch or chinese
    auctionSearchCache[chinese] = result
    return result
  end

  local function TranslateItemNameText(text)
    text = NormalizeText(text)
    if text == "" or HasCN(text) then return end
    BuildItemNameMap()

    local exact = itemNameMap[text]
    if exact then return exact end

    for affix, localizedAffix in pairs(randomAffixMap) do
      local prefix = affix .. " "
      if string.sub(text, 1, string.len(prefix)) == prefix then
        local base = NormalizeText(string.sub(text, string.len(prefix) + 1))
        local baseCN = itemNameMap[base]
        if baseCN then return baseCN .. "（" .. localizedAffix .. "）" end
      end

      if string.sub(text, 1, string.len(affix)) == affix then
        local base = NormalizeText(string.sub(text, string.len(affix) + 1))
        local baseCN = itemNameMap[base]
        if baseCN then return baseCN .. "（" .. localizedAffix .. "）" end
      end

      local suffix = " " .. affix
      if string.sub(text, -string.len(suffix)) == suffix then
        local base = NormalizeText(string.sub(text, 1, string.len(text) - string.len(suffix)))
        local baseCN = itemNameMap[base]
        if baseCN then return baseCN .. "（" .. localizedAffix .. "）" end
      end
    end
  end

  local function TranslateTextObject(object)
    if not object or not object.GetText or not object.SetText then return end
    local text = object:GetText()
    if not text or text == "" then return end

    local color = string.match(text, "(|c%x%x%x%x%x%x%x%x)")
    local clean = string.gsub(text, "|c%x%x%x%x%x%x%x%x", "")
    clean = string.gsub(clean, "|r", "")
    local translated = textMap[clean] or textMap[text] or TranslateItemNameText(clean)
    if translated and translated ~= clean then
      object.EpochCNRawText = text
      if color then
        object:SetText(color .. translated .. "|r")
      else
        object:SetText(translated)
      end
    end
  end

  local function TranslateNamedText(name, value)
    local frame = getglobal(name)
    if frame and frame.SetText then frame:SetText(value) end
    local text = getglobal(name .. "Text")
    if text and text.SetText then text:SetText(value) end
  end

  local function TranslateStaticAuctionText()
    TranslateNamedText("AuctionFrameBrowse", "浏览")
    TranslateNamedText("AuctionFrameBids", "竞标")
    TranslateNamedText("AuctionFrameAuctions", "拍卖")
    TranslateNamedText("BrowseSearchButton", "搜索")
    TranslateNamedText("BrowseResetButton", "重置")
    TranslateNamedText("BrowseBidButton", "竞标")
    TranslateNamedText("BrowseBuyoutButton", "一口价")
    TranslateNamedText("BidBidButton", "竞标")
    TranslateNamedText("BidBuyoutButton", "一口价")
    TranslateNamedText("AuctionsCreateAuctionButton", "开始拍卖")
    TranslateNamedText("AuctionsCancelAuctionButton", "取消拍卖")
    TranslateNamedText("AuctionsDurationText", "持续时间")

    if UIDropDownMenu_SetText then
      if BrowseDropDown then UIDropDownMenu_SetText(BrowseDropDown, "全部") end
      if BrowseLevelDropDown then UIDropDownMenu_SetText(BrowseLevelDropDown, "等级") end
      if BrowseQualityDropDown then UIDropDownMenu_SetText(BrowseQualityDropDown, "品质") end
    end
  end

  local function TranslateFilterButtons()
    for i = 1, 80 do
      local button = getglobal("AuctionFilterButton" .. i)
      if button then
        TranslateTextObject(button)
        TranslateTextObject(getglobal("AuctionFilterButton" .. i .. "Text"))
      end
    end
  end

  local function TranslateAuctionItems()
    for i = 1, 50 do
      TranslateTextObject(getglobal("BrowseButton" .. i .. "Name"))
      TranslateTextObject(getglobal("BrowseButton" .. i .. "NameText"))
      TranslateTextObject(getglobal("AuctionatorEntry" .. i .. "_EntryText"))
      TranslateTextObject(getglobal("AuctionatorEntry" .. i .. "_PerItem_Text"))
      TranslateTextObject(getglobal("Atr_HEntry" .. i .. "_EntryText"))
    end
  end

  local function TranslateSearchBox(editBox)
    if not editBox or not editBox.GetText or not editBox.SetText then return end
    local text = editBox:GetText()
    if not text or text == "" or not HasCN(text) then return end
    local english = FindEnglishSearchTerm(text)
    if english and english ~= "" and english ~= text then
      editBox.EpochCNChineseSearchText = text
      editBox:SetText(english)
    end
  end

  local function RestoreSearchBox(editBox)
    if editBox and editBox.EpochCNChineseSearchText and editBox.SetText then
      editBox:SetText(editBox.EpochCNChineseSearchText)
      editBox.EpochCNChineseSearchText = nil
    end
  end

  local function PatchQueryAuctionItems()
    if EpochCNRawQueryAuctionItems or not QueryAuctionItems then return end
    EpochCNRawQueryAuctionItems = QueryAuctionItems
    QueryAuctionItems = function(name, minLevel, maxLevel, invTypeIndex, classIndex, subclassIndex, page, isUsable, qualityIndex, getAll, ...)
      if type(name) == "string" and HasCN(name) then
        name = FindEnglishSearchTerm(name)
      end
      return EpochCNRawQueryAuctionItems(name, minLevel, maxLevel, invTypeIndex, classIndex, subclassIndex, page, isUsable, qualityIndex, getAll, ...)
    end
  end

  local function PatchSearchControls()
    PatchQueryAuctionItems()

    if BrowseSearchButton and not BrowseSearchButton.EpochCNSearchPatched then
      BrowseSearchButton.EpochCNSearchPatched = true
      BrowseSearchButton:HookScript("PreClick", function()
        TranslateSearchBox(BrowseName)
      end)
      BrowseSearchButton:HookScript("PostClick", function()
        RestoreSearchBox(BrowseName)
      end)
    end

    if BrowseName and not BrowseName.EpochCNSearchPatched then
      BrowseName.EpochCNSearchPatched = true
      BrowseName:HookScript("OnEnterPressed", function(self)
        TranslateSearchBox(self)
        RestoreSearchBox(self)
      end)
    end

    if Atr_Search_Button and not Atr_Search_Button.EpochCNSearchPatched then
      Atr_Search_Button.EpochCNSearchPatched = true
      Atr_Search_Button:HookScript("PreClick", function()
        TranslateSearchBox(Atr_Search_Box)
      end)
      Atr_Search_Button:HookScript("PostClick", function()
        RestoreSearchBox(Atr_Search_Box)
      end)
    end

    if Atr_Search_Box and not Atr_Search_Box.EpochCNSearchPatched then
      Atr_Search_Box.EpochCNSearchPatched = true
      Atr_Search_Box:HookScript("OnEnterPressed", function(self)
        TranslateSearchBox(self)
        RestoreSearchBox(self)
      end)
    end
  end

  local hooked = false
  local function HookAuctionUI()
    if hooked then return end
    hooked = true
    PatchSearchControls()

    if hooksecurefunc then
      if AuctionFrameFilters_Update then hooksecurefunc("AuctionFrameFilters_Update", TranslateFilterButtons) end
      if AuctionFrameBrowse_Update then hooksecurefunc("AuctionFrameBrowse_Update", function()
        TranslateFilterButtons()
        TranslateAuctionItems()
      end) end
      if AuctionFrameBrowse_UpdateArrows then hooksecurefunc("AuctionFrameBrowse_UpdateArrows", TranslateAuctionItems) end
      if Atr_Update_Auctions then hooksecurefunc("Atr_Update_Auctions", TranslateAuctionItems) end
      if Atr_DisplaySearchResults then hooksecurefunc("Atr_DisplaySearchResults", TranslateAuctionItems) end
      if Atr_BuildList then hooksecurefunc("Atr_BuildList", TranslateAuctionItems) end
    end

    if AuctionFrameFilter_OnClick and not EpochCNRawAuctionFrameFilter_OnClick then
      EpochCNRawAuctionFrameFilter_OnClick = AuctionFrameFilter_OnClick
      AuctionFrameFilter_OnClick = function(self, button)
        local displayText = self.GetText and self:GetText()
        if self.EpochCNRawText and self.SetText then
          self:SetText(self.EpochCNRawText)
        end
        EpochCNRawAuctionFrameFilter_OnClick(self, button)
        if displayText and self.SetText then
          self:SetText(displayText)
        end
        TranslateFilterButtons()
      end
    end

    if AuctionFrame and AuctionFrame.HookScript then
      AuctionFrame:HookScript("OnShow", function()
        TranslateStaticAuctionText()
        TranslateFilterButtons()
        PatchSearchControls()
        TranslateAuctionItems()
      end)
    end
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("ADDON_LOADED")
  frame:RegisterEvent("AUCTION_HOUSE_SHOW")
  frame:RegisterEvent("AUCTION_ITEM_LIST_UPDATE")
  frame:SetScript("OnEvent", function(_, event, addon)
    if event == "ADDON_LOADED" and addon ~= "Blizzard_AuctionUI" then return end
    TranslateStaticAuctionText()
    TranslateFilterButtons()
    PatchSearchControls()
    TranslateAuctionItems()
    HookAuctionUI()
  end)
end)
