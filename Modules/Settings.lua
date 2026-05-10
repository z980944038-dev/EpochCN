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

  local function CreateCheck(parent, label, key, tooltip, x, y)
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

  local function CreateSettingsPanel()
    if panel then return panel end

    panel = CreateFrame("Frame", "EpochCNSettingsFrame", UIParent)
    panel:SetSize(430, 530)
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
    title:SetPoint("TOP", panel, "TOP", 0, -18)
    title:SetText("|cff33ffccEpoch|cffffffffCN|r 设置")

    local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -5, -5)

    local version = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    version:SetPoint("TOPLEFT", panel, "TOPLEFT", 26, -42)
    version:SetText("版本 " .. tostring(E.version) .. "  ·  " .. tostring(E.designLabel))

    CreateHeader(panel, "基础汉化", 26, -70)
    CreateCheck(panel, "任务日志与任务追踪", "questLog", "任务标题、描述、目标、完成文本等。", 26, -94)
    CreateCheck(panel, "Tooltip 汉化", "tooltip", "物品、NPC、技能、任务目标等鼠标提示。", 226, -94)
    CreateCheck(panel, "拍卖行中文搜索/显示", "auctionHouse", "拍卖行物品名中文显示与中文搜索映射。", 26, -124)
    CreateCheck(panel, "常规界面文本", "ui", "普通窗口显示层文本汉化，避开动作条和法术按钮。", 226, -124)
    CreateCheck(panel, "FrameXML 显示层映射", "globalStrings", "只建立安全文本映射，不写 Blizzard 全局变量。", 26, -154)
    CreateCheck(panel, "独立任务追踪 UI", "questTracker", "EpochCN 的任务追踪文本增强。", 226, -154)

    CreateHeader(panel, "Tooltip 选项", 26, -190)
    CreateCheck(panel, "显示插件标签", "showDesignTag", "在 Tooltip 追加说明中显示 EpochCN 信息标签。", 26, -214)
    CreateCheck(panel, "显示数据来源", "showSource", "在追加说明中显示数据来源。", 226, -214)

    CreateHeader(panel, "地图与任务标记", 26, -250)
    CreateCheck(panel, "内置世界地图标记", "worldMap", "实验功能，启用后建议重载；如与 pfQuest 重叠可关闭。", 26, -274)
    CreateCheck(panel, "显示地图任务点", "worldMapPins", "控制 EpochCN 内置地图任务点绘制。", 226, -274)
    CreateCheck(panel, "可接任务 NPC 标记", "availableQuestPins", "显示可接任务 NPC 标记。", 26, -304)
    CreateCheck(panel, "隐藏低等级可接任务", "hideLowLevelAvailableQuestPins", "隐藏低于角色等级一定范围的可接任务标记（参考 pfQuest）。", 226, -304)
    CreateCheck(panel, "小地图任务目标", "minimapQuestPins", "在小地图显示当前区域附近的任务目标。", 26, -334)
    CreateCheck(panel, "小地图只显示目标", "minimapQuestObjectivesOnly", "小地图默认只显示当前任务目标/交还点，减少干扰。", 226, -334)
    CreateCheck(panel, "任务自动同步", "questAutoSync", "尽量同步当前任务 ID 与任务追踪数据。", 26, -364)

    CreateHeader(panel, "调试与维护", 26, -400)
    CreateCheck(panel, "调试输出", "debug", "在聊天框输出 EpochCN 调试信息。", 26, -424)
    CreateCheck(panel, "关闭 pfQuest 追踪器", "disablePFQuestTracker", "减少任务追踪重复显示，重载后生效。", 226, -424)

    CreateButton(panel, "打印状态", 86, 26, -462, function()
      E:Print("已加载 " .. tostring(E.version) .. "，任务=" .. tostring(EpochCNDB.questLog) .. "，Tooltip=" .. tostring(EpochCNDB.tooltip) .. "，拍卖行=" .. tostring(EpochCNDB.auctionHouse))
    end)
    CreateButton(panel, "Tooltip 调试", 100, 118, -462, function()
      if E.DumpTooltipLines then E:DumpTooltipLines(GameTooltip) end
    end)
    CreateButton(panel, "重载界面", 86, 224, -462, function()
      ReloadUI()
    end)
    CreateButton(panel, "关闭", 70, 316, -462, function()
      panel:Hide()
    end)

    reloadNotice = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    reloadNotice:SetPoint("BOTTOMLEFT", panel, "BOTTOMLEFT", 28, 24)
    reloadNotice:SetText("|cffffcc00设置已保存。模块开关通常需要重载界面或重进游戏后完全生效。|r")
    reloadNotice:Hide()

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

    local donorLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    donorLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -208)
    donorLine:SetWidth(384)
    donorLine:SetJustifyH("LEFT")
    donorLine:SetText("|cff33ff99ethon|r、|cff33ff99王大强|r、|cff33ff99manmanain|r、|cff33ff99xiongbaobao|r\n|cff33ff99Shizuka|r、|cff33ff99Soulwisp|r、|cff33ff99Jynxen|r、|cff33ff99hcafei|r\n以及未留名的兄弟们，感谢你们的支持！")

    -- Special thanks
    local thanksHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    thanksHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -262)
    thanksHeader:SetText("|cffffd200特别鸣谢|r")

    local thanksLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    thanksLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -280)
    thanksLine:SetWidth(384)
    thanksLine:SetJustifyH("LEFT")
    thanksLine:SetText("|cffffff00kook-暗色弧|r、|cffffff00小武哥儿|r、|cffffff00飞翔鸟|r、|cffffff00加特林|r、|cffffff00嘹咋咧|r、|cffffff00狄卢|r\n等前期大佬们对汉化工作的大力支持与帮助！")

    -- Contact
    local contactHeader = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    contactHeader:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -324)
    contactHeader:SetText("|cffffd200反馈与支持|r")

    local contactLine = aboutPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    contactLine:SetPoint("TOPLEFT", aboutPanel, "TOPLEFT", 28, -342)
    contactLine:SetWidth(384)
    contactLine:SetJustifyH("LEFT")
    contactLine:SetText("数据源：https://epochhead.com/\n游戏内输入 /ecn 打开设置面板")

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
    minimapButton:SetSize(32, 32)
    minimapButton:SetFrameStrata("MEDIUM")
    minimapButton:RegisterForClicks("LeftButtonUp", "RightButtonUp", "MiddleButtonUp")
    minimapButton:RegisterForDrag("LeftButton")

    local icon = minimapButton:CreateTexture(nil, "BACKGROUND")
    icon:SetSize(20, 20)
    icon:SetPoint("CENTER", 0, 1)
    icon:SetTexture("Interface\\Icons\\INV_Misc_Book_09")

    local border = minimapButton:CreateTexture(nil, "OVERLAY")
    border:SetSize(54, 54)
    border:SetPoint("CENTER")
    border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")

    minimapButton:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")

    minimapButton:SetScript("OnClick", function(_, button)
      if button == "RightButton" then
        if not minimapMenu then
          minimapMenu = CreateFrame("Frame", "EpochCNMinimapMenu", UIParent, "UIDropDownMenuTemplate")
        end
        UIDropDownMenu_Initialize(minimapMenu, BuildMinimapMenu, "MENU")
        ToggleDropDownMenu(1, nil, minimapMenu, "cursor", 0, 0)
      elseif button == "MiddleButton" then
        E:ToggleAboutPanel()
      else
        E:ToggleSettingsPanel()
      end
    end)

    minimapButton:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_LEFT")
      GameTooltip:SetText("|cff33ffccEpochCN|r  v" .. tostring(E.version), 0.2, 1, 0.8)
      GameTooltip:AddLine("左键：打开设置", 1, 1, 1)
      GameTooltip:AddLine("中键：关于", 1, 1, 1)
      GameTooltip:AddLine("右键：更多选项", 1, 1, 1)
      GameTooltip:AddLine("拖动：移动图标", 0.6, 0.6, 0.6)
      GameTooltip:Show()
    end)
    minimapButton:SetScript("OnLeave", function() GameTooltip:Hide() end)

    minimapButton:SetScript("OnDragStart", function(self)
      self:SetScript("OnUpdate", function()
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
      end)
    end)
    minimapButton:SetScript("OnDragStop", function(self)
      self:SetScript("OnUpdate", nil)
      UpdateMinimapButtonPosition()
    end)

    UpdateMinimapButtonPosition()
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
    TranslateKnownFrames()
    CreateSettingsPanel()
    CreateMinimapButton()

    -- Login broadcast (once per session)
    if not loginBroadcastDone then
      loginBroadcastDone = true
      local prefix = "|cff33ffccEpoch|cffffffffCN|r"
      E:Print("|cff33ffccEpochCN|r v" .. tostring(E.version) .. " 已加载，/ecn 打开设置。")
      E:Print("|cffffd200汉化捐赠者|r:|cff33ff99ethon|r、|cff33ff99王大强|r、|cff33ff99manmanain|r、|cff33ff99xiongbaobao|r、|cff33ff99Shizuka|r、|cff33ff99Soulwisp|r、|cff33ff99Jynxen|r、|cff33ff99hcafei|r、还有未留名兄弟")
      E:Print("|cffffd200特别鸣谢|r:|cffffff00kook-暗色弧|r、|cffffff00小武哥儿|r、|cffffff00飞翔鸟|r、|cffffff00加特林|r、|cffffff00嘹咋咧|r、|cffffff00狄卢|r 等前期大佬")
    end
  end)
end)
