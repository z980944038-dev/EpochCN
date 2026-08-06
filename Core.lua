local addonName = ...
local E = EpochCN or {}
EpochCN = E

E.name = addonName or "EpochCN"
E.version = "0.8.0-core"
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
  questTracker = true,   -- 任务追踪 UI 汉化
  disablePFQuestTracker = true,
  forcePFQuestMap = false,
  appendTooltip = false,
  showDesignTag = true,
  showSource = false,
  minimapButtonHide = false,
  minimapButtonAngle = 225,
  forceChineseClientLocale = true,
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
      E:Print("数据：任务=" .. tostring(QustCN_Data_CN and "QuestCN" or "无") .. "，技能=patch-Z.MPQ，物品=" .. tostring(TPCN_ItemData and "已加载" or "无"))
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

-- WoW 3.3.5a 没有 C_Timer。短延迟任务共用一个按需显示的计时帧；
-- 队列为空时自动隐藏，不产生常驻 OnUpdate 开销。
function E:After(delay, callback)
  if type(callback) ~= "function" then return end
  self.timers = self.timers or {}
  table.insert(self.timers, { remaining = tonumber(delay) or 0, callback = callback })
  if not self.timerFrame then
    local owner = self
    self.timerFrame = CreateFrame("Frame")
    self.timerFrame:Hide()
    self.timerFrame:SetScript("OnUpdate", function(frame, elapsed)
      for index = #owner.timers, 1, -1 do
        local timer = owner.timers[index]
        timer.remaining = timer.remaining - elapsed
        if timer.remaining <= 0 then
          table.remove(owner.timers, index)
          local ok, err = pcall(timer.callback)
          if not ok then owner:Debug("延迟任务执行失败: " .. tostring(err)) end
        end
      end
      if #owner.timers == 0 then frame:Hide() end
    end)
  end
  self.timerFrame:Show()
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
  if LoadTPCNGlobalData then LoadTPCNGlobalData() end
  if LoadTPCNItemData then LoadTPCNItemData() end
  if LoadEpochCNItemNameMap then LoadEpochCNItemNameMap() end
  if LoadEpochCNItemOverlayData then LoadEpochCNItemOverlayData() end
  if LoadEpochCNTooltipLineData then LoadEpochCNTooltipLineData() end
  if LoadTPCNUnitData then LoadTPCNUnitData() end
  if LoadEpochCNObjectiveNameData then LoadEpochCNObjectiveNameData() end
  if LoadEpochCNQuestData then LoadEpochCNQuestData() end
  if LoadEpochCNQuestTitleIndex then LoadEpochCNQuestTitleIndex() end
  if (EpochCNDB.worldMap or EpochCNDB.minimapQuestPins) and LoadEpochCNMapData then
    LoadEpochCNMapData()
  end
  if LoadEpochCNEpochHeadData then LoadEpochCNEpochHeadData() end
  if LoadEpochCNEpochDBSupplementData then LoadEpochCNEpochDBSupplementData() end
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
    -- 移除 $z（区域名）、$c（职业）、$g（性别）—— 必须在 $ 兜底之前
    text = string.gsub(text, "%$[zZcCgG]", "")
    -- 移除孤立 $，避免公式被部分清洗后残留（放在最后兜底）
    text = string.gsub(text, "%$", "")

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

  if EpochCN_QuestTitleIndex then
    for title, id in pairs(EpochCN_QuestTitleIndex) do
      RegisterQuestTitle(id, title)
    end
  end

  if EpochCN_EpochDBQuestAliases then
    for title, id in pairs(EpochCN_EpochDBQuestAliases) do
      RegisterQuestTitle(id, title)
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
      if type(name) == "string" and name ~= ""
        and string.find(name, "[A-Za-z]")
        and not string.find(name, "[\128-\255]") then
        self.itemNameCounts[name] = (self.itemNameCounts[name] or 0) + 1
      end
    end
  end
  CountItemNames(TPCN_ItemData)
  CountItemNames(EpochCN_ItemOverlayData)

end

-- 覆盖统计只在设置页首次打开时计算，避免每次登录扫描大型数据表。
function E:BuildStats()
  if self.statsBuilt then return self.stats or {} end
  self.statsBuilt = true
  local stats = {
    unitTotal = 0, unitChinese = 0, questTotal = 0, itemNameMapTotal = 0,
  }
  if TPCN_UnitData then
    for _, data in pairs(TPCN_UnitData) do
      stats.unitTotal = stats.unitTotal + 1
      if data[1] and string.find(data[1], "[\128-\255]") then stats.unitChinese = stats.unitChinese + 1 end
    end
  end
  if QustCN_Data_CN then for _ in pairs(QustCN_Data_CN) do stats.questTotal = stats.questTotal + 1 end end
  if EpochCN_EpochQuestData then for _ in pairs(EpochCN_EpochQuestData) do stats.questTotal = stats.questTotal + 1 end end
  if EpochCN_ItemNameMap then for _ in pairs(EpochCN_ItemNameMap) do stats.itemNameMapTotal = stats.itemNameMapTotal + 1 end end
  self.stats = stats
  return stats
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

  if EpochCN_EpochQuestData and type(EpochCN_EpochQuestData[id]) == "table" then
    return EpochCN_EpochQuestData[id]
  end

  if QustCN_Data_CN and type(QustCN_Data_CN[id]) == "table" then
    return QustCN_Data_CN[id]
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

  -- 缓存前置：已缓存则直接返回，避免每次重复执行 overlay 合并
  self.cache = self.cache or {}
  self.cache.itemData = self.cache.itemData or {}
  if self.cache.itemData[id] then
    return self.cache.itemData[id]
  end

  local overlay = EpochCN_ItemOverlayData and EpochCN_ItemOverlayData[id]
  local base = TPCN_ItemData and TPCN_ItemData[id]
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

