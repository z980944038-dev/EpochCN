-- LFGBoard.lua
-- 中文玩家组队招募板
-- 通过 addon channel 在公会/队伍/自定义频道内广播组队需求，
-- 提供游戏内可浏览的组队列表面板。

EpochCN:RegisterModule("LFGBoard", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  EpochCNDB.social.lfgEnabled = EpochCNDB.social.lfgEnabled ~= false

  if not EpochCNDB.social.lfgEnabled then return end

  local LFG_PREFIX = "EPOCHCN_LFG"
  local LFG_EXPIRE_TIME = 300     -- 招募信息过期时间（秒）
  local LFG_BROADCAST_CD = 30     -- 广播冷却（秒）
  local LFG_REPOST_INTERVAL = 120 -- 自动重发间隔（秒）
  local MAX_LFG_ENTRIES = 50      -- 最大列表条目

  -- 注册 addon 消息前缀
  if RegisterAddonMessagePrefix then
    pcall(RegisterAddonMessagePrefix, LFG_PREFIX)
  end

  -- 副本/活动中文名映射
  local dungeonNames = {
    -- 经典副本
    ["RFC"] = "怒焰裂谷",
    ["DM"] = "死亡矿井",
    ["WC"] = "哀嚎洞穴",
    ["SFK"] = "影牙城堡",
    ["BFD"] = "黑暗深渊",
    ["STOCKS"] = "监狱",
    ["GNOMER"] = "诺莫瑞根",
    ["SM"] = "血色修道院",
    ["RFD"] = "剃刀高地",
    ["RFK"] = "剃刀沼泽",
    ["ULDA"] = "奥达曼",
    ["ZF"] = "祖尔法拉克",
    ["MARA"] = "玛拉顿",
    ["ST"] = "阿塔哈卡神庙",
    ["BRD"] = "黑石深渊",
    ["LBRS"] = "黑石塔下层",
    ["UBRS"] = "黑石塔上层",
    ["STRAT"] = "斯坦索姆",
    ["SCHOLO"] = "通灵学院",
    ["DIRE"] = "厄运之槌",
    -- TBC 副本
    ["RAMPS"] = "地狱火城墙",
    ["BF"] = "血熔炉",
    ["SP"] = "奴隶围栏",
    ["UB"] = "幽暗沼泽",
    ["MT"] = "法力陵墓",
    ["AC"] = "奥金尼地穴",
    ["SH"] = "塞泰克大厅",
    ["SL"] = "暗影迷宫",
    ["OHF"] = "旧希尔斯布莱德丘陵",
    ["BM"] = "黑色沼泽",
    ["MECH"] = "能源舰",
    ["BOT"] = "生态船",
    ["ARC"] = "禁魔监狱",
    ["SV"] = "蒸汽地窖",
    ["MGT"] = "魔导师平台",
    -- WotLK 副本
    ["UK"] = "乌特加德城堡",
    ["NEXUS"] = "魔枢",
    ["AN"] = "艾卓-尼鲁布",
    ["OK"] = "达克萨隆要塞",
    ["VH"] = "紫罗兰监狱",
    ["DTK"] = "达克萨隆要塞",
    ["GD"] = "古达克",
    ["HOS"] = "岩石大厅",
    ["HOL"] = "闪电大厅",
    ["COS"] = "净化斯坦索姆",
    ["UP"] = "乌特加德之巅",
    ["OCCI"] = "魔环",
    ["TOC5"] = "冠军的试炼",
    ["FOS"] = "灵魂熔炉",
    ["POS"] = "映像大厅",
    ["HOR"] = "恐惧之厅",
    -- 团本
    ["MC"] = "熔火之心",
    ["BWL"] = "黑翼之巢",
    ["AQ20"] = "安其拉废墟",
    ["AQ40"] = "安其拉神殿",
    ["ZG"] = "祖尔格拉布",
    ["ONY"] = "奥妮克希亚的巢穴",
    ["NAXX"] = "纳克萨玛斯",
    ["OS"] = "黑曜石圣殿",
    ["VOA"] = "阿尔卡冯的宝库",
    ["EYE"] = "永恒之眼",
    ["ULDU"] = "奥杜尔",
    ["TOC"] = "十字军的试炼",
    ["ICC"] = "冰冠堡垒",
    ["RS"] = "红玉圣殿",
    -- PvP
    ["BG"] = "战场",
    ["ARENA"] = "竞技场",
    ["WSG"] = "战歌峡谷",
    ["AB"] = "阿拉希盆地",
    ["AV"] = "奥特兰克山谷",
    ["EOTS"] = "风暴之眼",
    ["SOTA"] = "远古海滩",
    ["IOC"] = "征服之岛",
    -- 其他
    ["WORLD"] = "世界Boss",
    ["QUEST"] = "任务",
    ["OTHER"] = "其他",
  }

  -- 职业角色需求
  local roleNames = {
    ["TANK"] = "坦克",
    ["HEALER"] = "治疗",
    ["DPS"] = "输出",
    ["ANY"] = "任意",
  }

  -- 运行时数据
  local lfgEntries = {}       -- 当前招募列表
  local myPosting = nil       -- 我的发布
  local lastBroadcast = 0     -- 上次广播时间
  local repostTimer = 0       -- 自动重发计时器
  local lfgPanel = nil        -- UI 面板
  local newEntryNotified = {} -- 已通知过的发布（避免重复通知）

  local frame = CreateFrame("Frame")

  ---------------------------------------------------------------------------
  -- 工具函数
  ---------------------------------------------------------------------------
  local function StripRealmName(fullName)
    if not fullName then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)")
    end
    return fullName
  end

  local function GetDungeonDisplayName(code)
    return dungeonNames[string.upper(code or "")] or code or "未知"
  end

  local function GetRoleDisplayName(code)
    return roleNames[string.upper(code or "")] or code or ""
  end

  local function CleanupExpired()
    local now = time()
    local newEntries = {}
    for _, entry in ipairs(lfgEntries) do
      if now - (entry.timestamp or 0) < LFG_EXPIRE_TIME then
        table.insert(newEntries, entry)
      end
    end
    lfgEntries = newEntries
  end

  ---------------------------------------------------------------------------
  -- 广播与接收
  ---------------------------------------------------------------------------
  -- 消息格式: POST:副本代码:最低等级:需坦:需治:需DPS:备注
  -- 消息格式: CANCEL:发布者

  local function BroadcastLFG(entry)
    if not entry then return end
    local now = time()
    if now - lastBroadcast < LFG_BROADCAST_CD then
      E:Print("|cffff6666广播冷却中，请稍后再试。|r")
      return
    end
    lastBroadcast = now

    local msg = string.format("POST:%s:%d:%d:%d:%d:%s",
      entry.dungeon or "OTHER",
      entry.minLevel or 1,
      entry.needTank and 1 or 0,
      entry.needHealer and 1 or 0,
      entry.needDPS or 0,
      entry.note or ""
    )

    -- 向公会广播
    if IsInGuild and IsInGuild() then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "GUILD")
    end

    -- 向自定义频道广播
    local channelNum = GetChannelName("EpochCN")
    if channelNum and channelNum > 0 then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "CHANNEL")
    end

    E:Print("|cff33ffcc组队信息已广播。|r")
  end

  local function CancelLFG()
    if not myPosting then
      E:Print("你当前没有发布组队信息。")
      return
    end

    local msg = "CANCEL:" .. (StripRealmName(UnitName("player")) or "")

    if IsInGuild and IsInGuild() then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "GUILD")
    end
    local channelNum = GetChannelName("EpochCN")
    if channelNum and channelNum > 0 then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "CHANNEL")
    end

    myPosting = nil
    E:Print("已取消组队发布。")
  end

  local function OnLFGMessage(prefix, message, channel, sender)
    if prefix ~= LFG_PREFIX then return end
    sender = StripRealmName(sender)
    if not sender then return end

    local msgType, rest = string.match(message, "^(%u+):(.*)$")
    if not msgType then return end

    if msgType == "POST" then
      local dungeon, minLevel, needTank, needHealer, needDPS, note =
        string.match(rest, "^([^:]*):([^:]*):([^:]*):([^:]*):([^:]*):(.*)$")

      if not dungeon then return end

      -- 移除该玩家的旧发布
      local newEntries = {}
      for _, entry in ipairs(lfgEntries) do
        if entry.sender ~= sender then
          table.insert(newEntries, entry)
        end
      end
      lfgEntries = newEntries

      -- 添加新发布
      table.insert(lfgEntries, {
        sender = sender,
        dungeon = dungeon,
        dungeonName = GetDungeonDisplayName(dungeon),
        minLevel = tonumber(minLevel) or 1,
        needTank = needTank == "1",
        needHealer = needHealer == "1",
        needDPS = tonumber(needDPS) or 0,
        note = note or "",
        timestamp = time(),
      })

      -- 新招募到达通知（不是自己发的，且未通知过）
      local notifyKey = sender .. ":" .. dungeon .. ":" .. tostring(time())
      if sender ~= StripRealmName(UnitName("player")) and not newEntryNotified[sender] then
        newEntryNotified[sender] = true
        local displayName = GetDungeonDisplayName(dungeon)
        local needs = {}
        if needTank == "1" then table.insert(needs, "坦克") end
        if needHealer == "1" then table.insert(needs, "治疗") end
        local dpsNum = tonumber(needDPS) or 0
        if dpsNum > 0 then table.insert(needs, "DPS x" .. dpsNum) end
        local needStr = #needs > 0 and (" 需要: " .. table.concat(needs, "/")) or ""
        E:Print(string.format("|cff88ccff[招募]|r %s 招人去 |cffffd200%s|r%s%s",
          sender, displayName, needStr, (note and note ~= "") and (" - " .. note) or ""))
        -- 触发小地图按钮闪烁
        if E.FlashMinimapButton then E:FlashMinimapButton() end
      end

      -- 限制列表大小
      while #lfgEntries > MAX_LFG_ENTRIES do
        table.remove(lfgEntries, 1)
      end

      -- 刷新面板
      if lfgPanel and lfgPanel:IsShown() then
        E:RefreshLFGPanel()
      end
      return
    end

    if msgType == "CANCEL" then
      local newEntries = {}
      for _, entry in ipairs(lfgEntries) do
        if entry.sender ~= sender then
          table.insert(newEntries, entry)
        end
      end
      lfgEntries = newEntries

      if lfgPanel and lfgPanel:IsShown() then
        E:RefreshLFGPanel()
      end
      return
    end
  end

  ---------------------------------------------------------------------------
  -- UI 面板
  ---------------------------------------------------------------------------
  local entryFrames = {}

  local function CreateLFGPanel()
    if lfgPanel then return lfgPanel end

    lfgPanel = CreateFrame("Frame", "EpochCNLFGFrame", UIParent)
    lfgPanel:SetSize(420, 460)
    lfgPanel:SetPoint("CENTER")
    lfgPanel:SetFrameStrata("DIALOG")
    lfgPanel:SetMovable(true)
    lfgPanel:EnableMouse(true)
    lfgPanel:RegisterForDrag("LeftButton")
    lfgPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    lfgPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    lfgPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true,
      tileSize = 32,
      edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    lfgPanel:Hide()

    -- 标题
    local title = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", lfgPanel, "TOP", 0, -18)
    title:SetText("|cff33ffccEpochCN|r 组队招募板")

    -- 关闭按钮
    local close = CreateFrame("Button", nil, lfgPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", lfgPanel, "TOPRIGHT", -5, -5)

    -- 刷新按钮
    local refreshBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    refreshBtn:SetSize(60, 22)
    refreshBtn:SetPoint("TOPRIGHT", lfgPanel, "TOPRIGHT", -36, -16)
    refreshBtn:SetText("刷新")
    refreshBtn:SetScript("OnClick", function()
      CleanupExpired()
      E:RefreshLFGPanel()
      E:Print("招募列表已刷新。")
    end)

    -- 列表区域
    local listHeader = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    listHeader:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -48)
    listHeader:SetText("|cffffd200发布者        副本          需求          备注|r")

    -- 创建列表行
    for i = 1, 8 do
      local row = CreateFrame("Button", nil, lfgPanel)
      row:SetSize(380, 28)
      row:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -68 - (i - 1) * 30)
      row:EnableMouse(true)

      local bg = row:CreateTexture(nil, "BACKGROUND")
      bg:SetAllPoints()
      bg:SetTexture("Interface\\Buttons\\UI-Listbox-Highlight2")
      bg:SetAlpha(0)
      row.bg = bg

      local senderText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      senderText:SetPoint("LEFT", row, "LEFT", 4, 0)
      senderText:SetWidth(80)
      senderText:SetJustifyH("LEFT")
      row.senderText = senderText

      local dungeonText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      dungeonText:SetPoint("LEFT", row, "LEFT", 88, 0)
      dungeonText:SetWidth(90)
      dungeonText:SetJustifyH("LEFT")
      row.dungeonText = dungeonText

      local needText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      needText:SetPoint("LEFT", row, "LEFT", 182, 0)
      needText:SetWidth(90)
      needText:SetJustifyH("LEFT")
      row.needText = needText

      local noteText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      noteText:SetPoint("LEFT", row, "LEFT", 276, 0)
      noteText:SetWidth(100)
      noteText:SetJustifyH("LEFT")
      row.noteText = noteText

      row:SetScript("OnEnter", function(self)
        self.bg:SetAlpha(0.3)
        if self.entry then
          GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
          GameTooltip:SetText(self.entry.dungeonName or "未知", 1, 0.82, 0)
          GameTooltip:AddLine("发布者: " .. (self.entry.sender or ""), 1, 1, 1)
          if self.entry.needTank then GameTooltip:AddLine("需要坦克", 0.2, 0.6, 1) end
          if self.entry.needHealer then GameTooltip:AddLine("需要治疗", 0.2, 1, 0.2) end
          if self.entry.needDPS and self.entry.needDPS > 0 then
            GameTooltip:AddLine("需要输出 x" .. self.entry.needDPS, 1, 0.2, 0.2)
          end
          if self.entry.note and self.entry.note ~= "" then
            GameTooltip:AddLine("备注: " .. self.entry.note, 0.8, 0.8, 0.8)
          end
          GameTooltip:AddLine(" ")
          GameTooltip:AddLine("左键点击密语该玩家", 0.5, 0.5, 0.5)
          GameTooltip:Show()
        end
      end)
      row:SetScript("OnLeave", function(self)
        self.bg:SetAlpha(0)
        GameTooltip:Hide()
      end)
      row:SetScript("OnClick", function(self)
        if self.entry and self.entry.sender then
          ChatFrame_OpenChat("/w " .. self.entry.sender .. " ")
        end
      end)

      row:Hide()
      entryFrames[i] = row
    end

    -- 底部：发布区域
    local postHeader = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    postHeader:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -320)
    postHeader:SetText("|cffffd200快速发布|r")

    -- 副本输入
    local dungeonLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dungeonLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -342)
    dungeonLabel:SetText("副本代码:")

    local dungeonInput = CreateFrame("EditBox", "EpochCNLFGDungeonInput", lfgPanel, "InputBoxTemplate")
    dungeonInput:SetSize(80, 20)
    dungeonInput:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 90, -340)
    dungeonInput:SetAutoFocus(false)
    dungeonInput:SetMaxLetters(20)
    dungeonInput:SetText("")

    -- 备注输入
    local noteLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    noteLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 180, -342)
    noteLabel:SetText("备注:")

    local noteInput = CreateFrame("EditBox", "EpochCNLFGNoteInput", lfgPanel, "InputBoxTemplate")
    noteInput:SetSize(120, 20)
    noteInput:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 210, -340)
    noteInput:SetAutoFocus(false)
    noteInput:SetMaxLetters(40)
    noteInput:SetText("")

    -- 需求勾选
    local tankCheck = CreateFrame("CheckButton", nil, lfgPanel, "OptionsCheckButtonTemplate")
    tankCheck:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -368)
    tankCheck:SetChecked(false)
    local tankLabel = tankCheck:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    tankLabel:SetPoint("LEFT", tankCheck, "RIGHT", 0, 1)
    tankLabel:SetText("坦克")

    local healerCheck = CreateFrame("CheckButton", nil, lfgPanel, "OptionsCheckButtonTemplate")
    healerCheck:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 90, -368)
    healerCheck:SetChecked(false)
    local healerLabel = healerCheck:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    healerLabel:SetPoint("LEFT", healerCheck, "RIGHT", 0, 1)
    healerLabel:SetText("治疗")

    local dpsLabel2 = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dpsLabel2:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 160, -372)
    dpsLabel2:SetText("DPS需求数:")

    local dpsInput = CreateFrame("EditBox", "EpochCNLFGDPSInput", lfgPanel, "InputBoxTemplate")
    dpsInput:SetSize(30, 20)
    dpsInput:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 230, -370)
    dpsInput:SetAutoFocus(false)
    dpsInput:SetMaxLetters(1)
    dpsInput:SetText("0")
    dpsInput:SetNumeric(true)

    -- 发布按钮
    local postBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    postBtn:SetSize(80, 24)
    postBtn:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 20, -400)
    postBtn:SetText("发布")
    postBtn:SetScript("OnClick", function()
      local dungeon = dungeonInput:GetText() or "OTHER"
      if dungeon == "" then dungeon = "OTHER" end
      local note = noteInput:GetText() or ""
      local needTank = tankCheck:GetChecked() and true or false
      local needHealer = healerCheck:GetChecked() and true or false
      local needDPS = tonumber(dpsInput:GetText()) or 0

      myPosting = {
        dungeon = string.upper(dungeon),
        minLevel = UnitLevel("player") or 1,
        needTank = needTank,
        needHealer = needHealer,
        needDPS = needDPS,
        note = note,
      }

      BroadcastLFG(myPosting)
      CleanupExpired()
      E:RefreshLFGPanel()
    end)

    -- 取消按钮
    local cancelBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    cancelBtn:SetSize(80, 24)
    cancelBtn:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 110, -400)
    cancelBtn:SetText("取消发布")
    cancelBtn:SetScript("OnClick", function()
      CancelLFG()
      E:RefreshLFGPanel()
    end)

    -- 提示
    local helpText = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    helpText:SetPoint("BOTTOMLEFT", lfgPanel, "BOTTOMLEFT", 20, 14)
    helpText:SetWidth(380)
    helpText:SetJustifyH("LEFT")
    helpText:SetText("|cff888888副本代码示例: ICC, NAXX, TOC, BRD, SM, DM 等。点击列表行可密语对方。|r")

    return lfgPanel
  end

  function E:RefreshLFGPanel()
    if not lfgPanel then return end
    CleanupExpired()

    for i = 1, 8 do
      local row = entryFrames[i]
      local entry = lfgEntries[i]
      if entry then
        row.entry = entry
        row.senderText:SetText(entry.sender or "")
        row.dungeonText:SetText(entry.dungeonName or entry.dungeon or "")

        local needs = {}
        if entry.needTank then table.insert(needs, "|cff3399ff坦|r") end
        if entry.needHealer then table.insert(needs, "|cff33ff33治|r") end
        if entry.needDPS and entry.needDPS > 0 then
          table.insert(needs, "|cffff3333DPS x" .. entry.needDPS .. "|r")
        end
        row.needText:SetText(table.concat(needs, " "))
        row.noteText:SetText(entry.note or "")
        row:Show()
      else
        row.entry = nil
        row:Hide()
      end
    end
  end

  function E:ToggleLFGPanel()
    local panel = CreateLFGPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      CleanupExpired()
      E:RefreshLFGPanel()
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 斜杠命令
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    if msg == "lfg" then
      E:ToggleLFGPanel()
      return true
    end

    if msg == "lfg cancel" then
      CancelLFG()
      return true
    end

    -- /ecn lfg post ICC 需要治疗速刷
    if string.find(msg, "^lfg post") then
      local args = string.match(msg, "^lfg post%s+(.+)$")
      if args then
        local dungeon = string.match(args, "^(%S+)")
        local note = string.match(args, "^%S+%s+(.+)$") or ""
        myPosting = {
          dungeon = string.upper(dungeon or "OTHER"),
          minLevel = UnitLevel("player") or 1,
          needTank = string.find(note, "坦") ~= nil,
          needHealer = string.find(note, "治") ~= nil or string.find(note, "奶") ~= nil,
          needDPS = 0,
          note = note,
        }
        BroadcastLFG(myPosting)
      else
        E:Print("用法: /ecn lfg post <副本代码> [备注]")
        E:Print("示例: /ecn lfg post ICC 需要治疗速刷")
      end
      return true
    end

    if msg == "lfg refresh" then
      CleanupExpired()
      local count = #lfgEntries
      E:Print(string.format("当前招募列表: %d 条", count))
      for i, entry in ipairs(lfgEntries) do
        if i <= 10 then
          E:Print(string.format("  [%s] %s - %s", entry.sender or "?", entry.dungeonName or entry.dungeon or "?", entry.note or ""))
        end
      end
      if count > 10 then
        E:Print("  ...使用 /ecn lfg 打开面板查看全部。")
      end
      return true
    end

    if msg == "lfg codes" or msg == "lfg help" then
      E:Print("|cff33ffcc组队招募板命令：|r")
      E:Print("  /ecn lfg - 打开招募面板")
      E:Print("  /ecn lfg post <代码> [备注] - 发布招募")
      E:Print("  /ecn lfg cancel - 取消我的招募")
      E:Print("  /ecn lfg refresh - 查看当前列表")
      E:Print("  /ecn lfg codes - 查看副本代码")
      E:Print("|cffffd200常用副本代码：|r")
      E:Print("  |cff88ccff经典|r: RFC DM WC SFK BFD SM RFD RFK ZF MARA ST BRD LBRS UBRS STRAT SCHOLO DIRE")
      E:Print("  |cff88ccff团本|r: MC BWL AQ20 AQ40 ZG ONY NAXX OS VOA EYE ULDU TOC ICC RS")
      E:Print("  |cff88ccffWotLK|r: UK NEXUS AN VH DTK HOS HOL COS UP TOC5 FOS POS HOR")
      E:Print("  |cff88ccff其他|r: WORLD(世界Boss) QUEST(任务) BG(战场) ARENA(竞技场)")
      return true
    end

    -- /ecn lfg apply <玩家名> - 向某个招募者申请
    if string.find(msg, "^lfg apply") then
      local target = string.match(msg, "^lfg apply%s+(%S+)")
      if target then
        -- 找到该玩家的招募信息
        local found = nil
        for _, entry in ipairs(lfgEntries) do
          if entry.sender == target then
            found = entry
            break
          end
        end
        if found then
          local _, myClassEn = UnitClass("player")
          local myLevel = UnitLevel("player") or 0
          local applyMsg = string.format("你好，我想加入你的 %s 队伍。Lv.%d %s",
            found.dungeonName or found.dungeon or "?", myLevel, myClassEn or "")
          ChatFrame_OpenChat("/w " .. target .. " " .. applyMsg)
        else
          ChatFrame_OpenChat("/w " .. target .. " ")
        end
      else
        E:Print("用法: /ecn lfg apply <玩家名>")
      end
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 事件处理
  ---------------------------------------------------------------------------
  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")

  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "CHAT_MSG_ADDON" then
      OnLFGMessage(...)
      return
    end

    if event == "PLAYER_ENTERING_WORLD" then
      -- 启动自动重发计时器（轻量：无发布时仅累加计数器）
      local repostFrame = CreateFrame("Frame")
      repostFrame:SetScript("OnUpdate", function(_, elapsed)
        repostTimer = repostTimer + elapsed
        if repostTimer < LFG_REPOST_INTERVAL then return end
        repostTimer = 0

        -- 清理过期条目（轻量操作）
        CleanupExpired()

        -- 仅在有发布时才执行重发逻辑
        if not myPosting then return end
        local now = time()
        if now - lastBroadcast < LFG_BROADCAST_CD then return end

        lastBroadcast = now
        local msg = string.format("POST:%s:%d:%d:%d:%d:%s",
          myPosting.dungeon or "OTHER",
          myPosting.minLevel or 1,
          myPosting.needTank and 1 or 0,
          myPosting.needHealer and 1 or 0,
          myPosting.needDPS or 0,
          myPosting.note or ""
        )
        if IsInGuild and IsInGuild() then
          pcall(SendAddonMessage, LFG_PREFIX, msg, "GUILD")
        end
        local channelNum = GetChannelName("EpochCN")
        if channelNum and channelNum > 0 then
          pcall(SendAddonMessage, LFG_PREFIX, msg, "CHANNEL")
        end
        E:Debug("LFG: 自动重发招募信息")
      end)
    end
  end)

  E:Debug("LFGBoard 模块已注册")
end)
