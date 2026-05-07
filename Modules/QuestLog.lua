EpochCN:RegisterModule("QuestLog", function(E)
  if not EpochCNDB.questLog then return end

  myGetQuestLogTitle = myGetQuestLogTitle or E.raw.GetQuestLogTitle
  myGetQuestLogQuestText = myGetQuestLogQuestText or E.raw.GetQuestLogQuestText
  myGetQuestLogLeaderBoard = myGetQuestLogLeaderBoard or E.raw.GetQuestLogLeaderBoard
  myGetQuestLogCompletionText = myGetQuestLogCompletionText or E.raw.GetQuestLogCompletionText
  myGetAbandonQuestName = myGetAbandonQuestName or E.raw.GetAbandonQuestName
  myGetTitleText = myGetTitleText or E.raw.GetTitleText
  myGetQuestText = myGetQuestText or E.raw.GetQuestText
  myGetObjectiveText = myGetObjectiveText or E.raw.GetObjectiveText
  myGetRewardText = myGetRewardText or E.raw.GetRewardText
  myGetProgressText = myGetProgressText or E.raw.GetProgressText
  myGetGreetingText = myGetGreetingText or E.raw.GetGreetingText

  -- 目标缓存大小限制：超出时清空（每次最多存储约 512 条目标文本翻译）
  local OBJECTIVE_CACHE_MAX = 512
  local objectiveCacheSize = 0

  local function SafeSetObjectiveCache(key, value)
    if E.cache.objective[key] ~= nil then return end
    if objectiveCacheSize >= OBJECTIVE_CACHE_MAX then
      E.cache.objective = {}
      objectiveCacheSize = 0
    end
    E.cache.objective[key] = value
    objectiveCacheSize = objectiveCacheSize + 1
  end

  local function PlainReplaceOnce(text, search, replacement)
    local start, finish = string.find(text, search, 1, true)
    if not start then return text end
    return string.sub(text, 1, start - 1) .. replacement .. string.sub(text, finish + 1)
  end

  local function Trim(text)
    if not text then return text end
    return (string.gsub(string.gsub(text, "^%s+", ""), "%s+$", ""))
  end

  local function ReplacePlayerTokens(text)
    if not text then return text end
    local playerName = UnitName and UnitName("player") or ""
    local className = UnitClass and select(1, UnitClass("player")) or ""
    text = string.gsub(text, "$[Nn]", playerName)
    text = string.gsub(text, "$[Cc]", className)
    text = string.gsub(text, "<玩家>", playerName)
    text = string.gsub(text, "<职业>", className)
    text = string.gsub(text, "<player>", playerName)
    text = string.gsub(text, "<class>", className)
    return text
  end

  local objectiveNameIndex

  local function AddObjectiveCandidate(index, english, chinese)
    if type(english) ~= "string" or type(chinese) ~= "string" then return end
    if english == "" or chinese == "" or english == chinese or string.match(english, "^%d+$") then return end
    if string.len(english) <= 2 then return end

    local bestToken
    for token in string.gmatch(english, "[A-Za-z][A-Za-z'%-]+") do
      if string.len(token) > 2 and (not bestToken or string.len(token) > string.len(bestToken)) then
        bestToken = token
      end
    end
    if not bestToken then return end

    index[bestToken] = index[bestToken] or {}
    table.insert(index[bestToken], { english, chinese })
  end

  local function GetObjectiveNameIndex()
    if objectiveNameIndex then return objectiveNameIndex end
    objectiveNameIndex = {}
    if EpochCN_ObjectiveNameData then
      for english, chinese in pairs(EpochCN_ObjectiveNameData) do
        AddObjectiveCandidate(objectiveNameIndex, english, chinese)
      end
    end
    if EpochCN_Overrides and EpochCN_Overrides.englishUnits then
      for english, chinese in pairs(EpochCN_Overrides.englishUnits) do
        AddObjectiveCandidate(objectiveNameIndex, english, chinese)
      end
    end
    return objectiveNameIndex
  end

  -- ============================================================
  -- pfDB 反向索引（英文名 → 中文名），延迟构建，避免每次查找遍历数万条目
  -- ============================================================
  local pfReverseIndex    -- { [englishName] = chineseName }
  local pfReverseBuilt = false

  local function BuildPfReverseIndex()
    if pfReverseBuilt then return end
    pfReverseBuilt = true
    pfReverseIndex = {}
    if not pfDB then return end

    local catalogPairs = {
      { pfDB["units"]   and pfDB["units"]["enUS"],   pfDB["units"]   and (pfDB["units"]["zhCN"]   or pfDB["units"]["loc"]) },
      { pfDB["items"]   and pfDB["items"]["enUS"],   pfDB["items"]   and (pfDB["items"]["zhCN"]   or pfDB["items"]["loc"]) },
      { pfDB["objects"] and pfDB["objects"]["enUS"],  pfDB["objects"] and (pfDB["objects"]["zhCN"]  or pfDB["objects"]["loc"]) },
    }
    for _, pair in ipairs(catalogPairs) do
      local en, cn = pair[1], pair[2]
      if en and cn then
        for id, name in pairs(en) do
          if cn[id] and not pfReverseIndex[name] then
            pfReverseIndex[name] = cn[id]
          end
        end
      end
    end
  end

  local function TranslateObjectiveSubject(subject)
    subject = Trim(subject)
    if not subject or subject == "" then return subject end

    local cacheKey = "__subject__" .. subject
    if E.cache.objective[cacheKey] then return E.cache.objective[cacheKey] end

    local translated = subject

    -- 1) 直接精确匹配（O(1) 哈希查找）
    if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[subject] then
      translated = EpochCN_ObjectiveNameData[subject]
    end

    if translated == subject and EpochCN_Overrides and EpochCN_Overrides.englishUnits and EpochCN_Overrides.englishUnits[subject] then
      translated = EpochCN_Overrides.englishUnits[subject]
    end

    -- 2) pfDB 反向索引查找（O(1)，替代原来的 O(N) 全量遍历）
    if translated == subject then
      BuildPfReverseIndex()
      if pfReverseIndex and pfReverseIndex[subject] then
        translated = pfReverseIndex[subject]
      end
    end

    -- 3) 部分匹配兜底（仅对仍未翻译的文本，且 Overrides 表极小）
    if translated == subject and EpochCN_Overrides and EpochCN_Overrides.englishUnits then
      for english, chinese in pairs(EpochCN_Overrides.englishUnits) do
        if string.find(subject, english, 1, true) then
          translated = PlainReplaceOnce(subject, english, chinese)
          break
        end
      end
    end

    SafeSetObjectiveCache(cacheKey, translated)
    return translated
  end

  local function TranslateObjectiveSuffix(suffix)
    if not suffix or suffix == "" then return "" end
    suffix = string.gsub(suffix, "%s*%((Complete)%)", " (完成)")
    suffix = string.gsub(suffix, "%s*%((Completed)%)", " (完成)")
    suffix = string.gsub(suffix, "%s*%((Done)%)", " (完成)")
    suffix = string.gsub(suffix, "%s*%((Failed)%)", " (失败)")
    return suffix
  end

  local function ReplaceKnownObjectiveName(text)
    if not text or not EpochCN_ObjectiveNameData then return text end
    local subject, rest = string.match(text, "^(.-)(:%s*[%-%d]+/[%-%d]+.*)$")
    if subject and rest then
      return TranslateObjectiveSubject(subject) .. rest
    end

    local checked = {}
    local index = GetObjectiveNameIndex()
    for token in string.gmatch(text, "[A-Za-z][A-Za-z'%-]+") do
      local candidates = index[token]
      if candidates then
        for _, pair in ipairs(candidates) do
          local english, chinese = pair[1], pair[2]
          if not checked[english] then
            checked[english] = true
            if string.find(text, english, 1, true) then
              return PlainReplaceOnce(text, english, chinese)
            end
          end
        end
      end
    end
    return text
  end

  -- 区域名称反向索引（英文→中文），延迟构建
  local zoneReverseIndex
  local zoneReverseBuilt = false

  local function BuildZoneReverseIndex()
    if zoneReverseBuilt then return end
    zoneReverseBuilt = true
    zoneReverseIndex = {
      ["Eastern Plaguelands"] = "东瘟疫之地",
      ["Western Plaguelands"] = "西瘟疫之地",
      ["Blackrock Depths"] = "黑石深渊",
      ["Blackrock Mountain"] = "黑石山",
      ["Blackrock Spire"] = "黑石塔",
      ["Scholomance"] = "通灵学院",
      ["Stratholme"] = "斯坦索姆",
    }
    if pfDB and pfDB["zones"] and pfDB["zones"]["enUS"] and pfDB["zones"]["loc"] then
      for id, name in pairs(pfDB["zones"]["enUS"]) do
        if pfDB["zones"]["loc"][id] and not zoneReverseIndex[name] then
          zoneReverseIndex[name] = pfDB["zones"]["loc"][id]
        end
      end
    end
  end

  local function TranslateHeader(title)
    if not title then return title end
    BuildZoneReverseIndex()
    return zoneReverseIndex[title] or title
  end

  local function TranslateQuestTitleText(text)
    if not text or text == "" then return text end
    local prefix, title = string.match(text, "^(%s*%[[^%]]+%]%s*)(.+)$")
    title = title or text
    local data = E:GetQuestData(E:GetQuestIDByTitle(title))
    if data and data[1] then
      return (prefix or "") .. data[1]
    end
    return text
  end

  local function ApplyQuestOfferText()
    local data = E:GetCurrentQuestData()
    if not data then return end

    -- 接任务面板文本（QuestInfoFrame / QuestDetailFrame）
    if data[1] and QuestInfoTitleHeader and QuestInfoTitleHeader.GetText and QuestInfoTitleHeader.SetText then
      local current = QuestInfoTitleHeader:GetText()
      local prefix = current and string.match(current, "^(%s*%[[^%]]+%]%s*)")
      QuestInfoTitleHeader:SetText((prefix or "") .. data[1])
    end
    if data[2] and QuestInfoObjectivesText and QuestInfoObjectivesText.SetText then
      QuestInfoObjectivesText:SetText(ReplacePlayerTokens(data[2]))
    end
    if data[3] and data[3] ~= "" and QuestInfoDescriptionText and QuestInfoDescriptionText.SetText then
      QuestInfoDescriptionText:SetText(ReplacePlayerTokens(data[3]))
    end

    -- 进度检查面板文本（QuestFrameProgressPanel）
    if data[1] and QuestProgressTitleText and QuestProgressTitleText.SetText then
      QuestProgressTitleText:SetText(data[1])
    end
    if data[3] and data[3] ~= "" and QuestProgressText and QuestProgressText.SetText then
      QuestProgressText:SetText(ReplacePlayerTokens(data[3]))
    end

    -- 交任务奖励面板文本（QuestFrameRewardPanel）
    if data[1] and QuestRewardTitleText and QuestRewardTitleText.SetText then
      QuestRewardTitleText:SetText(data[1])
    end
    if data[3] and data[3] ~= "" and QuestRewardText and QuestRewardText.SetText then
      QuestRewardText:SetText(ReplacePlayerTokens(data[3]))
    end
  end

  local function ApplyQuestChoiceButtons()
    for i = 1, 32 do
      local button = getglobal("QuestTitleButton" .. i)
      if button and button.GetText and button.SetText then
        local text = button:GetText()
        local translated = TranslateQuestTitleText(text)
        if translated and translated ~= text then button:SetText(translated) end
      end

      button = getglobal("GossipTitleButton" .. i)
      if button and button.GetText and button.SetText then
        local text = button:GetText()
        local translated = TranslateQuestTitleText(text)
        if translated and translated ~= text then button:SetText(translated) end
      end
    end
  end

  function E:LocalizeQuestOfferFrame()
    ApplyQuestOfferText()
    ApplyQuestChoiceButtons()
  end

  function E:TranslateObjective(text)
    if not text then return text end
    if E.cache.objective[text] then return E.cache.objective[text] end

    local translated = text

    -- 先做精确查找（O(1)），再做部分匹配（只匹配第一个后 break）
    if EpochCN_Overrides and EpochCN_Overrides.englishUnits then
      if EpochCN_Overrides.englishUnits[translated] then
        translated = EpochCN_Overrides.englishUnits[translated]
      else
        for english, chinese in pairs(EpochCN_Overrides.englishUnits) do
          if string.find(translated, english, 1, true) then
            translated = PlainReplaceOnce(translated, english, chinese)
            break
          end
        end
      end
    end

    translated = string.gsub(translated, "<class>", UnitClass and select(1, UnitClass("player")) or "")
    translated = string.gsub(translated, "<player>", UnitName and UnitName("player") or "")

    local subject, cur, need, suffixText = string.match(translated, "^(.-)%s+[Ss]lain:%s*([%-%d]+)/([%-%d]+)(.*)$")
    if subject then
      translated = "已杀死 " .. TranslateObjectiveSubject(subject) .. ": " .. cur .. "/" .. need .. TranslateObjectiveSuffix(suffixText)
    else
      subject, cur, need, suffixText = string.match(translated, "^(.-)%s+[Kk]illed:%s*([%-%d]+)/([%-%d]+)(.*)$")
      if subject then
        translated = "已击杀 " .. TranslateObjectiveSubject(subject) .. ": " .. cur .. "/" .. need .. TranslateObjectiveSuffix(suffixText)
      else
        subject, cur, need, suffixText = string.match(translated, "^(.-):%s*([%-%d]+)/([%-%d]+)(.*)$")
        if subject then
          translated = TranslateObjectiveSubject(subject) .. ": " .. cur .. "/" .. need .. TranslateObjectiveSuffix(suffixText)
        else
          local suffix = EpochCN_Glossary and EpochCN_Glossary.objectiveSuffix or {}
          for en, zh in pairs(suffix) do
            translated = string.gsub(translated, en, zh)
          end
          translated = string.gsub(translated, "%((Complete)%)", "(完成)")
          translated = string.gsub(translated, "%((Completed)%)", "(完成)")
          translated = string.gsub(translated, "%((Done)%)", "(完成)")
          translated = string.gsub(translated, "%((Failed)%)", "(失败)")
          translated = ReplaceKnownObjectiveName(translated)
        end
      end
    end

    translated = string.gsub(translated, "已杀死([^:]+):", "已杀死 %1:")
    translated = ReplacePlayerTokens(translated)

    SafeSetObjectiveCache(text, translated)
    return translated
  end

  function GetQuestLogQuestText()
    local text, objective = E.raw.GetQuestLogQuestText()
    local questLogIndex = GetQuestLogSelection()
    local _, _, _, _, _, _, _, _, id = E.raw.GetQuestLogTitle(questLogIndex)
    id = E:GetQuestID(questLogIndex, id)

    local data = E:GetQuestData(id)
    if data then
      objective = data[2] or objective
      text = data[3] or text
      text = ReplacePlayerTokens(text)
      objective = ReplacePlayerTokens(objective)
    end

    return text, objective
  end

  function GetQuestLogLeaderBoard(i, questLogIndex)
    local text, objectiveType, finished = E.raw.GetQuestLogLeaderBoard(i, questLogIndex)
    if not questLogIndex then questLogIndex = GetQuestLogSelection() end

    if objectiveType == "log" then
      local _, _, _, _, _, _, _, _, id = E.raw.GetQuestLogTitle(questLogIndex)
      id = E:GetQuestID(questLogIndex, id)
      local data = E:GetQuestData(id)
      if data and data[2] then text = data[2] end
    else
      text = E:TranslateObjective(text)
    end

    return text, objectiveType, finished
  end

  function GetQuestLogCompletionText(questLogIndex)
    local text = E.raw.GetQuestLogCompletionText(questLogIndex)
    questLogIndex = questLogIndex or GetQuestLogSelection()
    local _, _, _, _, _, _, _, _, id = E.raw.GetQuestLogTitle(questLogIndex)
    id = E:GetQuestID(questLogIndex, id)

    local data = E:GetQuestData(id)
    if data and data[2] then text = data[2] end
    return ReplacePlayerTokens(text)
  end

  function GetQuestLogTitle(index)
    local title, level, tag, group, header, collapsed, complete, daily, id = E.raw.GetQuestLogTitle(index)
    if header then
      return TranslateHeader(title), level, tag, group, header, collapsed, complete, daily, id
    end

    id = E:GetQuestID(index, id)
    local data = E:GetQuestData(id)
    if data and data[1] then title = data[1] end
    return title, level, tag, group, header, collapsed, complete, daily, id
  end

  function GetAbandonQuestName()
    local text = E.raw.GetAbandonQuestName()
    local questLogIndex = GetQuestLogSelection()
    local _, _, _, _, _, _, _, _, id = E.raw.GetQuestLogTitle(questLogIndex)
    id = E:GetQuestID(questLogIndex, id)

    local data = E:GetQuestData(id)
    if data and data[1] then text = data[1] end
    return text
  end

  -- ============================================================
  -- NPC 任务对话框汉化（接任务/进度/交任务界面）
  -- WoW QuestFrame 调用的是与 QuestLog 完全不同的四个全局函数，
  -- 必须在此单独 Hook。
  -- ============================================================

  -- 使用 CaptureRawAPI 阶段保存的原始函数，避免捕获 pfQuest 的 hook 版本
  local origGetTitleText    = E.raw.GetTitleText    or GetTitleText
  local origGetQuestText    = E.raw.GetQuestText    or GetQuestText
  local origGetProgressText = E.raw.GetProgressText or GetProgressText
  local origGetRewardText   = E.raw.GetRewardText   or GetRewardText
  local origGetGreetingText = E.raw.GetGreetingText or GetGreetingText

  -- 对话框当前展示的任务 ID（由 GetTitleText 解析后缓存）
  local dialogQuestID = nil

  -- 解析当前对话框任务 ID
  -- 优先 GetQuestID()（WotLK 原生 API，最可靠），
  -- 其次 questIDByTitle 映射（英/中文均支持），
  -- 最后扫任务日志（用于在途任务交任务界面）
  local function ResolveDialogQuestID(title)
    if not title or title == "" then return nil end
    -- 1) 最可靠：WotLK GetQuestID() 直接返回当前对话框任务 ID
    if E.raw.GetCurrentQuestID then
      local ok, id = pcall(E.raw.GetCurrentQuestID)
      if ok and tonumber(id) and tonumber(id) > 0 then return tonumber(id) end
    end
    -- 2) questIDByTitle 映射（含英文标题，由 BuildLookupTables 从 pfDB 注册）
    if E.questIDByTitle then
      local id = E.questIDByTitle[title]
      if id then return id end
      if E.NormalizeQuestTitle then
        local norm = E:NormalizeQuestTitle(title)
        if norm and norm ~= "" and E.questIDByTitle[norm] then return E.questIDByTitle[norm] end
      end
    end
    -- 3) 遍历任务日志（交任务时对话框标题与日志原始英文标题一致）
    if GetNumQuestLogEntries then
      local n = GetNumQuestLogEntries()
      for i = 1, n do
        local t, _, _, _, isHeader, _, _, _, rawID = E.raw.GetQuestLogTitle(i)
        if not isHeader and t == title then return E:GetQuestID(i, rawID) end
      end
    end
    return nil
  end

  -- 替换任务标题（用于 QuestFrame 顶部标题行）
  function GetTitleText()
    local rawTitle = origGetTitleText and origGetTitleText() or ""
    dialogQuestID = ResolveDialogQuestID(rawTitle)
    if dialogQuestID then
      local data = E:GetQuestData(dialogQuestID)
      if data and data[1] and data[1] ~= "" then return data[1] end
    end
    return rawTitle
  end

  -- 替换任务描述（NPC 接任务时的描述文本）
  function GetQuestText()
    local engText = origGetQuestText and origGetQuestText() or ""
    if dialogQuestID then
      local data = E:GetQuestData(dialogQuestID)
      if data and data[3] and data[3] ~= "" then return ReplacePlayerTokens(data[3]) end
    end
    return engText
  end

  -- 替换进度文本（玩家持有任务但未完成时 NPC 说的话）
  -- GetProgressText 不保证在 GetTitleText 之后调用，需独立解析 ID
  function GetProgressText()
    local engText = origGetProgressText and origGetProgressText() or ""
    local id = dialogQuestID
    if not id and E.raw.GetCurrentQuestID then
      local ok, v = pcall(E.raw.GetCurrentQuestID)
      if ok and tonumber(v) and tonumber(v) > 0 then id = tonumber(v) end
    end
    if id then
      local data = E:GetQuestData(id)
      if data and data[3] and data[3] ~= "" then return ReplacePlayerTokens(data[3]) end
    end
    return engText
  end

  -- 替换奖励/完成文本（交还任务时 NPC 说的话）
  function GetRewardText()
    local engText = origGetRewardText and origGetRewardText() or ""
    local id = dialogQuestID
    if not id and E.raw.GetCurrentQuestID then
      local ok, v = pcall(E.raw.GetCurrentQuestID)
      if ok and tonumber(v) and tonumber(v) > 0 then id = tonumber(v) end
    end
    if id then
      local data = E:GetQuestData(id)
      if data and data[3] and data[3] ~= "" then return ReplacePlayerTokens(data[3]) end
    end
    return engText
  end

  -- 替换问候语（NPC 同时有多个任务时的问候文本，无翻译则保持原文）
  function GetGreetingText()
    return origGetGreetingText and origGetGreetingText() or ""
  end

  local refreshFrame = CreateFrame("Frame")
  local refreshPending = false
  local function ScheduleQuestOfferRefresh()
    if refreshPending then return end
    refreshPending = true
    refreshFrame:Show()
  end
  refreshFrame:Hide()
  refreshFrame:SetScript("OnUpdate", function(self)
    self:Hide()
    refreshPending = false
    if E.LocalizeQuestOfferFrame then E:LocalizeQuestOfferFrame() end
  end)

  -- 接任务面板
  if QuestFrame and QuestFrame.HookScript then
    QuestFrame:HookScript("OnShow", ScheduleQuestOfferRefresh)
  end
  if QuestInfoFrame and QuestInfoFrame.HookScript then
    QuestInfoFrame:HookScript("OnShow", ScheduleQuestOfferRefresh)
  end
  -- 进度检查面板
  if QuestFrameProgressPanel and QuestFrameProgressPanel.HookScript then
    QuestFrameProgressPanel:HookScript("OnShow", ScheduleQuestOfferRefresh)
  end
  -- 交任务奖励面板
  if QuestFrameRewardPanel and QuestFrameRewardPanel.HookScript then
    QuestFrameRewardPanel:HookScript("OnShow", ScheduleQuestOfferRefresh)
  end
  if hooksecurefunc then
    if QuestFrame_ShowQuestDetails  then hooksecurefunc("QuestFrame_ShowQuestDetails",  ScheduleQuestOfferRefresh) end
    if QuestFrame_ShowQuestOffer    then hooksecurefunc("QuestFrame_ShowQuestOffer",    ScheduleQuestOfferRefresh) end
    if QuestFrame_ShowQuestComplete then hooksecurefunc("QuestFrame_ShowQuestComplete", ScheduleQuestOfferRefresh) end
    if QuestFrame_ShowQuestProgress then hooksecurefunc("QuestFrame_ShowQuestProgress", ScheduleQuestOfferRefresh) end
    if QuestFrameGreetingPanel_OnShow then hooksecurefunc("QuestFrameGreetingPanel_OnShow", ScheduleQuestOfferRefresh) end
  end
end)
