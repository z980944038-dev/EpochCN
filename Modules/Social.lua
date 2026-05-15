-- Social.lua
-- 华人玩家发现与通讯录核心模块
-- 通过 addon 消息自动发现同样安装了 EpochCN 的玩家，建立中文玩家网络。
-- 功能：心跳发现、目标框标记、Tooltip 标记、上线通知、通讯录管理
--
-- 性能注意事项：
-- - 心跳计时器使用单一 OnUpdate，间隔 120 秒广播
-- - 不注册 UPDATE_MOUSEOVER_UNIT（高频事件），Tooltip 通过 HookScript 处理
-- - CleanupExpiredPlayers 有节流保护，最多每 30 秒执行一次
-- - 通讯录大小限制 200 条，避免 SavedVariables 膨胀

EpochCN:RegisterModule("Social", function(E)
  local SOCIAL_PREFIX = "EPOCHCN_SOC"
  local HEARTBEAT_INTERVAL = 120  -- 心跳广播间隔（秒）
  local PLAYER_EXPIRE_TIME = 600  -- 玩家记录过期时间（秒）
  local MAX_CONTACTS = 200        -- 通讯录最大条目
  local CLEANUP_INTERVAL = 30     -- 清理间隔节流（秒）

  -- 注册 addon 消息前缀
  if RegisterAddonMessagePrefix then
    pcall(RegisterAddonMessagePrefix, SOCIAL_PREFIX)
  end

  -- 初始化持久化数据
  EpochCNDB.social = EpochCNDB.social or {}
  EpochCNDB.social.enabled = EpochCNDB.social.enabled ~= false
  EpochCNDB.social.showTargetIcon = EpochCNDB.social.showTargetIcon ~= false
  EpochCNDB.social.showTooltipTag = EpochCNDB.social.showTooltipTag ~= false
  EpochCNDB.social.onlineNotify = EpochCNDB.social.onlineNotify ~= false
  EpochCNDB.social.autoJoinChannel = EpochCNDB.social.autoJoinChannel ~= false
  EpochCNDB.social.contacts = EpochCNDB.social.contacts or {}
  EpochCNDB.social.notes = EpochCNDB.social.notes or {}
  EpochCNDB.social.blocklist = EpochCNDB.social.blocklist or {}

  if not EpochCNDB.social.enabled then return end

  -- 运行时状态
  local onlinePlayers = {}   -- 当前在线的中文玩家
  local onlineCount = 0      -- 缓存的在线人数（避免频繁遍历）
  local heartbeatTimer = 0
  local initialized = false
  local playerName = ""
  local playerLevel = 0
  local playerClass = ""
  local notifiedPlayers = {} -- 本次会话已通知过上线的玩家
  local lastCleanup = 0      -- 上次清理时间戳

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

  local function GetPlayerInfo()
    playerName = StripRealmName(UnitName("player")) or ""
    playerLevel = UnitLevel("player") or 0
    local _, classEn = UnitClass("player")
    playerClass = classEn or ""
  end

  local function GetGroupChannel()
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then return "RAID" end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then return "PARTY" end
    return nil
  end

  local function SafeSend(message, channel)
    if not SendAddonMessage then return end
    pcall(SendAddonMessage, SOCIAL_PREFIX, message, channel)
  end

  local function GetClassColor(class)
    if not class or class == "" then return "|cffffffff" end
    local colors = RAID_CLASS_COLORS and RAID_CLASS_COLORS[class]
    if colors then
      return string.format("|cff%02x%02x%02x", colors.r * 255, colors.g * 255, colors.b * 255)
    end
    return "|cffffffff"
  end

  local function IsBlocked(name)
    return EpochCNDB.social.blocklist[name] == true
  end

  -- 节流清理：最多每 CLEANUP_INTERVAL 秒执行一次
  local function CleanupExpiredPlayers()
    local now = time()
    if now - lastCleanup < CLEANUP_INTERVAL then return end
    lastCleanup = now

    local newCount = 0
    for name, data in pairs(onlinePlayers) do
      if now - (data.lastSeen or 0) > PLAYER_EXPIRE_TIME then
        onlinePlayers[name] = nil
      else
        newCount = newCount + 1
      end
    end
    onlineCount = newCount
  end

  ---------------------------------------------------------------------------
  -- 心跳广播
  ---------------------------------------------------------------------------
  local function BroadcastHeartbeat()
    local zone = GetZoneText and GetZoneText() or ""
    local msg = string.format("HB:%s:%d:%s:%s", E.version or "0", playerLevel, playerClass, zone)

    if IsInGuild and IsInGuild() then
      SafeSend(msg, "GUILD")
    end

    local groupChannel = GetGroupChannel()
    if groupChannel then
      SafeSend(msg, groupChannel)
    end

    local channelNum = GetChannelName("EpochCN")
    if channelNum and channelNum > 0 then
      SafeSend(msg, "CHANNEL")
    end
  end

  ---------------------------------------------------------------------------
  -- 玩家记录管理
  ---------------------------------------------------------------------------
  local function RecordPlayer(name, version, level, class, zone)
    if not name or name == "" or name == playerName then return end
    if IsBlocked(name) then return end

    local isNew = not onlinePlayers[name]

    onlinePlayers[name] = {
      version = version or "?",
      level = tonumber(level) or 0,
      class = class or "",
      zone = zone or "",
      lastSeen = time(),
    }

    if isNew then
      onlineCount = onlineCount + 1
      -- 上线通知（仅首次发现时）
      if EpochCNDB.social.onlineNotify and not notifiedPlayers[name] then
        notifiedPlayers[name] = true
        local colorCode = GetClassColor(class)
        E:Print(string.format("|cff88ccff[社交]|r %s%s|r (Lv.%d) 在线", colorCode, name, tonumber(level) or 0))
        if E.FlashMinimapButton then E:FlashMinimapButton() end
      end
    end

    -- 更新持久化通讯录（节流：只在新玩家或间隔超过 60 秒时写入）
    local contacts = EpochCNDB.social.contacts
    local existing = contacts[name]
    if isNew or not existing or (time() - (existing.lastSeen or 0) > 60) then
      contacts[name] = {
        version = version or "?",
        level = tonumber(level) or 0,
        class = class or "",
        zone = zone or "",
        lastSeen = time(),
      }

      -- 限制通讯录大小（仅在新增时检查）
      if isNew then
        local count = 0
        for _ in pairs(contacts) do count = count + 1 end
        if count > MAX_CONTACTS then
          local oldest, oldestTime = nil, time()
          for n, data in pairs(contacts) do
            if data.lastSeen and data.lastSeen < oldestTime then
              oldest = n
              oldestTime = data.lastSeen
            end
          end
          if oldest then contacts[oldest] = nil end
        end
      end
    end
  end

  ---------------------------------------------------------------------------
  -- 消息处理
  ---------------------------------------------------------------------------
  local function OnAddonMessage(prefix, message, channel, sender)
    if prefix ~= SOCIAL_PREFIX then return end
    sender = StripRealmName(sender)
    if not sender or sender == playerName then return end

    local msgType, rest = string.match(message, "^(%u+):(.*)$")
    if not msgType then return end

    if msgType == "HB" then
      local version, level, class, zone = string.match(rest, "^([^:]*):([^:]*):([^:]*):?(.*)$")
      RecordPlayer(sender, version, tonumber(level), class, zone)
      return
    end

    if msgType == "PING" then
      local zone = GetZoneText and GetZoneText() or ""
      local reply = string.format("PONG:%s:%d:%s:%s", E.version or "0", playerLevel, playerClass, zone)
      if channel == "GUILD" then
        SafeSend(reply, "GUILD")
      elseif channel == "PARTY" or channel == "RAID" then
        SafeSend(reply, GetGroupChannel() or "PARTY")
      end
      return
    end

    if msgType == "PONG" then
      local version, level, class, zone = string.match(rest, "^([^:]*):([^:]*):([^:]*):?(.*)$")
      RecordPlayer(sender, version, tonumber(level), class, zone)
      return
    end

    if msgType == "HELLO" then
      local colorCode = GetClassColor(onlinePlayers[sender] and onlinePlayers[sender].class or "")
      E:Print(string.format("|cff88ccff[社交]|r %s%s|r 向你打了个招呼！", colorCode, sender))
      return
    end
  end

  ---------------------------------------------------------------------------
  -- 目标框中文玩家标记
  ---------------------------------------------------------------------------
  local targetIcon = nil

  local function UpdateTargetIcon()
    if not EpochCNDB.social.showTargetIcon then return end
    if not TargetFrame then return end

    local name = StripRealmName(UnitName("target"))
    local isPlayer = UnitIsPlayer("target")
    local isChinese = name and isPlayer and onlinePlayers[name] ~= nil

    if isChinese then
      if not targetIcon then
        targetIcon = TargetFrame:CreateTexture("EpochCNTargetSocialIcon", "OVERLAY")
        targetIcon:SetSize(16, 16)
        targetIcon:SetPoint("LEFT", TargetFrame, "LEFT", 6, 18)
        targetIcon:SetTexture("Interface\\Icons\\INV_Misc_Book_09")
      end
      targetIcon:Show()
    else
      if targetIcon then targetIcon:Hide() end
    end
  end

  ---------------------------------------------------------------------------
  -- Tooltip 中文玩家标记（通过 HookScript，不注册高频事件）
  ---------------------------------------------------------------------------
  local function OnTooltipSetUnit(tooltip)
    if not EpochCNDB.social.showTooltipTag then return end
    if not tooltip then return end

    local _, unit = tooltip:GetUnit()
    if not unit or not UnitIsPlayer(unit) then return end

    local name = StripRealmName(UnitName(unit))
    if not name then return end

    local data = onlinePlayers[name]
    if data then
      tooltip:AddLine(" ")
      tooltip:AddLine("|cff33ffcc[EpochCN 中文玩家]|r  v" .. (data.version or "?"), 0.2, 1, 0.8)
      if data.zone and data.zone ~= "" then
        tooltip:AddLine("  区域: " .. data.zone, 0.7, 0.7, 0.7)
      end
      local note = EpochCNDB.social.notes[name]
      if note and note ~= "" then
        tooltip:AddLine("  备注: " .. note, 0.9, 0.8, 0.2)
      end
      tooltip:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 公开 API
  ---------------------------------------------------------------------------
  function E:GetOnlineChinesePlayers()
    return onlinePlayers
  end

  function E:GetChinesePlayerCount()
    -- 返回缓存的计数，不触发遍历
    return onlineCount
  end

  function E:IsChinesePlayer(name)
    if not name then return false end
    return onlinePlayers[StripRealmName(name)] ~= nil
  end

  function E:GetContactNote(name)
    return EpochCNDB.social.notes[name]
  end

  function E:SetContactNote(name, note)
    if not name or name == "" then return end
    if note == "" then note = nil end
    EpochCNDB.social.notes[name] = note
  end

  function E:GetAllContacts()
    return EpochCNDB.social.contacts or {}
  end

  function E:BlockPlayer(name)
    if not name or name == "" then return end
    EpochCNDB.social.blocklist[name] = true
    if onlinePlayers[name] then
      onlinePlayers[name] = nil
      onlineCount = onlineCount - 1
    end
    E:Print(string.format("已屏蔽 %s 的社交消息。", name))
  end

  function E:UnblockPlayer(name)
    if not name or name == "" then return end
    EpochCNDB.social.blocklist[name] = nil
    E:Print(string.format("已取消屏蔽 %s。", name))
  end

  function E:SayHelloTo(name)
    if not name or name == "" then return end
    if IsInGuild and IsInGuild() then
      SafeSend("HELLO:" .. name, "GUILD")
    end
    local groupChannel = GetGroupChannel()
    if groupChannel then
      SafeSend("HELLO:" .. name, groupChannel)
    end
    E:Print(string.format("已向 %s 打招呼。", name))
  end

  function E:InviteChinesePlayer(name)
    if not name or name == "" then return end
    InviteUnit(name)
    if onlinePlayers[name] then
      SendChatMessage("你好，邀请你组队~", "WHISPER", nil, name)
    end
  end

  ---------------------------------------------------------------------------
  -- 社交面板 UI（延迟创建，仅在打开时构建）
  ---------------------------------------------------------------------------
  local socialPanel = nil

  local function CreateSocialPanel()
    if socialPanel then return socialPanel end

    socialPanel = CreateFrame("Frame", "EpochCNSocialFrame", UIParent)
    socialPanel:SetSize(360, 420)
    socialPanel:SetPoint("CENTER")
    socialPanel:SetFrameStrata("DIALOG")
    socialPanel:SetMovable(true)
    socialPanel:EnableMouse(true)
    socialPanel:RegisterForDrag("LeftButton")
    socialPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    socialPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    socialPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true, tileSize = 32, edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    socialPanel:Hide()

    local title = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", socialPanel, "TOP", 0, -18)
    title:SetText("|cff33ffccEpochCN|r 中文玩家")

    local close = CreateFrame("Button", nil, socialPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", socialPanel, "TOPRIGHT", -5, -5)

    socialPanel.countText = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    socialPanel.countText:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 20, -44)

    socialPanel.rows = {}
    for i = 1, 10 do
      local row = CreateFrame("Button", nil, socialPanel)
      row:SetSize(320, 22)
      row:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 20, -64 - (i - 1) * 24)
      row:EnableMouse(true)

      local bg = row:CreateTexture(nil, "BACKGROUND")
      bg:SetAllPoints()
      bg:SetTexture("Interface\\Buttons\\UI-Listbox-Highlight2")
      bg:SetAlpha(0)
      row.bg = bg

      row.nameText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.nameText:SetPoint("LEFT", row, "LEFT", 4, 0)
      row.nameText:SetWidth(100)
      row.nameText:SetJustifyH("LEFT")

      row.infoText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.infoText:SetPoint("LEFT", row, "LEFT", 108, 0)
      row.infoText:SetWidth(100)
      row.infoText:SetJustifyH("LEFT")

      row.zoneText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.zoneText:SetPoint("LEFT", row, "LEFT", 212, 0)
      row.zoneText:SetWidth(108)
      row.zoneText:SetJustifyH("LEFT")

      row:SetScript("OnEnter", function(self)
        self.bg:SetAlpha(0.3)
        if self.playerName then
          GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
          GameTooltip:SetText(self.playerName, 1, 0.82, 0)
          local note = EpochCNDB.social.notes[self.playerName]
          if note then GameTooltip:AddLine("备注: " .. note, 0.9, 0.8, 0.2) end
          GameTooltip:AddLine(" ")
          GameTooltip:AddLine("左键: 密语  |  右键: 邀请组队", 0.5, 0.5, 0.5)
          GameTooltip:Show()
        end
      end)
      row:SetScript("OnLeave", function(self)
        self.bg:SetAlpha(0)
        GameTooltip:Hide()
      end)
      row:RegisterForClicks("LeftButtonUp", "RightButtonUp")
      row:SetScript("OnClick", function(self, button)
        if not self.playerName then return end
        if button == "RightButton" then
          InviteUnit(self.playerName)
        else
          ChatFrame_OpenChat("/w " .. self.playerName .. " ")
        end
      end)

      row:Hide()
      socialPanel.rows[i] = row
    end

    local refreshBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    refreshBtn:SetSize(60, 22)
    refreshBtn:SetPoint("BOTTOMLEFT", socialPanel, "BOTTOMLEFT", 20, 16)
    refreshBtn:SetText("刷新")
    refreshBtn:SetScript("OnClick", function() E:RefreshSocialPanel() end)

    local closeBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    closeBtn:SetSize(60, 22)
    closeBtn:SetPoint("BOTTOMRIGHT", socialPanel, "BOTTOMRIGHT", -20, 16)
    closeBtn:SetText("关闭")
    closeBtn:SetScript("OnClick", function() socialPanel:Hide() end)

    -- QQ 群交流信息
    local qqInfo = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    qqInfo:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 42)
    qqInfo:SetText("|cffffd200QQ 交流群:|r |cff33ffcc1097800503|r  (点击复制)")

    local qqBtn = CreateFrame("Button", nil, socialPanel)
    qqBtn:SetSize(280, 16)
    qqBtn:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 40)
    qqBtn:SetScript("OnClick", function()
      -- 打开编辑框让玩家复制群号
      if not socialPanel.qqCopyBox then
        local box = CreateFrame("EditBox", nil, socialPanel, "InputBoxTemplate")
        box:SetSize(120, 20)
        box:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 58)
        box:SetAutoFocus(true)
        box:SetMaxLetters(20)
        box:SetText("1097800503")
        box:HighlightText()
        box:SetScript("OnEscapePressed", function(self) self:Hide() end)
        box:SetScript("OnEnterPressed", function(self) self:Hide() end)
        socialPanel.qqCopyBox = box
      else
        socialPanel.qqCopyBox:SetText("1097800503")
        socialPanel.qqCopyBox:Show()
        socialPanel.qqCopyBox:SetFocus()
        socialPanel.qqCopyBox:HighlightText()
      end
    end)
    qqBtn:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_TOP")
      GameTooltip:SetText("QQ 群: 1097800503", 1, 0.82, 0)
      GameTooltip:AddLine("点击复制群号，加群与其他中文玩家交流", 1, 1, 1, true)
      GameTooltip:Show()
    end)
    qqBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)

    return socialPanel
  end

  function E:RefreshSocialPanel()
    if not socialPanel then return end
    CleanupExpiredPlayers()

    local sorted = {}
    for name, data in pairs(onlinePlayers) do
      table.insert(sorted, { name = name, data = data })
    end
    table.sort(sorted, function(a, b) return (a.data.level or 0) > (b.data.level or 0) end)

    socialPanel.countText:SetText(string.format("|cff88ccff在线中文玩家: %d|r", #sorted))

    for i = 1, 10 do
      local row = socialPanel.rows[i]
      local entry = sorted[i]
      if entry then
        row.nameText:SetText(GetClassColor(entry.data.class) .. entry.name .. "|r")
        row.infoText:SetText(string.format("Lv.%d  v%s", entry.data.level or 0, entry.data.version or "?"))
        row.zoneText:SetText("|cff999999" .. (entry.data.zone or "") .. "|r")
        row.playerName = entry.name
        row:Show()
      else
        row.playerName = nil
        row:Hide()
      end
    end
  end

  function E:ToggleSocialPanel()
    local panel = CreateSocialPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      E:RefreshSocialPanel()
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 斜杠命令
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    if msg == "social" or msg == "cn players" then
      E:ToggleSocialPanel()
      return true
    end

    if msg == "social list" then
      CleanupExpiredPlayers()
      local count = 0
      E:Print("|cff33ffcc当前在线中文玩家：|r")
      for name, data in pairs(onlinePlayers) do
        count = count + 1
        local colorCode = GetClassColor(data.class)
        local zone = data.zone and data.zone ~= "" and ("  " .. data.zone) or ""
        E:Print(string.format("  %s%s|r  Lv.%d  v%s%s", colorCode, name, data.level or 0, data.version or "?", zone))
      end
      if count == 0 then
        E:Print("  暂未发现其他中文玩家在线。")
      else
        E:Print(string.format("  共 %d 名中文玩家在线。", count))
      end
      return true
    end

    if string.find(msg, "^note ") then
      local target, note = string.match(msg, "^note%s+(%S+)%s*(.*)")
      if target then
        if note and note ~= "" then
          E:SetContactNote(target, note)
          E:Print(string.format("已为 %s 设置备注：%s", target, note))
        else
          local existing = E:GetContactNote(target)
          if existing then
            E:Print(string.format("%s 的备注：%s", target, existing))
          else
            E:Print(string.format("%s 暂无备注。", target))
          end
        end
        return true
      end
    end

    if string.find(msg, "^hello ") then
      local target = string.match(msg, "^hello%s+(%S+)")
      if target then E:SayHelloTo(target); return true end
    end

    if string.find(msg, "^block ") then
      local target = string.match(msg, "^block%s+(%S+)")
      if target then E:BlockPlayer(target); return true end
    end

    if string.find(msg, "^unblock ") then
      local target = string.match(msg, "^unblock%s+(%S+)")
      if target then E:UnblockPlayer(target); return true end
    end

    if msg == "contacts" then
      local contacts = E:GetAllContacts()
      local sorted = {}
      for name, data in pairs(contacts) do
        table.insert(sorted, { name = name, data = data })
      end
      table.sort(sorted, function(a, b) return (a.data.lastSeen or 0) > (b.data.lastSeen or 0) end)
      E:Print("|cff33ffcc通讯录（最近联系）：|r")
      local shown = 0
      for _, entry in ipairs(sorted) do
        shown = shown + 1
        if shown <= 20 then
          local note = EpochCNDB.social.notes[entry.name] or ""
          local noteStr = note ~= "" and ("  |cff888888[" .. note .. "]|r") or ""
          local online = onlinePlayers[entry.name] and "|cff33ff99[在线]|r " or ""
          E:Print(string.format("  %s%s  Lv.%d  %s%s", online, entry.name, entry.data.level or 0, entry.data.class or "", noteStr))
        end
      end
      if shown == 0 then
        E:Print("  通讯录为空。")
      elseif shown > 20 then
        E:Print(string.format("  ...共 %d 条记录（仅显示前 20 条）", shown))
      end
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 事件处理（精简：不注册 UPDATE_MOUSEOVER_UNIT 高频事件）
  ---------------------------------------------------------------------------
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:RegisterEvent("PARTY_MEMBERS_CHANGED")
  frame:RegisterEvent("RAID_ROSTER_UPDATE")
  frame:RegisterEvent("PLAYER_TARGET_CHANGED")

  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "CHAT_MSG_ADDON" then
      OnAddonMessage(...)
      return
    end

    if event == "PLAYER_ENTERING_WORLD" then
      if initialized then return end
      initialized = true
      GetPlayerInfo()

      -- Hook GameTooltip（一次性，不注册事件）
      if GameTooltip and GameTooltip.HookScript then
        GameTooltip:HookScript("OnTooltipSetUnit", OnTooltipSetUnit)
      end

      -- 延迟初始化：5 秒后发送 PING 和首次心跳，然后启动计时器
      local initFrame = CreateFrame("Frame")
      initFrame.elapsed = 0
      initFrame:SetScript("OnUpdate", function(self, elapsed)
        self.elapsed = self.elapsed + elapsed
        if self.elapsed < 5 then return end
        -- 切换为心跳计时器（复用同一个 frame，不再创建新的）
        self.elapsed = 0
        self:SetScript("OnUpdate", function(self2, elapsed2)
          heartbeatTimer = heartbeatTimer + elapsed2
          if heartbeatTimer >= HEARTBEAT_INTERVAL then
            heartbeatTimer = 0
            GetPlayerInfo()
            BroadcastHeartbeat()
            CleanupExpiredPlayers()
          end
        end)

        -- 首次 PING + 心跳
        if IsInGuild and IsInGuild() then
          SafeSend("PING:1", "GUILD")
        end
        local groupChannel = GetGroupChannel()
        if groupChannel then
          SafeSend("PING:1", groupChannel)
        end
        BroadcastHeartbeat()
      end)
      return
    end

    if event == "PARTY_MEMBERS_CHANGED" or event == "RAID_ROSTER_UPDATE" then
      BroadcastHeartbeat()
      return
    end

    if event == "PLAYER_TARGET_CHANGED" then
      UpdateTargetIcon()
      return
    end
  end)

  ---------------------------------------------------------------------------
  -- 密语追踪（轻量：仅记录通讯录，不做额外处理）
  ---------------------------------------------------------------------------
  local whisperFrame = CreateFrame("Frame")
  whisperFrame:RegisterEvent("CHAT_MSG_WHISPER")
  whisperFrame:SetScript("OnEvent", function(_, event, message, sender)
    if event ~= "CHAT_MSG_WHISPER" then return end
    local name = StripRealmName(sender)
    if not name or name == "" or onlinePlayers[name] then return end

    -- 仅当消息含中文字符时记录
    if message and string.find(message, "[\128-\255]") then
      local contacts = EpochCNDB.social.contacts
      if not contacts[name] then
        contacts[name] = {
          version = "?", level = 0, class = "",
          lastSeen = time(), source = "whisper",
        }
      end
    end
  end)

  E:Debug("Social 模块已注册")
end)
