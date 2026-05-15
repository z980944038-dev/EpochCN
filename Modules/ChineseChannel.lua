-- ChineseChannel.lua
-- 中文聊天频道模块
-- 自动加入约定的英文名自定义频道，作为华人玩家公共交流频道。
-- 游戏不支持中文频道名，使用英文名 "EpochCN"。
-- 功能：自动加入、/cn 快捷发送、频道人数统计、欢迎消息

EpochCN:RegisterModule("ChineseChannel", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  if EpochCNDB.social.autoJoinChannel == false then return end

  local CHANNEL_NAME = "EpochCN"
  local joined = false
  local channelNum = 0
  local channelMembers = {}  -- 频道内已知成员
  local frame = CreateFrame("Frame")
  local ensureFrame = CreateFrame("Frame")
  ensureFrame:Hide()

  ---------------------------------------------------------------------------
  -- 工具函数
  ---------------------------------------------------------------------------
  local function GetChannelNumber()
    local num = GetChannelName(CHANNEL_NAME)
    return (num and num > 0) and num or 0
  end

  local function StripRealmName(fullName)
    if not fullName then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)")
    end
    return fullName
  end

  local function IsPlayerName(name)
    local playerName = UnitName and UnitName("player")
    name = StripRealmName(name)
    return name and playerName and name == playerName
  end

  local function RefreshChannelMembers()
    channelMembers = {}
    local num = GetChannelNumber()
    if num <= 0 then return 0 end
    -- 3.3.5 没有直接获取频道成员列表的 API
    -- 我们通过收到的消息来追踪成员
    return 0
  end

  local function EnableChannelForChatWindow(windowID)
    if not windowID then return end

    if AddChatWindowChannel then
      pcall(AddChatWindowChannel, windowID, CHANNEL_NAME)
    end

    local chatFrame = getglobal and getglobal("ChatFrame" .. tostring(windowID))
    if chatFrame and ChatFrame_AddChannel then
      pcall(ChatFrame_AddChannel, chatFrame, CHANNEL_NAME)
    end
  end

  local function EnsureChannelVisible()
    if GetChannelNumber() <= 0 then return false end

    local defaultID = 1
    if DEFAULT_CHAT_FRAME and DEFAULT_CHAT_FRAME.GetID then
      local ok, id = pcall(DEFAULT_CHAT_FRAME.GetID, DEFAULT_CHAT_FRAME)
      if ok and id then defaultID = id end
    end
    EnableChannelForChatWindow(defaultID)

    local maxWindows = NUM_CHAT_WINDOWS or 10
    for i = 1, maxWindows do
      local chatFrame = getglobal and getglobal("ChatFrame" .. i)
      if chatFrame and (not chatFrame.IsShown or chatFrame:IsShown()) then
        EnableChannelForChatWindow(i)
      end
    end

    if FCF_SavePositionAndDimensions then
      pcall(FCF_SavePositionAndDimensions)
    end
    return true
  end

  local function ScheduleEnsureChannelVisible()
    ensureFrame.elapsed = 0
    ensureFrame.nextCheck = 0
    ensureFrame.attempts = 0
    ensureFrame:SetScript("OnUpdate", function(self, elapsed)
      self.elapsed = (self.elapsed or 0) + elapsed
      if self.elapsed < (self.nextCheck or 0) then return end

      self.attempts = (self.attempts or 0) + 1
      EnsureChannelVisible()

      if self.attempts >= 8 then
        self:SetScript("OnUpdate", nil)
        self:Hide()
        return
      end

      self.nextCheck = self.elapsed + 0.75
    end)
    ensureFrame:Show()
  end

  local function JoinCNChannel()
    if joined then
      EnsureChannelVisible()
      ScheduleEnsureChannelVisible()
      return
    end

    -- 检查是否已在频道中
    local num = GetChannelNumber()
    if num > 0 then
      channelNum = num
      joined = true
      EnsureChannelVisible()
      ScheduleEnsureChannelVisible()
      E:Debug("ChineseChannel: 已在频道 " .. CHANNEL_NAME .. " (编号 " .. num .. ")")
      return
    end

    -- 加入频道
    if JoinChannelByName then
      JoinChannelByName(CHANNEL_NAME)
      -- 延迟检查是否加入成功
      local checker = CreateFrame("Frame")
      checker.elapsed = 0
      checker:SetScript("OnUpdate", function(self, elapsed)
        self.elapsed = self.elapsed + elapsed
        if self.elapsed < 1.5 then return end
        self:SetScript("OnUpdate", nil)

        local n = GetChannelNumber()
        if n > 0 then
          channelNum = n
          joined = true
          EnsureChannelVisible()
          ScheduleEnsureChannelVisible()
          E:Print("|cff33ffcc已加入中文频道|r [" .. CHANNEL_NAME .. "] (/" .. n .. ")")
          E:Print("|cff888888使用 /cn <消息> 或 /" .. n .. " <消息> 发送到中文频道。|r")
        else
          E:Debug("ChineseChannel: 加入频道失败")
        end
      end)
    end
  end

  ---------------------------------------------------------------------------
  -- /cn 快捷命令
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_CN1 = "/cn"
  SlashCmdList["EPOCHCN_CN"] = function(msg)
    if not msg or msg == "" then
      local num = GetChannelNumber()
      if num > 0 then
        local memberCount = 0
        for _ in pairs(channelMembers) do memberCount = memberCount + 1 end
        E:Print("|cff33ffcc中文频道|r [" .. CHANNEL_NAME .. "] 编号: /" .. num)
        if memberCount > 0 then
          E:Print(string.format("|cff888888已知频道成员: %d 人|r", memberCount))
        end
        E:Print("|cff888888使用 /cn <消息> 发送到中文频道。|r")
        E:Print("|cff888888使用 /cn who 查看频道成员。|r")
      else
        E:Print("|cffff6666未加入中文频道。正在尝试加入...|r")
        JoinCNChannel()
      end
      return
    end

    -- 子命令
    local cmd = string.lower(msg)

    if cmd == "who" or cmd == "list" then
      local count = 0
      E:Print("|cff33ffcc中文频道已知成员：|r")
      for name, data in pairs(channelMembers) do
        count = count + 1
        if count <= 20 then
          local ago = time() - (data.lastMsg or 0)
          local agoStr = ""
          if ago < 60 then
            agoStr = "刚刚"
          elseif ago < 3600 then
            agoStr = string.format("%d分钟前", math.floor(ago / 60))
          else
            agoStr = string.format("%d小时前", math.floor(ago / 3600))
          end
          E:Print(string.format("  %s  (最后发言: %s)", name, agoStr))
        end
      end
      if count == 0 then
        E:Print("  暂无记录。频道成员会在发言后被记录。")
      elseif count > 20 then
        E:Print(string.format("  ...共 %d 人", count))
      end
      return
    end

    if cmd == "leave" then
      local num = GetChannelNumber()
      if num > 0 then
        LeaveChannelByName(CHANNEL_NAME)
        joined = false
        channelNum = 0
        E:Print("已离开中文频道。")
      else
        E:Print("当前未在中文频道中。")
      end
      return
    end

    if cmd == "join" then
      if joined then
        E:Print("已在中文频道中。")
      else
        JoinCNChannel()
      end
      return
    end

    -- 发送消息
    local num = GetChannelNumber()
    if num > 0 then
      SendChatMessage(msg, "CHANNEL", nil, num)
    else
      E:Print("|cffff6666未加入中文频道，无法发送消息。正在尝试加入...|r")
      JoinCNChannel()
    end
  end

  ---------------------------------------------------------------------------
  -- 频道消息追踪
  ---------------------------------------------------------------------------
  local function OnChannelMessage(message, sender, language, channelString, target, flags, unknown, channelNumber, channelName)
    if not sender then return end
    -- 检查是否来自 EpochCN 频道
    if not channelName then return end
    if string.lower(channelName) ~= string.lower(CHANNEL_NAME) then return end

    local name = StripRealmName(sender)
    if not name or name == "" then return end

    -- 记录频道成员
    channelMembers[name] = {
      lastMsg = time(),
    }

    -- 同时通知 Social 模块记录该玩家
    if EpochCNDB.social and EpochCNDB.social.contacts then
      if not EpochCNDB.social.contacts[name] then
        EpochCNDB.social.contacts[name] = {
          version = "?",
          level = 0,
          class = "",
          lastSeen = time(),
          source = "channel",
        }
      else
        EpochCNDB.social.contacts[name].lastSeen = time()
      end
    end
  end

  ---------------------------------------------------------------------------
  -- 公开 API
  ---------------------------------------------------------------------------
  function E:GetChineseChannelNumber()
    return GetChannelNumber()
  end

  function E:IsInChineseChannel()
    return GetChannelNumber() > 0
  end

  function E:SendToChineseChannel(message)
    if not message or message == "" then return false end
    local num = GetChannelNumber()
    if num > 0 then
      SendChatMessage(message, "CHANNEL", nil, num)
      return true
    end
    return false
  end

  function E:GetChannelMemberCount()
    local count = 0
    for _ in pairs(channelMembers) do count = count + 1 end
    return count
  end

  ---------------------------------------------------------------------------
  -- 事件处理
  ---------------------------------------------------------------------------
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("CHAT_MSG_CHANNEL")
  frame:RegisterEvent("CHAT_MSG_CHANNEL_JOIN")
  frame:RegisterEvent("CHAT_MSG_CHANNEL_LEAVE")

  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "PLAYER_ENTERING_WORLD" then
      -- 延迟加入频道，避免登录时频道系统未就绪
      frame.joinDelay = 0
      frame:SetScript("OnUpdate", function(self, elapsed)
        self.joinDelay = (self.joinDelay or 0) + elapsed
        if self.joinDelay < 8 then return end
        self:SetScript("OnUpdate", nil)
        JoinCNChannel()
      end)
      return
    end

    if event == "CHAT_MSG_CHANNEL" then
      -- 3.3.5 参数: message, sender, language, channelString, target, flags, unknown, channelNumber, channelName
      local message, sender, language, channelString, target, flags, unknown, chNum, chName = ...
      OnChannelMessage(message, sender, language, channelString, target, flags, unknown, chNum, chName)
      return
    end

    if event == "CHAT_MSG_CHANNEL_JOIN" then
      -- 有人加入频道
      local _, sender, _, _, _, _, _, _, chName = ...
      if chName and string.lower(chName) == string.lower(CHANNEL_NAME) then
        if IsPlayerName(sender) then
          EnsureChannelVisible()
          ScheduleEnsureChannelVisible()
        end
        local name = StripRealmName(sender)
        if name and name ~= "" then
          channelMembers[name] = channelMembers[name] or { lastMsg = 0 }
        end
      end
      return
    end

    if event == "CHAT_MSG_CHANNEL_LEAVE" then
      -- 有人离开频道
      local _, sender, _, _, _, _, _, _, chName = ...
      if chName and string.lower(chName) == string.lower(CHANNEL_NAME) then
        local name = StripRealmName(sender)
        if name then
          channelMembers[name] = nil
        end
      end
      return
    end
  end)

  E:Debug("ChineseChannel 模块已注册（含频道成员追踪）")
end)
