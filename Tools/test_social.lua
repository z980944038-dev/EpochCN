-- 社交模块独立加载测试
-- 仅加载 Social/ChineseChannel/LFGBoard/QuickChat/Feedback/Settings 模块，
-- 验证模块注册、初始化、API 调用、斜杠命令注册无错误。
--
-- 用法（在 EpochCN 根目录）：
--   lua Tools/test_social.lua

-- ============================================================
-- WoW API stubs（极简，足以让模块完成初始化）
-- ============================================================

local _G = _G or _ENV
_G.getglobal = function(k) return _G[k] end

local chatMessages = {}

_G.DEFAULT_CHAT_FRAME = { AddMessage = function(_, msg) table.insert(chatMessages, tostring(msg)) end }

local function makeFrame(frameType, name)
  local f = {
    __scripts = {},
    __hooks = {},
    __text = "",
    __frameType = frameType or "Frame",
    __isShown = false,
  }
  local mt = {__index = function() return function() end end}
  setmetatable(f, mt)
  f.RegisterEvent = function() end
  f.UnregisterEvent = function() end
  f.SetScript = function(self, scriptName, fn) self.__scripts[scriptName] = fn end
  f.HookScript = function(self, scriptName, fn)
    self.__hooks[scriptName] = self.__hooks[scriptName] or {}
    table.insert(self.__hooks[scriptName], fn)
  end
  f.GetScript = function(self, scriptName) return self.__scripts[scriptName] end
  f.Show = function(self) self.__isShown = true end
  f.Hide = function(self) self.__isShown = false end
  f.IsShown = function(self) return self.__isShown end
  f.IsVisible = function(self) return self.__isShown end
  f.SetPoint = function() end
  f.SetSize = function() end
  f.SetWidth = function() end
  f.SetHeight = function() end
  f.SetText = function(self, t) self.__text = t end
  f.GetText = function(self) return self.__text or "" end
  f.SetTexture = function() end
  f.SetTexCoord = function() end
  f.SetVertexColor = function() end
  f.SetAlpha = function() end
  f.SetBlendMode = function() end
  f.ClearAllPoints = function() end
  f.SetFrameStrata = function() end
  f.SetFrameLevel = function() end
  f.GetFrameLevel = function() return 1 end
  f.RegisterForClicks = function() end
  f.RegisterForDrag = function() end
  f.SetMovable = function() end
  f.EnableMouse = function() end
  f.EnableMouseWheel = function() end
  f.StartMoving = function() end
  f.StopMovingOrSizing = function() end
  f.SetBackdrop = function() end
  f.CreateFontString = function(self, n) return makeFrame("FontString", n) end
  f.CreateTexture = function() return makeFrame("Texture") end
  f.GetRegions = function() return end
  f.GetChildren = function() return end
  f.GetName = function() return name end
  f.GetObjectType = function(self) return self.__frameType end
  f.SetJustifyH = function() end
  f.SetHighlightTexture = function() end
  f.SetAllPoints = function() end
  f.SetOwner = function() end
  f.AddLine = function() end
  f.AddDoubleLine = function() end
  f.NumLines = function() return 0 end
  f.GetWidth = function() return 100 end
  f.GetHeight = function() return 100 end
  f.GetEffectiveScale = function() return 1 end
  f.GetParent = function() return nil end
  f.GetOwner = function() return nil end
  f.SetID = function() end
  f.GetID = function() return 1 end
  f.SetChecked = function() end
  f.GetChecked = function() return false end
  f.SetMaxLetters = function() end
  f.SetAutoFocus = function() end
  f.SetNumeric = function() end
  f.HighlightText = function() end
  f.ClearFocus = function() end
  f.SetFocus = function() end
  f.SetFontObject = function() end
  f.SetMultiLine = function() end
  f.SetMinMaxValues = function() end
  f.SetValue = function() end
  f.SetValueStep = function() end
  f.GetMinMaxValues = function() return 0, 0 end
  f.GetValue = function() return 0 end
  f.LockHighlight = function() end
  f.UnlockHighlight = function() end
  f.Disable = function() end
  f.Enable = function() end
  if name then _G[name] = f end
  return f
end

_G.CreateFrame = function(frameType, name) return makeFrame(frameType, name) end

