local addonName = ...
local E = EpochCN or {}
EpochCN = E

E.name = addonName or "EpochCN"
E.version = "0.4.47"
E.designLabel = "汉化组"
E.modules = E.modules or {}
E.moduleOrder = E.moduleOrder or {}
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
  appendTooltip = true,
  showDesignTag = true,
  showSource = false,
  minimapButtonHide = false,
  minimapButtonAngle = 225,
  updateCheck = true,  -- 自动检查新版本（通过公会/队伍广播）
  debug = false,
  mapIconDefaultsVersion = "",
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
  if LoadTPCNSpellData52 then LoadTPCNSpellData52() end
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

  -- ============================================================
  -- 清洗法术数据中未解析的 DBC 公式/占位符 token
  -- 避免 Tooltip、角色面板、技能书等任何位置都显示残留
  -- ============================================================
  local function SanitizeDBCTokens(text)
    if type(text) ~= "string" or text == "" then return text end
    -- 移除 法术ID前缀+m/除数 组合，如 "54928m1/1000"、"1144440m2/-1000.2"
    text = string.gsub(text, "%d%d%d%d+m%d+/[%-%d%.]*", "")
    -- 移除独立的 mX/除数 公式，如 "m1/1000"、"m2/1000.1"
    text = string.gsub(text, "m%d+/[%-%d%.]+", "")
    -- 移除 /除数;sX 条件引用，如 "/1000;s1"、"/1000;s2"
    text = string.gsub(text, "/%d*%.?%d*;s%d+", "")
    -- 移除 0-mX/除数 范围公式，如 "0-m1/1000.2"
    text = string.gsub(text, "0%-m%d+/[%d%.]+", "")
    -- 移除 5位以上法术ID+sX 法术引用
    text = string.gsub(text, "%d%d%d%d%d+s%d+", "")
    -- 移除 dX 持续时间引用 token
    text = string.gsub(text, "%d%d%d%d%d+d", "")
    -- 移除 aX 范围引用
    text = string.gsub(text, "%d%d%d%d+a%d+", "")
    -- 移除独立的 @req:xxx@ 前置条件标记
    text = string.gsub(text, "@req:%d+@%s*\n?", "")
    text = string.gsub(text, "@req:[^@]+@%s*\n?", "")
    -- 移除孤立的小写 s/S/h/d 百分号，如 "h%"、"S2%" 在无对应数字时
    text = string.gsub(text, "([^%a%d])[hHsSdDaAm][%d]?%%", "%1")
    -- 修复 token 被清除后留下的"孤立单位"残留：
    --   "冷却时间秒。" -> "冷却时间。"
    --   "获得%的法术" -> "获得?的法术"
    --   "提高%。" -> "提高。"
    text = string.gsub(text, "(%S)%%(的)", "%1%2")
    text = string.gsub(text, "%%(的)", "%1")
    text = string.gsub(text, "(%S)%%(，)", "%1%2")
    text = string.gsub(text, "(%S)%%%s*。", "%1。")
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

  SanitizeSpellTable(TPCN_SpellData_52)
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

  local sources = { TPCN_SpellData_Epoch, TPCN_SpellData_Season, TPCN_SpellData_52 }
  for _, source in pairs(sources) do
    if source then
      for _, data in pairs(source) do
        if data and data[1] then
          self.spellTextByName[data[1]] = data
        end
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
  if TPCN_SpellData_52 and TPCN_SpellData_52[id] then return TPCN_SpellData_52[id] end
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
    return {
      overlay[1] and overlay[1] ~= "" and overlay[1] or base[1],
      overlay[2] and overlay[2] ~= "" and overlay[2] or base[2],
      overlay[3] and overlay[3] ~= "" and overlay[3] or base[3],
      overlay[4],
      overlay[5],
      overlay[6],
    }
  end
  return overlay or base
end

function E:GetUnitData(id)
  id = tonumber(id)
  if not id then return end
  if EpochCN_Overrides and EpochCN_Overrides.units and EpochCN_Overrides.units[id] then
    return EpochCN_Overrides.units[id]
  end
  return TPCN_UnitData and TPCN_UnitData[id]
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
  DisableMapIconDefaults(EpochCNDB)
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
