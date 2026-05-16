EpochCN:RegisterModule("Settings", function(E)
  if not EpochCNDB.settingsPanel then return end

  local panel
  local aboutPanel
  local minimapButton
  local minimapMenu
  local reloadNotice
  local loginBroadcastDone = false

  local function TranslateText(text)
    if not text or text == "" then return text end
    if E.localizedTextByRaw and E.localizedTextByRaw[text] then
      return E.localizedTextByRaw[text]
    end
    if EpochCN_Overrides and EpochCN_Overrides.maps and EpochCN_Overrides.maps[text] then
      return EpochCN_Overrides.maps[text]
    end
    return text
  end

  local function IsUnsafeFrame(frame)
    local name = frame and frame.GetName and frame:GetName()
    if not name then return end

    return string.find(name, "^ActionButton")
      or string.find(name, "^MultiBar")
      or string.find(name, "^BonusActionButton")
      or string.find(name, "^PetActionButton")
      or string.find(name, "^ShapeshiftButton")
      or string.find(name, "^PossessButton")
      or string.find(name, "^MultiCast")
      or string.find(name, "^VehicleMenuBarActionButton")
      or string.find(name, "^SpellButton")
      or string.find(name, "^CharacterMicroButton")
      or string.find(name, "^SpellbookMicroButton")
      or string.find(name, "^TalentMicroButton")
      or string.find(name, "^AchievementMicroButton")
      or string.find(name, "^QuestLogMicroButton")
      or string.find(name, "^GuildMicroButton")
      or string.find(name, "^PVPMicroButton")
      or string.find(name, "^LFDMicroButton")
      or string.find(name, "^EJMicroButton")
      or string.find(name, "^MainMenuMicroButton")
      or string.find(name, "^HelpMicroButton")
      or string.find(name, "^MainMenuBar")
      or name == "SpellBookFrame"
  end

  function E:TranslateFrameText(frame, depth)
    if not frame or depth and depth > 8 then return end
    if IsUnsafeFrame(frame) then return end
    depth = depth or 0

    if frame.GetRegions then
      for _, region in pairs({ frame:GetRegions() }) do
        if region and region.GetText and region.SetText then
          local text = region:GetText()
          local translated = TranslateText(text)
          if translated and translated ~= text then
            region:SetText(translated)
          end
        end
      end
    end

    if frame.GetChildren then
      for _, child in pairs({ frame:GetChildren() }) do
        E:TranslateFrameText(child, depth + 1)
      end
    end
  end

  local targets = {
    "GameMenuFrame",
    "InterfaceOptionsFrame",
    "VideoOptionsFrame",
    "AudioOptionsFrame",
    "SoundOptionsFrame",
    "KeyBindingFrame",
    "MacOptionsFrame",
    "HelpFrame",
    "Graphics_RightQuality",
    "PlayerTalentFrame",
    "InspectTalentFrame",
  }

  local function TranslateKnownFrames()
    for _, name in pairs(targets) do
      local frame = getglobal(name)
      if frame then E:TranslateFrameText(frame) end
    end
  end

  local function MarkReload()
    if reloadNotice then reloadNotice:Show() end
  end

  local function CreateCheck(parent, label, key, tooltip, x, y, onChanged)
    local check = CreateFrame("CheckButton", nil, parent, "OptionsCheckButtonTemplate")
    check:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    check:SetChecked(EpochCNDB[key])
    check.key = key

    local text = check:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    text:SetPoint("LEFT", check, "RIGHT", 2, 1)
    text:SetText(label)
    check.label = text

    check:SetScript("OnClick", function(self)
      EpochCNDB[self.key] = self:GetChecked() and true or false
      if onChanged then onChanged(EpochCNDB[self.key]) end
      MarkReload()
    end)

    check:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      GameTooltip:SetText(label, 1, 0.82, 0)
      if tooltip then GameTooltip:AddLine(tooltip, 1, 1, 1, true) end
      GameTooltip:Show()
    end)
    check:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return check
  end

  -- 嵌套设置：状态存储在 EpochCNDB[parentKey][childKey]，避免污染顶层
  local function CreateNestedCheck(parent, label, parentKey, childKey, tooltip, x, y, onChanged, defaultTrue)
    local check = CreateFrame("CheckButton", nil, parent, "OptionsCheckButtonTemplate")
    check:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    EpochCNDB[parentKey] = EpochCNDB[parentKey] or {}
    local current = EpochCNDB[parentKey][childKey]
    if current == nil and defaultTrue then current = true end
    check:SetChecked(current and true or false)
    check.parentKey = parentKey
    check.childKey = childKey

    local text = check:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    text:SetPoint("LEFT", check, "RIGHT", 2, 1)
    text:SetText(label)
    check.label = text

    check:SetScript("OnClick", function(self)
      EpochCNDB[self.parentKey] = EpochCNDB[self.parentKey] or {}
      local enabled = self:GetChecked() and true or false
      EpochCNDB[self.parentKey][self.childKey] = enabled
      if onChanged then onChanged(enabled) end
      MarkReload()
    end)

    check:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      GameTooltip:SetText(label, 1, 0.82, 0)
      if tooltip then GameTooltip:AddLine(tooltip, 1, 1, 1, true) end
      GameTooltip:Show()
    end)
    check:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return check
  end

  local function CreateButton(parent, label, width, x, y, onClick)
    local button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    button:SetSize(width, 24)
    button:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    button:SetText(label)
    button:SetScript("OnClick", onClick)
    return button
  end

  local function CreateHeader(parent, text, x, y)
    local fs = parent:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    fs:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    fs:SetText(text)
    return fs
  end

  local function CreateSection(parent, title, x, y, w, h)
    local section = CreateFrame("Frame", nil, parent)
    section:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    section:SetSize(w, h)
    section:SetBackdrop({
      bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
      edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
      tile = true, tileSize = 16, edgeSize = 12,
      insets = { left = 3, right = 3, top = 3, bottom = 3 },
    })
    if section.SetBackdropColor then
      section:SetBackdropColor(0.02, 0.08, 0.06, 0.78)
    end
    if section.SetBackdropBorderColor then
      section:SetBackdropBorderColor(0.25, 0.45, 0.38, 0.85)
    end

    local header = section:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    header:SetPoint("TOPLEFT", section, "TOPLEFT", 12, -10)
    header:SetText("|cffffd200" .. title .. "|r")
    section.header = header
    return section
  end

  local function CreatePage(parent)
    local page = CreateFrame("Frame", nil, parent)
    page:SetPoint("TOPLEFT", parent, "TOPLEFT", 144, -72)
    page:SetSize(448, 414)
    page:Hide()
    return page
  end

  local function CreateNavButton(parent, label, x, y, onClick)
    local button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    button:SetSize(104, 26)
    button:SetPoint("TOPLEFT", parent, "TOPLEFT", x, y)
    button:SetText(label)
    button:SetScript("OnClick", onClick)
    return button
  end

  local function CreateSettingsPanel()
    if panel then return panel end

    panel = CreateFrame("Frame", "EpochCNSettingsFrame", UIParent)
    panel:SetSize(620, 560)
    panel:SetPoint("CENTER")
    panel:SetFrameStrata("DIALOG")
    panel:SetMovable(true)
    panel:EnableMouse(true)
    panel:RegisterForDrag("LeftButton")
    panel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    panel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    panel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true,
      tileSize = 32,
      edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    panel:Hide()

    local title = panel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", panel, "TOPLEFT", 28, -20)
    title:SetText("|cff33ffccEpoch|cffffffffCN|r 设置中心")

    local subtitle = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    subtitle:SetPoint("TOPLEFT", panel, "TOPLEFT", 28, -42)
    subtitle:SetText("按模块管理汉化、地图标记、社交协作与维护工具。")

    local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -5, -5)

    local version = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    version:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -34, -43)
    version:SetText("版本 " .. tostring(E.version) .. "  ·  " .. tostring(E.designLabel))

    local navBg = CreateFrame("Frame", nil, panel)
    navBg:SetPoint("TOPLEFT", panel, "TOPLEFT", 22, -72)
    navBg:SetSize(112, 414)
    navBg:SetBackdrop({
      bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
      edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
      tile = true, tileSize = 16, edgeSize = 12,
      insets = { left = 3, right = 3, top = 3, bottom = 3 },
    })
    if navBg.SetBackdropColor then
      navBg:SetBackdropColor(0.02, 0.07, 0.06, 0.86)
    end
    if navBg.SetBackdropBorderColor then
      navBg:SetBackdropBorderColor(0.18, 0.38, 0.34, 0.9)
    end

    local navTitle = navBg:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    navTitle:SetPoint("TOP", navBg, "TOP", 0, -12)
    navTitle:SetText("|cff33ffcc功能分类|r")

    local pages = {}
    pages.basic = CreatePage(panel)
    pages.map = CreatePage(panel)
    pages.social = CreatePage(panel)
    pages.tools = CreatePage(panel)

    local navButtons = {}
    local function ShowPage(key)
      for pageKey, page in pairs(pages) do
        if pageKey == key then page:Show() else page:Hide() end
      end
      for pageKey, button in pairs(navButtons) do
        if pageKey == key then
          button:SetText("|cff33ffcc" .. button.rawLabel .. "|r")
        else
          button:SetText(button.rawLabel)
        end
      end
    end

    navButtons.basic = CreateNavButton(navBg, "基础汉化", 4, -44, function() ShowPage("basic") end)
    navButtons.basic.rawLabel = "基础汉化"
    navButtons.map = CreateNavButton(navBg, "地图任务", 4, -78, function() ShowPage("map") end)
    navButtons.map.rawLabel = "地图任务"
    navButtons.social = CreateNavButton(navBg, "社交协作", 4, -112, function() ShowPage("social") end)
    navButtons.social.rawLabel = "社交协作"
    navButtons.tools = CreateNavButton(navBg, "工具维护", 4, -146, function() ShowPage("tools") end)
    navButtons.tools.rawLabel = "工具维护"

    local basicCore = CreateSection(pages.basic, "基础汉化", 0, 0, 448, 190)
    CreateCheck(basicCore, "任务日志与任务追踪", "questLog", "任务标题、描述、目标、完成文本等。", 12, -34)
    CreateCheck(basicCore, "Tooltip 汉化", "tooltip", "物品、NPC、技能、任务目标等鼠标提示。", 224, -34)
    CreateCheck(basicCore, "拍卖行中文搜索/显示", "auctionHouse", "拍卖行物品名中文显示与中文搜索映射。", 12, -66)
    CreateCheck(basicCore, "常规界面文本", "ui", "普通窗口显示层文本汉化，避开动作条和法术按钮。", 224, -66)
    CreateCheck(basicCore, "FrameXML 显示层映射", "globalStrings", "只建立安全文本映射，不写 Blizzard 全局变量。", 12, -98)
    CreateCheck(basicCore, "独立任务追踪 UI", "questTracker", "EpochCN 的任务追踪文本增强。", 224, -98)
    CreateCheck(basicCore, "客户端语言环境 zhCN", "forceChineseClientLocale", "参考 AddonLocale 写入 GAME_LOCALE=zhCN；支持该变量的插件会优先使用简体中文。关闭后清除 EpochCN 写入的 zhCN。", 12, -130, function(enabled)
      if E.ApplyClientLocalePreference then E:ApplyClientLocalePreference() end
      E:Print("客户端语言环境：" .. (enabled and "已配置为 zhCN" or "已关闭") .. "（建议重载界面后完全生效）")
    end)

    local tooltipOptions = CreateSection(pages.basic, "Tooltip 选项", 0, -206, 448, 92)
    CreateCheck(tooltipOptions, "显示插件标签", "showDesignTag", "在 Tooltip 追加说明中显示 EpochCN 信息标签。", 12, -36)
    CreateCheck(tooltipOptions, "显示数据来源", "showSource", "在追加说明中显示数据来源。", 224, -36)

    local mapWorld = CreateSection(pages.map, "地图与任务标记", 0, 0, 448, 198)
    CreateCheck(mapWorld, "内置世界地图标记", "worldMap", "实验功能，启用后建议重载；如与 pfQuest 重叠可关闭。", 12, -36)
    CreateCheck(mapWorld, "显示地图任务点", "worldMapPins", "控制 EpochCN 内置地图任务点绘制。", 224, -36)
    CreateCheck(mapWorld, "可接任务 NPC 标记", "availableQuestPins", "显示可接任务 NPC 标记。", 12, -68)
    CreateCheck(mapWorld, "隐藏低等级可接任务", "hideLowLevelAvailableQuestPins", "隐藏低于角色等级一定范围的可接任务标记（参考 pfQuest）。", 224, -68)
    CreateCheck(mapWorld, "小地图任务目标", "minimapQuestPins", "在小地图显示当前区域附近的任务目标。", 12, -100)
    CreateCheck(mapWorld, "小地图只显示目标", "minimapQuestObjectivesOnly", "小地图默认只显示当前任务目标/交还点，减少干扰。", 224, -100)
    CreateCheck(mapWorld, "任务自动同步", "questAutoSync", "尽量同步当前任务 ID 与任务追踪数据。", 12, -132)

    -- 一次性清理老版本污染顶层的 social_*_ui 残留键
    EpochCNDB.social = EpochCNDB.social or {}
    EpochCNDB.social_enabled_ui = nil
    EpochCNDB.social_channel_ui = nil
    EpochCNDB.social_lfg_ui = nil
    EpochCNDB.social_qc_ui = nil

    local socialCore = CreateSection(pages.social, "社交功能", 0, 0, 448, 272)
    CreateNestedCheck(socialCore, "华人玩家发现", "social", "enabled",
      "通过 addon 消息自动发现安装了 EpochCN 的中文玩家。关闭后所有社交功能都会停用。",
      12, -36, nil, true)
    CreateNestedCheck(socialCore, "自动加入中文频道", "social", "autoJoinChannel",
      "登录时自动加入 EpochCN 公共频道。",
      224, -36, nil, true)

    CreateNestedCheck(socialCore, "组队招募板", "social", "lfgEnabled",
      "启用中文玩家专属 LFG 系统。",
      12, -66, nil, true)
    CreateNestedCheck(socialCore, "快捷短语 (/qc)", "social", "quickChatEnabled",
      "启用中英双语快捷短语系统。",
      224, -66, nil, true)

    CreateNestedCheck(socialCore, "目标框中文玩家图标", "social", "showTargetIcon",
      "选中中文玩家时在目标框显示标记图标。",
      12, -96, nil, true)
    CreateNestedCheck(socialCore, "Tooltip 中文玩家标签", "social", "showTooltipTag",
      "鼠标悬停中文玩家时在 Tooltip 显示版本/区域/备注。",
      224, -96, nil, true)

    CreateNestedCheck(socialCore, "上线通知", "social", "onlineNotify",
      "首次发现新中文玩家时在聊天框提示。",
      12, -126, nil, true)
    CreateNestedCheck(socialCore, "上线呼吸灯", "social", "flashMinimap",
      "新玩家上线/招募到达时小地图按钮闪烁。",
      224, -126, nil, true)

    CreateNestedCheck(socialCore, "记录密语为联系人", "social", "recordWhisper",
      "收到中文密语时自动加入通讯录。",
      12, -156, nil, true)
    CreateNestedCheck(socialCore, "智能密语翻译", "social", "quickChatSmartWhisper",
      "/qcw 向中文玩家发中文，向外国人发英文。",
      224, -156, nil, true)

    CreateNestedCheck(socialCore, "自动公会标签", "social", "autoTagGuildmate",
      "心跳广播识别到同公会成员时自动添加「公会」标签。",
      12, -186, nil, true)
    CreateNestedCheck(socialCore, "短语双语模式", "social", "quickChatBilingual",
      "/qc 默认同时发送中英文，例如「谢谢 (Thank you)」。",
      224, -186, nil, false)

    CreateNestedCheck(socialCore, "上线只提醒一次", "social", "onlineNotifyOnceOnly",
      "本次登录后同一玩家上线只提示第一次（避免重连刷屏）。",
      12, -216, nil, false)

    local socialActions = CreateSection(pages.social, "快捷入口", 0, -288, 448, 74)
    CreateButton(socialActions, "中文玩家", 92, 12, -36, function()
      if E.ToggleSocialPanel then E:ToggleSocialPanel() end
    end)
    CreateButton(socialActions, "组队招募", 92, 116, -36, function()
      if E.ToggleLFGPanel then E:ToggleLFGPanel() end
    end)
    CreateButton(socialActions, "快捷短语", 92, 220, -36, function()
      if E.ToggleQuickChatPanel then E:ToggleQuickChatPanel() end
    end)
    CreateButton(socialActions, "反馈建议", 92, 324, -36, function()
      if E.ToggleFeedbackPanel then E:ToggleFeedbackPanel() end
    end)

    local maintenance = CreateSection(pages.tools, "调试与维护", 0, 0, 448, 122)
    CreateCheck(maintenance, "调试输出", "debug", "在聊天框输出 EpochCN 调试信息。", 12, -36)
    CreateCheck(maintenance, "关闭 pfQuest 追踪器", "disablePFQuestTracker", "减少任务追踪重复显示，重载后生效。", 224, -36)

    CreateButton(maintenance, "打印状态", 92, 12, -78, function()
      E:Print("已加载 " .. tostring(E.version) .. "，任务=" .. tostring(EpochCNDB.questLog) .. "，Tooltip=" .. tostring(EpochCNDB.tooltip) .. "，拍卖行=" .. tostring(EpochCNDB.auctionHouse) .. "，语言=" .. tostring(GAME_LOCALE or "默认"))
    end)
    CreateButton(maintenance, "Tooltip 调试", 102, 116, -78, function()
      if E.DumpTooltipLines then E:DumpTooltipLines(GameTooltip) end
    end)
    CreateButton(maintenance, "重载界面", 92, 230, -78, function()
      ReloadUI()
    end)
    CreateButton(maintenance, "关闭", 74, 334, -78, function()
      panel:Hide()
    end)

    local statsSection = CreateSection(pages.tools, "汉化覆盖统计", 0, -146, 448, 116)
    local statsText = statsSection:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    statsText:SetPoint("TOPLEFT", statsSection, "TOPLEFT", 14, -38)
    statsText:SetWidth(412)
    statsText:SetJustifyH("LEFT")
    local stats = E.stats or {}
    local unitPct = stats.unitTotal and stats.unitTotal > 0 and string.format("%.1f%%", stats.unitChinese / stats.unitTotal * 100) or "N/A"
    local spellPct = stats.spellCount and stats.spellCount > 0 and string.format("%.1f%%", stats.spellWithDesc / stats.spellCount * 100) or "N/A"
    statsText:SetText(
      "|cff88ccff任务数据：|r" .. tostring(stats.questTotal or 0) .. " 条" ..
      "    |cff88ccff物品映射：|r" .. tostring(stats.itemNameMapTotal or 0) .. " 条\n" ..
      "|cff88ccff单位名称：|r" .. tostring(stats.unitChinese or 0) .. "/" .. tostring(stats.unitTotal or 0) .. " (" .. unitPct .. ")" ..
      "    |cff88ccff法术数据：|r" .. tostring(stats.spellWithDesc or 0) .. "/" .. tostring(stats.spellCount or 0) .. " (" .. spellPct .. ")"
    )

    reloadNotice = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    reloadNotice:SetPoint("BOTTOMLEFT", panel, "BOTTOMLEFT", 28, 24)
    reloadNotice:SetText("|cffffcc00设置已保存。模块开关通常需要重载界面或重进游戏后完全生效。|r")
    reloadNotice:Hide()

    ShowPage("basic")

    return panel
  end

  function E:ToggleSettingsPanel()
    local frame = CreateSettingsPanel()
    if frame:IsShown() then
      frame:Hide()
    else
      frame:Show()
    end
  end

  function E:EnsureSettingsPanel()
    return CreateSettingsPanel()
  end

  ---------------------------------------------------------------------------
  -- About Panel (关于)
  ---------------------------------------------------------------------------
  local function CreateAboutPanel()
    if aboutPanel then return aboutPanel end

    aboutPanel = CreateFrame("Frame", "EpochCNAboutFrame", UIParent)
    aboutPanel:SetSize(440, 420)
    aboutPanel:SetPoint("CENTER")
    aboutPanel:SetFrameStrata("DIALOG")
    aboutPanel:SetMovable(true)
    aboutPanel:EnableMouse(true)
    aboutPanel:RegisterForDrag("LeftButton")
    aboutPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    aboutPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    aboutPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true,
      tileSize = 32,
      edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    aboutPanel:Hide()

    local close = CreateFrame("Button", nil, aboutPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", aboutPanel, "TOPRIGHT", -5, -5)

    -- Title
    local title = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", aboutPanel, "TOP", 0, -18)
    title:SetText("|cff33ffccEpoch|cffffffffCN|r 关于")

    -- Version & Author
    local verLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    verLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -48)
    verLine:SetText("|cff88ccff版本：|r" .. tostring(E.version))

    local authorLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    authorLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -68)
    authorLine:SetText("|cff88ccff作者：|r" .. tostring(E.designLabel))

    local descLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    descLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -92)
    descLine:SetWidth(384)
    descLine:SetJustifyH("LEFT")
    descLine:SetText("Project Epoch 独立中文整合插件。任务汉化、任务追踪、天赋技能与界面汉化，内置独立的 pfQuest 风格世界地图任务标记核心。")

    -- Data source
    local dataHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    dataHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -132)
    dataHeader:SetText("|cffffd200数据来源|r")

    local dataLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dataLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -150)
    dataLine:SetWidth(384)
    dataLine:SetJustifyH("LEFT")
    dataLine:SetText("EpochHead: https://epochhead.com/\npfQuest-epoch · QuestCN · Tooltips_Chinese 社区数据")

    -- Donors
    local donorHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    donorHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -190)
    donorHeader:SetText("|cffffd200汉化捐赠者|r")

    local donorTopLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    donorTopLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -208)
    donorTopLine:SetWidth(384)
    donorTopLine:SetJustifyH("LEFT")
    donorTopLine:SetText("|cffffd200特别感谢：|r|cffff8000erha|r |cffffd200的大力支持|r")

    local donorLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    donorLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -232)
    donorLine:SetWidth(384)
    donorLine:SetJustifyH("LEFT")
    donorLine:SetText("|cff33ff99ethon|r、|cff33ff99王大强|r、|cff33ff99manmanain|r、|cff33ff99xiongbaobao|r\n|cff33ff99Shizuka|r、|cff33ff99Soulwisp|r、|cff33ff99Jynxen|r、|cff33ff99hcafei|r\n|cff33ff99Sylyss|r、|cff33ff99卡萨丁|r、|cff33ff99Sixthoo|r，以及未留名的兄弟们，感谢你们的支持！")

    -- Special thanks
    local thanksHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    thanksHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -290)
    thanksHeader:SetText("|cffffd200特别鸣谢|r")

    local thanksLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    thanksLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -308)
    thanksLine:SetWidth(384)
    thanksLine:SetJustifyH("LEFT")
    thanksLine:SetText("|cffffff00kook-暗色弧|r、|cffffff00飞翔鸟|r、|cffffff00加特林|r、|cffffff00嘹咋咧|r、|cffffff00狄卢|r\n等前期大佬们对汉化工作的大力支持与帮助！")

    -- Contact
    local contactHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    contactHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -338)
    contactHeader:SetText("|cffffd200反馈与支持|r")

    local contactLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    contactLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -356)
    contactLine:SetWidth(384)
    contactLine:SetJustifyH("LEFT")
    contactLine:SetText("数据源：https://epochhead.com/\nQQ 交流群：1097800503\n游戏内输入 /ecn 打开设置面板")

    -- Close button at bottom
    local closeBtn = CreateFrame("Button", nil, aboutPanel, "UIPanelButtonTemplate")
    closeBtn:SetSize(80, 24)
    closeBtn:SetPoint("BOTTOM", aboutPanel, "BOTTOM", 0, 20)
    closeBtn:SetText("关闭")
    closeBtn:SetScript("OnClick", function() aboutPanel:Hide() end)

    return aboutPanel
  end

  function E:ToggleAboutPanel()
    local frame = CreateAboutPanel()
    if frame:IsShown() then
      frame:Hide()
    else
      frame:Show()
    end
  end

  local function BuildMinimapMenu()
    local info = UIDropDownMenu_CreateInfo()
    info.text = "|cff33ffccEpochCN|r  v" .. tostring(E.version)
    info.isTitle = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "打开设置"
    info.notCheckable = true
    info.func = function() CloseDropDownMenus(); E:ToggleSettingsPanel() end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "关于"
    info.notCheckable = true
    info.func = function() CloseDropDownMenus(); E:ToggleAboutPanel() end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = " "
    info.notClickable = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "地图标记：" .. (EpochCNDB.worldMap and "|cff33ff99开启|r" or "|cffff6666关闭|r")
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      EpochCNDB.worldMap = not EpochCNDB.worldMap
      E:Print("地图标记：" .. (EpochCNDB.worldMap and "已开启" or "已关闭") .. "（重载界面后完全生效）")
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "Tooltip 汉化：" .. (EpochCNDB.tooltip and "|cff33ff99开启|r" or "|cffff6666关闭|r")
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      EpochCNDB.tooltip = not EpochCNDB.tooltip
      E:Print("Tooltip 汉化：" .. (EpochCNDB.tooltip and "已开启" or "已关闭") .. "（重载界面后完全生效）")
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "任务日志：" .. (EpochCNDB.questLog and "|cff33ff99开启|r" or "|cffff6666关闭|r")
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      EpochCNDB.questLog = not EpochCNDB.questLog
      E:Print("任务日志汉化：" .. (EpochCNDB.questLog and "已开启" or "已关闭") .. "（重载界面后完全生效）")
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = " "
    info.notClickable = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = " "
    info.notClickable = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "|cff88ccff社交功能|r"
    info.isTitle = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "中文玩家列表"
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      if E.ToggleSocialPanel then E:ToggleSocialPanel() end
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "组队招募板"
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      if E.ToggleLFGPanel then E:ToggleLFGPanel() end
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "快捷短语"
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      if E.ToggleQuickChatPanel then E:ToggleQuickChatPanel() end
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "反馈建议"
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      if E.ToggleFeedbackPanel then E:ToggleFeedbackPanel() end
    end
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = " "
    info.notClickable = true
    info.notCheckable = true
    UIDropDownMenu_AddButton(info)

    info = UIDropDownMenu_CreateInfo()
    info.text = "隐藏图标"
    info.notCheckable = true
    info.func = function()
      CloseDropDownMenus()
      EpochCNDB.minimapButtonHide = true
      if minimapButton then minimapButton:Hide() end
      E:Print("小地图按钮已隐藏。/ecn icon 可重新显示。")
    end
    UIDropDownMenu_AddButton(info)
  end

  local function UpdateMinimapButtonPosition()
    if not minimapButton then return end
    local angle = EpochCNDB.minimapButtonAngle or 225
    local radians = math.rad(angle)
    local radius = 80
    minimapButton:ClearAllPoints()
    minimapButton:SetPoint("CENTER", Minimap, "CENTER", math.cos(radians) * radius, math.sin(radians) * radius)
  end

  local function CreateMinimapButton()
    if minimapButton or not Minimap or EpochCNDB.minimapButtonHide then return end

    minimapButton = CreateFrame("Button", "EpochCNMinimapButton", Minimap)
    minimapButton:SetSize(34, 34)
    minimapButton:SetFrameStrata("MEDIUM")
    minimapButton:SetFrameLevel(8)
    minimapButton:RegisterForClicks("LeftButtonUp", "RightButtonUp", "MiddleButtonUp")
    minimapButton:RegisterForDrag("LeftButton")

    -- 圆形背景底色
    local bg = minimapButton:CreateTexture(nil, "BACKGROUND")
    bg:SetSize(26, 26)
    bg:SetPoint("CENTER", 0, 0)
    bg:SetTexture("Interface\\CHARACTERFRAME\\TempPortraitAlphaMask")
    bg:SetVertexColor(0.12, 0.12, 0.14, 0.92)

    -- 主图标：使用翻译/语言相关图标
    local icon = minimapButton:CreateTexture(nil, "ARTWORK")
    icon:SetSize(18, 18)
    icon:SetPoint("CENTER", 0, 0)
    icon:SetTexture("Interface\\Icons\\INV_Misc_Book_09")
    minimapButton.icon = icon

    local mark = minimapButton:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    mark:SetPoint("CENTER", minimapButton, "CENTER", 0, 0)
    mark:SetText("|cff33ffcc中|r")
    minimapButton.mark = mark

    -- 圆形边框（移除 — 用户反馈外框多余且移位）
    -- local border = minimapButton:CreateTexture(nil, "OVERLAY")
    -- border:SetSize(54, 54)
    -- border:SetPoint("CENTER", 0, 0)
    -- border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
    -- minimapButton.border = border

    -- 在线中文玩家数量角标
    local badge = minimapButton:CreateFontString(nil, "OVERLAY", "NumberFontNormalSmall")
    badge:SetPoint("BOTTOMRIGHT", minimapButton, "BOTTOMRIGHT", 2, -2)
    badge:SetText("")
    badge:SetTextColor(0.2, 1, 0.6)
    minimapButton.badge = badge

    -- 高亮效果
    local highlight = minimapButton:CreateTexture(nil, "HIGHLIGHT")
    highlight:SetSize(26, 26)
    highlight:SetPoint("CENTER", 0, 0)
    highlight:SetTexture("Interface\\CHARACTERFRAME\\TempPortraitAlphaMask")
    highlight:SetVertexColor(0.2, 1, 0.8, 0.3)
    highlight:SetBlendMode("ADD")

    -- 呼吸灯动画（有新消息/新玩家时闪烁）
    minimapButton.glowAlpha = 0
    minimapButton.glowDir = 1
    minimapButton.glowActive = false

    local glow = minimapButton:CreateTexture(nil, "ARTWORK", nil, 1)
    glow:SetSize(30, 30)
    glow:SetPoint("CENTER", 0, 0)
    glow:SetTexture("Interface\\CHARACTERFRAME\\TempPortraitAlphaMask")
    glow:SetVertexColor(0.2, 1, 0.8, 0)
    glow:SetBlendMode("ADD")
    minimapButton.glow = glow

    -- 定时更新角标和呼吸灯
    minimapButton:SetScript("OnUpdate", function(self, elapsed)
      -- 拖拽位置更新（仅拖拽时执行）
      if self.isDragging then
        local mx, my = Minimap:GetCenter()
        local px, py = GetCursorPosition()
        local scale = Minimap:GetEffectiveScale()
        px, py = px / scale, py / scale
        local dx, dy = px - mx, py - my
        local angle
        if math.atan2 then
          angle = math.deg(math.atan2(dy, dx))
        elseif dx == 0 then
          angle = dy >= 0 and 90 or -90
        else
          angle = math.deg(math.atan(dy / dx))
          if dx < 0 then angle = angle + 180 end
        end
        EpochCNDB.minimapButtonAngle = angle
        UpdateMinimapButtonPosition()
        return  -- 拖拽时跳过其他逻辑，减少开销
      end

      -- 更新在线人数角标（每 10 秒）
      self.badgeTimer = (self.badgeTimer or 0) + elapsed
      if self.badgeTimer >= 10 then
        self.badgeTimer = 0
        local count = E.GetChinesePlayerCount and E:GetChinesePlayerCount() or 0
        if count > 0 then
          self.badge:SetText(tostring(count))
        else
          self.badge:SetText("")
        end
      end

      -- 呼吸灯动画（仅激活时执行）
      if self.glowActive then
        self.glowAlpha = self.glowAlpha + self.glowDir * elapsed * 1.5
        if self.glowAlpha >= 0.6 then
          self.glowAlpha = 0.6
          self.glowDir = -1
        elseif self.glowAlpha <= 0 then
          self.glowAlpha = 0
          self.glowDir = 1
          self.glowCycles = (self.glowCycles or 0) + 1
          if self.glowCycles >= 3 then
            self.glowActive = false
            self.glowCycles = 0
          end
        end
        self.glow:SetAlpha(self.glowAlpha)
      end
    end)

    minimapButton:SetScript("OnClick", function(_, button)
      if button == "RightButton" then
        if not minimapMenu then
          minimapMenu = CreateFrame("Frame", "EpochCNMinimapMenu", UIParent, "UIDropDownMenuTemplate")
        end
        UIDropDownMenu_Initialize(minimapMenu, BuildMinimapMenu, "MENU")
        ToggleDropDownMenu(1, nil, minimapMenu, "cursor", 0, 0)
      elseif button == "MiddleButton" then
        -- 中键打开社交面板
        if E.ToggleSocialPanel then
          E:ToggleSocialPanel()
        else
          E:ToggleAboutPanel()
        end
      else
        E:ToggleSettingsPanel()
      end
    end)

    minimapButton:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_LEFT")
      GameTooltip:SetText("|cff33ffccEpoch|cffffffffCN|r", 0.2, 1, 0.8)
      GameTooltip:AddLine("v" .. tostring(E.version) .. "  " .. tostring(E.designLabel), 0.6, 0.6, 0.6)
      GameTooltip:AddLine(" ")

      -- 显示在线中文玩家数
      local count = E.GetChinesePlayerCount and E:GetChinesePlayerCount() or 0
      if count > 0 then
        GameTooltip:AddLine("|cff33ffcc" .. count .. "|r 名中文玩家在线", 0.2, 1, 0.6)
      end

      -- 显示频道状态
      local chNum = E.GetChineseChannelNumber and E:GetChineseChannelNumber() or 0
      if chNum > 0 then
        GameTooltip:AddLine("|cff88ccff中文频道|r 已连接 (/" .. chNum .. ")", 0.5, 0.8, 1)
      end

      GameTooltip:AddLine(" ")
      GameTooltip:AddLine("|cffffffffL键|r 设置  |cffffffffM键|r 社交  |cffffffffR键|r 菜单", 0.7, 0.7, 0.7)
      GameTooltip:AddLine("|cff666666拖动移动位置|r", 0.4, 0.4, 0.4)
      GameTooltip:Show()
    end)
    minimapButton:SetScript("OnLeave", function() GameTooltip:Hide() end)

    minimapButton:SetScript("OnDragStart", function(self)
      self.isDragging = true
    end)
    minimapButton:SetScript("OnDragStop", function(self)
      self.isDragging = false
      UpdateMinimapButtonPosition()
    end)

    UpdateMinimapButtonPosition()
  end

  -- 触发小地图按钮呼吸灯（供其他模块调用）
  function E:FlashMinimapButton()
    if minimapButton then
      minimapButton.glowActive = true
      minimapButton.glowCycles = 0
      minimapButton.glowAlpha = 0
      minimapButton.glowDir = 1
    end
  end

  function E:ShowMinimapButton()
    EpochCNDB.minimapButtonHide = false
    if minimapButton then
      minimapButton:Show()
      UpdateMinimapButtonPosition()
    else
      CreateMinimapButton()
    end
  end

  for _, name in pairs(targets) do
    local frame = getglobal(name)
    if frame and frame.HookScript then
      frame:HookScript("OnShow", function()
        TranslateKnownFrames()
      end)
    end
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:SetScript("OnEvent", function()
    local ok, err = pcall(TranslateKnownFrames)
    if not ok then
      E:Debug("界面文本初始化失败: " .. tostring(err))
    end

    ok, err = pcall(CreateMinimapButton)
    if not ok then
      E:Print("|cffff6666小地图按钮创建失败：|r" .. tostring(err))
      E:Print("你仍可输入 |cffffd200/ecn|r 打开设置。")
    end

    -- Login broadcast (once per session)
    if not loginBroadcastDone then
      loginBroadcastDone = true
      E:Print("|cff33ffccEpochCN|r v" .. tostring(E.version) .. " 已加载，/ecn 打开设置。")
      E:Print("|cffffd200汉化捐赠者|r: |cffff8000erha|r、|cff33ff99ethon|r、|cff33ff99王大强|r、|cff33ff99manmanain|r、|cff33ff99xiongbaobao|r、|cff33ff99Shizuka|r、|cff33ff99Soulwisp|r、|cff33ff99Jynxen|r、|cff33ff99hcafei|r、|cff33ff99Sylyss|r、|cff33ff99卡萨丁|r、|cff33ff99Sixthoo|r、还有未留名兄弟")
    end
  end)
end)