-- 通用全局
_G.UIParent = makeFrame("Frame", "UIParent")
_G.GameTooltip = makeFrame("Frame", "GameTooltip")
_G.GameTooltipTextLeft1 = makeFrame("FontString", "GameTooltipTextLeft1")
_G.WorldFrame = makeFrame("Frame", "WorldFrame")
_G.Minimap = makeFrame("Frame", "Minimap")
_G.TargetFrame = makeFrame("Frame", "TargetFrame")
_G.WatchFrame = makeFrame("Frame", "WatchFrame")

_G.NUM_CHAT_WINDOWS = 7
_G.MAX_SKILLLINE_TABS = 8
_G.SPELLS_PER_PAGE = 12
_G.BOOKTYPE_SPELL = "spell"
_G.BOOKTYPE_PET = "pet"
_G.UNKNOWN = "Unknown"
_G.WATCHFRAME_MAXQUESTS = 10

-- 玩家信息
_G.UnitName = function() return "TestPlayer" end
_G.UnitLevel = function() return 80 end
_G.UnitClass = function() return "战士", "WARRIOR" end
_G.UnitRace = function() return "人类", "Human" end
_G.UnitFactionGroup = function() return "Alliance" end
_G.UnitGUID = function() return "0xF13000000A" end
_G.UnitIsPlayer = function() return false end
_G.UnitIsAFK = function() return false end
_G.UnitIsDND = function() return false end
_G.GetGuildInfo = function() return "TestGuild" end
_G.IsInGuild = function() return false end
_G.GetGameTime = function() return 12, 30 end
_G.GetZoneText = function() return "暴风城" end
_G.GetSubZoneText = function() return "" end
_G.GetTime = function() return os.clock() end
_G.time = function() return os.time() end
_G.date = date

-- 队伍
_G.GetNumPartyMembers = function() return 0 end
_G.GetNumRaidMembers = function() return 0 end
_G.GetRaidRosterInfo = function() return "Member1" end
_G.InviteUnit = function() end

-- 频道
local joinedChannel = false
local lastJoinedChannel
local lastLeftChannel
local lastListedChannel
local lastAddonMessage
local addonMessages = {}
_G.GetChannelName = function(name)
  if name == "china" and joinedChannel then return 7 end
  return 0
end
_G.JoinChannelByName = function(name) lastJoinedChannel = name; joinedChannel = true end
_G.LeaveChannelByName = function(name) lastLeftChannel = name; joinedChannel = false end
_G.AddChatWindowChannel = function() end
_G.ChatFrame_AddChannel = function() end
_G.ChatFrame_OpenChat = function() end
_G.ListChannelByName = function(name) lastListedChannel = name end
_G.FCF_SavePositionAndDimensions = function() end
_G.SendChatMessage = function(msg, ch, lang, target)
  table.insert(chatMessages, "CHAT[" .. tostring(ch) .. "]: " .. tostring(msg))
end
_G.SendAddonMessage = function(prefix, message, channel, target)
  lastAddonMessage = { prefix = prefix, message = message, channel = channel, target = target }
  table.insert(addonMessages, lastAddonMessage)
end
_G.RegisterAddonMessagePrefix = function() end

-- 任务
_G.GetNumQuestLogEntries = function() return 0 end
_G.GetQuestLogTitle = function() return "Title" end
_G.GetQuestLogQuestText = function() return "", "" end
_G.GetQuestLogLeaderBoard = function() return "", "log", false end
_G.GetQuestLogCompletionText = function() return "" end
_G.GetAbandonQuestName = function() return "" end
_G.GetTitleText = function() return "" end
_G.GetQuestText = function() return "" end
_G.GetObjectiveText = function() return "" end
_G.GetRewardText = function() return "" end
_G.GetProgressText = function() return "" end
_G.GetGreetingText = function() return "" end
_G.GetQuestID = function() return 0 end
_G.GetNumQuestLeaderBoards = function() return 0 end
_G.GetQuestLogSelection = function() return 1 end

-- 物品/法术
_G.GetItemInfo = function() return "Item" end
_G.GetItemStats = function() return {} end
_G.GetSpellTabInfo = function() return "Tab" end
_G.GetSpellBookItemInfo = function() return "spell", 1 end
_G.GetSpellBookItemName = function() return "Spell", "Rank 1" end
_G.GetSpellName = function() return "Spell", "Rank 1" end

-- Auction
_G.GetCursorMoney = function() return 0 end
_G.GetMoney = function() return 0 end

