local addonName = ...
local E = EpochCN or {}
EpochCN = E

E.name = addonName or "EpochCN"
E.version = "0.7.2"
E.designLabel = "汉化组"
E.modules = E.modules or {}
E.moduleOrder = E.moduleOrder or {}
E.slashHandlers = E.slashHandlers or {}
E.raw = E.raw or {}
E.cache = E.cache or { objective = {}, tooltip = {}, questID = {} }
E.nameMap = E.nameMap or {}
E.resolvingQuestID = false

local defaults = {
  enabled = true,
  questLog = true,
  tooltip = true,
  auctionHouse = true,
  ui = true,
  globalStrings = true,
  settingsPanel = true,
  pfQuestBridge = false,
  worldMap = false,      -- 默认关闭 EpochCN 自带世界地图任务标记
  worldMapPins = false,
  worldMapTrackingMode = "off",
  worldMapShowStartPins = false,
  worldMapShowAvailablePins = false,
  worldMapShowFinishPins = false,
  worldMapShowObjectivePins = false,
  minimapQuestPins = false,
  minimapQuestObjectivesOnly = false,
  worldMapClusterRadius = 0.018,
  worldMapPinSize = 16,
  worldMapObjectivePinSize = 2,
  availableQuestPins = false,
  availableQuestLevelRange = 3,
  hideLowLevelAvailableQuestPins = true,
  availableQuestLowLevelRange = 4,
  questAutoSync = true,
  questProgressNotify = true,
  questProgressPartyChat = false,
  questTracker = true,   -- 任务追踪 UI 汉化
  disablePFQuestTracker = true,
  forcePFQuestMap = false,
  appendTooltip = false,
  showDesignTag = true,
  showSource = false,
  minimapButtonHide = false,
  minimapButtonAngle = 225,
  forceChineseClientLocale = true,
  updateCheck = true,  -- 自动检查新版本（通过公会/队伍广播）
  debug = false,
  mapIconDefaultsVersion = "",
  tooltipPlacementVersion = "",
}

local charDefaults = {
  pfQuestBridgeApplied = false,
  completedQuests = {},
  worldMapManualSelection = {},
  worldMapHiddenQuests = {},
}

local function MergeDefaults(target, source)
  target = target or {}
  for key, value in pairs(source) do
    if target[key] == nil then target[key] = value end
  end
  return target
end

function E:ApplyClientLocalePreference()
  local enabled = true
  if EpochCNDB and EpochCNDB.forceChineseClientLocale ~= nil then
    enabled = EpochCNDB.forceChineseClientLocale and true or false
  end

  if enabled then
    GAME_LOCALE = "zhCN"
  elseif GAME_LOCALE == "zhCN" then
    GAME_LOCALE = nil
  end
end

E:ApplyClientLocalePreference()

local function DisableMapIconDefaults(target)
  if not target or target.mapIconDefaultsVersion == "0.4.47" then return end
  target.worldMap = false
  target.worldMapPins = false
  target.worldMapTrackingMode = "off"
  target.worldMapShowStartPins = false
  target.worldMapShowAvailablePins = false
  target.worldMapShowFinishPins = false
  target.worldMapShowObjectivePins = false
  target.minimapQuestPins = false
  target.minimapQuestObjectivesOnly = false
  target.availableQuestPins = false
  target.mapIconDefaultsVersion = "0.4.47"
end

local function DisableAppendedTooltipDefaults(target)
  if not target or target.tooltipPlacementVersion == "0.4.48" then return end
  target.appendTooltip = false
  target.tooltipPlacementVersion = "0.4.48"
end

function E:Debug(message)
  if EpochCNDB and EpochCNDB.debug and DEFAULT_CHAT_FRAME then
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ffccEpoch|cffffffffCN: " .. tostring(message))
  end
end

function E:Print(message)
  if DEFAULT_CHAT_FRAME then
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ffccEpoch|cffffffffCN|r: " .. tostring(message))
  end
end

function E:RegisterSlashCommands()
  SLASH_EPOCHCN1 = "/ecn"
  SLASH_EPOCHCN2 = "/epochcn"
  SlashCmdList["EPOCHCN"] = function(msg)
    msg = string.lower(msg or "")

    for _, handler in ipairs(E.slashHandlers or {}) do
      local ok, handled = pcall(handler, msg)
      if ok and handled then
        return
      end
      if not ok then
        E:Debug("斜杠命令扩展执行失败: " .. tostring(handled))
      end
    end

    if msg == "" or msg == "config" or msg == "options" or msg == "settings" then
      if E.ToggleSettingsPanel then
        E:ToggleSettingsPanel()
      else
        E:Print("设置模块尚未加载。")
      end
      return
    end

    if msg == "status" then
      E:Print("已加载 " .. tostring(E.version) .. "，界面=" .. tostring(EpochCNDB.ui) .. "，任务=" .. tostring(EpochCNDB.questLog) .. "，Tooltip=" .. tostring(EpochCNDB.tooltip))
      E:Print("数据：任务=" .. tostring(QustCN_Data_CN and "QuestCN" or "无") .. "，技能=" .. tostring(TPCN_SpellData_Epoch and "Epoch" or "无") .. "，物品=" .. tostring(TPCN_ItemData and "已加载" or "无"))
      return
    end

    if msg == "about" then
      if E.ToggleAboutPanel then
        E:ToggleAboutPanel()
      else
        E:Print("设置模块尚未加载。")
      end
      return
    end

    if msg == "icon" then
      if E.ShowMinimapButton then
        E:ShowMinimapButton()
      else
        E:Print("设置模块尚未加载。")
      end
      return
    end

    if msg == "debug" then
      EpochCNDB.debug = not EpochCNDB.debug
      E:Print("debug = " .. tostring(EpochCNDB.debug))
      return
    end

    if msg == "tipdump" then
      if E.DumpTooltipLines then
        E:DumpTooltipLines(GameTooltip)
      else
        E:Print("Tooltip 模块尚未加载。")
      end
      return
    end

    E:Print("命令：/ecn 打开设置，/ecn about 关于，/ecn status 查看状态，/ecn icon 显示小地图按钮，/ecn debug 切换调试，/ecn tipdump 打印当前鼠标 Tooltip 文本。")
  end
