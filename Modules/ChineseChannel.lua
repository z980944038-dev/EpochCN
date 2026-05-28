-- ChineseChannel.lua  v2  (EpochCN 0.7.1)
-- 中文公共聊天频道：自动加入 china 频道，提供 /cn 快捷发送、真实成员列表、加入退出事件追踪
--
-- 修复点：
--   * 老版用 channel name 字段比对，但 3.3.5 的 CHAT_MSG_CHANNEL_JOIN/LEAVE 的 channelName
--     字段经常包含 "数字. 名称" 或为空，改用 channelNumber 与 GetChannelName 反查比较
--   * 用 ListChannelByName + CHAT_MSG_CHANNEL_LIST 拉取真实成员快照，
--     /cn who 不再只显示发过言的人
--   * /cn leave 用 pcall 包装，离开后清理 joined 状态
--   * 玩家手动 /leave 时通过 LEFT_CHANNEL 系统消息复位
--   * 无限重试加入改为有限尝试 + 指数退避

EpochCN:RegisterModule("ChineseChannel", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  if EpochCNDB.social.autoJoinChannel == false then return end

  ---------------------------------------------------------------------------
  -- 常量
  ---------------------------------------------------------------------------
  local CHANNEL_NAME      = "china"
  local INITIAL_DELAY     = 8         -- 登录后延迟（秒）
  local JOIN_RETRY_MAX    = 4         -- 加入失败重试次数
  local LIST_REFRESH_INTV = 60        -- 主动拉取成员快照间隔（秒）
  local MEMBER_EXPIRE     = 1800      -- 成员记录过期（秒），未发言/未在快照
  local WELCOME_INTERVAL  = 86400     -- 同一玩家欢迎间隔（24 小时）

  ---------------------------------------------------------------------------
  -- SavedVariables
  ---------------------------------------------------------------------------
  local DB = EpochCNDB.social
  if DB.cnChannelWelcomed == nil then DB.cnChannelWelcomed = {} end  -- 已欢迎过的玩家时间戳

  ---------------------------------------------------------------------------
  -- 运行时状态
  ---------------------------------------------------------------------------
  local joined        = false
  local channelNum    = 0
  local channelMembers = {}    -- name => { lastMsg, source }
  local joinAttempts  = 0
  local listRefreshTimer = 0
  local pendingListRefresh = false
  local initialized   = false

  local frame = CreateFrame("Frame")
  -- 共享一次性定时器 frame，避免每次重试都创建新 frame
  local timerFrame = CreateFrame("Frame")
  timerFrame:Hide()

  ---------------------------------------------------------------------------
  -- 工具
  ---------------------------------------------------------------------------
  local function StripRealmName(fullName)
    if not fullName or fullName == "" then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)") or fullName
    end
    return fullName
  end

  local function GetMyName()
    return StripRealmName(UnitName and UnitName("player"))
  end

  local function IsPlayerName(name)
    name = StripRealmName(name)
    local me = GetMyName()
    return me and name and name == me
  end

  local function ResolveChannelNumber()
    if not GetChannelName then return 0 end
    local n = GetChannelName(CHANNEL_NAME)
    return (n and n > 0) and n or 0
  end

  ---------------------------------------------------------------------------
  -- 频道窗口可见性（确保中文频道消息显示在聊天窗口里）
  ---------------------------------------------------------------------------
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
    if ResolveChannelNumber() <= 0 then return false end
    local maxWindows = NUM_CHAT_WINDOWS or 10
    for i = 1, maxWindows do
      local cf = getglobal and getglobal("ChatFrame" .. i)
      if cf and (not cf.IsShown or cf:IsShown()) then
        EnableChannelForChatWindow(i)
      end
    end
    if FCF_SavePositionAndDimensions then pcall(FCF_SavePositionAndDimensions) end
    return true
  end

  ---------------------------------------------------------------------------
  -- 拉取真实成员列表（主动）
  ---------------------------------------------------------------------------
  local function RequestMemberList()
    local n = ResolveChannelNumber()
    if n <= 0 then return end
    if ListChannelByName then
      pcall(ListChannelByName, CHANNEL_NAME)
      pendingListRefresh = true
    elseif ChannelList then
      pcall(ChannelList, n)
      pendingListRefresh = true
    end
  end

  ---------------------------------------------------------------------------
  -- 加入频道（带重试，避免无限循环）
  ---------------------------------------------------------------------------
  local JoinCNChannel  -- 前向声明，下面 ScheduleJoinRetry 内部要引用

  local function ScheduleJoinRetry(delay)
    delay = delay or 2
    timerFrame.elapsed = 0
    timerFrame.timerDelay = delay
    timerFrame.timerCallback = JoinCNChannel
    timerFrame:SetScript("OnUpdate", function(self, e)
      self.elapsed = self.elapsed + e
      if self.elapsed < self.timerDelay then return end
      self:Hide()  -- 停止 OnUpdate
      if self.timerCallback then self.timerCallback() end
    end)
    timerFrame:Show()  -- 启动 OnUpdate
  end

  function JoinCNChannel()
    -- 已加入：补一次窗口可见
    local n = ResolveChannelNumber()
    if n > 0 then
      channelNum = n
      joined = true
      EnsureChannelVisible()
      RequestMemberList()
      return
    end

    if joinAttempts >= JOIN_RETRY_MAX then
      E:Debug("ChineseChannel: 已尝试 " .. JOIN_RETRY_MAX .. " 次仍未加入，放弃自动加入。")
      return
    end
    joinAttempts = joinAttempts + 1

    if not JoinChannelByName then return end
    pcall(JoinChannelByName, CHANNEL_NAME)

    -- 1.5 秒后检查是否成功（复用共享定时器）
    timerFrame.elapsed = 0
    timerFrame.timerDelay = 1.5
    timerFrame.timerCallback = function()
      local result = ResolveChannelNumber()
      if result > 0 then
        channelNum = result
        joined = true
        EnsureChannelVisible()
        RequestMemberList()
        if E.BroadcastSocialHeartbeat then E:BroadcastSocialHeartbeat() end
        -- 加入成功后启动周期刷新
        if refreshFrame then refreshFrame:Show() end
        E:Print("|cff33ffcc已加入中文频道|r [" .. CHANNEL_NAME .. "] (/" .. result .. ")")
        E:Print("|cff888888使用 /cn <消息> 或 /" .. result .. " <消息> 发送到中文频道。|r")
      else
        E:Debug("ChineseChannel: 第 " .. joinAttempts .. " 次加入失败，将重试。")
        ScheduleJoinRetry(2 * joinAttempts)  -- 退避
      end
    end
    timerFrame:SetScript("OnUpdate", function(self, e)
      self.elapsed = self.elapsed + e
      if self.elapsed < self.timerDelay then return end
      self:Hide()
      if self.timerCallback then self.timerCallback() end
    end)
    timerFrame:Show()
  end

  ---------------------------------------------------------------------------
  -- 频道事件
  ---------------------------------------------------------------------------
  local function IsOurChannel(channelNumberArg, channelNameArg)
    -- channelNumber 比 channelName 更可靠（3.3.5 的 channelName 经常为空）
    if channelNumberArg and channelNumberArg > 0 then
      if channelNum > 0 and channelNumberArg == channelNum then return true end
      -- 不一定缓存了 channelNum，反查一次
      local n = ResolveChannelNumber()
      if n > 0 and channelNumberArg == n then
        channelNum = n
        return true
      end
    end
    if channelNameArg and channelNameArg ~= "" then
      -- 名称可能是 "数字. 名称" 格式，或纯名称
      if string.find(string.lower(channelNameArg), string.lower(CHANNEL_NAME), 1, true) then
        return true
      end
    end
    return false
  end

  local function RecordSpeaker(name, source)
    if not name or name == "" then return end
    name = StripRealmName(name)
    channelMembers[name] = channelMembers[name] or {}
    channelMembers[name].lastMsg = time()
    channelMembers[name].source = source or "speak"

    -- 通知 Social 模块记录到通讯录
    if EpochCNDB.social and EpochCNDB.social.contacts then
      local c = EpochCNDB.social.contacts
      if not c[name] then
        c[name] = {
          version = "?", level = 0, classEn = "",
          firstSeen = time(), lastSeen = time(),
          encounterCount = 1, source = "channel",
        }
      else
        c[name].lastSeen = time()
        c[name].encounterCount = (c[name].encounterCount or 0) + 1
      end
    end
  end

  local function OnChannelMessage(message, sender, language, channelString, target, flags, unknown, channelNumberArg, channelNameArg)
    if not IsOurChannel(channelNumberArg, channelNameArg) then return end
    if not sender or sender == "" then return end
    RecordSpeaker(sender, "speak")
  end

  local function OnChannelJoin(message, sender, _, _, _, _, _, channelNumberArg, channelNameArg)
    if not IsOurChannel(channelNumberArg, channelNameArg) then return end
    if IsPlayerName(sender) then
      -- 自己加入：刷新窗口可见、列表
      EnsureChannelVisible()
      RequestMemberList()
      joined = true
      channelNum = ResolveChannelNumber()
      return
    end
    local name = StripRealmName(sender)
    if not name or name == "" then return end
    channelMembers[name] = channelMembers[name] or {}
    channelMembers[name].joined = time()
    channelMembers[name].source = channelMembers[name].source or "join"
    -- 同时记录到通讯录
    if EpochCNDB.social and EpochCNDB.social.contacts then
      local c = EpochCNDB.social.contacts
      if not c[name] then
        c[name] = {
          version = "?", level = 0, classEn = "",
          firstSeen = time(), lastSeen = time(),
          encounterCount = 1, source = "channel",
        }
      end
    end
  end

  local function OnChannelLeave(message, sender, _, _, _, _, _, channelNumberArg, channelNameArg)
    if not IsOurChannel(channelNumberArg, channelNameArg) then return end
    if IsPlayerName(sender) then
      -- 自己被移除/离开
      joined = false
      channelNum = 0
      channelMembers = {}
      E:Print("|cffff9900已离开中文频道。|r 输入 /cn join 重新加入。")
      return
    end
    local name = StripRealmName(sender)
    if name then channelMembers[name] = nil end
  end

  -- CHAT_MSG_CHANNEL_LIST: message 包含一行成员列表，每行是 "玩家名"，sender 是请求者
  local function OnChannelList(message, sender, _, _, _, _, _, channelNumberArg, channelNameArg)
    if not IsOurChannel(channelNumberArg, channelNameArg) then return end
    if not pendingListRefresh then return end  -- 只接受我们主动请求的回应
    pendingListRefresh = false

    -- 3.3.5 频道列表是单行字符串，玩家名以 ", " 分隔
    if not message or message == "" then return end
    -- 移除前缀（"频道频道频道里有以下玩家:" 等）
    local cleaned = string.gsub(message, "[，,。]+%s*", ", ")
    local now = time()
    -- 清空旧成员快照（保留 lastMsg 较新的）
    for name, data in pairs(channelMembers) do
      if data.source == "list" and (now - (data.lastMsg or 0)) > MEMBER_EXPIRE then
        channelMembers[name] = nil
      end
    end
    for token in string.gmatch(cleaned, "([^,]+)") do
      local trimmed = string.gsub(token, "^%s+", "")
      trimmed = string.gsub(trimmed, "%s+$", "")
      -- 去除可能的 "<玩家名>" 形如尖括号或 GM 标记
      trimmed = string.gsub(trimmed, "[%<%>%s]", "")
      if trimmed ~= "" and not string.find(trimmed, "[，。、:]") then
        local clean = StripRealmName(trimmed)
        if clean and clean ~= "" then
          channelMembers[clean] = channelMembers[clean] or { source = "list" }
          channelMembers[clean].lastSnapshot = now
          channelMembers[clean].source = channelMembers[clean].source or "list"
        end
      end
    end
  end

  ---------------------------------------------------------------------------
  -- 公开 API
  ---------------------------------------------------------------------------
  function E:GetChineseChannelNumber()
    return ResolveChannelNumber()
  end

  function E:IsInChineseChannel()
    return ResolveChannelNumber() > 0
  end

  function E:SendToChineseChannel(message)
    if not message or message == "" then return false end
    local n = ResolveChannelNumber()
    if n > 0 then
      SendChatMessage(message, "CHANNEL", nil, n)
      return true
    end
    return false
  end

  function E:GetChannelMemberCount()
    local n = 0
    for _ in pairs(channelMembers) do n = n + 1 end
    return n
  end

  function E:GetChannelMembers()
    return channelMembers
  end

  function E:RequestChannelMemberList()
    RequestMemberList()
  end

  ---------------------------------------------------------------------------
  -- /cn 命令
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_CN1 = "/cn"
  SlashCmdList["EPOCHCN_CN"] = function(msg)
    msg = msg or ""
    if msg == "" then
      local n = ResolveChannelNumber()
      if n > 0 then
        local count = E:GetChannelMemberCount()
        E:Print("|cff33ffcc中文频道|r [" .. CHANNEL_NAME .. "] 编号: /" .. n)
        E:Print(string.format("|cff888888已知频道成员: %d 人 (/cn who 查看)|r", count))
        E:Print("|cff888888使用 /cn <消息> 发送，/cn leave 退出，/cn refresh 刷新成员列表。|r")
      else
        E:Print("|cffff6666未加入中文频道。正在尝试加入...|r")
        joinAttempts = 0
        JoinCNChannel()
      end
      return
    end

    local cmd = string.lower(msg)

    if cmd == "who" or cmd == "list" then
      RequestMemberList()  -- 拉一次最新
      local rows = {}
      for name, data in pairs(channelMembers) do
        table.insert(rows, { name = name, data = data })
      end
      table.sort(rows, function(a, b)
        return (a.data.lastMsg or a.data.lastSnapshot or 0) > (b.data.lastMsg or b.data.lastSnapshot or 0)
      end)
      E:Print(string.format("|cff33ffcc中文频道成员：%d 人|r", #rows))
      for i = 1, math.min(#rows, 25) do
        local r = rows[i]
        local lastMsg = r.data.lastMsg or 0
        local agoStr
        if lastMsg == 0 then
          agoStr = "未发言"
        else
          local ago = time() - lastMsg
          if ago < 60 then agoStr = "刚刚"
          elseif ago < 3600 then agoStr = string.format("%d分钟前", math.floor(ago / 60))
          else agoStr = string.format("%d小时前", math.floor(ago / 3600)) end
        end
        E:Print(string.format("  %s  |cff888888(%s)|r", r.name, agoStr))
      end
      if #rows == 0 then
        E:Print("  暂无记录。/cn refresh 拉取频道成员快照。")
      elseif #rows > 25 then
        E:Print(string.format("  ...另有 %d 人", #rows - 25))
      end
      return
    end

    if cmd == "refresh" then
      RequestMemberList()
      E:Print("已请求频道成员列表，请稍候...")
      return
    end

    if cmd == "leave" then
      local n = ResolveChannelNumber()
      if n > 0 and LeaveChannelByName then
        pcall(LeaveChannelByName, CHANNEL_NAME)
        joined = false
        channelNum = 0
        channelMembers = {}
        E:Print("已离开中文频道。")
      else
        E:Print("当前未在中文频道中。")
      end
      return
    end

    if cmd == "join" then
      if joined and ResolveChannelNumber() > 0 then
        E:Print("已在中文频道中。")
      else
        joinAttempts = 0
        JoinCNChannel()
      end
      return
    end

    if cmd == "help" then
      E:Print("|cff33ffcc中文频道命令：|r")
      E:Print("  /cn <消息>     - 发送到中文频道")
      E:Print("  /cn who        - 查看频道成员（含真实快照）")
      E:Print("  /cn refresh    - 主动刷新成员列表")
      E:Print("  /cn join       - 加入频道")
      E:Print("  /cn leave      - 离开频道")
      return
    end

    -- 发送消息
    local n = ResolveChannelNumber()
    if n > 0 then
      SendChatMessage(msg, "CHANNEL", nil, n)
    else
      E:Print("|cffff6666未加入中文频道，正在尝试加入...|r")
      joinAttempts = 0
      JoinCNChannel()
    end
  end

  ---------------------------------------------------------------------------
  -- 事件
  ---------------------------------------------------------------------------
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("CHAT_MSG_CHANNEL")
  frame:RegisterEvent("CHAT_MSG_CHANNEL_JOIN")
  frame:RegisterEvent("CHAT_MSG_CHANNEL_LEAVE")
  frame:RegisterEvent("CHAT_MSG_CHANNEL_LIST")
  frame:RegisterEvent("CHANNEL_UI_UPDATE")

  frame:SetScript("OnEvent", function(self, event, ...)
    if event == "PLAYER_ENTERING_WORLD" then
      if initialized then return end
      initialized = true
      -- 延迟加入（使用主 frame 的 OnUpdate，加入后自动切换到 nil）
      self.joinDelay = 0
      self:SetScript("OnUpdate", function(s, e)
        s.joinDelay = (s.joinDelay or 0) + e
        if s.joinDelay < INITIAL_DELAY then return end
        s:SetScript("OnUpdate", nil)
        joinAttempts = 0
        JoinCNChannel()
      end)
      return
    end

    if event == "CHAT_MSG_CHANNEL" then
      OnChannelMessage(...)
      return
    end

    if event == "CHAT_MSG_CHANNEL_JOIN" then
      OnChannelJoin(...)
      return
    end

    if event == "CHAT_MSG_CHANNEL_LEAVE" then
      OnChannelLeave(...)
      return
    end

    if event == "CHAT_MSG_CHANNEL_LIST" then
      OnChannelList(...)
      return
    end

    if event == "CHANNEL_UI_UPDATE" then
      -- 频道 UI 更新：可能加入/离开了某个频道，刷新一次状态
      local n = ResolveChannelNumber()
      if n > 0 and not joined then
        joined = true
        channelNum = n
        EnsureChannelVisible()
      elseif n == 0 and joined then
        joined = false
        channelNum = 0
        channelMembers = {}
      end
      return
    end
  end)

  -- 周期刷新成员列表（轻量）—— 初始隐藏，加入频道后才启动
  local refreshFrame = CreateFrame("Frame")
  refreshFrame:Hide()  -- 初始隐藏，加入频道成功后 Show()
  refreshFrame:SetScript("OnUpdate", function(self, e)
    listRefreshTimer = listRefreshTimer + e
    if listRefreshTimer < LIST_REFRESH_INTV then return end
    listRefreshTimer = 0
    if joined and ResolveChannelNumber() > 0 then
      RequestMemberList()
    else
      self:Hide()  -- 未加入频道时停止 OnUpdate
    end
  end)

  E:Debug("ChineseChannel v2 模块已加载")
end)
