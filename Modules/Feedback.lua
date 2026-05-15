-- Feedback.lua
-- 用户反馈收集模块
-- 提供游戏内反馈面板，玩家可提交翻译错误、功能建议、Bug 报告等。
-- 反馈数据保存到 SavedVariables，支持导出格式化文本供玩家复制到 GitHub Issues。
--
-- 收集方式：
-- 1. 本地 SavedVariables 存储（开发者可通过工具脚本批量提取）
-- 2. 导出格式化 Markdown 到编辑框，方便玩家 Ctrl+C 粘贴到 GitHub Issues
--
-- 性能注意：
-- - 无 OnUpdate，纯用户交互驱动
-- - UI 面板延迟创建，仅在打开时构建
-- - SavedVariables 写入仅在提交时发生

EpochCN:RegisterModule("Feedback", function(E)
  local MAX_FEEDBACK_STORED = 50   -- 本地最多存储条目
  local GITHUB_ISSUES_URL = "https://github.com/z980944038-dev/EpochCN/issues"

  -- 初始化持久化数据
  EpochCNDB.feedback = EpochCNDB.feedback or {}
  EpochCNDB.feedback.history = EpochCNDB.feedback.history or {}

  -- 反馈类型定义
  local feedbackTypes = {
    { key = "translation", label = "翻译错误", color = "|cffff9900", desc = "物品/NPC/技能/任务翻译不正确" },
    { key = "missing", label = "缺失翻译", color = "|cffffff00", desc = "某处仍显示英文，需要补充翻译" },
    { key = "bug", label = "Bug 报告", color = "|cffff3333", desc = "插件功能异常、报错、卡顿等" },
    { key = "suggestion", label = "功能建议", color = "|cff33ccff", desc = "希望添加的新功能或改进" },
    { key = "other", label = "其他", color = "|cff999999", desc = "其他反馈" },
  }

  local feedbackTypeByKey = {}
  for _, ft in ipairs(feedbackTypes) do
    feedbackTypeByKey[ft.key] = ft
  end

  ---------------------------------------------------------------------------
  -- 工具函数
  ---------------------------------------------------------------------------
  local function GetTimestamp()
    local h, m = GetGameTime()
    return string.format("%02d:%02d", h, m)
  end

  local function TruncateText(text, maxLen)
    if not text then return "" end
    if string.len(text) <= maxLen then return text end
    return string.sub(text, 1, maxLen - 3) .. "..."
  end

  local function GetEnvironmentInfo()
    local info = {}
    table.insert(info, "EpochCN v" .. (E.version or "?"))
    table.insert(info, "Lv." .. tostring(UnitLevel("player") or 0))
    local _, classEn = UnitClass("player")
    table.insert(info, classEn or "?")
    table.insert(info, GetZoneText and GetZoneText() or "?")
    return table.concat(info, " | ")
  end

  ---------------------------------------------------------------------------
  -- 反馈提交
  ---------------------------------------------------------------------------
  local function SubmitFeedback(feedbackType, content, context)
    if not content or content == "" then
      E:Print("|cffff6666请输入反馈内容。|r")
      return false
    end

    local entry = {
      type = feedbackType or "other",
      content = TruncateText(content, 500),
      context = context or "",
      version = E.version or "?",
      player = UnitName("player") or "?",
      level = UnitLevel("player") or 0,
      zone = GetZoneText and GetZoneText() or "",
      timestamp = time(),
      timeStr = GetTimestamp(),
    }

    -- 保存到本地历史
    local history = EpochCNDB.feedback.history
    table.insert(history, entry)

    -- 限制存储大小
    while #history > MAX_FEEDBACK_STORED do
      table.remove(history, 1)
    end

    local typeInfo = feedbackTypeByKey[feedbackType] or feedbackTypeByKey["other"]
    E:Print(string.format("|cff33ff99反馈已保存！|r 类型: %s%s|r", typeInfo.color, typeInfo.label))
    E:Print("|cff888888使用 /ecn feedback export 可导出全部反馈，复制后提交到 GitHub Issues。|r")
    E:Print("|cff88ccff提交地址: |r" .. GITHUB_ISSUES_URL)

    return true
  end

  ---------------------------------------------------------------------------
  -- 导出功能（生成 Markdown 格式文本供复制到 GitHub）
  ---------------------------------------------------------------------------
  local exportFrame = nil

  local function CreateExportFrame()
    if exportFrame then return exportFrame end

    exportFrame = CreateFrame("Frame", "EpochCNFeedbackExportFrame", UIParent)
    exportFrame:SetSize(520, 380)
    exportFrame:SetPoint("CENTER")
    exportFrame:SetFrameStrata("FULLSCREEN_DIALOG")
    exportFrame:SetMovable(true)
    exportFrame:EnableMouse(true)
    exportFrame:RegisterForDrag("LeftButton")
    exportFrame:SetScript("OnDragStart", function(self) self:StartMoving() end)
    exportFrame:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    exportFrame:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true, tileSize = 32, edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    exportFrame:Hide()

    local title = exportFrame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", exportFrame, "TOP", 0, -16)
    title:SetText("|cff33ffcc反馈导出|r")

    local subtitle = exportFrame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    subtitle:SetPoint("TOP", exportFrame, "TOP", 0, -36)
    subtitle:SetText("Ctrl+A 全选，Ctrl+C 复制，粘贴到 GitHub Issues 提交")

    local close = CreateFrame("Button", nil, exportFrame, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", exportFrame, "TOPRIGHT", -5, -5)

    -- 滚动编辑框
    local scrollFrame = CreateFrame("ScrollFrame", "EpochCNFBExportScroll", exportFrame, "UIPanelScrollFrameTemplate")
    scrollFrame:SetPoint("TOPLEFT", exportFrame, "TOPLEFT", 16, -54)
    scrollFrame:SetPoint("BOTTOMRIGHT", exportFrame, "BOTTOMRIGHT", -32, 44)

    local editBox = CreateFrame("EditBox", "EpochCNFBExportEditBox", scrollFrame)
    editBox:SetMultiLine(true)
    editBox:SetFontObject(GameFontHighlightSmall)
    editBox:SetWidth(456)
    editBox:SetAutoFocus(false)
    editBox:SetScript("OnEscapePressed", function(self)
      self:ClearFocus()
      exportFrame:Hide()
    end)
    scrollFrame:SetScrollChild(editBox)
    exportFrame.editBox = editBox

    -- 全选按钮
    local selectBtn = CreateFrame("Button", nil, exportFrame, "UIPanelButtonTemplate")
    selectBtn:SetSize(80, 22)
    selectBtn:SetPoint("BOTTOMLEFT", exportFrame, "BOTTOMLEFT", 16, 14)
    selectBtn:SetText("全选")
    selectBtn:SetScript("OnClick", function()
      editBox:SetFocus()
      editBox:HighlightText()
    end)

    -- 关闭按钮
    local closeBtn = CreateFrame("Button", nil, exportFrame, "UIPanelButtonTemplate")
    closeBtn:SetSize(60, 22)
    closeBtn:SetPoint("BOTTOMRIGHT", exportFrame, "BOTTOMRIGHT", -16, 14)
    closeBtn:SetText("关闭")
    closeBtn:SetScript("OnClick", function() exportFrame:Hide() end)

    return exportFrame
  end

  local function ShowExport(text)
    local frame = CreateExportFrame()
    frame.editBox:SetText(text)
    frame:Show()
    frame.editBox:SetFocus()
    frame.editBox:HighlightText()
  end

  local function ExportAllFeedback()
    local history = EpochCNDB.feedback.history
    if #history == 0 then
      E:Print("暂无反馈记录可导出。")
      return
    end

    local lines = {}
    table.insert(lines, "## EpochCN 用户反馈")
    table.insert(lines, "")
    table.insert(lines, "**版本:** " .. (E.version or "?"))
    table.insert(lines, "**反馈条数:** " .. #history)
    table.insert(lines, "")
    table.insert(lines, "---")

    for i, entry in ipairs(history) do
      local typeInfo = feedbackTypeByKey[entry.type] or feedbackTypeByKey["other"]
      table.insert(lines, "")
      table.insert(lines, "### " .. typeInfo.label .. " #" .. i)
      table.insert(lines, "")
      table.insert(lines, "- **玩家:** " .. (entry.player or "?") .. " (Lv." .. tostring(entry.level or 0) .. ")")
      table.insert(lines, "- **区域:** " .. (entry.zone or ""))
      table.insert(lines, "- **插件版本:** " .. (entry.version or "?"))
      if entry.context and entry.context ~= "" then
        table.insert(lines, "- **相关内容:** " .. entry.context)
      end
      table.insert(lines, "")
      table.insert(lines, "> " .. (entry.content or ""))
    end

    ShowExport(table.concat(lines, "\n"))
  end

  -- 导出单条反馈
  local function ExportSingleFeedback(entry)
    if not entry then return end
    local typeInfo = feedbackTypeByKey[entry.type] or feedbackTypeByKey["other"]

    local lines = {}
    table.insert(lines, "## " .. typeInfo.label)
    table.insert(lines, "")
    table.insert(lines, "**环境:**")
    table.insert(lines, "- EpochCN 版本: " .. (entry.version or "?"))
    table.insert(lines, "- 角色: " .. (entry.player or "?") .. " (Lv." .. tostring(entry.level or 0) .. ")")
    table.insert(lines, "- 区域: " .. (entry.zone or ""))
    table.insert(lines, "")
    if entry.context and entry.context ~= "" then
      table.insert(lines, "**相关物品/NPC/任务:** " .. entry.context)
      table.insert(lines, "")
    end
    table.insert(lines, "**描述:**")
    table.insert(lines, "")
    table.insert(lines, entry.content or "")

    ShowExport(table.concat(lines, "\n"))
  end

  ---------------------------------------------------------------------------
  -- 反馈面板 UI
  ---------------------------------------------------------------------------
  local feedbackPanel = nil
  local selectedType = "translation"

  local function CreateFeedbackPanel()
    if feedbackPanel then return feedbackPanel end

    feedbackPanel = CreateFrame("Frame", "EpochCNFeedbackFrame", UIParent)
    feedbackPanel:SetSize(440, 400)
    feedbackPanel:SetPoint("CENTER")
    feedbackPanel:SetFrameStrata("DIALOG")
    feedbackPanel:SetMovable(true)
    feedbackPanel:EnableMouse(true)
    feedbackPanel:RegisterForDrag("LeftButton")
    feedbackPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    feedbackPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    feedbackPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true, tileSize = 32, edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    feedbackPanel:Hide()

    -- 标题
    local title = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", feedbackPanel, "TOP", 0, -16)
    title:SetText("|cff33ffccEpochCN|r 反馈")

    local close = CreateFrame("Button", nil, feedbackPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", feedbackPanel, "TOPRIGHT", -5, -5)

    -- 反馈类型选择
    local typeLabel = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    typeLabel:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 20, -44)
    typeLabel:SetText("|cffffd200反馈类型:|r")

    local typeButtons = {}
    feedbackPanel.typeIndicator = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    feedbackPanel.typeIndicator:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 90, -46)

    for i, ft in ipairs(feedbackTypes) do
      local btn = CreateFrame("Button", nil, feedbackPanel, "UIPanelButtonTemplate")
      btn:SetSize(76, 20)
      btn:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 20 + ((i - 1) % 5) * 80, -64)
      btn:SetText(ft.label)
      btn.key = ft.key
      btn:SetScript("OnClick", function(self)
        selectedType = self.key
        local info = feedbackTypeByKey[selectedType]
        feedbackPanel.typeIndicator:SetText(info.color .. info.label .. "|r - " .. info.desc)
      end)
      btn:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(ft.label, 1, 0.82, 0)
        GameTooltip:AddLine(ft.desc, 1, 1, 1, true)
        GameTooltip:Show()
      end)
      btn:SetScript("OnLeave", function() GameTooltip:Hide() end)
      typeButtons[i] = btn
    end

    -- 初始显示
    local initInfo = feedbackTypeByKey[selectedType]
    feedbackPanel.typeIndicator:SetText(initInfo.color .. initInfo.label .. "|r - " .. initInfo.desc)

    -- 相关内容输入（物品名/NPC名/任务名等）
    local contextLabel = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    contextLabel:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 20, -94)
    contextLabel:SetText("|cffffd200相关内容:|r (物品/NPC/任务名，可选)")

    local contextInput = CreateFrame("EditBox", "EpochCNFBContextInput", feedbackPanel, "InputBoxTemplate")
    contextInput:SetSize(390, 20)
    contextInput:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 24, -112)
    contextInput:SetAutoFocus(false)
    contextInput:SetMaxLetters(100)
    contextInput:SetText("")
    feedbackPanel.contextInput = contextInput

    -- 反馈内容输入
    local contentLabel = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    contentLabel:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 20, -140)
    contentLabel:SetText("|cffffd200详细描述:|r")

    -- 多行输入框（使用 ScrollFrame + EditBox）
    local scrollBg = CreateFrame("Frame", nil, feedbackPanel)
    scrollBg:SetPoint("TOPLEFT", feedbackPanel, "TOPLEFT", 18, -158)
    scrollBg:SetPoint("BOTTOMRIGHT", feedbackPanel, "BOTTOMRIGHT", -18, 80)
    scrollBg:SetBackdrop({
      bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
      edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
      tile = true, tileSize = 16, edgeSize = 12,
      insets = { left = 3, right = 3, top = 3, bottom = 3 },
    })
    scrollBg:SetBackdropColor(0, 0, 0, 0.6)

    local scrollFrame = CreateFrame("ScrollFrame", "EpochCNFBContentScroll", scrollBg, "UIPanelScrollFrameTemplate")
    scrollFrame:SetPoint("TOPLEFT", scrollBg, "TOPLEFT", 6, -6)
    scrollFrame:SetPoint("BOTTOMRIGHT", scrollBg, "BOTTOMRIGHT", -24, 6)

    local contentInput = CreateFrame("EditBox", "EpochCNFBContentInput", scrollFrame)
    contentInput:SetMultiLine(true)
    contentInput:SetFontObject(GameFontHighlightSmall)
    contentInput:SetWidth(370)
    contentInput:SetAutoFocus(false)
    contentInput:SetMaxLetters(500)
    contentInput:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    scrollFrame:SetScrollChild(contentInput)
    feedbackPanel.contentInput = contentInput

    -- 底部按钮
    local submitBtn = CreateFrame("Button", nil, feedbackPanel, "UIPanelButtonTemplate")
    submitBtn:SetSize(80, 24)
    submitBtn:SetPoint("BOTTOMLEFT", feedbackPanel, "BOTTOMLEFT", 20, 16)
    submitBtn:SetText("提交")
    submitBtn:SetScript("OnClick", function()
      local content = contentInput:GetText() or ""
      local context = contextInput:GetText() or ""
      if SubmitFeedback(selectedType, content, context) then
        contentInput:SetText("")
        contextInput:SetText("")
      end
    end)

    local exportBtn = CreateFrame("Button", nil, feedbackPanel, "UIPanelButtonTemplate")
    exportBtn:SetSize(80, 24)
    exportBtn:SetPoint("BOTTOM", feedbackPanel, "BOTTOM", 0, 16)
    exportBtn:SetText("导出全部")
    exportBtn:SetScript("OnClick", function()
      ExportAllFeedback()
    end)

    local historyBtn = CreateFrame("Button", nil, feedbackPanel, "UIPanelButtonTemplate")
    historyBtn:SetSize(80, 24)
    historyBtn:SetPoint("BOTTOMRIGHT", feedbackPanel, "BOTTOMRIGHT", -100, 16)
    historyBtn:SetText("历史")
    historyBtn:SetScript("OnClick", function()
      E:ShowFeedbackHistory()
    end)

    local closeBtn = CreateFrame("Button", nil, feedbackPanel, "UIPanelButtonTemplate")
    closeBtn:SetSize(60, 24)
    closeBtn:SetPoint("BOTTOMRIGHT", feedbackPanel, "BOTTOMRIGHT", -20, 16)
    closeBtn:SetText("关闭")
    closeBtn:SetScript("OnClick", function() feedbackPanel:Hide() end)

    -- 环境信息
    local envText = feedbackPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    envText:SetPoint("BOTTOMLEFT", feedbackPanel, "BOTTOMLEFT", 20, 44)
    envText:SetText("|cff666666" .. GetEnvironmentInfo() .. "|r")

    return feedbackPanel
  end

  function E:ToggleFeedbackPanel()
    local panel = CreateFeedbackPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 历史记录查看
  ---------------------------------------------------------------------------
  function E:ShowFeedbackHistory()
    local history = EpochCNDB.feedback.history
    if #history == 0 then
      E:Print("暂无反馈历史。")
      return
    end

    E:Print(string.format("|cff33ffcc反馈历史|r（共 %d 条）：", #history))
    local start = math.max(1, #history - 9)  -- 显示最近 10 条
    for i = start, #history do
      local entry = history[i]
      local typeInfo = feedbackTypeByKey[entry.type] or feedbackTypeByKey["other"]
      local preview = TruncateText(entry.content, 40)
      E:Print(string.format("  #%d %s%s|r: %s", i, typeInfo.color, typeInfo.label, preview))
    end
    E:Print("|cff888888使用 /ecn feedback export 导出全部，或 /ecn feedback clear 清空。|r")
  end

  ---------------------------------------------------------------------------
  -- 快速反馈（从 Tooltip 直接提交翻译问题）
  ---------------------------------------------------------------------------
  function E:QuickFeedbackFromTarget()
    local context = ""
    -- 尝试获取当前目标/鼠标悬停的名称作为上下文
    if UnitExists("target") then
      context = UnitName("target") or ""
    elseif GameTooltip and GameTooltip:IsShown() then
      local line1 = GameTooltipTextLeft1 and GameTooltipTextLeft1:GetText()
      if line1 then context = line1 end
    end

    -- 打开反馈面板并预填上下文
    local panel = CreateFeedbackPanel()
    panel:Show()
    if context ~= "" then
      panel.contextInput:SetText(context)
    end
    selectedType = "translation"
    local info = feedbackTypeByKey[selectedType]
    panel.typeIndicator:SetText(info.color .. info.label .. "|r - " .. info.desc)
  end

  ---------------------------------------------------------------------------
  -- 斜杠命令
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    if msg == "feedback" or msg == "fb" then
      E:ToggleFeedbackPanel()
      return true
    end

    if msg == "feedback export" or msg == "fb export" then
      ExportAllFeedback()
      return true
    end

    if msg == "feedback history" or msg == "fb history" then
      E:ShowFeedbackHistory()
      return true
    end

    if msg == "feedback clear" or msg == "fb clear" then
      local count = #(EpochCNDB.feedback.history or {})
      EpochCNDB.feedback.history = {}
      E:Print(string.format("已清空 %d 条反馈记录。", count))
      return true
    end

    if msg == "feedback quick" or msg == "fb quick" then
      E:QuickFeedbackFromTarget()
      return true
    end

    -- /ecn fb <类型> <内容> — 快速提交
    if string.find(msg, "^fb ") or string.find(msg, "^feedback ") then
      local prefix = string.find(msg, "^fb ") and "fb " or "feedback "
      local rest = string.sub(msg, string.len(prefix) + 1)
      local fbType, content = string.match(rest, "^(%S+)%s+(.+)$")
      if fbType and content then
        if not feedbackTypeByKey[fbType] then
          -- 类型不存在，整体当作内容
          content = rest
          fbType = "other"
        end
        SubmitFeedback(fbType, content, "")
        return true
      end
    end

    return false
  end)

  E:Debug("Feedback 模块已注册")
end)
