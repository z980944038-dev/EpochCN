-- Social.lua  v2  (EpochCN 0.7.1)
-- 华人玩家发现、通讯录、目标标记、社交面板（在线/通讯录/黑名单 三标签页）
--
-- 设计要点：
--   1. 心跳协议 v2（HB2:...） 携带版本/等级/职业/种族/阵营/公会/区域/状态
--      同时兼容老协议 HB:.../PONG:...
--   2. 通讯录数据结构升级：firstSeen, lastSeen, encounterCount, classEn, race,
--      faction, guild, lastZone, tags[], note, ignored
--   3. 黑名单与忽略名单分离：blocklist=不接收消息；ignored=不显示在线提示
--   4. 单 OnUpdate 计时器，节流清理；不注册 UPDATE_MOUSEOVER_UNIT
--   5. PARTY_MEMBERS_CHANGED / RAID_ROSTER_UPDATE 触发心跳带 5 秒冷却
--   6. 公开 API 全部 nil-safe，可被其他模块独立调用

EpochCN:RegisterModule("Social", function(E)
  ---------------------------------------------------------------------------
  -- 常量
  ---------------------------------------------------------------------------
  local SOCIAL_PREFIX        = "EPOCHCN_SOC"
  local PROTOCOL_VERSION     = 2
  local HEARTBEAT_INTERVAL   = 120         -- 心跳广播间隔（秒）
  local HEARTBEAT_JITTER     = 30          -- 心跳抖动 ±N 秒，避免广播洪峰
  local PLAYER_EXPIRE_TIME   = 600         -- 在线列表过期（秒，超出移除）
  local MAX_CONTACTS         = 500         -- 通讯录最大条目（旧版 200 太小）
  local CLEANUP_INTERVAL     = 30          -- 清理间隔节流（秒）
  local TARGET_HB_COOLDOWN   = 5           -- 队伍变化触发心跳的最短间隔
  local MAX_NOTIFY_PER_MIN   = 6           -- 每分钟最多 N 条上线提醒，防刷屏
  local MAX_LIST_ROWS        = 16          -- 在线/通讯录面板每页行数
  local NOTE_MAX_LEN         = 60          -- 备注长度限制
  local TAG_MAX_LEN          = 12          -- 单个标签长度限制
  local TAG_MAX_COUNT        = 5           -- 每位联系人最多标签数

  ---------------------------------------------------------------------------
  -- SavedVariables 初始化（一次性，所有键都给默认值）
  ---------------------------------------------------------------------------
  local DB
  local function InitDB()
    EpochCNDB.social = EpochCNDB.social or {}
    DB = EpochCNDB.social
    if DB.enabled == nil           then DB.enabled = true              end
    if DB.showTargetIcon == nil    then DB.showTargetIcon = true       end
    if DB.showTooltipTag == nil    then DB.showTooltipTag = true       end
    if DB.onlineNotify == nil      then DB.onlineNotify = true         end
    if DB.onlineNotifyOnceOnly == nil then DB.onlineNotifyOnceOnly = false end
    if DB.flashMinimap == nil      then DB.flashMinimap = true         end
    if DB.recordWhisper == nil     then DB.recordWhisper = true        end
    if DB.autoTagGuildmate == nil  then DB.autoTagGuildmate = true     end
    if DB.autoTagPartymate == nil  then DB.autoTagPartymate = true     end
    DB.contacts  = DB.contacts  or {}
    DB.notes     = DB.notes     or {}    -- 兼容老版本，迁移到 contacts.note
    DB.tags      = DB.tags      or {}    -- name => { tag1=true, tag2=true }
    DB.blocklist = DB.blocklist or {}
    DB.muted     = DB.muted     or {}    -- 不显示在线提醒，但仍记录
    -- 一次性迁移老版 notes 到 contacts
    for name, note in pairs(DB.notes) do
      if note and note ~= "" then
        DB.contacts[name] = DB.contacts[name] or {
          version = "?", level = 0, classEn = "", lastSeen = time(),
          firstSeen = time(), encounterCount = 1, source = "legacy",
        }
        if not DB.contacts[name].note then DB.contacts[name].note = note end
      end
    end
  end

  InitDB()
  if not DB.enabled then return end

  ---------------------------------------------------------------------------
  -- 注册 addon 消息前缀
  ---------------------------------------------------------------------------
  if RegisterAddonMessagePrefix then
    pcall(RegisterAddonMessagePrefix, SOCIAL_PREFIX)
  end

  ---------------------------------------------------------------------------
  -- 运行时状态
  ---------------------------------------------------------------------------
  local onlinePlayers   = {}          -- name => { version, level, classEn, race, faction, guild, zone, status, lastSeen }
  local onlineCount     = 0
  local heartbeatTimer  = math.random(0, HEARTBEAT_JITTER)
  local heartbeatNext   = HEARTBEAT_INTERVAL + math.random(-HEARTBEAT_JITTER, HEARTBEAT_JITTER)
  local lastGroupHB     = 0
  local lastCleanup     = 0
  local notifiedThisSession = {}      -- name => true，本次登录已通知
  local notifyTimestamps = {}         -- 时间戳数组，用于节流
  local initialized     = false
  local socialPanel
  local targetIcon

  -- 当前角色信息（按需刷新）
  local me = { name = "", level = 0, classEn = "", race = "", faction = "", guild = "" }

  ---------------------------------------------------------------------------
  -- 工具函数
  ---------------------------------------------------------------------------
  local function StripRealmName(fullName)
    if not fullName or fullName == "" then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)") or fullName
    end
    return fullName
  end

  local function HasCJK(text)
    return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
  end

  local function GetClassColor(classEn)
    if not classEn or classEn == "" then return "|cffffffff" end
    local c = RAID_CLASS_COLORS and RAID_CLASS_COLORS[classEn]
    if c and c.r and c.g and c.b then
      return string.format("|cff%02x%02x%02x",
        math.floor(c.r * 255 + 0.5),
        math.floor(c.g * 255 + 0.5),
        math.floor(c.b * 255 + 0.5))
    end
    return "|cffffffff"
  end

  local CN_CLASS = {
    WARRIOR = "战士", PALADIN = "圣骑士", HUNTER = "猎人", ROGUE = "潜行者",
    PRIEST = "牧师", DEATHKNIGHT = "死亡骑士", SHAMAN = "萨满", MAGE = "法师",
    WARLOCK = "术士", DRUID = "德鲁伊",
  }

  local CN_FACTION = { Alliance = "联盟", Horde = "部落" }

  local function ClassToCN(classEn)
    if not classEn or classEn == "" then return "" end
    return CN_CLASS[string.upper(classEn)] or classEn
  end

  local function FactionToCN(factionEn)
    return CN_FACTION[factionEn] or factionEn or ""
  end

  local function FactionShort(faction)
    if faction == "Alliance" then return "A" end
    if faction == "Horde" then return "H" end
    return faction or ""
  end

  local function ShortFactionToFull(short)
    if short == "A" then return "Alliance" end
    if short == "H" then return "Horde" end
    return short or ""
  end

  local function PlayerStatus()
    if UnitIsAFK and UnitIsAFK("player") then return 1 end
    if UnitIsDND and UnitIsDND("player") then return 2 end
    return 0
  end

  local function StatusToCN(s)
    s = tonumber(s) or 0
    if s == 1 then return "|cffffd200[AFK]|r" end
    if s == 2 then return "|cffff6666[DND]|r" end
    return ""
  end

  local function RefreshPlayerInfo()
    me.name    = StripRealmName(UnitName("player")) or ""
    me.level   = UnitLevel("player") or 0
    local _, classEn = UnitClass("player")
    me.classEn = classEn or ""
    local _, raceEn  = UnitRace("player")
    me.race    = raceEn or ""
    me.faction = (UnitFactionGroup and UnitFactionGroup("player")) or ""
    me.guild   = (GetGuildInfo and GetGuildInfo("player")) or ""
  end

  local function GetGroupChannel()
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then return "RAID" end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then return "PARTY" end
    return nil
  end

  local function SafeSend(message, channel, target)
    if not SendAddonMessage or not message or not channel then return end
    pcall(SendAddonMessage, SOCIAL_PREFIX, message, channel, target)
  end

  local function NotifyAllowed()
    if not DB.onlineNotify then return false end
    -- 节流：清理 60 秒前的时间戳
    local now = time()
    local i = 1
    while i <= #notifyTimestamps do
      if now - notifyTimestamps[i] > 60 then
        table.remove(notifyTimestamps, i)
      else
        i = i + 1
      end
    end
    if #notifyTimestamps >= MAX_NOTIFY_PER_MIN then return false end
    table.insert(notifyTimestamps, now)
    return true
  end

  local function IsBlocked(name)
    return name and DB.blocklist[name] == true
  end

  local function IsMuted(name)
    return name and DB.muted[name] == true
  end

  ---------------------------------------------------------------------------
  -- 节流清理
  ---------------------------------------------------------------------------
  local function CleanupExpiredPlayers(force)
    local now = time()
    if not force and now - lastCleanup < CLEANUP_INTERVAL then return end
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
  -- 通讯录管理
  ---------------------------------------------------------------------------
  local function CountContacts()
    local n = 0
    for _ in pairs(DB.contacts) do n = n + 1 end
    return n
  end

  local function PruneContactsIfFull()
    local n = CountContacts()
    if n <= MAX_CONTACTS then return end
    -- 删除最旧 lastSeen 的非 tagged/无 note 联系人
    local victims = {}
    for name, data in pairs(DB.contacts) do
      local hasTag = DB.tags[name] and next(DB.tags[name])
      local hasNote = data.note and data.note ~= ""
      if not hasTag and not hasNote then
        table.insert(victims, { name = name, ts = data.lastSeen or 0 })
      end
    end
    table.sort(victims, function(a, b) return a.ts < b.ts end)
    local toRemove = n - MAX_CONTACTS
    for i = 1, math.min(toRemove, #victims) do
      DB.contacts[victims[i].name] = nil
      DB.tags[victims[i].name] = nil
    end
  end

  local function UpdateContact(name, fields, source)
    if not name or name == "" then return end
    local c = DB.contacts[name]
    if not c then
      c = {
        firstSeen = time(),
        encounterCount = 0,
        source = source or "addon",
      }
      DB.contacts[name] = c
    end
    if fields then
      for k, v in pairs(fields) do
        if v ~= nil and v ~= "" then c[k] = v end
      end
    end
    c.lastSeen = time()
    c.encounterCount = (c.encounterCount or 0) + 1
    -- 自动标签
    if DB.autoTagGuildmate and IsInGuild and IsInGuild() and fields and fields.guild and me.guild ~= "" and fields.guild == me.guild then
      DB.tags[name] = DB.tags[name] or {}
      DB.tags[name]["公会"] = true
    end
    PruneContactsIfFull()
  end

  ---------------------------------------------------------------------------
  -- 玩家上线记录
  ---------------------------------------------------------------------------
  local function RecordPlayer(name, fields, source)
    if not name or name == "" or name == me.name then return end
    if IsBlocked(name) then return end
    fields = fields or {}

    local isNew = onlinePlayers[name] == nil
    onlinePlayers[name] = {
      version  = fields.version or "?",
      level    = tonumber(fields.level) or 0,
      classEn  = fields.classEn or "",
      race     = fields.race or "",
      faction  = fields.faction or "",
      guild    = fields.guild or "",
      zone     = fields.zone or "",
      status   = tonumber(fields.status) or 0,
      lastSeen = time(),
    }
    if isNew then
      onlineCount = onlineCount + 1
      -- 上线提醒
      local alreadyNotified = DB.onlineNotifyOnceOnly and notifiedThisSession[name]
      if not alreadyNotified and not IsMuted(name) and NotifyAllowed() then
        notifiedThisSession[name] = true
        local color = GetClassColor(fields.classEn)
        local lv = tonumber(fields.level) or 0
        local cnClass = ClassToCN(fields.classEn)
        local guildPart = (fields.guild and fields.guild ~= "") and (" |cff88ff88<" .. fields.guild .. ">|r") or ""
        E:Print(string.format("|cff88ccff[社交]|r %s%s|r Lv.%d %s%s 上线",
          color, name, lv, cnClass, guildPart))
        if DB.flashMinimap and E.FlashMinimapButton then E:FlashMinimapButton() end
      end
    end

    UpdateContact(name, {
      version = fields.version,
      level   = fields.level,
      classEn = fields.classEn,
      race    = fields.race,
      faction = fields.faction,
      guild   = fields.guild,
      lastZone = fields.zone,
    }, source or "addon")
  end

  ---------------------------------------------------------------------------
  -- 心跳协议
  ---------------------------------------------------------------------------
  -- v2 编码：HB2:version|level|classEn|race|faction|guild|zone|status
  -- 字段用 '|' 分隔（避免和实际地名/公会名中 ':' 冲突）；空字段用 '-'
  local function EncodeFields(version, level, classEn, race, faction, guild, zone, status)
    local function Esc(s)
      if not s or s == "" then return "-" end
      s = tostring(s)
      s = string.gsub(s, "|", "/")  -- 防分隔符冲突
      return s
    end
    return string.format("HB2:%s|%d|%s|%s|%s|%s|%s|%d",
      Esc(version), tonumber(level) or 0,
      Esc(classEn), Esc(race), Esc(FactionShort(faction)), Esc(guild), Esc(zone),
      tonumber(status) or 0)
  end

  local function DecodeHB2(rest)
    local v, lv, cls, race, fac, guild, zone, st =
      string.match(rest, "^([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)$")
    if not v then return nil end
    local function Unesc(s)
      if not s or s == "-" or s == "" then return "" end
      return s
    end
    return {
      version = Unesc(v),
      level   = tonumber(lv) or 0,
      classEn = Unesc(cls),
      race    = Unesc(race),
      faction = ShortFactionToFull(Unesc(fac)),
      guild   = Unesc(guild),
      zone    = Unesc(zone),
      status  = tonumber(st) or 0,
    }
  end

  -- 兼容老协议 HB:version:level:class:zone （:作分隔符，zone 可能含 :，所以 zone 是剩余全部）
  local function DecodeHB1(rest)
    local v, lv, cls, zone = string.match(rest, "^([^:]*):([^:]*):([^:]*):?(.*)$")
    if not v then return nil end
    return { version = v or "?", level = tonumber(lv) or 0, classEn = cls or "", zone = zone or "" }
  end

  local function BroadcastHeartbeat()
    RefreshPlayerInfo()
    local zone = GetZoneText and GetZoneText() or ""
    local msg = EncodeFields(E.version or "0", me.level, me.classEn, me.race, me.faction, me.guild, zone, PlayerStatus())

    if IsInGuild and IsInGuild() then
      SafeSend(msg, "GUILD")
    end
    local groupChannel = GetGroupChannel()
    if groupChannel then
      SafeSend(msg, groupChannel)
    end
    local channelNum = GetChannelName and GetChannelName("EpochCN")
    if channelNum and channelNum > 0 then
      SafeSend(msg, "CHANNEL", channelNum)  -- 3.3.5 频道地址需要数字
    end
  end

  ---------------------------------------------------------------------------
  -- addon 消息接收
  ---------------------------------------------------------------------------
  local function OnAddonMessage(prefix, message, channel, sender)
    if prefix ~= SOCIAL_PREFIX then return end
    sender = StripRealmName(sender)
    if not sender or sender == me.name then return end

    local msgType, rest = string.match(message or "", "^(%u+):(.*)$")
    if not msgType then return end

    if msgType == "HB2" then
      local fields = DecodeHB2(rest)
      if fields then RecordPlayer(sender, fields, "addon") end
      return
    end

    if msgType == "HB" then
      -- 兼容 v1
      local fields = DecodeHB1(rest)
      if fields then RecordPlayer(sender, fields, "addon") end
      return
    end

    if msgType == "PING" then
      -- 立即回复一个心跳给来源（窄频道）
      RefreshPlayerInfo()
      local zone = GetZoneText and GetZoneText() or ""
      local reply = EncodeFields(E.version or "0", me.level, me.classEn, me.race, me.faction, me.guild, zone, PlayerStatus())
      if channel == "WHISPER" then
        SafeSend(reply, "WHISPER", sender)
      elseif channel == "GUILD" then
        SafeSend(reply, "GUILD")
      elseif channel == "PARTY" or channel == "RAID" then
        SafeSend(reply, GetGroupChannel() or "PARTY")
      end
      return
    end

    if msgType == "HELLO" then
      -- 定向打招呼：HELLO:目标名
      local target = rest
      if target == me.name then
        local entry = onlinePlayers[sender] or {}
        local color = GetClassColor(entry.classEn)
        E:Print(string.format("|cff88ccff[社交]|r %s%s|r 向你打招呼！", color, sender))
        if DB.flashMinimap and E.FlashMinimapButton then E:FlashMinimapButton() end
      end
      return
    end
  end

  ---------------------------------------------------------------------------
  -- 目标框中文玩家图标
  ---------------------------------------------------------------------------
  local function UpdateTargetIcon()
    if not DB.showTargetIcon then
      if targetIcon then targetIcon:Hide() end
      return
    end
    if not TargetFrame then return end

    local name = StripRealmName(UnitName("target"))
    local isPlayer = UnitIsPlayer and UnitIsPlayer("target")
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
  -- Tooltip 标记
  ---------------------------------------------------------------------------
  local function OnTooltipSetUnit(tooltip)
    if not DB.showTooltipTag or not tooltip then return end

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
    end

    -- 不论是否在线，只要有备注/标签都显示
    local contact = DB.contacts[name]
    if contact and contact.note and contact.note ~= "" then
      tooltip:AddLine("  备注: " .. contact.note, 0.95, 0.85, 0.4)
    end
    local tags = DB.tags[name]
    if tags then
      local list = {}
      for tag in pairs(tags) do table.insert(list, tag) end
      if #list > 0 then
        table.sort(list)
        tooltip:AddLine("  标签: " .. table.concat(list, " · "), 0.6, 0.9, 0.6)
      end
    end

    if data or (contact and (contact.note or tags)) then
      tooltip:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 公开 API
  ---------------------------------------------------------------------------
  function E:GetOnlineChinesePlayers()
    CleanupExpiredPlayers()
    return onlinePlayers
  end

  function E:GetChinesePlayerCount()
    return onlineCount
  end

  function E:IsChinesePlayer(name)
    if not name then return false end
    return onlinePlayers[StripRealmName(name)] ~= nil
  end

  function E:GetContact(name)
    return name and DB.contacts[StripRealmName(name) or name]
  end

  function E:GetContactNote(name)
    local c = self:GetContact(name)
    return c and c.note
  end

  function E:SetContactNote(name, note)
    name = StripRealmName(name)
    if not name or name == "" then return end
    if note then note = string.sub(note, 1, NOTE_MAX_LEN) end
    DB.contacts[name] = DB.contacts[name] or {
      firstSeen = time(), lastSeen = time(),
      encounterCount = 0, source = "manual",
    }
    DB.contacts[name].note = (note ~= "" and note) or nil
    DB.notes[name] = nil  -- 清理老结构
    PruneContactsIfFull()
  end

  function E:GetContactTags(name)
    return DB.tags[StripRealmName(name) or name]
  end

  function E:AddContactTag(name, tag)
    name = StripRealmName(name)
    if not name or name == "" or not tag or tag == "" then return false end
    tag = string.sub(tag, 1, TAG_MAX_LEN)
    DB.tags[name] = DB.tags[name] or {}
    -- 限制每人标签数
    local n = 0
    for _ in pairs(DB.tags[name]) do n = n + 1 end
    if n >= TAG_MAX_COUNT and not DB.tags[name][tag] then
      E:Print(string.format("%s 标签数已达上限 %d。", name, TAG_MAX_COUNT))
      return false
    end
    DB.tags[name][tag] = true
    -- 也确保 contact 存在
    DB.contacts[name] = DB.contacts[name] or {
      firstSeen = time(), lastSeen = time(),
      encounterCount = 0, source = "manual",
    }
    return true
  end

  function E:RemoveContactTag(name, tag)
    name = StripRealmName(name)
    if not name or not tag then return end
    if DB.tags[name] then
      DB.tags[name][tag] = nil
      if not next(DB.tags[name]) then DB.tags[name] = nil end
    end
  end

  function E:GetAllContacts()
    return DB.contacts or {}
  end

  function E:RemoveContact(name)
    name = StripRealmName(name)
    if not name then return end
    DB.contacts[name] = nil
    DB.tags[name] = nil
    DB.notes[name] = nil
  end

  function E:BlockPlayer(name)
    name = StripRealmName(name)
    if not name or name == "" then return end
    DB.blocklist[name] = true
    if onlinePlayers[name] then
      onlinePlayers[name] = nil
      if onlineCount > 0 then onlineCount = onlineCount - 1 end
    end
    E:Print(string.format("已屏蔽 %s 的社交消息。", name))
  end

  function E:UnblockPlayer(name)
    name = StripRealmName(name)
    if not name then return end
    DB.blocklist[name] = nil
    E:Print(string.format("已取消屏蔽 %s。", name))
  end

  function E:MutePlayer(name)
    name = StripRealmName(name)
    if not name then return end
    DB.muted[name] = true
    E:Print(string.format("已静音 %s 的上线提醒（仍记录通讯录）。", name))
  end

  function E:UnmutePlayer(name)
    name = StripRealmName(name)
    if not name then return end
    DB.muted[name] = nil
    E:Print(string.format("已取消 %s 的静音。", name))
  end

  function E:SayHelloTo(name)
    name = StripRealmName(name)
    if not name or name == "" then return end
    -- 优先用 WHISPER 直接发到该玩家（最不打扰）
    local channels = {}
    if onlinePlayers[name] then
      table.insert(channels, { ch = "WHISPER", target = name })
    end
    -- 备份：公会和队伍
    if IsInGuild and IsInGuild() then
      table.insert(channels, { ch = "GUILD" })
    end
    local groupChannel = GetGroupChannel()
    if groupChannel then
      table.insert(channels, { ch = groupChannel })
    end
    if #channels == 0 then
      E:Print("没有可用频道发送打招呼消息（不在公会/队伍中，对方也未发现在线）。")
      return
    end
    for _, c in ipairs(channels) do
      SafeSend("HELLO:" .. name, c.ch, c.target)
    end
    E:Print(string.format("已向 %s 发送打招呼消息。", name))
  end

  function E:InviteChinesePlayer(name)
    name = StripRealmName(name)
    if not name or name == "" then return end
    if InviteUnit then pcall(InviteUnit, name) end
  end

  function E:WhisperContact(name)
    name = StripRealmName(name)
    if not name or name == "" then return end
    if ChatFrame_OpenChat then
      ChatFrame_OpenChat("/w " .. name .. " ")
    end
  end

  function E:RequestPing(channel, target)
    -- 主动 PING 发现在线玩家（按需调用）
    SafeSend("PING:" .. PROTOCOL_VERSION, channel or "GUILD", target)
  end

  ---------------------------------------------------------------------------
  -- 社交面板（三标签页：在线 / 通讯录 / 黑名单）
  ---------------------------------------------------------------------------
  local PANEL_W, PANEL_H = 460, 500
  local socialTab = "online"  -- online / contacts / blocked
  local socialFilter = ""     -- 搜索关键字
  local rowFrames = {}
  local searchBox

  local function PanelClose() if socialPanel then socialPanel:Hide() end end

  local function FormatLastSeen(ts)
    if not ts or ts == 0 then return "" end
    local diff = time() - ts
    if diff < 60 then return "刚刚" end
    if diff < 3600 then return string.format("%d分钟前", math.floor(diff / 60)) end
    if diff < 86400 then return string.format("%d小时前", math.floor(diff / 3600)) end
    return string.format("%d天前", math.floor(diff / 86400))
  end

  local function MatchFilter(name, contact, online)
    if not socialFilter or socialFilter == "" then return true end
    local f = string.lower(socialFilter)
    if string.find(string.lower(name), f, 1, true) then return true end
    if contact and contact.note and string.find(string.lower(contact.note), f, 1, true) then return true end
    if contact and contact.guild and contact.guild ~= "" and string.find(string.lower(contact.guild), f, 1, true) then return true end
    if online and online.zone and string.find(string.lower(online.zone), f, 1, true) then return true end
    -- 标签匹配
    local tags = DB.tags[name]
    if tags then
      for tag in pairs(tags) do
        if string.find(string.lower(tag), f, 1, true) then return true end
      end
    end
    return false
  end

  local function CollectOnlineRows()
    CleanupExpiredPlayers()
    local rows = {}
    for name, data in pairs(onlinePlayers) do
      local contact = DB.contacts[name]
      if MatchFilter(name, contact, data) then
        table.insert(rows, { name = name, online = data, contact = contact })
      end
    end
    table.sort(rows, function(a, b)
      return (a.online.level or 0) > (b.online.level or 0)
    end)
    return rows
  end

  local function CollectContactRows()
    local rows = {}
    for name, contact in pairs(DB.contacts) do
      if not DB.blocklist[name] then
        local online = onlinePlayers[name]
        if MatchFilter(name, contact, online) then
          table.insert(rows, { name = name, online = online, contact = contact })
        end
      end
    end
    table.sort(rows, function(a, b)
      -- 在线优先；其次按最近联系时间
      local ao = a.online and 1 or 0
      local bo = b.online and 1 or 0
      if ao ~= bo then return ao > bo end
      return (a.contact.lastSeen or 0) > (b.contact.lastSeen or 0)
    end)
    return rows
  end

  local function CollectBlockedRows()
    local rows = {}
    for name in pairs(DB.blocklist) do
      table.insert(rows, { name = name, contact = DB.contacts[name] })
    end
    table.sort(rows, function(a, b) return a.name < b.name end)
    return rows
  end

  local function UpdatePanelTitle()
    if not socialPanel then return end
    local label
    if socialTab == "online" then
      label = string.format("|cff33ffccEpochCN|r 中文玩家  |cff999999在线 %d|r", onlineCount)
    elseif socialTab == "contacts" then
      label = string.format("|cff33ffccEpochCN|r 通讯录  |cff999999%d 条|r", CountContacts())
    else
      local n = 0
      for _ in pairs(DB.blocklist) do n = n + 1 end
      label = string.format("|cff33ffccEpochCN|r 黑名单  |cff999999%d 人|r", n)
    end
    socialPanel.titleText:SetText(label)
  end

  local function ShowContactMenu(name)
    -- 简单弹出提示框：当前 3.3.5 不便嵌入 dropdown，用聊天命令提示
    E:Print(string.format("|cff33ffcc%s|r 操作命令：", name))
    E:Print("  /ecn note " .. name .. " <备注内容>")
    E:Print("  /ecn tag " .. name .. " <标签>     |  /ecn untag " .. name .. " <标签>")
    E:Print("  /ecn block " .. name .. "          |  /ecn unblock " .. name)
    E:Print("  /ecn mute " .. name .. "           |  /ecn unmute " .. name)
    E:Print("  /ecn forget " .. name .. "        （从通讯录删除）")
  end

  local function CreateSocialPanel()
    if socialPanel then return socialPanel end

    socialPanel = CreateFrame("Frame", "EpochCNSocialFrame", UIParent)
    socialPanel:SetSize(PANEL_W, PANEL_H)
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

    -- 标题
    socialPanel.titleText = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    socialPanel.titleText:SetPoint("TOP", socialPanel, "TOP", 0, -16)

    local close = CreateFrame("Button", nil, socialPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", socialPanel, "TOPRIGHT", -5, -5)

    -- 标签按钮
    local tabs = {
      { key = "online",   label = "在线" },
      { key = "contacts", label = "通讯录" },
      { key = "blocked",  label = "黑名单" },
    }
    socialPanel.tabBtns = {}
    for i, t in ipairs(tabs) do
      local btn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
      btn:SetSize(80, 22)
      btn:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 16 + (i - 1) * 84, -42)
      btn:SetText(t.label)
      btn.tabKey = t.key
      btn:SetScript("OnClick", function(self)
        socialTab = self.tabKey
        E:RefreshSocialPanel()
      end)
      socialPanel.tabBtns[t.key] = btn
    end

    -- 搜索框
    local searchLabel = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    searchLabel:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 16, -76)
    searchLabel:SetText("|cffffd200搜索:|r")

    searchBox = CreateFrame("EditBox", "EpochCNSocialSearchBox", socialPanel, "InputBoxTemplate")
    searchBox:SetSize(140, 20)
    searchBox:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 60, -74)
    searchBox:SetAutoFocus(false)
    searchBox:SetMaxLetters(40)
    searchBox:SetScript("OnTextChanged", function(self)
      socialFilter = self:GetText() or ""
      E:RefreshSocialPanel()
    end)
    searchBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    searchBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)

    local clearBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    clearBtn:SetSize(48, 20)
    clearBtn:SetPoint("LEFT", searchBox, "RIGHT", 8, 0)
    clearBtn:SetText("清空")
    clearBtn:SetScript("OnClick", function()
      searchBox:SetText("")
      searchBox:ClearFocus()
    end)

    local pingBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    pingBtn:SetSize(64, 20)
    pingBtn:SetPoint("TOPRIGHT", socialPanel, "TOPRIGHT", -16, -74)
    pingBtn:SetText("PING")
    pingBtn:SetScript("OnClick", function()
      if IsInGuild and IsInGuild() then E:RequestPing("GUILD") end
      local gc = GetGroupChannel()
      if gc then E:RequestPing(gc) end
      local ch = GetChannelName and GetChannelName("EpochCN")
      if ch and ch > 0 then SafeSend("PING:" .. PROTOCOL_VERSION, "CHANNEL", ch) end
      E:Print("已向公会/队伍/频道发送 PING，等待响应...")
    end)
    pingBtn:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_LEFT")
      GameTooltip:SetText("主动 PING", 1, 0.82, 0)
      GameTooltip:AddLine("向公会/队伍/中文频道发送询问，已安装 EpochCN 的玩家会自动回应。", 1, 1, 1, true)
      GameTooltip:Show()
    end)
    pingBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)

    -- 列表区域：行
    socialPanel.listHeader = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    socialPanel.listHeader:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 16, -106)
    socialPanel.listHeader:SetWidth(PANEL_W - 32)
    socialPanel.listHeader:SetJustifyH("LEFT")

    rowFrames = {}
    for i = 1, MAX_LIST_ROWS do
      local row = CreateFrame("Button", nil, socialPanel)
      row:SetSize(PANEL_W - 32, 22)
      row:SetPoint("TOPLEFT", socialPanel, "TOPLEFT", 16, -126 - (i - 1) * 22)

      local bg = row:CreateTexture(nil, "BACKGROUND")
      bg:SetAllPoints()
      bg:SetTexture("Interface\\Buttons\\UI-Listbox-Highlight2")
      bg:SetAlpha(0)
      row.bg = bg

      row.statusText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.statusText:SetPoint("LEFT", row, "LEFT", 4, 0)
      row.statusText:SetWidth(20)
      row.statusText:SetJustifyH("LEFT")

      row.nameText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.nameText:SetPoint("LEFT", row, "LEFT", 22, 0)
      row.nameText:SetWidth(110)
      row.nameText:SetJustifyH("LEFT")

      row.infoText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.infoText:SetPoint("LEFT", row, "LEFT", 132, 0)
      row.infoText:SetWidth(120)
      row.infoText:SetJustifyH("LEFT")

      row.metaText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.metaText:SetPoint("LEFT", row, "LEFT", 252, 0)
      row.metaText:SetWidth(160)
      row.metaText:SetJustifyH("LEFT")

      row:RegisterForClicks("LeftButtonUp", "RightButtonUp", "MiddleButtonUp")
      row:SetScript("OnEnter", function(self)
        self.bg:SetAlpha(0.3)
        if not self.playerName then return end
        local name = self.playerName
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        local color = GetClassColor(self.online and self.online.classEn or (self.contact and self.contact.classEn))
        GameTooltip:SetText(color .. name .. "|r", 1, 1, 1)

        local online = self.online
        local contact = self.contact
        if online then
          GameTooltip:AddLine(string.format("Lv.%d %s %s%s",
            online.level or 0,
            ClassToCN(online.classEn),
            FactionToCN(online.faction),
            online.race ~= "" and ("·" .. online.race) or ""), 0.9, 0.9, 0.9)
          if online.guild and online.guild ~= "" then
            GameTooltip:AddLine("公会: " .. online.guild, 0.5, 0.9, 0.5)
          end
          if online.zone and online.zone ~= "" then
            GameTooltip:AddLine("区域: " .. online.zone, 0.7, 0.7, 0.7)
          end
          if online.status and online.status ~= 0 then
            GameTooltip:AddLine("状态: " .. StatusToCN(online.status), 1, 0.82, 0.2)
          end
          GameTooltip:AddLine("插件: v" .. (online.version or "?"), 0.4, 0.6, 0.9)
        elseif contact then
          GameTooltip:AddLine(string.format("Lv.%d %s",
            contact.level or 0, ClassToCN(contact.classEn)), 0.7, 0.7, 0.7)
          if contact.guild and contact.guild ~= "" then
            GameTooltip:AddLine("公会: " .. contact.guild, 0.5, 0.9, 0.5)
          end
          GameTooltip:AddLine("最后见到: " .. FormatLastSeen(contact.lastSeen), 0.7, 0.7, 0.7)
          if contact.encounterCount and contact.encounterCount > 1 then
            GameTooltip:AddLine("相遇次数: " .. contact.encounterCount, 0.7, 0.7, 0.7)
          end
        end

        if contact and contact.note and contact.note ~= "" then
          GameTooltip:AddLine(" ")
          GameTooltip:AddLine("备注: " .. contact.note, 0.95, 0.85, 0.4, true)
        end
        local tags = DB.tags[name]
        if tags then
          local list = {}
          for tag in pairs(tags) do table.insert(list, tag) end
          if #list > 0 then
            table.sort(list)
            GameTooltip:AddLine("标签: " .. table.concat(list, " · "), 0.6, 0.9, 0.6)
          end
        end

        GameTooltip:AddLine(" ")
        if socialTab == "blocked" then
          GameTooltip:AddLine("|cffffd200左键|r 取消屏蔽", 0.6, 0.6, 0.6)
        else
          GameTooltip:AddLine("|cffffd200左键|r 密语   |cffffd200右键|r 邀请组队", 0.6, 0.6, 0.6)
          GameTooltip:AddLine("|cffffd200中键|r 显示操作菜单", 0.6, 0.6, 0.6)
        end
        GameTooltip:Show()
      end)
      row:SetScript("OnLeave", function(self)
        self.bg:SetAlpha(0)
        GameTooltip:Hide()
      end)
      row:SetScript("OnClick", function(self, button)
        if not self.playerName then return end
        if socialTab == "blocked" then
          if button == "LeftButton" then
            E:UnblockPlayer(self.playerName)
            E:RefreshSocialPanel()
          end
          return
        end
        if button == "LeftButton" then
          E:WhisperContact(self.playerName)
        elseif button == "RightButton" then
          E:InviteChinesePlayer(self.playerName)
        elseif button == "MiddleButton" then
          ShowContactMenu(self.playerName)
        end
      end)
      row:Hide()
      rowFrames[i] = row
    end

    -- 翻页
    socialPanel.pageInfo = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    socialPanel.pageInfo:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 60)

    socialPanel.prevBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    socialPanel.prevBtn:SetSize(60, 22)
    socialPanel.prevBtn:SetPoint("BOTTOM", socialPanel, "BOTTOM", -70, 56)
    socialPanel.prevBtn:SetText("< 上页")
    socialPanel.prevBtn:SetScript("OnClick", function()
      socialPanel.page = math.max(1, (socialPanel.page or 1) - 1)
      E:RefreshSocialPanel()
    end)

    socialPanel.nextBtn = CreateFrame("Button", nil, socialPanel, "UIPanelButtonTemplate")
    socialPanel.nextBtn:SetSize(60, 22)
    socialPanel.nextBtn:SetPoint("BOTTOM", socialPanel, "BOTTOM", 70, 56)
    socialPanel.nextBtn:SetText("下页 >")
    socialPanel.nextBtn:SetScript("OnClick", function()
      socialPanel.page = (socialPanel.page or 1) + 1
      E:RefreshSocialPanel()
    end)

    socialPanel.page = 1

    -- 底部 QQ 群
    local qqInfo = socialPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    qqInfo:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 30)
    qqInfo:SetText("|cffffd200QQ 交流群:|r |cff33ffcc1097800503|r")

    -- QQ 群号复制框（点击底部信息行后显示）
    local qqBtn = CreateFrame("Button", nil, socialPanel)
    qqBtn:SetSize(260, 16)
    qqBtn:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 28)
    qqBtn:SetScript("OnClick", function()
      if not socialPanel.qqCopyBox then
        local box = CreateFrame("EditBox", nil, socialPanel, "InputBoxTemplate")
        box:SetSize(140, 22)
        box:SetPoint("BOTTOM", socialPanel, "BOTTOM", 0, 6)
        box:SetAutoFocus(true)
        box:SetMaxLetters(20)
        box:SetText("1097800503")
        box:HighlightText()
        box:SetScript("OnEscapePressed", function(self) self:ClearFocus(); self:Hide() end)
        box:SetScript("OnEnterPressed", function(self) self:ClearFocus(); self:Hide() end)
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
      GameTooltip:SetText("点击复制 QQ 群号", 1, 0.82, 0)
      GameTooltip:Show()
    end)
    qqBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)

    return socialPanel
  end

  function E:RefreshSocialPanel()
    if not socialPanel then return end

    -- 标签按钮高亮
    for key, btn in pairs(socialPanel.tabBtns) do
      if key == socialTab then
        btn:LockHighlight()
      else
        btn:UnlockHighlight()
      end
    end

    UpdatePanelTitle()

    local rows
    if socialTab == "online" then
      rows = CollectOnlineRows()
      socialPanel.listHeader:SetText("|cffffd200状态  名字              等级·职业            公会/区域|r")
    elseif socialTab == "contacts" then
      rows = CollectContactRows()
      socialPanel.listHeader:SetText("|cffffd200状态  名字              等级·职业            最后见到/备注|r")
    else
      rows = CollectBlockedRows()
      socialPanel.listHeader:SetText("|cffffd200状态  名字              备注|r")
    end

    local totalPages = math.max(1, math.ceil(#rows / MAX_LIST_ROWS))
    socialPanel.page = math.min(socialPanel.page or 1, totalPages)
    local startIdx = (socialPanel.page - 1) * MAX_LIST_ROWS

    for i = 1, MAX_LIST_ROWS do
      local row = rowFrames[i]
      local entry = rows[startIdx + i]
      if entry then
        row.playerName = entry.name
        row.online = entry.online
        row.contact = entry.contact

        local color = GetClassColor((entry.online and entry.online.classEn) or (entry.contact and entry.contact.classEn))
        row.nameText:SetText(color .. entry.name .. "|r")

        if socialTab == "blocked" then
          row.statusText:SetText("|cffff6666✕|r")
          row.infoText:SetText("|cff999999已屏蔽|r")
          row.metaText:SetText(entry.contact and entry.contact.note or "")
        elseif entry.online then
          row.statusText:SetText("|cff33ff99●|r")
          local cnClass = ClassToCN(entry.online.classEn)
          local statusTag = entry.online.status ~= 0 and (" " .. StatusToCN(entry.online.status)) or ""
          row.infoText:SetText(string.format("Lv.%d %s%s", entry.online.level or 0, cnClass, statusTag))
          local meta = ""
          if entry.online.guild and entry.online.guild ~= "" then
            meta = "|cff88ff88<" .. entry.online.guild .. ">|r "
          end
          if entry.online.zone and entry.online.zone ~= "" then
            meta = meta .. "|cff999999" .. entry.online.zone .. "|r"
          end
          row.metaText:SetText(meta)
        else
          row.statusText:SetText("|cff666666○|r")
          local cnClass = ClassToCN(entry.contact and entry.contact.classEn or "")
          row.infoText:SetText(string.format("Lv.%d %s",
            (entry.contact and entry.contact.level) or 0, cnClass))
          local meta = ""
          if entry.contact and entry.contact.note and entry.contact.note ~= "" then
            meta = "|cffe5cc66" .. entry.contact.note .. "|r"
          else
            meta = "|cff666666" .. FormatLastSeen(entry.contact and entry.contact.lastSeen) .. "|r"
          end
          row.metaText:SetText(meta)
        end
        row:Show()
      else
        row.playerName = nil
        row.online = nil
        row.contact = nil
        row:Hide()
      end
    end

    socialPanel.pageInfo:SetText(string.format("|cff999999第 %d / %d 页  共 %d 条|r",
      socialPanel.page, totalPages, #rows))
    if socialPanel.page <= 1 then socialPanel.prevBtn:Disable() else socialPanel.prevBtn:Enable() end
    if socialPanel.page >= totalPages then socialPanel.nextBtn:Disable() else socialPanel.nextBtn:Enable() end
  end

  function E:ToggleSocialPanel()
    local panel = CreateSocialPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      socialPanel.page = 1
      socialFilter = ""
      if searchBox then searchBox:SetText("") end
      E:RefreshSocialPanel()
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 斜杠命令
  ---------------------------------------------------------------------------
  local function ParseNameAndArgs(rest)
    return string.match(rest or "", "^%s*(%S+)%s*(.*)%s*$")
  end

  E:RegisterSlashHandler(function(msg)
    msg = msg or ""

    if msg == "social" or msg == "cn players" then
      E:ToggleSocialPanel(); return true
    end

    if msg == "social list" or msg == "social online" then
      CleanupExpiredPlayers(true)
      local rows = CollectOnlineRows()
      E:Print(string.format("|cff33ffcc在线中文玩家：%d 人|r", #rows))
      for i = 1, math.min(#rows, 20) do
        local r = rows[i]
        local color = GetClassColor(r.online.classEn)
        local zone = (r.online.zone and r.online.zone ~= "") and ("  " .. r.online.zone) or ""
        E:Print(string.format("  %s%s|r  Lv.%d %s%s",
          color, r.name, r.online.level or 0, ClassToCN(r.online.classEn), zone))
      end
      if #rows == 0 then E:Print("  暂未发现其他中文玩家在线。") end
      if #rows > 20 then E:Print(string.format("  ...另有 %d 人，使用 /ecn social 查看完整列表。", #rows - 20)) end
      return true
    end

    if msg == "social ping" then
      if IsInGuild and IsInGuild() then E:RequestPing("GUILD") end
      local gc = GetGroupChannel()
      if gc then E:RequestPing(gc) end
      local ch = GetChannelName and GetChannelName("EpochCN")
      if ch and ch > 0 then SafeSend("PING:" .. PROTOCOL_VERSION, "CHANNEL", ch) end
      E:Print("已主动 PING 公会/队伍/中文频道。")
      return true
    end

    -- /ecn note <name> [备注]
    local target, args = string.match(msg, "^note%s+(%S+)%s*(.*)$")
    if target then
      if args and args ~= "" then
        E:SetContactNote(target, args)
        E:Print(string.format("已为 %s 设置备注：%s", target, args))
      else
        local existing = E:GetContactNote(target)
        if existing then
          E:Print(string.format("%s 备注：%s", target, existing))
        else
          E:Print(string.format("%s 暂无备注。用法: /ecn note %s 内容", target, target))
        end
      end
      return true
    end

    target, args = string.match(msg, "^tag%s+(%S+)%s*(.*)$")
    if target then
      if args and args ~= "" then
        if E:AddContactTag(target, args) then
          E:Print(string.format("已为 %s 添加标签：%s", target, args))
        end
      else
        local tags = DB.tags[target]
        if tags and next(tags) then
          local list = {}
          for tag in pairs(tags) do table.insert(list, tag) end
          E:Print(string.format("%s 的标签：%s", target, table.concat(list, " · ")))
        else
          E:Print(string.format("%s 暂无标签。", target))
        end
      end
      return true
    end

    target, args = string.match(msg, "^untag%s+(%S+)%s+(.+)$")
    if target then
      E:RemoveContactTag(target, args)
      E:Print(string.format("已移除 %s 的标签：%s", target, args))
      return true
    end

    target = string.match(msg, "^block%s+(%S+)$")
    if target then E:BlockPlayer(target); return true end

    target = string.match(msg, "^unblock%s+(%S+)$")
    if target then E:UnblockPlayer(target); return true end

    target = string.match(msg, "^mute%s+(%S+)$")
    if target then E:MutePlayer(target); return true end

    target = string.match(msg, "^unmute%s+(%S+)$")
    if target then E:UnmutePlayer(target); return true end

    target = string.match(msg, "^forget%s+(%S+)$")
    if target then
      E:RemoveContact(target)
      E:Print(string.format("已从通讯录删除 %s。", target))
      return true
    end

    target = string.match(msg, "^hello%s+(%S+)$")
    if target then E:SayHelloTo(target); return true end

    if msg == "contacts" then
      local contacts = E:GetAllContacts()
      local rows = {}
      for name, data in pairs(contacts) do
        if not DB.blocklist[name] then
          table.insert(rows, { name = name, data = data })
        end
      end
      table.sort(rows, function(a, b) return (a.data.lastSeen or 0) > (b.data.lastSeen or 0) end)
      E:Print(string.format("|cff33ffcc通讯录：%d 条（按最近联系排序）|r", #rows))
      for i = 1, math.min(#rows, 20) do
        local r = rows[i]
        local note = r.data.note and r.data.note ~= "" and ("  |cffe5cc66[" .. r.data.note .. "]|r") or ""
        local online = onlinePlayers[r.name] and "|cff33ff99●|r " or "|cff666666○|r "
        E:Print(string.format("  %s%s  Lv.%d %s%s",
          online, r.name, r.data.level or 0, ClassToCN(r.data.classEn), note))
      end
      if #rows > 20 then E:Print(string.format("  ...另有 %d 条，/ecn social 切换到通讯录标签查看完整。", #rows - 20)) end
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 事件循环（单 OnUpdate，节流）
  ---------------------------------------------------------------------------
  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:RegisterEvent("PARTY_MEMBERS_CHANGED")
  frame:RegisterEvent("RAID_ROSTER_UPDATE")
  frame:RegisterEvent("PLAYER_TARGET_CHANGED")
  frame:RegisterEvent("PLAYER_GUILD_UPDATE")
  frame:RegisterEvent("PLAYER_FLAGS_CHANGED")  -- AFK/DND 切换
  frame:RegisterEvent("ZONE_CHANGED_NEW_AREA")

  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "CHAT_MSG_ADDON" then
      OnAddonMessage(...)
      return
    end

    if event == "PLAYER_ENTERING_WORLD" then
      if initialized then return end
      initialized = true
      RefreshPlayerInfo()

      -- Hook tooltip
      if GameTooltip and GameTooltip.HookScript then
        GameTooltip:HookScript("OnTooltipSetUnit", OnTooltipSetUnit)
      end

      -- 延迟 5 秒首次广播 + PING（避免与登录广播冲突）
      local initFrame = CreateFrame("Frame")
      initFrame.elapsed = 0
      initFrame:SetScript("OnUpdate", function(self, elapsed)
        self.elapsed = self.elapsed + elapsed
        if self.elapsed < 5 then return end
        self:SetScript("OnUpdate", nil)
        if IsInGuild and IsInGuild() then SafeSend("PING:" .. PROTOCOL_VERSION, "GUILD") end
        local gc = GetGroupChannel()
        if gc then SafeSend("PING:" .. PROTOCOL_VERSION, gc) end
        BroadcastHeartbeat()
      end)
      return
    end

    if event == "PARTY_MEMBERS_CHANGED" or event == "RAID_ROSTER_UPDATE" then
      local now = time()
      if now - lastGroupHB < TARGET_HB_COOLDOWN then return end
      lastGroupHB = now
      BroadcastHeartbeat()
      return
    end

    if event == "PLAYER_TARGET_CHANGED" then
      UpdateTargetIcon()
      return
    end

    if event == "PLAYER_GUILD_UPDATE" or event == "PLAYER_FLAGS_CHANGED" or event == "ZONE_CHANGED_NEW_AREA" then
      -- 状态变化时立即重发心跳（带冷却）
      local now = time()
      if now - lastGroupHB < TARGET_HB_COOLDOWN then return end
      lastGroupHB = now
      RefreshPlayerInfo()
      BroadcastHeartbeat()
      return
    end
  end)

  -- 心跳定时器
  local heartbeatFrame = CreateFrame("Frame")
  heartbeatFrame:SetScript("OnUpdate", function(_, elapsed)
    heartbeatTimer = heartbeatTimer + elapsed
    if heartbeatTimer >= heartbeatNext then
      heartbeatTimer = 0
      heartbeatNext = HEARTBEAT_INTERVAL + math.random(-HEARTBEAT_JITTER, HEARTBEAT_JITTER)
      BroadcastHeartbeat()
      CleanupExpiredPlayers()
      -- 同步刷新目标图标（玩家可能上线/下线）
      UpdateTargetIcon()
      -- 同步刷新面板（如果打开）
      if socialPanel and socialPanel:IsShown() then
        E:RefreshSocialPanel()
      end
    end
  end)

  ---------------------------------------------------------------------------
  -- 密语自动记录（含中文字符则进通讯录）
  ---------------------------------------------------------------------------
  local whisperFrame = CreateFrame("Frame")
  whisperFrame:RegisterEvent("CHAT_MSG_WHISPER")
  whisperFrame:RegisterEvent("CHAT_MSG_WHISPER_INFORM")
  whisperFrame:SetScript("OnEvent", function(_, event, message, sender)
    if not DB.recordWhisper then return end
    if not message or message == "" then return end
    local name = StripRealmName(sender)
    if not name or name == "" or name == me.name then return end
    if IsBlocked(name) then return end
    -- 中文字符判定：CHAT_MSG_WHISPER（收到的）才检测中文，发送的（INFORM）不检测
    if event == "CHAT_MSG_WHISPER" and not HasCJK(message) then return end

    UpdateContact(name, {}, "whisper")
  end)

  E:Debug("Social v2 模块已加载")
end)