-- 颜色
_G.RAID_CLASS_COLORS = {
  WARRIOR     = { r = 0.78, g = 0.61, b = 0.43 },
  PALADIN     = { r = 0.96, g = 0.55, b = 0.73 },
  HUNTER      = { r = 0.67, g = 0.83, b = 0.45 },
  ROGUE       = { r = 1.00, g = 0.96, b = 0.41 },
  PRIEST      = { r = 1.00, g = 1.00, b = 1.00 },
  DEATHKNIGHT = { r = 0.77, g = 0.12, b = 0.23 },
  SHAMAN      = { r = 0.00, g = 0.44, b = 0.87 },
  MAGE        = { r = 0.41, g = 0.80, b = 0.94 },
  WARLOCK     = { r = 0.58, g = 0.51, b = 0.79 },
  DRUID       = { r = 1.00, g = 0.49, b = 0.04 },
}

-- DropDown menu stubs
_G.UIDropDownMenu_Initialize = function() end
_G.UIDropDownMenu_CreateInfo = function() return {} end
_G.UIDropDownMenu_AddButton = function() end
_G.UIDropDownMenu_SetText = function() end
_G.UIDropDownMenu_SetWidth = function() end
_G.UIDropDownMenu_GetSelectedValue = function() return nil end
_G.ToggleDropDownMenu = function() end
_G.CloseDropDownMenus = function() end

_G.hooksecurefunc = function() end
_G.ReloadUI = function() end
_G.SLASH_EPOCHCN1 = nil
_G.SlashCmdList = {}

-- ============================================================
-- 加载 EpochCN
-- ============================================================
_G.EpochCNDB = { settingsPanel = true }
_G.EpochCNCharDB = {}

local addonName = "EpochCN"
local files = {}

-- 仅加载社交相关数据（TOC 中读取 Modules/Social.lua 等需要的依赖）
-- Core 必须先加载
local minimal = {
  "Core.lua",
  "Modules/Social.lua",
  "Modules/ChineseChannel.lua",
  "Modules/LFGBoard.lua",
  "Modules/QuickChat.lua",
  "Modules/Feedback.lua",
  "Modules/Settings.lua",
}

for _, f in ipairs(minimal) do
  -- 用一个表式 loadfile，把 ... 替换成 addonName
  local chunk, err = loadfile(f)
  if not chunk then
    print("LOAD COMPILE FAIL: " .. f .. " — " .. tostring(err))
    os.exit(1)
  end
  -- Lua 5.4+: setfenv 已移除，但模块用的是 addonName=... 包名表达式
  -- 直接传递 addonName 作为 vararg
  local ok, perr = pcall(chunk, addonName)
  if not ok then
    print("LOAD RUN FAIL: " .. f .. " — " .. tostring(perr))
    os.exit(1)
  end
  print("  LOAD OK  " .. f)
end

local E = _G.EpochCN
if not E then
  print("FAIL: EpochCN global not set")
  os.exit(1)
end

-- 模拟 Initialize（不调用 LoadSeedData，因为没加载 Data 表）
E.modules = E.modules or {}
E.moduleOrder = E.moduleOrder or {}

-- ADDON_LOADED 流程的简化版本：仅初始化社交模块
-- 直接执行：E:CaptureRawAPI() 是空 OK；BuildLookupTables 也跳过
-- 模块工厂在加载时已注册到 E.modules，需手动调用其初始化函数
-- 但是模块工厂被 RegisterModule 收集后，需要 Initialize 触发。
-- 这里直接逐个调用：
print("\n== 开始初始化模块 ==")
local socialModules = { "Social", "ChineseChannel", "LFGBoard", "QuickChat", "Feedback", "Settings" }
for _, name in ipairs(socialModules) do
  local init = E.modules[name]
  if not init then
    print("  FAIL " .. name .. " 未注册到 E.modules")
    os.exit(1)
  end
  local ok, err = pcall(init, E)
  if not ok then
    print("  FAIL " .. name .. " 初始化失败: " .. tostring(err))
    os.exit(1)
  end
  print("  OK   " .. name .. " 初始化成功")
end

-- ============================================================
-- API 调用测试
-- ============================================================
print("\n== API 调用测试 ==")

local function assert_(name, cond)
  if cond then
    print("  OK   " .. name)
  else
    print("  FAIL " .. name)
    os.exit(1)
  end
