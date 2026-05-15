-- QuickChat.lua
-- 快捷短语系统
-- 为不熟悉英文的玩家提供常用游戏短语的中英双语快捷发送。
-- 支持预设短语和自定义短语，可选同时发送中英文。

EpochCN:RegisterModule("QuickChat", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  EpochCNDB.social.quickChatEnabled = EpochCNDB.social.quickChatEnabled ~= false
  EpochCNDB.social.quickChatBilingual = EpochCNDB.social.quickChatBilingual or false
  EpochCNDB.social.customPhrases = EpochCNDB.social.customPhrases or {}

  if not EpochCNDB.social.quickChatEnabled then return end

  -- 预设短语库：{ 分类, 中文, 英文, 快捷码 }
  local phrases = {
    -- 组队类
    { "group", "有人去%s吗？", "LFM %s", "lfm" },
    { "group", "找队伍去%s", "LFG %s", "lfg" },
    { "group", "需要坦克", "Need tank", "tank" },
    { "group", "需要治疗", "Need healer", "heal" },
    { "group", "需要输出", "Need DPS", "dps" },
    { "group", "满了", "Full", "full" },
    { "group", "组满了谢谢", "Group is full, thanks", "gfull" },
    { "group", "邀请我", "Invite me please", "inv" },
    -- 交易类
    { "trade", "收%s，密我", "WTB %s, PST", "wtb" },
    { "trade", "出%s，密我", "WTS %s, PST", "wts" },
    { "trade", "多少钱？", "How much?", "price" },
    { "trade", "可以便宜点吗？", "Can you go lower?", "lower" },
    { "trade", "成交", "Deal", "deal" },
    { "trade", "免费赠送%s", "Free %s", "free" },
    -- 战斗类
    { "combat", "集火%s", "Focus %s", "focus" },
    { "combat", "打断", "Interrupt", "kick" },
    { "combat", "准备好了", "Ready", "rdy" },
    { "combat", "没准备好", "Not ready", "nrdy" },
    { "combat", "等一下", "Wait please", "wait" },
    { "combat", "开怪", "Pulling", "pull" },
    { "combat", "别动让我拉", "Let me pull", "lmp" },
    { "combat", "加血", "Heal me", "healme" },
    { "combat", "没蓝了", "OOM", "oom" },
    { "combat", "跑！", "Run!", "run" },
    { "combat", "散开", "Spread", "spread" },
    { "combat", "集合", "Stack", "stack" },
    -- 社交类
    { "social", "你好", "Hello", "hi" },
    { "social", "谢谢", "Thank you", "ty" },
    { "social", "不客气", "You're welcome", "yw" },
    { "social", "抱歉", "Sorry", "sry" },
    { "social", "再见", "Bye", "bye" },
    { "social", "做得好", "Good job", "gj" },
    { "social", "干得漂亮", "Nice", "nice" },
    { "social", "我是中国玩家", "I'm a Chinese player", "cn" },
    { "social", "有中文插件吗？", "Do you have Chinese addon?", "addon" },
    -- 副本类
    { "dungeon", "需要buff", "Buffs please", "buff" },
    { "dungeon", "我来数321开怪", "Pulling in 3, 2, 1", "321" },
    { "dungeon", "跟紧", "Stay close", "close" },
    { "dungeon", "这个给我", "Can I need this?", "need" },
    { "dungeon", "随便拿", "Greed it", "greed" },
    { "dungeon", "全部贪婪", "All greed", "agreed" },
  }

  -- 快捷码索引
  local phraseByCode = {}
  for _, p in ipairs(phrases) do
    phraseByCode[p[4]] = p
  end

  ---------------------------------------------------------------------------
  -- 发送逻辑
  ---------------------------------------------------------------------------
  local function GetChatTarget()
    -- 自动检测当前应该发送到的频道
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then return "RAID" end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then return "PARTY" end
    return "SAY"
  end

  local function SendPhrase(chinese, english, channel, extra)
    channel = channel or GetChatTarget()

    -- 替换 %s 占位符
    if extra and extra ~= "" then
      chinese = string.gsub(chinese, "%%s", extra)
      english = string.gsub(english, "%%s", extra)
    else
      chinese = string.gsub(chinese, "%%s", "")
      english = string.gsub(english, "%%s", "")
    end

    -- 清理多余空格
    chinese = string.gsub(chinese, "%s+", " ")
    chinese = string.gsub(chinese, "^%s+", "")
    chinese = string.gsub(chinese, "%s+$", "")
    english = string.gsub(english, "%s+", " ")
    english = string.gsub(english, "^%s+", "")
    english = string.gsub(english, "%s+$", "")

    if EpochCNDB.social.quickChatBilingual then
      -- 双语模式：发送 "中文 (English)"
      local combined = chinese .. " (" .. english .. ")"
      SendChatMessage(combined, channel)
    else
      -- 默认只发中文（队伍内多为中文玩家）
      SendChatMessage(chinese, channel)
    end
  end

  ---------------------------------------------------------------------------
  -- /qc 快捷命令
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QC1 = "/qc"
  SlashCmdList["EPOCHCN_QC"] = function(msg)
    if not msg or msg == "" then
      E:Print("|cff33ffcc快捷短语|r - 使用方法:")
      E:Print("  /qc <快捷码> [参数] - 发送预设短语")
      E:Print("  /qc list [分类] - 查看短语列表")
      E:Print("  /qc bilingual - 切换双语模式")
      E:Print("  示例: /qc lfm ICC  →  有人去ICC吗？")
      E:Print("  示例: /qc ty       →  谢谢")
      return
    end

    local cmd = string.lower(msg)

    -- 切换双语模式
    if cmd == "bilingual" or cmd == "bi" then
      EpochCNDB.social.quickChatBilingual = not EpochCNDB.social.quickChatBilingual
      if EpochCNDB.social.quickChatBilingual then
        E:Print("|cff33ff99双语模式已开启|r - 将同时发送中英文。")
      else
        E:Print("|cffff9900双语模式已关闭|r - 仅发送中文。")
      end
      return
    end

    -- 列出短语
    if string.find(cmd, "^list") then
      local category = string.match(cmd, "^list%s+(.+)$")
      E:Print("|cff33ffcc可用快捷短语：|r")
      local lastCat = ""
      for _, p in ipairs(phrases) do
        if not category or p[1] == category then
          if p[1] ~= lastCat then
            lastCat = p[1]
            local catNames = {
              group = "组队",
              trade = "交易",
              combat = "战斗",
              social = "社交",
              dungeon = "副本",
            }
            E:Print("  |cffffd200[" .. (catNames[lastCat] or lastCat) .. "]|r")
          end
          E:Print(string.format("    |cff88ccff%s|r → %s / %s", p[4], p[2], p[3]))
        end
      end
      E:Print("|cff888888分类: group, trade, combat, social, dungeon|r")
      return
    end

    -- 解析命令：快捷码 + 可选参数
    local code, extra = string.match(cmd, "^(%S+)%s*(.*)$")
    if not code then return end

    local phrase = phraseByCode[code]
    if phrase then
      SendPhrase(phrase[2], phrase[3], nil, extra)
    else
      -- 检查自定义短语
      local custom = EpochCNDB.social.customPhrases[code]
      if custom then
        SendPhrase(custom.cn or "", custom.en or custom.cn or "", nil, extra)
      else
        E:Print("|cffff6666未知快捷码: " .. code .. "|r。使用 /qc list 查看可用短语。")
      end
    end
  end

  ---------------------------------------------------------------------------
  -- 自定义短语管理
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    -- /ecn phrase add <code> <中文> | <英文>
    if string.find(msg, "^phrase add") then
      local args = string.match(msg, "^phrase add%s+(.+)$")
      if not args then
        E:Print("用法: /ecn phrase add <快捷码> <中文> | <英文>")
        return true
      end
      local code, rest = string.match(args, "^(%S+)%s+(.+)$")
      if not code or not rest then
        E:Print("用法: /ecn phrase add <快捷码> <中文> | <英文>")
        return true
      end
      local cn, en = string.match(rest, "^(.-)%s*|%s*(.+)$")
      if not cn then
        cn = rest
        en = rest
      end
      EpochCNDB.social.customPhrases[code] = { cn = cn, en = en }
      E:Print(string.format("|cff33ff99已添加自定义短语|r: %s → %s | %s", code, cn, en))
      return true
    end

    if string.find(msg, "^phrase remove") then
      local code = string.match(msg, "^phrase remove%s+(%S+)")
      if code and EpochCNDB.social.customPhrases[code] then
        EpochCNDB.social.customPhrases[code] = nil
        E:Print("已删除自定义短语: " .. code)
      else
        E:Print("未找到自定义短语: " .. (code or ""))
      end
      return true
    end

    if msg == "phrase list" then
      local count = 0
      E:Print("|cff33ffcc自定义短语：|r")
      for code, data in pairs(EpochCNDB.social.customPhrases) do
        count = count + 1
        E:Print(string.format("  |cff88ccff%s|r → %s | %s", code, data.cn or "", data.en or ""))
      end
      if count == 0 then
        E:Print("  暂无自定义短语。使用 /ecn phrase add <快捷码> <中文> | <英文> 添加。")
      end
      return true
    end

    if msg == "qc" then
      E:ToggleQuickChatPanel()
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 快捷短语面板 UI
  ---------------------------------------------------------------------------
  local qcPanel = nil
  local qcButtons = {}

  local function CreateQuickChatPanel()
    if qcPanel then return qcPanel end

    qcPanel = CreateFrame("Frame", "EpochCNQuickChatFrame", UIParent)
    qcPanel:SetSize(320, 400)
    qcPanel:SetPoint("CENTER", UIParent, "CENTER", 200, 0)
    qcPanel:SetFrameStrata("DIALOG")
    qcPanel:SetMovable(true)
    qcPanel:EnableMouse(true)
    qcPanel:RegisterForDrag("LeftButton")
    qcPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    qcPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    qcPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true,
      tileSize = 32,
      edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    qcPanel:Hide()

    -- 标题
    local title = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", qcPanel, "TOP", 0, -14)
    title:SetText("|cff33ffccEpochCN|r 快捷短语")

    -- 关闭按钮
    local close = CreateFrame("Button", nil, qcPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", qcPanel, "TOPRIGHT", -5, -5)

    -- 双语模式切换
    local biBtn = CreateFrame("Button", nil, qcPanel, "UIPanelButtonTemplate")
    biBtn:SetSize(80, 20)
    biBtn:SetPoint("TOPRIGHT", qcPanel, "TOPRIGHT", -32, -14)
    biBtn:SetScript("OnClick", function(self)
      EpochCNDB.social.quickChatBilingual = not EpochCNDB.social.quickChatBilingual
      if EpochCNDB.social.quickChatBilingual then
        self:SetText("|cff33ff99双语|r")
      else
        self:SetText("中文")
      end
    end)
    if EpochCNDB.social.quickChatBilingual then
      biBtn:SetText("|cff33ff99双语|r")
    else
      biBtn:SetText("中文")
    end

    -- 分类标签页
    local categories = {
      { key = "social", label = "社交" },
      { key = "group", label = "组队" },
      { key = "combat", label = "战斗" },
      { key = "trade", label = "交易" },
      { key = "dungeon", label = "副本" },
    }

    local currentCategory = "social"
    local buttonArea = CreateFrame("Frame", nil, qcPanel)
    buttonArea:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 14, -70)
    buttonArea:SetPoint("BOTTOMRIGHT", qcPanel, "BOTTOMRIGHT", -14, 40)

    local function RefreshButtons()
      -- 清除旧按钮
      for _, btn in ipairs(qcButtons) do
        btn:Hide()
      end
      qcButtons = {}

      local index = 0
      for _, p in ipairs(phrases) do
        if p[1] == currentCategory then
          index = index + 1
          local col = ((index - 1) % 2)
          local row = math.floor((index - 1) / 2)

          local btn = CreateFrame("Button", nil, buttonArea, "UIPanelButtonTemplate")
          btn:SetSize(138, 24)
          btn:SetPoint("TOPLEFT", buttonArea, "TOPLEFT", col * 144, -row * 28)
          btn:SetText(p[2])
          btn.phrase = p

          btn:SetScript("OnClick", function(self)
            SendPhrase(self.phrase[2], self.phrase[3], nil, "")
          end)
          btn:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
            GameTooltip:SetText(self.phrase[2], 1, 0.82, 0)
            GameTooltip:AddLine("英文: " .. self.phrase[3], 0.7, 0.7, 0.7)
            GameTooltip:AddLine("快捷码: /qc " .. self.phrase[4], 0.5, 0.8, 1)
            GameTooltip:Show()
          end)
          btn:SetScript("OnLeave", function() GameTooltip:Hide() end)

          table.insert(qcButtons, btn)
        end
      end
    end

    -- 分类标签按钮
    for i, cat in ipairs(categories) do
      local tabBtn = CreateFrame("Button", nil, qcPanel, "UIPanelButtonTemplate")
      tabBtn:SetSize(52, 20)
      tabBtn:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 14 + (i - 1) * 56, -42)
      tabBtn:SetText(cat.label)
      tabBtn:SetScript("OnClick", function()
        currentCategory = cat.key
        RefreshButtons()
      end)
    end

    -- 底部提示
    local helpText = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    helpText:SetPoint("BOTTOMLEFT", qcPanel, "BOTTOMLEFT", 16, 16)
    helpText:SetWidth(288)
    helpText:SetJustifyH("LEFT")
    helpText:SetText("|cff888888点击按钮发送到当前频道。命令行: /qc <快捷码> [参数]|r")

    RefreshButtons()
    return qcPanel
  end

  function E:ToggleQuickChatPanel()
    local panel = CreateQuickChatPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- /qcw 密语快捷短语（向目标或指定玩家发送）
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCW1 = "/qcw"
  SlashCmdList["EPOCHCN_QCW"] = function(msg)
    if not msg or msg == "" then
      E:Print("|cff33ffcc密语快捷短语|r - 向目标发送短语:")
      E:Print("  /qcw <快捷码> - 向当前目标密语")
      E:Print("  /qcw <玩家名> <快捷码> - 向指定玩家密语")
      return
    end

    local target, code
    -- 尝试解析为 "玩家名 快捷码"
    local arg1, arg2 = string.match(msg, "^(%S+)%s+(%S+)")
    if arg2 and phraseByCode[string.lower(arg2)] then
      target = arg1
      code = string.lower(arg2)
    elseif phraseByCode[string.lower(msg)] then
      -- 只有快捷码，向当前目标发送
      code = string.lower(msg)
      if UnitIsPlayer("target") then
        target = StripRealmName(UnitName("target"))
      end
    else
      -- 第一个参数可能是快捷码
      local c = string.match(msg, "^(%S+)")
      if c and phraseByCode[string.lower(c)] then
        code = string.lower(c)
        if UnitIsPlayer("target") then
          target = StripRealmName(UnitName("target"))
        end
      else
        E:Print("|cffff6666未知快捷码。使用 /qc list 查看可用短语。|r")
        return
      end
    end

    if not target then
      E:Print("|cffff6666请先选中一个玩家目标，或指定玩家名。|r")
      return
    end

    local phrase = phraseByCode[code]
    if phrase then
      local chinese = phrase[2]
      local english = phrase[3]
      chinese = string.gsub(chinese, "%%s", "")
      english = string.gsub(english, "%%s", "")
      chinese = string.gsub(chinese, "%s+", " ")
      chinese = string.gsub(chinese, "^%s+", "")
      chinese = string.gsub(chinese, "%s+$", "")

      if EpochCNDB.social.quickChatBilingual then
        english = string.gsub(english, "%s+", " ")
        english = string.gsub(english, "^%s+", "")
        english = string.gsub(english, "%s+$", "")
        SendChatMessage(chinese .. " (" .. english .. ")", "WHISPER", nil, target)
      else
        -- 如果目标是中文玩家，发中文；否则发英文
        local isCN = E.IsChinesePlayer and E:IsChinesePlayer(target)
        if isCN then
          SendChatMessage(chinese, "WHISPER", nil, target)
        else
          english = string.gsub(english, "%s+", " ")
          english = string.gsub(english, "^%s+", "")
          english = string.gsub(english, "%s+$", "")
          SendChatMessage(english, "WHISPER", nil, target)
        end
      end
    end
  end

  ---------------------------------------------------------------------------
  -- /qcs 对说（SAY）频道发送快捷短语
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCS1 = "/qcs"
  SlashCmdList["EPOCHCN_QCS"] = function(msg)
    if not msg or msg == "" then
      E:Print("用法: /qcs <快捷码> [参数] - 在说话频道发送短语")
      return
    end

    local code, extra = string.match(string.lower(msg), "^(%S+)%s*(.*)$")
    if not code then return end

    local phrase = phraseByCode[code]
    if phrase then
      SendPhrase(phrase[2], phrase[3], "SAY", extra)
    else
      E:Print("|cffff6666未知快捷码: " .. code .. "|r")
    end
  end

  local function StripRealmName(fullName)
    if not fullName then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)")
    end
    return fullName
  end

  E:Debug("QuickChat 模块已注册（含面板、密语快捷、SAY快捷）")
end)