end

function E:RegisterSlashHandler(handler)
  if type(handler) ~= "function" then return end
  table.insert(self.slashHandlers, handler)
end

function E:RegisterModule(name, init)
  if not self.modules[name] then
    table.insert(self.moduleOrder, name)
  end
  self.modules[name] = init
end

function E:CaptureRawAPI()
  self.raw.GetQuestLogTitle = myGetQuestLogTitle or self.raw.GetQuestLogTitle or GetQuestLogTitle
  self.raw.GetQuestLogQuestText = myGetQuestLogQuestText or self.raw.GetQuestLogQuestText or GetQuestLogQuestText
  self.raw.GetQuestLogLeaderBoard = myGetQuestLogLeaderBoard or self.raw.GetQuestLogLeaderBoard or GetQuestLogLeaderBoard
  self.raw.GetQuestLogCompletionText = myGetQuestLogCompletionText or self.raw.GetQuestLogCompletionText or GetQuestLogCompletionText
  self.raw.GetAbandonQuestName = myGetAbandonQuestName or self.raw.GetAbandonQuestName or GetAbandonQuestName
  self.raw.GetTitleText = myGetTitleText or self.raw.GetTitleText or GetTitleText
  self.raw.GetQuestText = myGetQuestText or self.raw.GetQuestText or GetQuestText
  self.raw.GetObjectiveText = myGetObjectiveText or self.raw.GetObjectiveText or GetObjectiveText
  self.raw.GetRewardText = myGetRewardText or self.raw.GetRewardText or GetRewardText
  self.raw.GetProgressText = myGetProgressText or self.raw.GetProgressText or GetProgressText
  self.raw.GetGreetingText = myGetGreetingText or self.raw.GetGreetingText or GetGreetingText
  self.raw.GetCurrentQuestID = self.raw.GetCurrentQuestID or GetQuestID
end

function E:LoadSeedData()
  if LoadTPCNSpellDataSeason then LoadTPCNSpellDataSeason() end
  if LoadTPCNSpellDataEpoch then LoadTPCNSpellDataEpoch() end
  if LoadEpochCNSpellRawData then LoadEpochCNSpellRawData() end
  if LoadTPCNGlobalData then LoadTPCNGlobalData() end
  if LoadTPCNCallBoardData then LoadTPCNCallBoardData() end
  if LoadTPCNItemData then LoadTPCNItemData() end
  if LoadEpochCNItemNameMap then LoadEpochCNItemNameMap() end
  if LoadEpochCNConsumableData then LoadEpochCNConsumableData() end
  if LoadEpochCNItemOverlayData then LoadEpochCNItemOverlayData() end
  if LoadEpochCNTooltipLineData then LoadEpochCNTooltipLineData() end
  if LoadTPCNUnitData then LoadTPCNUnitData() end
  if LoadEpochCNObjectiveNameData then LoadEpochCNObjectiveNameData() end
  if LoadEpochCNQuestData then LoadEpochCNQuestData() end
  if LoadEpochCNMapData then LoadEpochCNMapData() end
  if LoadEpochCNEpochHeadData then LoadEpochCNEpochHeadData() end
end