-- 词根翻译词典已提取到 Data/UnitNameDict.lua
-- 通过全局变量引用，方便独立更新翻译数据
local englishUnitWordMap = EpochCN_UnitNameDict or {}
local englishUnitModifierOnly = EpochCN_UnitModifierOnly or {}
local englishObjectWordMap = EpochCN_ObjectNameDict or {}
local englishObjectModifierOnly = EpochCN_ObjectModifierOnly or {}

local function HasCJK(text)
  return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
end

-- ============================================================
-- 内部/技术性名称黑名单关键词（不应显示到界面上）
-- ============================================================
local internalNameBlacklist = {
  "placeholder", "dummy", "trigger", "bunny", "target", "credit",
  "marker", "visual", "controller", "event", "proxy", "transform",
  "invisible", "invis", "dnd", "only gm can see it",
  "test", "unused", "deprecated",
}
-- 物体名称额外的黑名单关键词
local objectExtraBlacklist = { "spawner", "waypoint" }

local function IsInternalName(english, extraBlacklist)
  local lower = string.lower(english)
  for _, keyword in ipairs(internalNameBlacklist) do
    if string.find(lower, keyword, 1, true) then return true end
  end
  if extraBlacklist then
    for _, keyword in ipairs(extraBlacklist) do
      if string.find(lower, keyword, 1, true) then return true end
    end
  end
  if string.find(english, "<", 1, true) or string.find(english, "[", 1, true) then
    return true
  end
  return false
end

-- ============================================================
-- 通用词根翻译引擎：将英文名按词根字典逐词翻译
-- wordMap: 词根 → 中文 映射表
-- modifierOnly: 仅为修饰词的词集合（不能单独构成有意义的翻译）
-- ============================================================
local function TranslateByWordMap(english, wordMap, modifierOnly)
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
      local translated = wordMap[phrase]
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

  -- 纯修饰词组合不算有意义的翻译
  local hasNonModifier = false
  for _, word in ipairs(usedWords) do
    if not modifierOnly[word] then
      hasNonModifier = true
      break
    end
  end
  if not hasNonModifier then return nil end

  return table.concat(translatedParts)
end

function E:TranslateEnglishUnitName(english)
  if type(english) ~= "string" or english == "" then return nil end
  english = self.NormalizeDisplayText and self:NormalizeDisplayText(english) or english
  if not english or english == "" or HasCJK(english) or not string.find(english, "[A-Za-z]") then return nil end

  -- 优先查询直接映射表
  if self.nameMap and self.nameMap[english] then return self.nameMap[english] end
  if EpochCN_Overrides and EpochCN_Overrides.englishUnits and EpochCN_Overrides.englishUnits[english] then
    return EpochCN_Overrides.englishUnits[english]
  end
  if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[english] then
    return EpochCN_ObjectiveNameData[english]
  end

  -- 过滤技术性内部名称
  if IsInternalName(english) then return nil end

  return TranslateByWordMap(english, englishUnitWordMap, englishUnitModifierOnly)
end

function E:TranslateEnglishObjectName(english)
  if type(english) ~= "string" or english == "" then return nil end
  english = self.NormalizeDisplayText and self:NormalizeDisplayText(english) or english
  if not english or english == "" or HasCJK(english) or not string.find(english, "[A-Za-z]") then return nil end

  -- 优先查询直接映射表
  if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[english] then
    return EpochCN_ObjectiveNameData[english]
  end

  -- 过滤技术性内部名称（物体额外过滤 spawner/waypoint）
  if IsInternalName(english, objectExtraBlacklist) then return nil end

  return TranslateByWordMap(english, englishObjectWordMap, englishObjectModifierOnly)
end

function E:RegisterEnglishUnitName(english, chinese)
  if type(english) ~= "string" or type(chinese) ~= "string" then return end
  if english == "" or chinese == "" or english == chinese then return end
  self.nameMap = self.nameMap or {}
  self.nameMap[english] = chinese
end

function E:Initialize()
  EpochCNDB = MergeDefaults(EpochCNDB, defaults)
  EpochCNDB.social = nil
  EpochCNDB.social_enabled_ui = nil
  EpochCNDB.social_channel_ui = nil
  EpochCNDB.social_lfg_ui = nil
  EpochCNDB.social_qc_ui = nil
  EpochCNDB.questAutoSync = nil
  EpochCNDB.questProgressNotify = nil
  EpochCNDB.questProgressPartyChat = nil
  EpochCNDB.updateCheck = nil
  EpochCNDB.globalStrings = nil
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