end

local function hasAddonChannel(channel, target)
  for _, msg in ipairs(addonMessages) do
    if msg.channel == channel and (target == nil or msg.target == target) then
      return true
    end
  end
  return false
end

assert_("E:GetChinesePlayerCount() == 0", E:GetChinesePlayerCount() == 0)
assert_("E:IsChinesePlayer('Foo') == false", E:IsChinesePlayer("Foo") == false)
assert_("E:GetAllContacts() 是 table", type(E:GetAllContacts()) == "table")
assert_("E:GetChineseChannelNumber() == 0", E:GetChineseChannelNumber() == 0)
assert_("E:GetLFGEntries() 是 table", type(E:GetLFGEntries()) == "table")
assert_("E:HasMyLFGPosting() == false", E:HasMyLFGPosting() == false)

-- 设置/读取备注
E:SetContactNote("TestPlayer2", "测试备注")
assert_("E:GetContactNote 写入读取", E:GetContactNote("TestPlayer2") == "测试备注")

-- 添加/移除标签
assert_("AddContactTag 成功", E:AddContactTag("TestPlayer3", "公会"))
local tags = E:GetContactTags("TestPlayer3")
assert_("GetContactTags 返回包含 标签", tags and tags["公会"] == true)
E:RemoveContactTag("TestPlayer3", "公会")
local tags2 = E:GetContactTags("TestPlayer3")
assert_("RemoveContactTag 成功", not tags2 or not tags2["公会"])

-- 屏蔽/取消屏蔽
E:BlockPlayer("Spammer")
assert_("BlockPlayer 写入", _G.EpochCNDB.social.blocklist["Spammer"] == true)
E:UnblockPlayer("Spammer")
assert_("UnblockPlayer 移除", _G.EpochCNDB.social.blocklist["Spammer"] == nil)

-- 静音
E:MutePlayer("Quieter")
assert_("MutePlayer 写入", _G.EpochCNDB.social.muted["Quieter"] == true)
E:UnmutePlayer("Quieter")
assert_("UnmutePlayer 移除", _G.EpochCNDB.social.muted["Quieter"] == nil)

-- 联系人删除
E:SetContactNote("ToForget", "x")
assert_("SetContactNote 创建联系人", _G.EpochCNDB.social.contacts["ToForget"] ~= nil)
E:RemoveContact("ToForget")
assert_("RemoveContact 删除", _G.EpochCNDB.social.contacts["ToForget"] == nil)

-- LFG 发布
local pubOK = E:PublishLFG({
  dungeon    = "ICC",
  minLevel   = 80,
  maxLevel   = 80,
  needTank   = true,
  needHealer = true,
  needDPS    = 3,
  note       = "速刷",
})
assert_("E:PublishLFG 成功", pubOK)
assert_("E:HasMyLFGPosting() == true", E:HasMyLFGPosting())
E:CancelLFG()
assert_("E:CancelLFG 后 HasMyLFGPosting() == false", not E:HasMyLFGPosting())

-- ============================================================
-- 斜杠命令测试
-- ============================================================
print("\n== 斜杠命令注册测试 ==")
-- Core 的 /ecn 主命令需要手动注册（test 没走 Initialize 全流程）
E:RegisterSlashCommands()
assert_("/cn 注册", _G.SlashCmdList["EPOCHCN_CN"] ~= nil)
assert_("/qc 注册", _G.SlashCmdList["EPOCHCN_QC"] ~= nil)
assert_("/qcw 注册", _G.SlashCmdList["EPOCHCN_QCW"] ~= nil)
assert_("/qcs 注册", _G.SlashCmdList["EPOCHCN_QCS"] ~= nil)
assert_("/qcc 注册", _G.SlashCmdList["EPOCHCN_QCC"] ~= nil)
assert_("/qcr 注册", _G.SlashCmdList["EPOCHCN_QCR"] ~= nil)

-- /qc 调用（不应崩）
local function pcall_slash(slash, msg)
  local fn = _G.SlashCmdList[slash]
  local ok, err = pcall(fn, msg)
  if not ok then
    print("  FAIL " .. slash .. " '" .. tostring(msg) .. "' " .. tostring(err))
    os.exit(1)
  end