function E:BuildLookupTables()
  self.localizedTextByRaw = self.localizedTextByRaw or {}
  self.spellTextByName = self.spellTextByName or {}
  self.questIDByTitle = self.questIDByTitle or {}
  self.stats = self.stats or {}

  -- ============================================================
  -- 清洗法术数据中未解析的 DBC 公式/占位符 token
  -- 避免 Tooltip、角色面板、技能书等任何位置都显示残留
  -- ============================================================
  local function SanitizeDBCTokens(text)
    if type(text) ~= "string" or text == "" then return text end

    -- ============================================================
    -- 第一阶段：移除 $ 前缀的 WoW DBC 占位符
    -- Epoch 私服不解析中文文本中的 $ 占位符，必须在数据加载时清除
    -- ============================================================

    -- 移除 ${...} 花括号公式块，如 "${$42208m1*8}"、"${$AP*0.2+$m1}"
    text = string.gsub(text, "%$%b{}", "")
    -- 移除 $(...} 混合括号公式块（翻译中常见的格式错误），如 "$($RAP*0.1+$27026m1}"
    text = string.gsub(text, "%$%(.-}", "")
    -- 移除 $(...) 圆括号公式块，如 "$($RAP*0.2+Sm1)"
    text = string.gsub(text, "%$%b()", "")
    -- 移除 $lxxx:yyy; 条件复数形式，如 "$l小松饼:小松饼;"
    text = string.gsub(text, "%$l[^;]*;", "")
    -- 移除 $/10;s2 除法引用格式
    text = string.gsub(text, "%$/[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $*15;s1 乘法引用格式
    text = string.gsub(text, "%$%*[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $SpellID+token 引用，如 "$42208m1"、"$27026o2"、"$7922d"、"$6788d"、"$26364s1"
    text = string.gsub(text, "%$%d+[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除 $RAP、$AP 等变量引用
    text = string.gsub(text, "%$RAP", "")
    text = string.gsub(text, "%$AP", "")
    -- 移除其它变量引用，如 $SPH、$rap、$HND
    text = string.gsub(text, "%$[A-Za-z_]+%d*", "")
    -- 移除标准单字母 token：$s1 $d $o1 $n $a1 $m1 $M1 $x1 $v $e $b1 $q1 $t1 等
    text = string.gsub(text, "%$[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    -- 移除孤立 $，避免公式被部分清洗后残留
    text = string.gsub(text, "%$", "")
    -- 移除 $z（区域名）、$c（职业）、$g（性别）
    text = string.gsub(text, "%$[zZcCgG]", "")

    -- ============================================================
    -- 第二阶段：清理残留的非 $ 前缀的 DBC 公式碎片
    -- ============================================================

    -- 移除 法术ID+m/除数 组合，如 "54928m1/1000"
    text = string.gsub(text, "%d%d%d%d+m%d+/[%-%d%.]*", "")
    -- 移除独立的 mX/除数 公式
    text = string.gsub(text, "m%d+/[%-%d%.]+", "")
    -- 移除 /除数;sX 条件引用
    text = string.gsub(text, "/%d*%.?%d*;s%d+", "")
    -- 移除 /77;10523m1、/10; 这类非 $ 前缀引用
    text = string.gsub(text, "/%d+;%d+[A-Za-z]%d*", "")
    text = string.gsub(text, "/%d+;[A-Za-z]%d*", "")
    text = string.gsub(text, "/%d+;", "")
    -- 移除 <bonus>、<percent> 这类占位符
    text = string.gsub(text, "<[^>]+>", "")
    -- 移除 ?s123[foo][bar] 条件片段中的控制头
    text = string.gsub(text, "%?[A-Za-z]%d+%[([^%]]*)%]%[[^%]]*%]", "%1")
    -- 移除 0-mX/除数 范围公式
    text = string.gsub(text, "0%-m%d+/[%d%.]+", "")
    -- 移除 5位以上法术ID+sX 法术引用
    text = string.gsub(text, "%d%d%d%d%d+s%d+", "")
    -- 移除 5位以上法术ID+d 持续时间引用
    text = string.gsub(text, "%d%d%d%d%d+d", "")
    -- 移除 4位以上法术ID+aX 范围引用
    text = string.gsub(text, "%d%d%d%d+a%d+", "")
    -- 移除 @req:xxx@ 前置条件标记
    text = string.gsub(text, "@req:%d+@%s*\n?", "")
    text = string.gsub(text, "@req:[^@]+@%s*\n?", "")

    -- ============================================================
    -- 第三阶段：修复清理后的文本瑕疵
    -- ============================================================

    -- 修复孤立百分号
    text = string.gsub(text, "([^%d])%%([，。、])", "%1%2")
    text = string.gsub(text, "([^%d])%%$", "%1")
    -- 清理多余空格
    text = string.gsub(text, "[ \t]+", " ")
    text = string.gsub(text, "^[ \t]+", "")
    text = string.gsub(text, "[ \t]+$", "")
    return text
  end


  local function SanitizeSpellTable(tbl)
    if type(tbl) ~= "table" then return end
    for _, entry in pairs(tbl) do
      if type(entry) == "table" and entry[2] then
        entry[2] = SanitizeDBCTokens(entry[2])
      end
    end
  end

  SanitizeSpellTable(TPCN_SpellData_Season)
  SanitizeSpellTable(TPCN_SpellData_Epoch)

  local function RegisterQuestTitle(id, title)
    id = tonumber(id)
    if not id or not title or title == "" then return end
    self.questIDByTitle[title] = id
    if self.NormalizeQuestTitle then
      local normalized = self:NormalizeQuestTitle(title)
      if normalized and normalized ~= "" then self.questIDByTitle[normalized] = id end
    end
  end

  local function RegisterSpellText(id, data)
    if not data or not data[1] then return end

    self.spellTextByName[data[1]] = data

    local raw = EpochCN_SpellRawData and EpochCN_SpellRawData[id]
    local rawName = raw and raw[1]
    if type(rawName) == "string" and rawName ~= "" then
      self.spellTextByName[rawName] = data
      self.localizedTextByRaw[rawName] = data[1]

      local rawRank = raw[2]
      if type(rawRank) == "string" and rawRank ~= "" then
        self.spellTextByName[rawName .. " " .. rawRank] = data
        self.localizedTextByRaw[rawName .. " " .. rawRank] = data[1]
      end
    end
  end

  local sources = { TPCN_SpellData_Epoch, TPCN_SpellData_Season }
  for _, source in pairs(sources) do
    if source then
      for id, data in pairs(source) do
        RegisterSpellText(id, data)
      end
    end
  end

  if QustCN_Data_CN then
    for id, data in pairs(QustCN_Data_CN) do
      if data and data[1] then RegisterQuestTitle(id, data[1]) end
    end
  end

  if EpochCN_EpochQuestData then
    for id, data in pairs(EpochCN_EpochQuestData) do
      if data then
        RegisterQuestTitle(id, data[1])
        RegisterQuestTitle(id, data[5])
      end
    end
  end

  if EpochCN_MapData then
    for id, data in pairs(EpochCN_MapData) do
      if data and data.t then RegisterQuestTitle(id, data.t) end
    end
  end

  -- 注册 pfDB 英文任务标题，以支持无 pfQuest 时对话框英文标题 → 任务 ID 的反查
  if pfDB and pfDB["quests"] then
    local function RegPfEnglish(src)
      if not src then return end
      for id, data in pairs(src) do
        if data and data["T"] then RegisterQuestTitle(id, data["T"]) end
      end
    end
    RegPfEnglish(pfDB["quests"]["enUS-epoch"])
    RegPfEnglish(pfDB["quests"]["enUS"])
  end

  -- 物品名计数表：在启动时预构建，避免第一次 Tooltip 悬停时才触发全量扫表
  self.itemNameCountsBuilt = true
  self.itemNameCounts = {}
  local function CountItemNames(source)
    if type(source) ~= "table" then return end
    for _, entry in pairs(source) do
      local name = entry and entry[1]
      if type(name) == "string" and name ~= "" then
        self.itemNameCounts[name] = (self.itemNameCounts[name] or 0) + 1
      end
    end
  end
  CountItemNames(TPCN_ItemData)
  CountItemNames(EpochCN_ItemOverlayData)
  CountItemNames(EpochCN_ConsumableData)

  -- 统计数据收集（供设置面板显示）
  self.stats.spellCount = 0
  self.stats.spellWithDesc = 0
  if TPCN_SpellData_Epoch then
    for id, data in pairs(TPCN_SpellData_Epoch) do
      self.stats.spellCount = self.stats.spellCount + 1
      if data[2] and data[2] ~= "" then self.stats.spellWithDesc = self.stats.spellWithDesc + 1 end
    end
  end
  if TPCN_SpellData_Season then
    for id, data in pairs(TPCN_SpellData_Season) do
      self.stats.spellCount = self.stats.spellCount + 1
      if data[2] and data[2] ~= "" then self.stats.spellWithDesc = self.stats.spellWithDesc + 1 end
    end
  end

  self.stats.unitTotal = 0
  self.stats.unitChinese = 0
  if TPCN_UnitData then
    for id, data in pairs(TPCN_UnitData) do
      self.stats.unitTotal = self.stats.unitTotal + 1
      if data[1] and string.find(data[1], "[\128-\255]") then
        self.stats.unitChinese = self.stats.unitChinese + 1
      end
    end
  end

  self.stats.questTotal = 0
  if QustCN_Data_CN then
    for _ in pairs(QustCN_Data_CN) do self.stats.questTotal = self.stats.questTotal + 1 end
  end
  if EpochCN_EpochQuestData then
    for _ in pairs(EpochCN_EpochQuestData) do self.stats.questTotal = self.stats.questTotal + 1 end
  end

  self.stats.itemNameMapTotal = 0
  if EpochCN_ItemNameMap then
    for _ in pairs(EpochCN_ItemNameMap) do self.stats.itemNameMapTotal = self.stats.itemNameMapTotal + 1 end
  end
end

function E:NormalizeDisplayText(text)
  if type(text) ~= "string" then return text end
  text = string.gsub(text, "|c%x%x%x%x%x%x%x%x(.-)|r", "%1")
  text = string.gsub(text, "|r", "")
  text = string.gsub(text, "\r", "\n")
  text = string.gsub(text, "%s+", " ")
  text = string.gsub(text, "^%s+", "")
  text = string.gsub(text, "%s+$", "")
  return text
end

function E:NormalizeQuestTitle(title)
  if not title then return title end
  title = string.gsub(title, "|c%x%x%x%x%x%x%x%x(.-)|r", "%1")
  title = string.gsub(title, "^%s*%[[^%]]+%]%s*", "")
  title = string.gsub(title, "^%s+", "")
  title = string.gsub(title, "%s+$", "")
  return title
end

function E:GetQuestIDByTitle(title)
  if not title or not self.questIDByTitle then return nil end
  return self.questIDByTitle[title] or self.questIDByTitle[self:NormalizeQuestTitle(title)]
end

function E:GetCurrentQuestData(title)
  local id
  if self.raw.GetCurrentQuestID then
    local ok, value = pcall(self.raw.GetCurrentQuestID)
    if ok and value and tonumber(value) and tonumber(value) > 0 then id = tonumber(value) end
  end

  if not id then
    if not title and self.raw.GetTitleText then
      local ok, value = pcall(self.raw.GetTitleText)
      if ok then title = value end
    end
    id = self:GetQuestIDByTitle(title)
  end

  return self:GetQuestData(id), id
end

function E:GetQuestID(questLogIndex, id)
  if id and tonumber(id) and tonumber(id) > 0 then return tonumber(id) end
  if not questLogIndex or self.resolvingQuestID then return id end
  if self.cache.questID[questLogIndex] then return self.cache.questID[questLogIndex] end

  if pfDatabase and pfDatabase.GetQuestIDs then
    self.resolvingQuestID = true
    local questIDs = pfDatabase:GetQuestIDs(questLogIndex)
    self.resolvingQuestID = false
    if questIDs and questIDs[1] and tonumber(questIDs[1]) then
      self.cache.questID[questLogIndex] = tonumber(questIDs[1])
      return self.cache.questID[questLogIndex]
    end
  end

  local title = self.raw.GetQuestLogTitle and self.raw.GetQuestLogTitle(questLogIndex)
  if title and self.questIDByTitle and self.questIDByTitle[title] then
    self.cache.questID[questLogIndex] = self.questIDByTitle[title]
    return self.cache.questID[questLogIndex]
  end

  return id
end

function E:GetQuestData(id)
  id = tonumber(id)
  if not id then return nil end

  if QustCN_Data_CN and type(QustCN_Data_CN[id]) == "table" then
    return QustCN_Data_CN[id]
  end

  if EpochCN_EpochQuestData and type(EpochCN_EpochQuestData[id]) == "table" then
    return EpochCN_EpochQuestData[id]
  end

  if pfDB and pfDB["quests"] and pfDB["quests"]["loc"] and pfDB["quests"]["loc"][id] then
    local quest = pfDB["quests"]["loc"][id]
    return { quest["T"], quest["O"], quest["D"], "pfQuest" }
  end
end

function E:GetSpellData(id)
  id = tonumber(id)
  if not id then return end
  if TPCN_SpellData_Epoch and TPCN_SpellData_Epoch[id] then return TPCN_SpellData_Epoch[id] end
  if TPCN_SpellData_Season and TPCN_SpellData_Season[id] then return TPCN_SpellData_Season[id] end
end

function E:GetSpellDataByName(name)
  if type(name) ~= "string" or name == "" or not self.spellTextByName then return end
  name = string.gsub(name, "|c%x%x%x%x%x%x%x%x(.-)|r", "%1")
  name = string.gsub(name, "|r", "")
  name = string.gsub(name, "\r", " ")
  name = string.gsub(name, "\n", " ")
  name = string.gsub(name, "%s+", " ")
  name = string.gsub(name, "^%s+", "")
  name = string.gsub(name, "%s+$", "")
  if name == "" then return end

  return self.spellTextByName[name]
    or self.spellTextByName[string.gsub(name, "%s+Rank%s+%d+$", "")]
    or self.spellTextByName[string.gsub(name, "%s+等级%s*%d+$", "")]
end

function E:GetItemData(id)
  id = tonumber(id)
  if not id then return end
  local consumable = EpochCN_ConsumableData and EpochCN_ConsumableData[id]
  local overlay = EpochCN_ItemOverlayData and EpochCN_ItemOverlayData[id]
  local base = TPCN_ItemData and TPCN_ItemData[id]
  if consumable and overlay then
    local mergedLineMap = {}
    if type(overlay[5]) == "table" then
      for raw, translated in pairs(overlay[5]) do
        mergedLineMap[raw] = translated
      end
    end
    if type(consumable[5]) == "table" then
      for raw, translated in pairs(consumable[5]) do
        mergedLineMap[raw] = translated
      end
    end
    overlay = {
      consumable[1] and consumable[1] ~= "" and consumable[1] or overlay[1],
      overlay[2] and overlay[2] ~= "" and overlay[2] or consumable[2],
      consumable[3] and consumable[3] ~= "" and consumable[3] or overlay[3],
      consumable[4] or overlay[4],
      mergedLineMap,
      consumable[6] or overlay[6],
    }
  else
    overlay = consumable or overlay
  end
  if overlay and base then
    overlay = {
      overlay[1] and overlay[1] ~= "" and overlay[1] or base[1],
      overlay[2] and overlay[2] ~= "" and overlay[2] or base[2],
      overlay[3] and overlay[3] ~= "" and overlay[3] or base[3],
      overlay[4],
      overlay[5],
      overlay[6],
    }
  end

  local data = overlay or base
  if not data then return end

  self.cache = self.cache or {}
  self.cache.itemData = self.cache.itemData or {}
  if self.cache.itemData[id] then
    return self.cache.itemData[id]
  end

  -- itemNameCounts 已在 BuildLookupTables 预构建，此处无需再扫表
  local name = data[1]
  if type(name) == "string"
    and name ~= ""
    and string.find(name, "[A-Za-z]")
    and not string.find(name, "[\128-\255]")
    and EpochCN_ItemNameMap
    and EpochCN_ItemNameMap[name]
    and EpochCN_ItemNameMap[name] ~= name
    and self.itemNameCounts
    and self.itemNameCounts[name] == 1
  then
    local resolved = {
      EpochCN_ItemNameMap[name],
      data[2],
      data[3],
      data[4],
      data[5],
      data[6],
    }
    self.cache.itemData[id] = resolved
    return resolved
  end

  self.cache.itemData[id] = data
  return data
end

function E:GetUnitData(id)
  id = tonumber(id)
  if not id then return end
  local data
  if EpochCN_Overrides and EpochCN_Overrides.units and EpochCN_Overrides.units[id] then
    data = EpochCN_Overrides.units[id]
  else
    data = TPCN_UnitData and TPCN_UnitData[id]
  end
  if not data then return end

  self.cache = self.cache or {}
  self.cache.unitData = self.cache.unitData or {}
  if self.cache.unitData[id] then
    return self.cache.unitData[id]
  end

  local name = data[1]
  if type(name) == "string"
    and name ~= ""
    and string.find(name, "[A-Za-z]")
    and not string.find(name, "[\128-\255]")
  then
    local translated = self.TranslateEnglishUnitName and self:TranslateEnglishUnitName(name)
    if translated and translated ~= name then
      local resolved = {
        translated,
        data[2],
        data[3],
        data[4],
        data[5],
        data[6],
      }
      self.cache.unitData[id] = resolved
      if self.RegisterEnglishUnitName then
        self:RegisterEnglishUnitName(name, translated)
      end
      return resolved
    end
    return data
  end

  self.cache.unitData[id] = data
  return data
end

local englishUnitWordMap = {
  ["Alliance"] = "联盟",
  ["Horde"] = "部落",
  ["Apprentice"] = "学徒",
  ["Journeyman"] = "熟练工",
  ["Adept"] = "大师",
  ["Trainer"] = "训练师",
  ["Vendor"] = "商人",
  ["Merchant"] = "商贩",
  ["Quartermaster"] = "军需官",
  ["Innkeeper"] = "旅店老板",
  ["Barkeep"] = "酒保",
  ["Flight Master"] = "飞行管理员",
  ["Auctioneer"] = "拍卖师",
  ["Banker"] = "银行家",
  ["Bouncer"] = "保镖",
  ["Recruit"] = "新兵",
  ["Footman"] = "步兵",
  ["Guard"] = "卫兵",
  ["Guardian"] = "守护者",
  ["Sentinel"] = "哨兵",
  ["Scout"] = "侦察兵",
  ["Warrior"] = "战士",
  ["Priest"] = "牧师",
  ["Mage"] = "法师",
  ["Shaman"] = "萨满",
  ["Rogue"] = "潜行者",
  ["Hunter"] = "猎人",
  ["Warlock"] = "术士",
  ["Paladin"] = "圣骑士",
  ["Druid"] = "德鲁伊",
  ["Deathguard"] = "死亡卫士",
  ["Lieutenant"] = "副队长",
  ["Captain"] = "队长",
  ["Marshal"] = "治安官",
  ["Commander"] = "指挥官",
  ["General"] = "将军",
  ["Sergeant"] = "中士",
  ["Corporal"] = "下士",
  ["Champion"] = "勇士",
  ["Chieftain"] = "酋长",
  ["Warlord"] = "督军",
  ["Overseer"] = "监工",
  ["Foreman"] = "工头",
  ["Peasant"] = "农夫",
  ["Worker"] = "工人",
  ["Peon"] = "苦工",
  ["Miner"] = "矿工",
  ["Thug"] = "暴徒",
  ["Bandit"] = "强盗",
  ["Cutthroat"] = "刺客",
  ["Brute"] = "暴徒",
  ["Spirit Healer"] = "灵魂医者",
  ["Spellcaster"] = "施法者",
  ["Geomancer"] = "风水师",
  ["Necromancer"] = "通灵师",
  ["Summoner"] = "召唤师",
  ["Healer"] = "治疗者",
  ["Berserker"] = "狂战士",
  ["Assassin"] = "刺客",
  ["Archer"] = "射手",
  ["Gunner"] = "枪手",
  ["Raider"] = "袭击者",
  ["Rider"] = "骑手",
  ["Forager"] = "觅食者",
  ["Reaver"] = "劫掠者",
  ["Enforcer"] = "打手",
  ["Thief"] = "盗贼",
  ["Looter"] = "掠夺者",
  ["Ambusher"] = "伏击者",
  ["Defender"] = "防御者",
  ["Warmaster"] = "统帅",
  ["Surveyor"] = "勘测员",
  ["Explorer"] = "探险者",
  ["Veteran"] = "老兵",
  ["Seasoned"] = "老练的",
  ["Stalker"] = "潜伏者",
  ["Watcher"] = "守望者",
  ["Sentry"] = "哨兵",
  ["Keeper"] = "守护者",
  ["Weaver"] = "编织者",
  ["Constructor"] = "构造者",
  ["Executioner"] = "行刑者",
  ["Vanquisher"] = "征服者",
  ["Chronomancer"] = "时空法师",
  ["Invader"] = "入侵者",
  ["Spellbreaker"] = "破法者",
  ["Binder"] = "缚法者",
  ["Mercenary"] = "雇佣兵",
  ["Soldier"] = "士兵",
  ["Prisoner"] = "囚犯",
  ["Refugee"] = "难民",
  ["Slave"] = "奴隶",
  ["Steed"] = "战马",
  ["Rhino"] = "犀牛",
  ["Fox"] = "狐狸",
  ["Gnoll"] = "豺狼人",
  ["Murloc"] = "鱼人",
  ["Kobold"] = "狗头人",
  ["Ogre"] = "食人魔",
  ["Satyr"] = "萨特",
  ["Harpy"] = "鹰身人",
  ["Centaur"] = "半人马",
  ["Naga"] = "纳迦",
  ["Raptor"] = "迅猛龙",
  ["Dragonkin"] = "龙人",
  ["Dragonspawn"] = "龙人",
  ["Whelp"] = "雏龙",
  ["Whelpling"] = "雏龙",
  ["Drake"] = "幼龙",
  ["Dragon"] = "龙",
  ["Demon"] = "恶魔",
  ["Imp"] = "小鬼",
  ["Felhunter"] = "魔犬",
  ["Succubus"] = "魅魔",
  ["Voidwalker"] = "虚空行者",
  ["Infernal"] = "地狱火",
  ["Skeleton"] = "骷髅",
  ["Zombie"] = "僵尸",
  ["Ghoul"] = "食尸鬼",
  ["Abomination"] = "憎恶",
  ["Banshee"] = "女妖",
  ["Ghost"] = "幽灵",
  ["Soul"] = "灵魂",
  ["Void"] = "虚空",
  ["Portal"] = "传送门",
  ["Troll"] = "巨魔",
  -- 新增：更多生物/职业/阵营
  ["Wolf"] = "狼",
  ["Worg"] = "座狼",
  ["Bear"] = "熊",
  ["Spider"] = "蜘蛛",
  ["Scorpion"] = "蝎子",
  ["Serpent"] = "蛇",
  ["Basilisk"] = "石化蜥蜴",
  ["Crocolisk"] = "鳄鱼",
  ["Bat"] = "蝙蝠",
  ["Owl"] = "猫头鹰",
  ["Eagle"] = "鹰",
  ["Hawk"] = "鹰",
  ["Boar"] = "野猪",
  ["Hyena"] = "土狼",
  ["Lion"] = "狮子",
  ["Tiger"] = "老虎",
  ["Panther"] = "黑豹",
  ["Gorilla"] = "猩猩",
  ["Slime"] = "软泥怪",
  ["Ooze"] = "软泥怪",
  ["Elemental"] = "元素",
  ["Golem"] = "傀儡",
  ["Construct"] = "构造体",
  ["Gargoyle"] = "石像鬼",
  ["Shade"] = "暗影",
  ["Wraith"] = "怨灵",
  ["Treant"] = "树人",
  ["Ravager"] = "破坏者",
  ["Mammoth"] = "猛犸象",
  ["Vrykul"] = "维库人",
  -- 新增：职业/称谓
  ["Initiate"] = "新手",
  ["Acolyte"] = "侍僧",
  ["Disciple"] = "门徒",
  ["Mystic"] = "神秘者",
  ["Seer"] = "先知",
  ["Oracle"] = "神谕者",
  ["Sage"] = "贤者",
  ["Scholar"] = "学者",
  ["Arcanist"] = "奥术师",
  ["Conjurer"] = "魔法师",
  ["Enchanter"] = "附魔师",
  ["Elementalist"] = "元素师",
  ["Knight"] = "骑士",
  ["Crusader"] = "十字军",
  ["Templar"] = "圣殿骑士",
  ["Vindicator"] = "维护者",
  ["Protector"] = "保护者",
  ["Avenger"] = "复仇者",
  ["Inquisitor"] = "审判官",
  ["Grunt"] = "步兵",
  ["Gladiator"] = "角斗士",
  ["Monk"] = "武僧",
  ["Sniper"] = "狙击手",
  ["Marksman"] = "射手",
  ["Rifleman"] = "步枪手",
  ["Engineer"] = "工程师",
  ["Mechanic"] = "机械师",
  ["Tinker"] = "工匠",
  ["Technician"] = "技师",
  ["Alchemist"] = "炼金术士",
  ["Apothecary"] = "药剂师",
  ["Blacksmith"] = "铁匠",
  ["Tailor"] = "裁缝",
  ["Cook"] = "厨师",
  ["Fisherman"] = "渔夫",
  ["Farmer"] = "农夫",
  ["Spy"] = "间谍",
  ["Infiltrator"] = "渗透者",
  ["Pirate"] = "海盗",
  ["Corsair"] = "海盗",
  ["Sailor"] = "水手",
  ["Harbinger"] = "先驱",
  ["Herald"] = "传令官",
  ["Emissary"] = "使者",
  ["Ambassador"] = "大使",
  ["Courier"] = "信使",
  ["Warden"] = "典狱官",
  ["Taskmaster"] = "监工",
  ["Archmage"] = "大法师",
  ["Battlemage"] = "战斗法师",
  ["Lich"] = "巫妖",
  ["Death Knight"] = "死亡骑士",
  ["Stable Master"] = "马厩管理员",
  ["Weapon Master"] = "武器大师",
  ["Battle Master"] = "战场军官",
  ["Patroller"] = "巡逻兵",
  ["Outrider"] = "先驱者",
  ["Tracker"] = "追踪者",
  ["Tamer"] = "驯兽师",
  ["Beastmaster"] = "驯兽师",
  ["Defias"] = "迪菲亚",
  ["Scarlet"] = "血色",
  ["Forsaken"] = "被遗忘者",
  ["Bloodsail"] = "血帆",
  ["Syndicate"] = "辛迪加",
  ["Infinite"] = "无尽",
  ["Frostwolf"] = "霜狼",
  ["Stormpike"] = "雷矛",
  ["Irondeep"] = "铁深",
  ["Coldmine"] = "冷矿",
  ["Skybreaker"] = "破天者",
  ["Kor'kron"] = "库卡隆",
  ["Anub'ar"] = "阿努巴尔",
  ["Drakkari"] = "达卡莱",
  ["Scourge"] = "天灾",
  ["Ethereal"] = "虚灵",
  ["Riverpaw"] = "河爪",
  ["Forest Troll"] = "森林巨魔",
  ["Bronze Dragonspawn"] = "青铜龙人",
  ["Green Dragonspawn"] = "绿龙人",
  ["White Dragonspawn"] = "白龙人",
  ["Blackrock"] = "黑石",
  ["Greater"] = "强大的",
  ["Lesser"] = "次级",
  ["Young"] = "年幼的",
  ["Ancient"] = "远古的",
  ["Elder"] = "年长的",
  ["Wounded"] = "受伤的",
  ["Injured"] = "受伤的",
  ["Dying"] = "垂死的",
  ["Captured"] = "被俘的",
  ["Freed"] = "获释的",
  ["Obedient"] = "驯服的",
  ["Juvenile"] = "幼年的",
  ["Savage"] = "野蛮",
  ["Fierce"] = "凶猛的",
  ["Wild"] = "野性的",
  ["Haunted"] = "闹鬼的",
  ["Cursed"] = "被诅咒的",
  -- 新增修饰词
  ["Enraged"] = "激怒的",
  ["Frenzied"] = "狂暴的",
  ["Rabid"] = "疯狂的",
  ["Diseased"] = "染病的",
  ["Plagued"] = "被瘟疫感染的",
  ["Corrupted"] = "被腐蚀的",
  ["Tainted"] = "被污染的",
  ["Withered"] = "枯萎的",
  ["Frozen"] = "冰冻的",
  ["Burning"] = "燃烧的",
  ["Molten"] = "熔火",
  ["Spectral"] = "幽灵",
  ["Undead"] = "亡灵",
  ["Skeletal"] = "骷髅",
  ["Giant"] = "巨型",
  ["Feral"] = "野性的",
  ["Armored"] = "装甲",
  ["Iron"] = "钢铁",
  ["Storm"] = "风暴",
  ["Frost"] = "冰霜",
  ["Dark"] = "黑暗",
  ["Twilight"] = "暮光",
  ["Fel"] = "邪能",
}

local englishUnitModifierOnly = {
  ["Greater"] = true,
  ["Lesser"] = true,
  ["Young"] = true,
  ["Ancient"] = true,
  ["Elder"] = true,
  ["Wounded"] = true,
  ["Injured"] = true,
  ["Dying"] = true,
  ["Savage"] = true,
  ["Fierce"] = true,
  ["Wild"] = true,
  ["Haunted"] = true,
  ["Cursed"] = true,
  ["Enraged"] = true,
  ["Frenzied"] = true,
  ["Rabid"] = true,
  ["Diseased"] = true,
  ["Plagued"] = true,
  ["Corrupted"] = true,
  ["Tainted"] = true,
  ["Withered"] = true,
  ["Frozen"] = true,
  ["Burning"] = true,
  ["Molten"] = true,
  ["Spectral"] = true,
  ["Undead"] = true,
  ["Skeletal"] = true,
  ["Giant"] = true,
  ["Feral"] = true,
  ["Armored"] = true,
  ["Iron"] = true,
  ["Storm"] = true,
  ["Frost"] = true,
  ["Dark"] = true,
  ["Twilight"] = true,
  ["Fel"] = true,
  ["Captured"] = true,
  ["Freed"] = true,
  ["Obedient"] = true,
  ["Juvenile"] = true,
}

local englishObjectWordMap = {
  ["Wooden Cage"] = "木制牢笼",
  ["Prison Cage"] = "囚笼",
  ["Treasure Chest"] = "宝箱",
  ["Supply Crate"] = "补给箱",
  ["Stone Obelisk"] = "石制方尖碑",
  ["Ritual Altar"] = "仪式祭坛",
  ["Ancient Brazier"] = "古代火盆",
  ["Dark Portal"] = "黑暗之门",
  ["Ancient Shrine"] = "远古神龛",
  ["Stone Tablet"] = "石碑",
  ["Wooden"] = "木制",
  ["Stone"] = "石制",
  ["Ancient"] = "远古的",
  ["Old"] = "旧的",
  ["Broken"] = "破损的",
  ["Damaged"] = "损坏的",
  ["Supply"] = "补给",
  ["Treasure"] = "宝藏",
  ["Prison"] = "囚禁",
  ["Ritual"] = "仪式",
  ["Dark"] = "黑暗",
  ["Arcane"] = "奥术",
  ["Rune"] = "符文",
  ["Cage"] = "牢笼",
  ["Chest"] = "箱子",
  ["Crate"] = "箱",
  ["Obelisk"] = "方尖碑",
  ["Brazier"] = "火盆",
  ["Altar"] = "祭坛",
  ["Shrine"] = "神龛",
  ["Relic"] = "圣物",
  ["Banner"] = "旗帜",
  ["Barrel"] = "桶",
  ["Totem"] = "图腾",
  ["Statue"] = "雕像",
  ["Tablet"] = "石碑",
  ["Crystal"] = "水晶",
  ["Orb"] = "宝珠",
  ["Torch"] = "火把",
  ["Portal"] = "传送门",
}

local englishObjectModifierOnly = {
  ["Wooden"] = true,
  ["Stone"] = true,
  ["Ancient"] = true,
  ["Old"] = true,
  ["Broken"] = true,
  ["Damaged"] = true,
  ["Supply"] = true,
  ["Treasure"] = true,
  ["Prison"] = true,
  ["Ritual"] = true,
  ["Dark"] = true,
  ["Arcane"] = true,
  ["Rune"] = true,
}

local function HasCJK(text)
  return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
end

function E:TranslateEnglishUnitName(english)
  if type(english) ~= "string" or english == "" then return nil end
  english = self.NormalizeDisplayText and self:NormalizeDisplayText(english) or english
  if not english or english == "" or HasCJK(english) or not string.find(english, "[A-Za-z]") then return nil end

  if self.nameMap and self.nameMap[english] then return self.nameMap[english] end
  if EpochCN_Overrides and EpochCN_Overrides.englishUnits and EpochCN_Overrides.englishUnits[english] then
    return EpochCN_Overrides.englishUnits[english]
  end
  if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[english] then
    return EpochCN_ObjectiveNameData[english]
  end

  local lower = string.lower(english)
  if string.find(lower, "placeholder", 1, true)
    or string.find(lower, "dummy", 1, true)
    or string.find(lower, "trigger", 1, true)
    or string.find(lower, "bunny", 1, true)
    or string.find(lower, "target", 1, true)
    or string.find(lower, "credit", 1, true)
    or string.find(lower, "marker", 1, true)
    or string.find(lower, "visual", 1, true)
    or string.find(lower, "controller", 1, true)
    or string.find(lower, "event", 1, true)
    or string.find(lower, "proxy", 1, true)
    or string.find(lower, "transform", 1, true)
    or string.find(lower, "invisible", 1, true)
    or string.find(lower, "invis", 1, true)
    or string.find(lower, "dnd", 1, true)
    or string.find(lower, "only gm can see it", 1, true)
    or string.find(lower, "test", 1, true)
    or string.find(lower, "unused", 1, true)
    or string.find(lower, "deprecated", 1, true)
    or string.find(english, "<", 1, true)
    or string.find(english, "[", 1, true)
  then
    return nil
  end

  local parts = {}
  for token in string.gmatch(english, "[A-Za-z][A-Za-z'%-]*") do
    table.insert(parts, token)
  end
  if #parts == 0 then return nil end

  local translatedParts = {}
  local usedWords = {}
  local index = 1
  while index <= #parts do
    local matched = false
    for length = math.min(3, #parts - index + 1), 1, -1 do
      local phrase = table.concat(parts, " ", index, index + length - 1)
      local translated = englishUnitWordMap[phrase]
      if translated then
        table.insert(translatedParts, translated)
        table.insert(usedWords, phrase)
        index = index + length
        matched = true
        break
      end
    end
    if not matched then
      return nil
    end
  end

  local hasNonModifier = false
  for _, word in ipairs(usedWords) do
    if not englishUnitModifierOnly[word] then
      hasNonModifier = true
      break
    end
  end
  if not hasNonModifier then return nil end

  return table.concat(translatedParts)
end

function E:TranslateEnglishObjectName(english)
  if type(english) ~= "string" or english == "" then return nil end
  english = self.NormalizeDisplayText and self:NormalizeDisplayText(english) or english
  if not english or english == "" or HasCJK(english) or not string.find(english, "[A-Za-z]") then return nil end

  if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[english] then
    return EpochCN_ObjectiveNameData[english]
  end

  local lower = string.lower(english)
  if string.find(lower, "placeholder", 1, true)
    or string.find(lower, "dummy", 1, true)
    or string.find(lower, "trigger", 1, true)
    or string.find(lower, "bunny", 1, true)
    or string.find(lower, "target", 1, true)
    or string.find(lower, "credit", 1, true)
    or string.find(lower, "marker", 1, true)
    or string.find(lower, "visual", 1, true)
    or string.find(lower, "controller", 1, true)
    or string.find(lower, "event", 1, true)
    or string.find(lower, "proxy", 1, true)
    or string.find(lower, "transform", 1, true)
    or string.find(lower, "invisible", 1, true)
    or string.find(lower, "invis", 1, true)
    or string.find(lower, "dnd", 1, true)
    or string.find(lower, "spawner", 1, true)
    or string.find(lower, "waypoint", 1, true)
    or string.find(lower, "only gm can see it", 1, true)
    or string.find(lower, "test", 1, true)
    or string.find(lower, "unused", 1, true)
    or string.find(lower, "deprecated", 1, true)
    or string.find(english, "<", 1, true)
    or string.find(english, "[", 1, true)
  then
    return nil
  end

  local parts = {}
  for token in string.gmatch(english, "[A-Za-z][A-Za-z'%-]*") do
    table.insert(parts, token)
  end
  if #parts == 0 then return nil end

  local translatedParts = {}
  local usedWords = {}
  local index = 1
  while index <= #parts do
    local matched = false
    for length = math.min(3, #parts - index + 1), 1, -1 do
      local phrase = table.concat(parts, " ", index, index + length - 1)
      local translated = englishObjectWordMap[phrase]
      if translated then
        table.insert(translatedParts, translated)
        table.insert(usedWords, phrase)
        index = index + length
        matched = true
        break
      end
    end
    if not matched then
      return nil
    end
  end

  local hasNonModifier = false
  for _, word in ipairs(usedWords) do
    if not englishObjectModifierOnly[word] then
      hasNonModifier = true
      break
    end
  end
  if not hasNonModifier then return nil end

  return table.concat(translatedParts)
end

function E:RegisterEnglishUnitName(english, chinese)
  if type(english) ~= "string" or type(chinese) ~= "string" then return end
  if english == "" or chinese == "" or english == chinese then return end
  self.nameMap = self.nameMap or {}
  self.nameMap[english] = chinese
end

function E:GetCallBoardData(id)
  id = tonumber(id)
  return id and TPCN_CallBoardData and TPCN_CallBoardData[id]
end

function E:Initialize()
  EpochCNDB = MergeDefaults(EpochCNDB, defaults)
  self:ApplyClientLocalePreference()
  DisableMapIconDefaults(EpochCNDB)
  DisableAppendedTooltipDefaults(EpochCNDB)
  EpochCNCharDB = MergeDefaults(EpochCNCharDB, charDefaults)
  if not EpochCNDB.enabled then return end

  self:CaptureRawAPI()
  self:LoadSeedData()
  self:BuildLookupTables()

  for _, name in ipairs(self.moduleOrder) do
    local init = self.modules[name]
    if type(init) == "function" then
      local ok, err = pcall(init, self)
      if not ok then self:Debug(name .. " 初始化失败: " .. tostring(err)) end
    end
  end

  self:RegisterSlashCommands()
  self:Debug("已加载 " .. self.version)
  self:Print("已加载 " .. self.version .. "。输入 /ecn 查看状态。")
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, event, name)
  if name == E.name then
    E:Initialize()
  end
end)
