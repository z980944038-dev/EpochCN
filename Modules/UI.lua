EpochCN:RegisterModule("UI", function(E)
  if not EpochCNDB.ui then return end

  local mapTranslations = EpochCN_Overrides and EpochCN_Overrides.maps or {}

  -- ============================================================
  -- 节流调度器：最多每 1 秒执行一次全量扫描
  -- 如果冷却期内收到请求，延迟到冷却结束后执行（不丢弃）
  -- ============================================================
  local pendingLocalize = false
  local lastLocalizeTime = 0
  local LOCALIZE_COOLDOWN = 1.0

  local scheduler = CreateFrame("Frame")
  scheduler:Hide()
  scheduler:SetScript("OnUpdate", function(self, elapsed)
    local now = GetTime()
    if now - lastLocalizeTime < LOCALIZE_COOLDOWN then return end
    self:Hide()
    pendingLocalize = false
    lastLocalizeTime = now
    E:LocalizeUI()
  end)

  local function ScheduleLocalize()
    if pendingLocalize then return end
    pendingLocalize = true
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
      translateTextCache = {}
      translateTextCacheSize = 0
    end
    translateTextCache[text] = result or false
    translateTextCacheSize = translateTextCacheSize + 1

    return result or text
  end

  local function SetText(name, text)
    local widget = getglobal(name)
    if widget and widget.SetText then widget:SetText(text) end
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
  local safeFrameCache = {}
  local unsafeFrameCache = {}

  local function IsUnsafeFrame(frame)
    local name = frame and frame.GetName and frame:GetName()
    if not name then return false end
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
  local function TranslateFontStrings(frame, depth)
    if not frame then return end
    if depth and depth > 6 then return end  -- 降低深度限制
    if IsUnsafeFrame(frame) then return end
    -- 跳过不可见的 frame（大幅减少无效遍历）
    if frame.IsVisible and not frame:IsVisible() then return end
    depth = depth or 0

    if frame.HookScript and not frame.EpochCNUIPatched then
      frame.EpochCNUIPatched = true
      pcall(frame.HookScript, frame, "OnShow", ScheduleLocalize)
    end

    if frame.GetRegions then
      for _, region in pairs({ frame:GetRegions() }) do
        if region and region.GetText and region.SetText then
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
        TranslateFontStrings(child, depth + 1)
      end
    end
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

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("ADDON_LOADED")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("WORLD_MAP_UPDATE")
  frame:RegisterEvent("CHARACTER_POINTS_CHANGED")
  frame:RegisterEvent("LEARNED_SPELL_IN_TAB")
  frame:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
  frame:RegisterEvent("SKILL_LINES_CHANGED")
  frame:RegisterEvent("SPELLS_CHANGED")
  frame:RegisterEvent("UPDATE_FACTION")
  -- 已移除高频战斗事件：UNIT_DAMAGE, UNIT_RANGEDDAMAGE, UNIT_RESISTANCES, UNIT_STATS, COMBAT_RATING_UPDATE
  frame:SetScript("OnEvent", function()
    ScheduleLocalize()
  end)

  for _, name in pairs(targets) do
    local target = getglobal(name)
    if target and target.HookScript then
      target:HookScript("OnShow", function()
        -- 清空翻译缓存：frame 内容可能已变化
        translateTextCache = {}
        translateTextCacheSize = 0
        ScheduleLocalize()
      end)
    end
  end

  E:LocalizeUI()
end)
