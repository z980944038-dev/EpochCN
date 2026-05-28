-- LFGBoard.lua  v2  (EpochCN 0.7.1)
-- 中文玩家组队招募板：通过 addon channel 在公会/中文频道广播组队需求，
-- 提供完整 UI（滚动列表、过滤、详细发布表单、申请追踪）。
--
-- 修复点：
--   * newEntryNotified 加入 5 分钟过期清理，避免内存泄漏
--   * OK/DTK 副本代码冗余修正
--   * 列表改为滚动框，可显示全部条目
--   * 过滤栏：按副本/角色/等级筛选
--   * 发布表单：等级范围、需求人数（坦/治/DPS）、备注
--   * 申请追踪：记录已申请过哪些招募（24 小时不重复申请）
--   * 角色信息广播：sender 的等级/职业/装等也作为附加信息发出
--   * 自己发布的不出现在自己列表（去重）
--   * 中文搜索：按副本中文名也能匹配

EpochCN:RegisterModule("LFGBoard", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  if EpochCNDB.social.lfgEnabled == nil then EpochCNDB.social.lfgEnabled = true end
  if not EpochCNDB.social.lfgEnabled then return end

  ---------------------------------------------------------------------------
  -- 常量
  ---------------------------------------------------------------------------
  local LFG_PREFIX           = "EPOCHCN_LFG"
  local CHANNEL_NAME         = "china"
  local LFG_PROTOCOL         = 2
  local LFG_EXPIRE_TIME      = 600       -- 招募过期（秒）— 提升到 10 分钟
  local LFG_BROADCAST_CD     = 30
  local LFG_REPOST_INTERVAL  = 180       -- 自动重发间隔
  local NOTIFY_EXPIRE        = 300       -- 通知去重过期
  local APPLY_COOLDOWN       = 86400     -- 重复申请冷却（24 小时）
  local MAX_LFG_ENTRIES      = 80
  local PANEL_W, PANEL_H     = 560, 540
  local LIST_ROWS            = 10        -- 可视行数（带滚动）

  ---------------------------------------------------------------------------
  -- 副本数据 (code => { 中文名, 类型(D=5人副本/R=团本/B=战场/A=竞技场/W=世界Boss/Q=任务/O=其他), 推荐等级 })
  ---------------------------------------------------------------------------
  local DUNGEONS = {
    -- 经典 5 人副本
    RFC      = { "怒焰裂谷",       "D", 13 },
    DM       = { "死亡矿井",       "D", 17 },
    WC       = { "哀嚎洞穴",       "D", 17 },
    SFK      = { "影牙城堡",       "D", 22 },
    BFD      = { "黑暗深渊",       "D", 24 },
    STOCKS   = { "监狱",           "D", 26 },
    GNOMER   = { "诺莫瑞根",       "D", 29 },
    SMG      = { "血色修道院-墓地","D", 28 },
    SML      = { "血色修道院-图书馆", "D", 32 },
    SMA      = { "血色修道院-军械库", "D", 36 },
    SMC      = { "血色修道院-大教堂", "D", 38 },
    SM       = { "血色修道院",     "D", 32 },
    RFD      = { "剃刀高地",       "D", 38 },
    RFK      = { "剃刀沼泽",       "D", 32 },
    ULDA     = { "奥达曼",         "D", 41 },
    ZF       = { "祖尔法拉克",     "D", 46 },
    MARA     = { "玛拉顿",         "D", 47 },
    ST       = { "阿塔哈卡神庙",   "D", 50 },
    BRD      = { "黑石深渊",       "D", 52 },
    LBRS     = { "黑石塔下层",     "D", 55 },
    UBRS     = { "黑石塔上层",     "D", 58 },
    STRAT    = { "斯坦索姆",       "D", 56 },
    SCHOLO   = { "通灵学院",       "D", 56 },
    DIRE     = { "厄运之槌",       "D", 56 },
    -- TBC 5 人副本
    RAMPS    = { "地狱火城墙",     "D", 60 },
    BF       = { "血熔炉",         "D", 61 },
    SPC      = { "奴隶围栏",       "D", 62 },
    UB       = { "幽暗沼泽",       "D", 63 },
    MT       = { "法力陵墓",       "D", 64 },
    AC       = { "奥金尼地穴",     "D", 64 },
    SH       = { "塞泰克大厅",     "D", 65 },
    SLM      = { "暗影迷宫",       "D", 67 },
    OHF      = { "旧希尔斯布莱德", "D", 66 },
    BM       = { "黑色沼泽",       "D", 68 },
    MECH     = { "能源舰",         "D", 69 },
    BOT      = { "生态船",         "D", 70 },
    ARC      = { "禁魔监狱",       "D", 70 },
    SV       = { "蒸汽地窖",       "D", 70 },
    MGT      = { "魔导师平台",     "D", 70 },
    -- WotLK 5 人副本
    UK       = { "乌特加德城堡",   "D", 70 },
    NEXUS    = { "魔枢",           "D", 71 },
    AN       = { "艾卓-尼鲁布",    "D", 73 },
    OK       = { "古达克",         "D", 74 },
    VH       = { "紫罗兰监狱",     "D", 73 },
    DTK      = { "达克萨隆要塞",   "D", 75 },
    GD       = { "古达克",         "D", 74 },
    HOS      = { "岩石大厅",       "D", 75 },
    HOL      = { "闪电大厅",       "D", 75 },
    COS      = { "净化斯坦索姆",   "D", 80 },
    UP       = { "乌特加德之巅",   "D", 78 },
    OCCI     = { "魔环",           "D", 76 },
    TOC5     = { "冠军的试炼",     "D", 80 },
    FOS      = { "灵魂熔炉",       "D", 80 },
    POS      = { "映像大厅",       "D", 80 },
    HOR      = { "恐惧之厅",       "D", 80 },
    -- 经典 / TBC 团本
    MC       = { "熔火之心",       "R", 60 },
    BWL      = { "黑翼之巢",       "R", 60 },
    AQ20     = { "安其拉废墟",     "R", 60 },
    AQ40     = { "安其拉神殿",     "R", 60 },
    ZG       = { "祖尔格拉布",     "R", 60 },
    ONY      = { "奥妮克希亚的巢穴","R", 60 },
    -- WotLK 团本
    NAXX     = { "纳克萨玛斯",     "R", 80 },
    OS       = { "黑曜石圣殿",     "R", 80 },
    VOA      = { "阿尔卡冯的宝库", "R", 80 },
    EYE      = { "永恒之眼",       "R", 80 },
    ULDU     = { "奥杜尔",         "R", 80 },
    TOC      = { "十字军的试炼",   "R", 80 },
    ICC      = { "冰冠堡垒",       "R", 80 },
    RS       = { "红玉圣殿",       "R", 80 },
    -- PvP
    BG       = { "战场",           "B", 0  },
    ARENA    = { "竞技场",         "A", 70 },
    WSG      = { "战歌峡谷",       "B", 10 },
    AB       = { "阿拉希盆地",     "B", 20 },
    AV       = { "奥特兰克山谷",   "B", 51 },
    EOTS     = { "风暴之眼",       "B", 61 },
    SOTA     = { "远古海滩",       "B", 71 },
    IOC      = { "征服之岛",       "B", 71 },
    -- 其他
    WORLD    = { "世界Boss",       "W", 0  },
    QUEST    = { "任务",           "Q", 0  },
    DAILY    = { "日常",           "Q", 0  },
    OTHER    = { "其他",           "O", 0  },
  }

  -- 类型筛选
  local TYPE_NAMES = {
    ALL = "全部", D = "5人副本", R = "团本", B = "战场", A = "竞技场",
    W = "世界Boss", Q = "任务", O = "其他",
  }

  -- 反向：中文名 → code
  local CN_TO_CODE = {}
  for code, info in pairs(DUNGEONS) do
    CN_TO_CODE[info[1]] = code
  end

  ---------------------------------------------------------------------------
  -- 注册 addon prefix
  ---------------------------------------------------------------------------
  if RegisterAddonMessagePrefix then
    pcall(RegisterAddonMessagePrefix, LFG_PREFIX)
  end

  ---------------------------------------------------------------------------
  -- 运行时
  ---------------------------------------------------------------------------
  local lfgEntries = {}              -- list[i] = entry
  local lfgByCode  = {}              -- sender => entry index for quick replace
  local myPosting  = nil
  local lastBroadcast = 0
  local repostTimer = 0
  local cleanupTimer = 0
  local notifyExpiryQueue = {}       -- name => last notified ts

  -- 申请追踪：sender => lastApplyTime
  EpochCNDB.social.lfgApplied = EpochCNDB.social.lfgApplied or {}

  -- 过滤
  local filter = { type = "ALL", role = "ALL", levelMin = 1, levelMax = 80, search = "" }

  local lfgPanel
  local rowFrames
  local scrollOffset = 0
  local frame = CreateFrame("Frame")

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
    return StripRealmName(UnitName("player"))
  end

  local function IsPlayerInGuild()
    if IsInGuild and IsInGuild() then return true end
    local guild = GetGuildInfo and GetGuildInfo("player")
    return guild and guild ~= ""
  end

  local function MyClass()
    local _, c = UnitClass("player")
    return c or ""
  end

  local CN_CLASS = {
    WARRIOR = "战士", PALADIN = "圣骑士", HUNTER = "猎人", ROGUE = "潜行者",
    PRIEST = "牧师", DEATHKNIGHT = "死亡骑士", SHAMAN = "萨满", MAGE = "法师",
    WARLOCK = "术士", DRUID = "德鲁伊",
  }

  local function GetClassColor(classEn)
    local c = RAID_CLASS_COLORS and RAID_CLASS_COLORS[classEn or ""]
    if c and c.r and c.g and c.b then
      return string.format("|cff%02x%02x%02x",
        math.floor(c.r * 255 + 0.5), math.floor(c.g * 255 + 0.5), math.floor(c.b * 255 + 0.5))
    end
    return "|cffffffff"
  end

  local function ClassToCN(classEn)
    return CN_CLASS[string.upper(classEn or "")] or classEn or ""
  end

  local function GetDungeonInfo(code)
    code = string.upper(code or "")
    local info = DUNGEONS[code]
    if info then return info[1], info[2], info[3] end
    -- 用户自定义（中文输入），直接返回原文
    return code, "O", 0
  end

  local function CodeFromInput(input)
    if not input or input == "" then return "OTHER" end
    local up = string.upper(input)
    if DUNGEONS[up] then return up end
    -- 中文名匹配
    if CN_TO_CODE[input] then return CN_TO_CODE[input] end
    -- 模糊中文匹配
    for cn, code in pairs(CN_TO_CODE) do
      if string.find(cn, input, 1, true) then return code end
    end
    return up
  end

  local function FormatDungeonLabel(code)
    local cn, ty = GetDungeonInfo(code)
    return cn .. " |cff666666[" .. (TYPE_NAMES[ty] or ty) .. "]|r"
  end

  local function FormatTimeAgo(ts)
    if not ts or ts == 0 then return "" end
    local diff = time() - ts
    if diff < 60 then return diff .. "秒前" end
    if diff < 3600 then return math.floor(diff / 60) .. "分钟前" end
    return math.floor(diff / 3600) .. "小时前"
  end

  local function CleanupExpired()
    local now = time()
    -- 清理过期招募
    local kept = {}
    lfgByCode = {}
    for _, entry in ipairs(lfgEntries) do
      if now - (entry.timestamp or 0) < LFG_EXPIRE_TIME then
        table.insert(kept, entry)
        lfgByCode[entry.sender] = #kept
      end
    end
    lfgEntries = kept

    -- 清理过期通知去重表
    for name, ts in pairs(notifyExpiryQueue) do
      if now - ts > NOTIFY_EXPIRE then
        notifyExpiryQueue[name] = nil
      end
    end
  end

  local function MatchFilter(entry)
    local code = entry.dungeon or "OTHER"
    local cn, ty, _ = GetDungeonInfo(code)
    if filter.type ~= "ALL" and filter.type ~= ty then return false end
    -- 角色过滤
    if filter.role == "TANK" and not entry.needTank then return false end
    if filter.role == "HEALER" and not entry.needHealer then return false end
    if filter.role == "DPS" and (entry.needDPS or 0) <= 0 then return false end
    -- 等级过滤
    if entry.maxLevel and entry.maxLevel > 0 and filter.levelMin > entry.maxLevel then return false end
    if entry.minLevel and filter.levelMax < entry.minLevel then return false end
    -- 搜索
    if filter.search and filter.search ~= "" then
      local s = string.lower(filter.search)
      local hay = string.lower((entry.sender or "") .. " " .. (cn or "") .. " " .. (entry.note or "") .. " " .. (entry.senderClass or ""))
      if not string.find(hay, s, 1, true) then return false end
    end
    return true
  end

  ---------------------------------------------------------------------------
  -- 协议编码 (v2)
  -- POST2:dungeon|minLv|maxLv|needT|needH|needD|senderLv|senderClass|note
  -- CANCEL2:sender
  ---------------------------------------------------------------------------
  local function EncodePost(entry)
    local function Esc(s)
      if not s then return "-" end
      s = tostring(s)
      s = string.gsub(s, "|", "/")
      if s == "" then return "-" end
      return s
    end
    return string.format("POST2:%s|%d|%d|%d|%d|%d|%d|%s|%s",
      Esc(entry.dungeon or "OTHER"),
      tonumber(entry.minLevel) or 0,
      tonumber(entry.maxLevel) or 0,
      entry.needTank and 1 or 0,
      entry.needHealer and 1 or 0,
      tonumber(entry.needDPS) or 0,
      tonumber(entry.senderLevel) or 0,
      Esc(entry.senderClass or ""),
      Esc(entry.note or ""))
  end

  local function DecodePost(rest)
    local d, lo, hi, t, h, dps, slv, scls, note =
      string.match(rest, "^([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|(.*)$")
    if not d then return nil end
    local function Unesc(s)
      if not s or s == "-" or s == "" then return "" end
      return s
    end
    return {
      dungeon     = Unesc(d) ~= "" and Unesc(d) or "OTHER",
      minLevel    = tonumber(lo) or 0,
      maxLevel    = tonumber(hi) or 0,
      needTank    = t == "1",
      needHealer  = h == "1",
      needDPS     = tonumber(dps) or 0,
      senderLevel = tonumber(slv) or 0,
      senderClass = Unesc(scls),
      note        = Unesc(note),
    }
  end

  local function DecodePostV1(rest)
    -- POST:dungeon:minLv:t:h:dps:note
    local d, lo, t, h, dps, note = string.match(rest, "^([^:]*):([^:]*):([^:]*):([^:]*):([^:]*):(.*)$")
    if not d then return nil end
    return {
      dungeon = d ~= "" and d or "OTHER",
      minLevel = tonumber(lo) or 0,
      maxLevel = 0,
      needTank = t == "1",
      needHealer = h == "1",
      needDPS = tonumber(dps) or 0,
      senderLevel = 0,
      senderClass = "",
      note = note or "",
    }
  end

  ---------------------------------------------------------------------------
  -- 广播
  ---------------------------------------------------------------------------
  local function BroadcastEntry(entry, isRepost)
    if not entry then return end
    local now = time()
    if not isRepost and now - lastBroadcast < LFG_BROADCAST_CD then
      E:Print(string.format("|cffff6666广播冷却中（剩余 %d 秒）。|r", LFG_BROADCAST_CD - (now - lastBroadcast)))
      return false
    end
    lastBroadcast = now
    local msg = EncodePost(entry)
    if IsPlayerInGuild() then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "GUILD")
    end
    local channelNum = GetChannelName and GetChannelName(CHANNEL_NAME)
    if channelNum and channelNum > 0 then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "CHANNEL", channelNum)
    end
    if not isRepost then E:Print("|cff33ffcc组队信息已广播。|r") end
    return true
  end

  local function CancelLFG(silent)
    if not myPosting then
      if not silent then E:Print("你当前没有发布组队信息。") end
      return
    end
    local msg = "CANCEL2:" .. (GetMyName() or "")
    if IsPlayerInGuild() then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "GUILD")
    end
    local channelNum = GetChannelName and GetChannelName(CHANNEL_NAME)
    if channelNum and channelNum > 0 then
      pcall(SendAddonMessage, LFG_PREFIX, msg, "CHANNEL", channelNum)
    end
    -- 同时从本地列表移除
    local me = GetMyName()
    local kept = {}
    for _, entry in ipairs(lfgEntries) do
      if entry.sender ~= me then table.insert(kept, entry) end
    end
    lfgEntries = kept
    myPosting = nil
    if not silent then E:Print("已取消组队发布。") end
    if lfgPanel and lfgPanel:IsShown() then E:RefreshLFGPanel() end
  end

  ---------------------------------------------------------------------------
  -- 接收
  ---------------------------------------------------------------------------
  local function HandlePost(sender, decoded)
    -- 自己发的不入本地列表（避免列表里看到自己）
    if sender == GetMyName() then return end

    -- 移除该玩家旧条目
    local kept = {}
    for _, entry in ipairs(lfgEntries) do
      if entry.sender ~= sender then table.insert(kept, entry) end
    end
    lfgEntries = kept

    -- 加入新条目
    local entry = {
      sender      = sender,
      dungeon     = decoded.dungeon or "OTHER",
      minLevel    = decoded.minLevel or 0,
      maxLevel    = decoded.maxLevel or 0,
      needTank    = decoded.needTank,
      needHealer  = decoded.needHealer,
      needDPS     = decoded.needDPS or 0,
      senderLevel = decoded.senderLevel or 0,
      senderClass = decoded.senderClass or "",
      note        = decoded.note or "",
      timestamp   = time(),
    }
    table.insert(lfgEntries, entry)

    -- 通知去重（5 分钟内同一发布者只通知一次）
    local now = time()
    if not notifyExpiryQueue[sender] or (now - notifyExpiryQueue[sender]) > NOTIFY_EXPIRE then
      notifyExpiryQueue[sender] = now
      local cnName = (GetDungeonInfo(entry.dungeon)) or entry.dungeon
      local needs = {}
      if entry.needTank then table.insert(needs, "|cff3399ff坦|r") end
      if entry.needHealer then table.insert(needs, "|cff33ff33治|r") end
      if entry.needDPS and entry.needDPS > 0 then
        table.insert(needs, "|cffff3333DPS×" .. entry.needDPS .. "|r")
      end
      local needStr = #needs > 0 and ("[" .. table.concat(needs, " ") .. "] ") or ""
      local senderColor = GetClassColor(entry.senderClass)
      local lvStr = entry.senderLevel > 0 and (" Lv." .. entry.senderLevel) or ""
      local msg = string.format("|cff88ccff[招募]|r %s%s|r%s 招人去 |cffffd200%s|r %s%s",
        senderColor, sender, lvStr, cnName, needStr,
        (entry.note ~= "") and ("- " .. entry.note) or "")
      E:Print(msg)
      if E.FlashMinimapButton then E:FlashMinimapButton() end
    end

    -- 限制队列大小
    while #lfgEntries > MAX_LFG_ENTRIES do
      table.remove(lfgEntries, 1)
    end

    if lfgPanel and lfgPanel:IsShown() then E:RefreshLFGPanel() end
  end

  local function HandleCancel(sender)
    local kept = {}
    for _, entry in ipairs(lfgEntries) do
      if entry.sender ~= sender then table.insert(kept, entry) end
    end
    lfgEntries = kept
    notifyExpiryQueue[sender] = nil
    if lfgPanel and lfgPanel:IsShown() then E:RefreshLFGPanel() end
  end

  local function OnLFGMessage(prefix, message, channel, sender)
    if prefix ~= LFG_PREFIX then return end
    sender = StripRealmName(sender)
    if not sender or sender == "" then return end

    local msgType, rest = string.match(message or "", "^(%u+%d?):(.*)$")
    if not msgType then return end

    if msgType == "POST2" then
      local decoded = DecodePost(rest)
      if decoded then HandlePost(sender, decoded) end
      return
    end
    if msgType == "POST" then
      -- 兼容 v1
      local decoded = DecodePostV1(rest)
      if decoded then HandlePost(sender, decoded) end
      return
    end
    if msgType == "CANCEL2" or msgType == "CANCEL" then
      HandleCancel(sender)
      return
    end
  end

  ---------------------------------------------------------------------------
  -- 申请
  ---------------------------------------------------------------------------
  local function ApplyToEntry(entry)
    if not entry or not entry.sender then return end
    local me = GetMyName()
    if not me or entry.sender == me then return end

    local applied = EpochCNDB.social.lfgApplied
    local lastApply = applied[entry.sender] or 0
    if time() - lastApply < APPLY_COOLDOWN then
      E:Print(string.format("|cffff9900你最近已向 %s 申请过，跳过自动消息。|r", entry.sender))
      if ChatFrame_OpenChat then
        ChatFrame_OpenChat("/w " .. entry.sender .. " ")
      end
      return
    end

    applied[entry.sender] = time()
    local _, classEn = UnitClass("player")
    local lv = UnitLevel("player") or 0
    local cnClass = ClassToCN(classEn)
    local dungeonName = (GetDungeonInfo(entry.dungeon))
    local applyMsg = string.format("你好，想加入你的 %s 队伍。Lv.%d %s",
      dungeonName or entry.dungeon, lv, cnClass)
    SendChatMessage(applyMsg, "WHISPER", nil, entry.sender)
    E:Print(string.format("|cff33ff99已向 %s 发送申请密语|r", entry.sender))
  end

  ---------------------------------------------------------------------------
  -- 公开 API
  ---------------------------------------------------------------------------
  function E:GetLFGEntries() return lfgEntries end

  function E:GetMyLFGPosting() return myPosting end

  function E:HasMyLFGPosting() return myPosting ~= nil end

  function E:PublishLFG(entry)
    if not entry then return false end
    local _, classEn = UnitClass("player")
    entry.senderLevel = UnitLevel("player") or 0
    entry.senderClass = classEn or ""
    if BroadcastEntry(entry) then
      myPosting = entry
      return true
    end
    return false
  end

  function E:CancelLFG() CancelLFG() end

  ---------------------------------------------------------------------------
  -- UI
  ---------------------------------------------------------------------------
  local typeFilterDD, roleFilterDD

  local function CreateFilterDropdown(parent, anchor, x, y, items, currentKey, onSelect)
    local dd = CreateFrame("Frame", "EpochCNLFGFilter" .. tostring(GetTime()), parent, "UIDropDownMenuTemplate")
    dd:SetPoint("TOPLEFT", anchor, "TOPLEFT", x, y)
    UIDropDownMenu_SetWidth(dd, 80)
    UIDropDownMenu_SetText(dd, items[currentKey] or currentKey)
    dd.itemMap = items
    dd.SelectKey = function(key)
      UIDropDownMenu_SetText(dd, items[key] or key)
      if onSelect then onSelect(key) end
    end
    UIDropDownMenu_Initialize(dd, function(self, level)
      for k, v in pairs(items) do
        local info = UIDropDownMenu_CreateInfo()
        info.text = v
        info.value = k
        info.func = function() dd.SelectKey(k); CloseDropDownMenus() end
        info.checked = (k == currentKey)
        UIDropDownMenu_AddButton(info, level)
      end
    end)
    return dd
  end

  local function CreateLFGPanel()
    if lfgPanel then return lfgPanel end

    lfgPanel = CreateFrame("Frame", "EpochCNLFGFrame", UIParent)
    lfgPanel:SetSize(PANEL_W, PANEL_H)
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
      tile = true, tileSize = 32, edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    lfgPanel:Hide()

    -- 标题
    lfgPanel.title = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    lfgPanel.title:SetPoint("TOP", lfgPanel, "TOP", 0, -16)
    lfgPanel.title:SetText("|cff33ffccEpochCN|r 组队招募板")

    local close = CreateFrame("Button", nil, lfgPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", lfgPanel, "TOPRIGHT", -5, -5)

    -- 过滤栏
    local filterY = -44
    local typeLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    typeLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, filterY)
    typeLabel:SetText("|cffffd200类型:|r")

    typeFilterDD = CreateFilterDropdown(lfgPanel, lfgPanel, 50, filterY + 4,
      TYPE_NAMES, filter.type, function(k)
        filter.type = k
        scrollOffset = 0
        E:RefreshLFGPanel()
      end)

    local roleLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    roleLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 156, filterY)
    roleLabel:SetText("|cffffd200角色:|r")

    local roleItems = { ALL = "全部", TANK = "需坦克", HEALER = "需治疗", DPS = "需DPS" }
    roleFilterDD = CreateFilterDropdown(lfgPanel, lfgPanel, 196, filterY + 4,
      roleItems, filter.role, function(k)
        filter.role = k
        scrollOffset = 0
        E:RefreshLFGPanel()
      end)

    -- 搜索框
    local searchLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    searchLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 300, filterY)
    searchLabel:SetText("|cffffd200搜索:|r")

    local searchBox = CreateFrame("EditBox", "EpochCNLFGSearchBox", lfgPanel, "InputBoxTemplate")
    searchBox:SetSize(140, 18)
    searchBox:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 340, filterY + 2)
    searchBox:SetAutoFocus(false)
    searchBox:SetMaxLetters(40)
    searchBox:SetScript("OnTextChanged", function(self)
      filter.search = self:GetText() or ""
      scrollOffset = 0
      E:RefreshLFGPanel()
    end)
    searchBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    searchBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.searchBox = searchBox

    -- 列表标题
    local hdr = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    hdr:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, -82)
    hdr:SetText("|cffffd200发布者              副本                    需求          备注                时间|r")

    -- 列表区
    rowFrames = {}
    for i = 1, LIST_ROWS do
      local row = CreateFrame("Button", nil, lfgPanel)
      row:SetSize(PANEL_W - 32 - 18, 24)
      row:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, -100 - (i - 1) * 26)

      local bg = row:CreateTexture(nil, "BACKGROUND")
      bg:SetAllPoints()
      bg:SetTexture("Interface\\Buttons\\UI-Listbox-Highlight2")
      bg:SetAlpha(0)
      row.bg = bg

      row.senderText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.senderText:SetPoint("LEFT", row, "LEFT", 4, 0)
      row.senderText:SetWidth(120)
      row.senderText:SetJustifyH("LEFT")

      row.dungeonText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.dungeonText:SetPoint("LEFT", row, "LEFT", 122, 0)
      row.dungeonText:SetWidth(140)
      row.dungeonText:SetJustifyH("LEFT")

      row.needText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.needText:SetPoint("LEFT", row, "LEFT", 262, 0)
      row.needText:SetWidth(80)
      row.needText:SetJustifyH("LEFT")

      row.noteText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.noteText:SetPoint("LEFT", row, "LEFT", 340, 0)
      row.noteText:SetWidth(120)
      row.noteText:SetJustifyH("LEFT")

      row.timeText = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
      row.timeText:SetPoint("LEFT", row, "LEFT", 460, 0)
      row.timeText:SetWidth(70)
      row.timeText:SetJustifyH("LEFT")

      row:RegisterForClicks("LeftButtonUp", "RightButtonUp")
      row:SetScript("OnEnter", function(self)
        self.bg:SetAlpha(0.3)
        if not self.entry then return end
        local entry = self.entry
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        local cnName, ty = GetDungeonInfo(entry.dungeon)
        GameTooltip:SetText(cnName .. "  |cff999999[" .. (TYPE_NAMES[ty] or ty) .. "]|r", 1, 0.82, 0)
        local senderColor = GetClassColor(entry.senderClass)
        local lvStr = entry.senderLevel > 0 and ("Lv." .. entry.senderLevel) or ""
        local clsStr = entry.senderClass ~= "" and ClassToCN(entry.senderClass) or ""
        GameTooltip:AddLine(string.format("发布者: %s%s|r %s %s",
          senderColor, entry.sender, lvStr, clsStr), 1, 1, 1)
        if entry.minLevel and entry.minLevel > 0 then
          local lvRange = "等级范围: " .. entry.minLevel
          if entry.maxLevel and entry.maxLevel > 0 then
            lvRange = lvRange .. "-" .. entry.maxLevel
          else
            lvRange = lvRange .. "+"
          end
          GameTooltip:AddLine(lvRange, 0.8, 0.8, 0.8)
        end
        if entry.needTank then GameTooltip:AddLine("需要坦克", 0.2, 0.6, 1) end
        if entry.needHealer then GameTooltip:AddLine("需要治疗", 0.2, 1, 0.2) end
        if entry.needDPS and entry.needDPS > 0 then
          GameTooltip:AddLine("需要 DPS × " .. entry.needDPS, 1, 0.4, 0.4)
        end
        if entry.note and entry.note ~= "" then
          GameTooltip:AddLine(" ")
          GameTooltip:AddLine("备注: " .. entry.note, 0.95, 0.85, 0.4, true)
        end
        GameTooltip:AddLine(" ")
        GameTooltip:AddLine("发布于 " .. FormatTimeAgo(entry.timestamp), 0.6, 0.6, 0.6)
        local applied = EpochCNDB.social.lfgApplied[entry.sender]
        if applied and time() - applied < APPLY_COOLDOWN then
          GameTooltip:AddLine("|cffff9900你已申请过，距上次 " .. FormatTimeAgo(applied) .. "|r", 0.9, 0.6, 0)
        end
        GameTooltip:AddLine("|cffffd200左键|r 申请   |cffffd200右键|r 密语", 0.6, 0.6, 0.6)
        GameTooltip:Show()
      end)
      row:SetScript("OnLeave", function(self)
        self.bg:SetAlpha(0)
        GameTooltip:Hide()
      end)
      row:SetScript("OnClick", function(self, button)
        if not self.entry then return end
        if button == "RightButton" then
          if ChatFrame_OpenChat then
            ChatFrame_OpenChat("/w " .. self.entry.sender .. " ")
          end
        else
          ApplyToEntry(self.entry)
        end
      end)
      row:Hide()
      rowFrames[i] = row
    end

    -- 滚动条
    local scrollBar = CreateFrame("Slider", "EpochCNLFGScrollBar", lfgPanel, "UIPanelScrollBarTemplate")
    scrollBar:SetPoint("TOPRIGHT", lfgPanel, "TOPRIGHT", -16, -118)
    scrollBar:SetPoint("BOTTOMRIGHT", lfgPanel, "BOTTOMRIGHT", -16, 250)
    scrollBar:SetScript("OnValueChanged", nil)
    scrollBar:SetMinMaxValues(0, 0)
    scrollBar:SetValueStep(1)
    scrollBar:SetValue(0)
    scrollBar:SetWidth(16)
    scrollBar:SetScript("OnValueChanged", function(self, value)
      scrollOffset = math.floor(value)
      E:RefreshLFGPanel()
    end)
    lfgPanel.scrollBar = scrollBar

    -- 鼠标滚轮
    lfgPanel:EnableMouseWheel(true)
    lfgPanel:SetScript("OnMouseWheel", function(self, delta)
      local _, max = scrollBar:GetMinMaxValues()
      local newOffset = math.max(0, math.min(max, scrollOffset - delta))
      scrollBar:SetValue(newOffset)
    end)

    -- 发布表单
    local formY = -370
    local formHdr = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    formHdr:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, formY)
    formHdr:SetText("|cffffd200发布招募|r")

    local dgLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dgLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, formY - 22)
    dgLabel:SetText("副本:")

    local dgBox = CreateFrame("EditBox", "EpochCNLFGDgBox", lfgPanel, "InputBoxTemplate")
    dgBox:SetSize(140, 20)
    dgBox:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 60, formY - 20)
    dgBox:SetAutoFocus(false)
    dgBox:SetMaxLetters(40)
    dgBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    dgBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.dgBox = dgBox

    local dgHelp = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dgHelp:SetPoint("LEFT", dgBox, "RIGHT", 8, 0)
    dgHelp:SetText("|cff666666(英文代码或中文名)|r")

    -- 等级范围
    local lvLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    lvLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, formY - 50)
    lvLabel:SetText("等级:")

    local minLvBox = CreateFrame("EditBox", "EpochCNLFGMinLv", lfgPanel, "InputBoxTemplate")
    minLvBox:SetSize(40, 20)
    minLvBox:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 60, formY - 48)
    minLvBox:SetAutoFocus(false)
    minLvBox:SetMaxLetters(2)
    minLvBox:SetNumeric(true)
    minLvBox:SetText("1")
    minLvBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    minLvBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.minLvBox = minLvBox

    local lvDash = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    lvDash:SetPoint("LEFT", minLvBox, "RIGHT", 4, 0)
    lvDash:SetText("-")

    local maxLvBox = CreateFrame("EditBox", "EpochCNLFGMaxLv", lfgPanel, "InputBoxTemplate")
    maxLvBox:SetSize(40, 20)
    maxLvBox:SetPoint("LEFT", lvDash, "RIGHT", 4, 0)
    maxLvBox:SetAutoFocus(false)
    maxLvBox:SetMaxLetters(2)
    maxLvBox:SetNumeric(true)
    maxLvBox:SetText("80")
    maxLvBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    maxLvBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.maxLvBox = maxLvBox

    -- 角色需求
    local needLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    needLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 200, formY - 50)
    needLabel:SetText("需求:")

    local tankCheck = CreateFrame("CheckButton", nil, lfgPanel, "OptionsCheckButtonTemplate")
    tankCheck:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 240, formY - 48)
    local tankLab = tankCheck:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    tankLab:SetPoint("LEFT", tankCheck, "RIGHT", 0, 1)
    tankLab:SetText("|cff3399ff坦|r")
    lfgPanel.tankCheck = tankCheck

    local healCheck = CreateFrame("CheckButton", nil, lfgPanel, "OptionsCheckButtonTemplate")
    healCheck:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 290, formY - 48)
    local healLab = healCheck:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    healLab:SetPoint("LEFT", healCheck, "RIGHT", 0, 1)
    healLab:SetText("|cff33ff33治|r")
    lfgPanel.healCheck = healCheck

    local dpsLabel2 = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dpsLabel2:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 340, formY - 50)
    dpsLabel2:SetText("|cffff3333DPS|r:")

    local dpsBox = CreateFrame("EditBox", "EpochCNLFGDpsBox", lfgPanel, "InputBoxTemplate")
    dpsBox:SetSize(30, 20)
    dpsBox:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 380, formY - 48)
    dpsBox:SetAutoFocus(false)
    dpsBox:SetMaxLetters(1)
    dpsBox:SetNumeric(true)
    dpsBox:SetText("0")
    dpsBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    dpsBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.dpsBox = dpsBox

    -- 备注
    local noteLabel = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    noteLabel:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, formY - 78)
    noteLabel:SetText("备注:")

    local noteBox = CreateFrame("EditBox", "EpochCNLFGNoteBox", lfgPanel, "InputBoxTemplate")
    noteBox:SetSize(360, 20)
    noteBox:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 60, formY - 76)
    noteBox:SetAutoFocus(false)
    noteBox:SetMaxLetters(60)
    noteBox:SetText("")
    noteBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    noteBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    lfgPanel.noteBox = noteBox

    -- 发布按钮
    local postBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    postBtn:SetSize(100, 24)
    postBtn:SetPoint("TOPLEFT", lfgPanel, "TOPLEFT", 16, formY - 110)
    postBtn:SetText("发布招募")
    postBtn:SetScript("OnClick", function()
      local code = CodeFromInput(dgBox:GetText())
      local minLv = tonumber(minLvBox:GetText()) or 1
      local maxLv = tonumber(maxLvBox:GetText()) or 0
      if maxLv > 0 and maxLv < minLv then maxLv = minLv end
      local entry = {
        dungeon    = code,
        minLevel   = minLv,
        maxLevel   = maxLv,
        needTank   = tankCheck:GetChecked() and true or false,
        needHealer = healCheck:GetChecked() and true or false,
        needDPS    = tonumber(dpsBox:GetText()) or 0,
        note       = noteBox:GetText() or "",
      }
      if E:PublishLFG(entry) then
        E:RefreshLFGPanel()
      end
    end)

    local cancelBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    cancelBtn:SetSize(100, 24)
    cancelBtn:SetPoint("LEFT", postBtn, "RIGHT", 8, 0)
    cancelBtn:SetText("取消我的招募")
    cancelBtn:SetScript("OnClick", function()
      CancelLFG()
    end)

    local refreshBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    refreshBtn:SetSize(80, 24)
    refreshBtn:SetPoint("LEFT", cancelBtn, "RIGHT", 8, 0)
    refreshBtn:SetText("刷新")
    refreshBtn:SetScript("OnClick", function()
      CleanupExpired()
      E:RefreshLFGPanel()
    end)

    local codesBtn = CreateFrame("Button", nil, lfgPanel, "UIPanelButtonTemplate")
    codesBtn:SetSize(80, 24)
    codesBtn:SetPoint("LEFT", refreshBtn, "RIGHT", 8, 0)
    codesBtn:SetText("代码列表")
    codesBtn:SetScript("OnClick", function()
      E:Print("|cff33ffcc常用副本代码：|r")
      E:Print("|cff88ccff5人:|r RFC DM WC SFK BFD GNOMER SM RFD RFK ULDA ZF MARA ST BRD LBRS UBRS STRAT SCHOLO DIRE")
      E:Print("|cff88ccffTBC:|r RAMPS BF SPC UB MT AC SH SLM BM MECH BOT ARC SV MGT")
      E:Print("|cff88ccffWLK:|r UK NEXUS AN OK VH DTK GD HOS HOL COS UP OCCI TOC5 FOS POS HOR")
      E:Print("|cff88ccff团本:|r MC BWL AQ20 AQ40 ZG ONY NAXX OS VOA EYE ULDU TOC ICC RS")
      E:Print("|cff88ccffPvP:|r BG ARENA WSG AB AV EOTS SOTA IOC")
      E:Print("|cff88ccff其他:|r WORLD QUEST DAILY OTHER")
      E:Print("|cff666666也支持中文输入，例如「冰冠堡垒」自动识别为 ICC。|r")
    end)

    -- 底部状态
    lfgPanel.statusText = lfgPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    lfgPanel.statusText:SetPoint("BOTTOM", lfgPanel, "BOTTOM", 0, 16)
    lfgPanel.statusText:SetWidth(PANEL_W - 32)
    lfgPanel.statusText:SetJustifyH("CENTER")

    return lfgPanel
  end

  function E:RefreshLFGPanel()
    if not lfgPanel then return end
    CleanupExpired()

    -- 过滤
    local visible = {}
    for _, entry in ipairs(lfgEntries) do
      if MatchFilter(entry) then
        table.insert(visible, entry)
      end
    end
    -- 按发布时间倒序
    table.sort(visible, function(a, b) return (a.timestamp or 0) > (b.timestamp or 0) end)

    -- 滚动条
    local maxScroll = math.max(0, #visible - LIST_ROWS)
    lfgPanel.scrollBar:SetMinMaxValues(0, maxScroll)
    if scrollOffset > maxScroll then scrollOffset = maxScroll end

    for i = 1, LIST_ROWS do
      local row = rowFrames[i]
      local entry = visible[scrollOffset + i]
      if entry then
        row.entry = entry
        local senderColor = GetClassColor(entry.senderClass)
        local lvStr = entry.senderLevel > 0 and (" Lv." .. entry.senderLevel) or ""
        row.senderText:SetText(senderColor .. entry.sender .. "|r" .. lvStr)
        local cnName, ty = GetDungeonInfo(entry.dungeon)
        row.dungeonText:SetText(cnName .. " |cff666666[" .. (TYPE_NAMES[ty] or ty) .. "]|r")
        local needs = {}
        if entry.needTank then table.insert(needs, "|cff3399ff坦|r") end
        if entry.needHealer then table.insert(needs, "|cff33ff33治|r") end
        if entry.needDPS and entry.needDPS > 0 then
          table.insert(needs, "|cffff3333D" .. entry.needDPS .. "|r")
        end
        row.needText:SetText(table.concat(needs, " "))
        row.noteText:SetText(entry.note or "")
        row.timeText:SetText("|cff888888" .. FormatTimeAgo(entry.timestamp) .. "|r")
        row:Show()
      else
        row.entry = nil
        row:Hide()
      end
    end

    -- 更新标题与状态
    lfgPanel.title:SetText(string.format("|cff33ffccEpochCN|r 组队招募板  |cff999999%d 条|r", #visible))
    if myPosting then
      local cnName = (GetDungeonInfo(myPosting.dungeon))
      lfgPanel.statusText:SetText("|cff33ff99已发布:|r " .. cnName ..
        " |cff666666(每 " .. LFG_REPOST_INTERVAL .. " 秒自动重发)|r")
    else
      lfgPanel.statusText:SetText("|cff666666未发布招募，填写表单后点「发布招募」。|r")
    end
  end

  function E:ToggleLFGPanel()
    local panel = CreateLFGPanel()
    if panel:IsShown() then
      panel:Hide()
    else
      CleanupExpired()
      scrollOffset = 0
      filter.search = ""
      if lfgPanel.searchBox then lfgPanel.searchBox:SetText("") end
      E:RefreshLFGPanel()
      panel:Show()
    end
  end

  ---------------------------------------------------------------------------
  -- 斜杠命令
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    msg = msg or ""

    if msg == "lfg" then
      E:ToggleLFGPanel(); return true
    end

    if msg == "lfg cancel" then
      CancelLFG(); return true
    end

    if msg == "lfg refresh" then
      CleanupExpired()
      E:Print(string.format("|cff33ffcc当前招募列表：%d 条|r", #lfgEntries))
      for i = 1, math.min(#lfgEntries, 10) do
        local e = lfgEntries[i]
        local cn = (GetDungeonInfo(e.dungeon))
        E:Print(string.format("  [%s] %s %s%s", e.sender, cn,
          e.note ~= "" and ("- " .. e.note) or "",
          " (" .. FormatTimeAgo(e.timestamp) .. ")"))
      end
      if #lfgEntries > 10 then E:Print("  /ecn lfg 打开面板查看全部。") end
      return true
    end

    if msg == "lfg codes" or msg == "lfg help" then
      E:Print("|cff33ffcc组队招募板：|r")
      E:Print("  /ecn lfg               - 打开招募面板")
      E:Print("  /ecn lfg post <代码|中文> [备注] - 快速发布")
      E:Print("  /ecn lfg cancel        - 取消我的招募")
      E:Print("  /ecn lfg refresh       - 列出当前招募")
      E:Print("  /ecn lfg apply <玩家>  - 向某人申请")
      E:Print("|cffffd200常用副本代码：|r")
      E:Print("|cff88ccff5人副本:|r RFC DM SFK BFD GNOMER SM ZF MARA BRD LBRS UBRS STRAT SCHOLO DIRE")
      E:Print("|cff88ccffWLK 5人:|r UK NEXUS AN OK VH DTK GD COS UP TOC5 FOS POS HOR")
      E:Print("|cff88ccff团本:|r MC BWL ZG ONY NAXX OS VOA EYE ULDU TOC ICC RS")
      E:Print("|cff666666支持中文输入，例如「冰冠堡垒」自动识别。|r")
      return true
    end

    -- /ecn lfg post <code|中文> [备注]
    local args = string.match(msg, "^lfg post%s+(.+)$")
    if args then
      local code, note = string.match(args, "^(%S+)%s+(.+)$")
      if not code then code = args end
      note = note or ""
      local resolvedCode = CodeFromInput(code)
      local entry = {
        dungeon    = resolvedCode,
        minLevel   = 1,
        maxLevel   = 0,
        needTank   = string.find(note, "坦") ~= nil,
        needHealer = (string.find(note, "治") or string.find(note, "奶")) ~= nil,
        needDPS    = 0,
        note       = note,
      }
      -- 自动从备注解析 DPS×N
      local n = string.match(note, "[Dd][Pp][Ss]%s*[xX×]%s*(%d)")
      if n then entry.needDPS = tonumber(n) or 0 end
      E:PublishLFG(entry)
      return true
    end

    local target = string.match(msg, "^lfg apply%s+(%S+)$")
    if target then
      -- 找到该玩家的招募
      local found
      for _, e in ipairs(lfgEntries) do
        if e.sender == target then found = e; break end
      end
      if found then
        ApplyToEntry(found)
      else
        if ChatFrame_OpenChat then
          ChatFrame_OpenChat("/w " .. target .. " ")
        end
        E:Print(string.format("|cffff9900未在当前招募列表找到 %s 的发布，已为你打开密语窗口。|r", target))
      end
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 事件
  ---------------------------------------------------------------------------
  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "CHAT_MSG_ADDON" then
      OnLFGMessage(...)
      return
    end
  end)

  ---------------------------------------------------------------------------
  -- 重发 + 清理定时器（合并到一个 OnUpdate）
  ---------------------------------------------------------------------------
  local timerFrame = CreateFrame("Frame")
  timerFrame:SetScript("OnUpdate", function(_, elapsed)
    repostTimer = repostTimer + elapsed
    cleanupTimer = cleanupTimer + elapsed

    -- 每 60 秒清理一次
    if cleanupTimer >= 60 then
      cleanupTimer = 0
      CleanupExpired()
      if lfgPanel and lfgPanel:IsShown() then E:RefreshLFGPanel() end
    end

    -- 重发
    if repostTimer < LFG_REPOST_INTERVAL then return end
    repostTimer = 0
    if not myPosting then return end
    BroadcastEntry(myPosting, true)
    E:Debug("LFG: 自动重发招募信息")
  end)

  E:Debug("LFGBoard v2 模块已加载")
end)
