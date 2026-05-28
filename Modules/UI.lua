EpochCN:RegisterModule("UI", function(E)
  if not EpochCNDB.ui then return end

  local mapTranslations = EpochCN_Overrides and EpochCN_Overrides.maps or {}

  -- ============================================================
  -- 轻量调度器：同帧/短时间内的多次请求合并到下一帧执行
  -- 避免 Blizzard 先写英文、插件 1 秒后才补中文造成的页面跳字
  -- ============================================================
  local pendingLocalize = false
  local lastLocalizeTime = 0
  local localizeDelay = 0
  local localizeElapsed = 0
  local LOCALIZE_COALESCE_DELAY = 0.02
  local LOCALIZE_MIN_INTERVAL = 0.05

  local scheduler = CreateFrame("Frame")
  scheduler:Hide()
  scheduler:SetScript("OnUpdate", function(self, elapsed)
    if not pendingLocalize then
      self:Hide()
      return
    end

    localizeElapsed = localizeElapsed + elapsed
    if localizeElapsed < localizeDelay then return end

    local now = GetTime()
    if now - lastLocalizeTime < LOCALIZE_MIN_INTERVAL then return end

    self:Hide()
    pendingLocalize = false
    localizeDelay = 0
    localizeElapsed = 0
    lastLocalizeTime = now
    E:LocalizeUI()
  end)

  local function ScheduleLocalize(immediate)
    if immediate then
      localizeDelay = 0
    elseif not pendingLocalize then
      localizeDelay = LOCALIZE_COALESCE_DELAY
    end

    if pendingLocalize then return end
    pendingLocalize = true
    localizeElapsed = 0
    scheduler:Show()
  end

  -- ============================================================
  -- 文本翻译（O(1) 哈希查找，不含正则）
  -- ============================================================
  local function JoinLines(text)
    return E.NormalizeDisplayText and E:NormalizeDisplayText(text) or text
  end

  local function TranslateBaseText(text)
    if not text or text == "" then return nil end
    local normalized = JoinLines(text)
    local glossaryText = EpochCN_Glossary and EpochCN_Glossary.text or {}

    return (E.localizedTextByRaw and (E.localizedTextByRaw[text] or E.localizedTextByRaw[normalized]))
      or glossaryText[text]
      or glossaryText[normalized]
      or (TPCN_GlobalData and (TPCN_GlobalData[text] or TPCN_GlobalData[normalized]))
      or mapTranslations[text]
      or mapTranslations[normalized]
  end

  local function TranslateFormattedText(text)
    local normalized = JoinLines(text)
    local translated = TranslateBaseText(normalized)
    if translated then return translated end

    local label, suffix = string.match(normalized, "^(.-)(:)$")
    translated = label and TranslateBaseText(label)
    if translated then return translated .. suffix end

    local value
    label, value = string.match(normalized, "^(.-):%s*(.+)$")
    translated = label and TranslateBaseText(label)
    if translated then return translated .. ": " .. value end

    label, suffix = string.match(normalized, "^(.-)(：)$")
    translated = label and TranslateBaseText(label)
    if translated then return translated .. suffix end

    local base, rank = string.match(normalized, "^(.-)%s+[Rr]ank%s+(%d+)$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n等级 " .. rank end

    rank = string.match(normalized, "^[Rr]ank%s+(%d+)$")
    if rank then return "等级 " .. rank end

    local page = string.match(normalized, "^[Pp]age%s+(%d+)$")
    if page then return "第 " .. page .. " 页" end

    base = string.match(normalized, "^(.-)%s+[Pp]assive$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n被动" end

    base = string.match(normalized, "^(.-)%s+[Aa]rtisan$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n专家级" end

    base = string.match(normalized, "^(.-)%s+[Jj]ourneyman$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n中级" end

    base = string.match(normalized, "^(.-)%s+[Ee]xpert$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n高级" end

    base = string.match(normalized, "^(.-)%s+[Rr]acial%s+[Pp]ass%.%.%.$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. "\n种族被动" end

    local level, spec, class = string.match(normalized, "^[Ll]evel%s+(%d+)%s+(.+)%s+([%a]+)$")
    if level and spec and class then
      local specText = TranslateBaseText(spec) or spec
      local classText = TranslateBaseText(class) or class
      return "等级 " .. level .. " " .. specText .. classText
    end

    base, value = string.match(normalized, "^(.-)%s+([%-%d]+%s*/%s*[%-%d]+.*)$")
    translated = base and TranslateBaseText(base)
    if translated then return translated .. " " .. value end

    return nil
  end

  -- 翻译结果缓存：避免对同一文本反复执行 10+ 次 string.match
  local translateTextCache = {}
  local translateTextCacheSize = 0
  local TRANSLATE_TEXT_CACHE_MAX = 1024

  local function TranslateText(text)
    if not text or text == "" then return text end

    -- 快速缓存查询
    local cached = translateTextCache[text]
    if cached ~= nil then
      return cached or text  -- false 表示无翻译
    end

    local result = TranslateBaseText(text) or TranslateFormattedText(text)

    -- 存入缓存
    if translateTextCacheSize >= TRANSLATE_TEXT_CACHE_MAX then
      -- 淘汰约一半的条目而非全清，减少冷启动性能抖动
      local evictTarget = math.floor(TRANSLATE_TEXT_CACHE_MAX / 2)
      local evicted = 0
      for k in pairs(translateTextCache) do
        translateTextCache[k] = nil
        evicted = evicted + 1
        if evicted >= evictTarget then break end
      end
      translateTextCacheSize = translateTextCacheSize - evicted
    end
    translateTextCache[text] = result or false
    translateTextCacheSize = translateTextCacheSize + 1

    return result or text
  end

  local function SetText(name, text)
    local widget = getglobal(name)
    if widget and widget.SetText then widget:SetText(text) end
  end

  local function ResetTranslateCache()
    -- 复用同一表对象（减少 GC 碎片），WoW 3.3.5 提供全局 table.wipe
    if table.wipe then
      table.wipe(translateTextCache)
    else
      translateTextCache = {}
    end
    translateTextCacheSize = 0
  end

  -- ============================================================
  -- 不安全框架排除列表（哈希 set，避免 18 次 string.find）
  -- ============================================================
  local unsafeFramePrefixes = {
    "ActionButton", "MultiBar", "BonusActionButton", "PetActionButton",
    "ShapeshiftButton", "PossessButton", "MultiCast", "VehicleMenuBarActionButton",
    "SpellButton", "CharacterMicroButton", "SpellbookMicroButton", "TalentMicroButton",
    "AchievementMicroButton", "QuestLogMicroButton", "GuildMicroButton", "PVPMicroButton",
    "LFDMicroButton", "EJMicroButton", "MainMenuMicroButton", "HelpMicroButton",
    "MainMenuBar",
  }
  -- 已扫描过的安全 frame name 缓存
  local unsafeFrameNames = {
    WorldMapButton = true,
  }
  local safeFrameCache = {}
  local unsafeFrameCache = {}

  local function IsUnsafeFrame(frame)
    local name = frame and frame.GetName and frame:GetName()
    if not name then return false end
    if unsafeFrameNames[name] then return true end
    if safeFrameCache[name] then return false end
    if unsafeFrameCache[name] then return true end

    for _, prefix in ipairs(unsafeFramePrefixes) do
      if string.sub(name, 1, string.len(prefix)) == prefix then
        unsafeFrameCache[name] = true
        return true
      end
    end
    safeFrameCache[name] = true
    return false
  end

  -- ============================================================
  -- TranslateFontStrings：只扫描**可见**frame，减少无效遍历
  -- ============================================================
  local LocalizeFrameNow
  local ApplyTranslatedFontString
  local HookDynamicFontString
  local HookDynamicFrameText

  local function HookScrollRefreshFrame(frame)
    if not frame or not frame.HookScript or frame.EpochCNScrollRefreshHooked then return end
    local name = frame.GetName and frame:GetName()
    if not name or not string.find(name, "Scroll", 1, true) then return end

    frame.EpochCNScrollRefreshHooked = true
    local function RefreshAfterScroll(self)
      ResetTranslateCache()
      LocalizeFrameNow((self and self.GetParent and self:GetParent()) or self)
      ScheduleLocalize(true)
    end

    pcall(frame.HookScript, frame, "OnVerticalScroll", RefreshAfterScroll)
    pcall(frame.HookScript, frame, "OnMouseWheel", RefreshAfterScroll)
    pcall(frame.HookScript, frame, "OnValueChanged", RefreshAfterScroll)
    pcall(frame.HookScript, frame, "OnClick", RefreshAfterScroll)
  end

  local function TranslateFontStrings(frame, depth, visited)
    if not frame then return end
    if depth and depth > 6 then return end  -- 降低深度限制
    visited = visited or {}
    if visited[frame] then return end
    visited[frame] = true

    if IsUnsafeFrame(frame) then return end
    -- 跳过不可见的 frame（大幅减少无效遍历）
    if frame.IsVisible and not frame:IsVisible() then return end
    depth = depth or 0

    if frame.HookScript and not frame.EpochCNUIPatched then
      frame.EpochCNUIPatched = true
      pcall(frame.HookScript, frame, "OnShow", function(self)
        LocalizeFrameNow(self)
      end)
    end
    HookScrollRefreshFrame(frame)

    if frame.GetRegions then
      for _, region in pairs({ frame:GetRegions() }) do
        if region and region.GetText and region.SetText then
          HookDynamicFontString(region)
          local text = region:GetText()
          if text and text ~= "" then
            local translated = TranslateText(text)
            if translated and translated ~= text then
              region:SetText(translated)
            end
          end
        end
      end
    end

    if frame.GetChildren then
      for _, child in pairs({ frame:GetChildren() }) do
        TranslateFontStrings(child, depth + 1, visited)
      end
    end
  end

  LocalizeFrameNow = function(frame)
    if not frame or IsUnsafeFrame(frame) then return end
    HookDynamicFrameText(frame)
    TranslateFontStrings(frame)
  end

  local targets = {
    "AchievementFrame",
    "AuctionFrame",
    "BankFrame",
    "BarberShopFrame",
    "BattlefieldFrame",
    "CalendarFrame",
    "CharacterFrame",
    "ChatConfigFrame",
    "FriendsFrame",
    "GameMenuFrame",
    "GMSurveyFrame",
    "GuildBankFrame",
    "HelpFrame",
    "InspectFrame",
    "InterfaceOptionsFrame",
    "ItemSocketingFrame",
    "KeyBindingFrame",
    "LFDParentFrame",
    "MacroFrame",
    "MerchantFrame",
    "PVPFrame",
    "PlayerTalentFrame",
    "ReputationFrame",
    "QuestFrame",
    "QuestLogFrame",
    "RaidFrame",
    "SkillFrame",
    "SpellBookFrame",
    "TaxiFrame",
    "TimeManagerFrame",
    "TokenFrame",
    "TradeSkillFrame",
    "VideoOptionsFrame",
    "AudioOptionsFrame",
    "WorldMapFrame",
  }

  local characterTabTextMap = {
    ["Abilities"] = "技能",
    ["Character"] = "装备",
    ["Currency"] = "货币",
    ["Honor"] = "荣誉",
    ["Pet"] = "宠物",
    ["Reputation"] = "声望",
    ["Skills"] = "技能",
  }

  local function LocalizeCharacterTabs()
    for i = 1, 8 do
      local tab = getglobal("CharacterFrameTab" .. i)
      if tab and tab.GetText and tab.SetText and (not tab.IsShown or tab:IsShown()) then
        local text = tab:GetText()
        local translated = characterTabTextMap[text] or TranslateText(text)
        if translated and translated ~= text then
          tab:SetText(translated)
        end
      end
    end
  end

  ApplyTranslatedFontString = function(fontString, text)
    if not fontString or fontString.EpochCNSettingText then return end
    if type(text) ~= "string" or text == "" then return end

    local translated = TranslateText(text)
    if translated and translated ~= text then
      fontString.EpochCNSettingText = true
      fontString:SetText(translated)
      fontString.EpochCNSettingText = false
    end
  end

  HookDynamicFontString = function(fontString)
    if not fontString or fontString.EpochCNDynamicTextHooked then return end
    if not fontString.GetText or not fontString.SetText then return end

    fontString.EpochCNDynamicTextHooked = true
    if hooksecurefunc then
      pcall(hooksecurefunc, fontString, "SetText", function(self, text)
        ApplyTranslatedFontString(self, text)
      end)
    end

    ApplyTranslatedFontString(fontString, fontString:GetText())
  end

  HookDynamicFrameText = function(frame, depth, visited)
    if not frame or (depth and depth > 8) then return end
    if IsUnsafeFrame(frame) then return end
    visited = visited or {}
    if visited[frame] then return end
    visited[frame] = true
    depth = depth or 0

    if frame.GetRegions then
      for _, region in pairs({ frame:GetRegions() }) do
        HookDynamicFontString(region)
      end
    end

    if frame.GetChildren then
      for _, child in pairs({ frame:GetChildren() }) do
        HookDynamicFrameText(child, depth + 1, visited)
      end
    end
  end

  local function LocalizeSkillFrameNow()
    local frame = SkillFrame or getglobal("SkillFrame")
    if not frame then return end
    HookDynamicFrameText(frame)
    TranslateFontStrings(frame)
  end

  local function LocalizeSkillFrameSoon()
    ResetTranslateCache()
    LocalizeSkillFrameNow()
    ScheduleLocalize(true)
  end

  local function HookSkillScrollFrame()
    local frameNames = {
      "SkillFrameScrollFrame",
      "SkillFrameScrollFrameScrollBar",
      "SkillFrameScrollFrameScrollBarScrollUpButton",
      "SkillFrameScrollFrameScrollBarScrollDownButton",
    }

    for _, name in pairs(frameNames) do
      local frame = getglobal(name)
      if frame and frame.HookScript and not frame.EpochCNSkillScrollHooked then
        frame.EpochCNSkillScrollHooked = true
        pcall(frame.HookScript, frame, "OnValueChanged", LocalizeSkillFrameSoon)
        pcall(frame.HookScript, frame, "OnVerticalScroll", LocalizeSkillFrameSoon)
        pcall(frame.HookScript, frame, "OnMouseWheel", LocalizeSkillFrameSoon)
        pcall(frame.HookScript, frame, "OnClick", LocalizeSkillFrameSoon)
      end
    end
  end

  local function LocalizeCharacterPanels()
    LocalizeCharacterTabs()
    HookSkillScrollFrame()
    LocalizeSkillFrameNow()

    for _, name in pairs({ "CharacterFrame", "SkillFrame", "ReputationFrame" }) do
      local frame = getglobal(name)
      if frame and (not frame.IsVisible or frame:IsVisible()) then
        TranslateFontStrings(frame)
      end
    end
  end

  function E:LocalizeUI()
    local glossary = EpochCN_Glossary or {}
    for name, text in pairs(glossary.ui or {}) do SetText(name, text) end
    for name, text in pairs(glossary.buttons or {}) do SetText(name, text) end

    if WorldMapFrameAreaLabel and WorldMapFrameAreaLabel.GetText then
      local areaText = WorldMapFrameAreaLabel:GetText()
      if areaText and mapTranslations[areaText] then
        WorldMapFrameAreaLabel:SetText(mapTranslations[areaText])
      end
    end

    for _, name in pairs(targets) do
      local frame = getglobal(name)
      -- 只扫描存在且可见的 frame
      if frame and frame.IsVisible and frame:IsVisible() then
        TranslateFontStrings(frame)
      end
    end

    LocalizeCharacterTabs()
  end

  -- 任务日志更新时仅翻译任务相关 frame，不全量扫描所有 UI
  local questTargets = { "QuestFrame", "QuestLogFrame" }
  local function LocalizeQuestFrames()
    local glossary = EpochCN_Glossary or {}
    for name, text in pairs(glossary.ui or {}) do SetText(name, text) end
    for name, text in pairs(glossary.buttons or {}) do SetText(name, text) end
    for _, name in pairs(questTargets) do
      local frame = getglobal(name)
      if frame then TranslateFontStrings(frame) end
    end
  end

  if QuestLog_Update then
    hooksecurefunc("QuestLog_Update", LocalizeQuestFrames)
  end

  if QuestLog_UpdateQuestDetails then
    hooksecurefunc("QuestLog_UpdateQuestDetails", LocalizeQuestFrames)
  end

  if CharacterFrame_ShowSubFrame then
    hooksecurefunc("CharacterFrame_ShowSubFrame", function()
      LocalizeCharacterPanels()
    end)
  end

  if SkillFrame_Update then
    hooksecurefunc("SkillFrame_Update", function()
      LocalizeCharacterPanels()
    end)
  end

  if SkillFrame_OnVerticalScroll then
    hooksecurefunc("SkillFrame_OnVerticalScroll", LocalizeSkillFrameSoon)
  end

  if SkillFrame_OnShow then
    hooksecurefunc("SkillFrame_OnShow", LocalizeSkillFrameSoon)
  end

  if ReputationFrame_Update then
    hooksecurefunc("ReputationFrame_Update", function()
      LocalizeCharacterPanels()
    end)
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("ADDON_LOADED")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("WORLD_MAP_UPDATE")
  frame:RegisterEvent("CHARACTER_POINTS_CHANGED")
  frame:RegisterEvent("LEARNED_SPELL_IN_TAB")
  frame:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
  frame:RegisterEvent("SKILL_LINES_CHANGED")
  frame:RegisterEvent("SPELLS_CHANGED")
  -- 已移除 UPDATE_FACTION：声望变化在战斗中过于频繁，依赖 ReputationFrame
  -- 的 OnShow hook 做按需扫描即可
  -- 已移除高频战斗事件：UNIT_DAMAGE, UNIT_RANGEDDAMAGE, UNIT_RESISTANCES, UNIT_STATS, COMBAT_RATING_UPDATE
  frame:SetScript("OnEvent", function()
    HookSkillScrollFrame()
    ScheduleLocalize()
  end)

  for _, name in pairs(targets) do
    local target = getglobal(name)
    if target and target.HookScript then
      target:HookScript("OnShow", function(self)
        -- 清空翻译缓存：frame 内容可能已变化
        ResetTranslateCache()
        LocalizeFrameNow(self)
        ScheduleLocalize(true)
      end)
    end
  end

  for _, name in pairs({ "CharacterFrame", "SkillFrame", "ReputationFrame" }) do
    local target = getglobal(name)
    if target and target.HookScript then
      target:HookScript("OnShow", function()
        ResetTranslateCache()
        LocalizeCharacterPanels()
        ScheduleLocalize(true)
      end)
    end
  end

  HookSkillScrollFrame()
  E:LocalizeUI()
end)