end
pcall_slash("EPOCHCN_QC", "")
pcall_slash("EPOCHCN_QC", "ty")
pcall_slash("EPOCHCN_QC", "list")
pcall_slash("EPOCHCN_QC", "list group")
pcall_slash("EPOCHCN_QC", "find 谢谢")
pcall_slash("EPOCHCN_QC", "bilingual")
pcall_slash("EPOCHCN_QC", "smart")
pcall_slash("EPOCHCN_QC", "lfm ICC")
pcall_slash("EPOCHCN_QC", "unknowncode")
pcall_slash("EPOCHCN_QCW", "")
pcall_slash("EPOCHCN_QCW", "ty")
pcall_slash("EPOCHCN_QCW", "Player1 ty")
pcall_slash("EPOCHCN_QCS", "ty")
pcall_slash("EPOCHCN_QCC", "ty")
pcall_slash("EPOCHCN_QCR", "")
pcall_slash("EPOCHCN_CN", "")
pcall_slash("EPOCHCN_CN", "who")
pcall_slash("EPOCHCN_CN", "refresh")
pcall_slash("EPOCHCN_CN", "leave")
pcall_slash("EPOCHCN_CN", "join")
assert_("/cn join 使用 china 频道", lastJoinedChannel == "china")
pcall_slash("EPOCHCN_CN", "help")
pcall_slash("EPOCHCN_CN", "你好世界")  -- 发送
assert_("/cn refresh 使用 china 频道", lastListedChannel == "china")
print("  OK   全部斜杠命令调用无报错")

-- /ecn 子命令
print("\n== /ecn 子命令测试 ==")
assert_("/ecn 注册", _G.SlashCmdList["EPOCHCN"] ~= nil)
local epochcnSlash = _G.SlashCmdList["EPOCHCN"]
local function pcall_ecn(msg)
  local ok, err = pcall(epochcnSlash, msg)
  if not ok then
    print("  FAIL /ecn '" .. msg .. "' " .. tostring(err))
    os.exit(1)
  end
end
pcall_ecn("social")
pcall_ecn("social list")
addonMessages = {}
pcall_ecn("social ping")
assert_("/ecn social ping 补充公会频道", hasAddonChannel("GUILD"))
assert_("/ecn social ping 使用 china 频道", hasAddonChannel("CHANNEL", 7))
pcall_ecn("contacts")
pcall_ecn("note Foo 这是一个测试备注")
pcall_ecn("note Foo")
pcall_ecn("tag Foo 战友")
pcall_ecn("tag Foo")
pcall_ecn("untag Foo 战友")
pcall_ecn("block Bar")
pcall_ecn("unblock Bar")
pcall_ecn("mute Baz")
pcall_ecn("unmute Baz")
pcall_ecn("hello Foo")
pcall_ecn("forget Foo")
pcall_ecn("lfg")
pcall_ecn("lfg cancel")
pcall_ecn("lfg refresh")
pcall_ecn("lfg codes")
pcall_ecn("lfg post ICC 速刷")
pcall_ecn("lfg post 冰冠堡垒 团长有意向 dps×3")
pcall_ecn("lfg apply Bar")
pcall_ecn("phrase add abc 你好 | hi")
pcall_ecn("phrase list")
pcall_ecn("phrase remove abc")
print("  OK   全部 /ecn 子命令调用无报错")

-- 主要面板打开/关闭（Toggle）
print("\n== 面板 Toggle 测试 ==")
local function pcall_panel(name, fn)
  local ok, err = pcall(fn)
  if not ok then
    print("  FAIL " .. name .. " — " .. tostring(err))
    os.exit(1)
  end
  print("  OK   " .. name)
end
pcall_panel("E:ToggleSocialPanel()", function() E:ToggleSocialPanel() end)
pcall_panel("E:ToggleSocialPanel() 第二次", function() E:ToggleSocialPanel() end)
pcall_panel("E:ToggleLFGPanel()", function() E:ToggleLFGPanel() end)
pcall_panel("E:ToggleLFGPanel() 第二次", function() E:ToggleLFGPanel() end)
pcall_panel("E:ToggleQuickChatPanel()", function() E:ToggleQuickChatPanel() end)
pcall_panel("E:ToggleFeedbackPanel()", function() E:ToggleFeedbackPanel() end)
pcall_panel("E:ToggleSettingsPanel()", function() E:ToggleSettingsPanel() end)

print("\n[PASS] 社交模块所有测试通过！")
