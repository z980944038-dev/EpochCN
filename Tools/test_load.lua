-- 模拟 WoW 3.3.5 环境测试 EpochCN 插件加载
-- 运行: cd 到 EpochCN 根目录，然后 ./lua-5.1.5/src/lua Tools/test_load.lua

-- Stub WoW globals
local chatMessages = {}
_G.getglobal = function(k) return _G[k] end
_G.CreateFrame = function(frameType, name, parent, template)
  local f = { __scripts = {}, __hooks = {}, __text = "", __frameType = frameType or "Frame" }
  local mt = {__index = function(_, key)
    return function() return nil end
  end}
  setmetatable(f, mt)
  f.RegisterEvent = function() end
  f.SetScript = function(self, scriptName, func) self.__scripts[scriptName] = func end
  f.HookScript = function(self, scriptName, func)
    self.__hooks[scriptName] = self.__hooks[scriptName] or {}
    table.insert(self.__hooks[scriptName], func)
  end
  f.FireScript = function(self, scriptName, ...)
    local script = self.__scripts[scriptName]
    if script then script(self, ...) end
    local hooks = self.__hooks[scriptName] or {}
    for _, hook in ipairs(hooks) do
      hook(self, ...)
    end
  end
  f.Show = function() end
  f.Hide = function() end
  f.IsShown = function() return false end
  f.IsVisible = function() return false end
  f.SetPoint = function() end
  f.SetSize = function() end
  f.SetWidth = function() end
  f.SetHeight = function() end
  f.SetText = function(self, text) self.__text = text end
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
  f.StartMoving = function() end
  f.StopMovingOrSizing = function() end
  f.SetBackdrop = function() end
  f.CreateFontString = function(_, childName) return _G.CreateFrame("FontString", childName) end
  f.CreateTexture = function() return _G.CreateFrame() end
  f.GetRegions = function() return end
  f.GetChildren = function() return end
  f.GetName = function() return name end
  f.GetObjectType = function() return f.__frameType end
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
  if name then _G[name] = f end
  return f
end
_G.DEFAULT_CHAT_FRAME = { AddMessage = function(_, msg) table.insert(chatMessages, tostring(msg)) end }
_G.UIParent = _G.CreateFrame()
_G.GameTooltip = _G.CreateFrame("GameTooltip", "GameTooltip")
_G.GameTooltipTextLeft1 = _G.CreateFrame("FontString", "GameTooltipTextLeft1")
_G.GameTooltipTextLeft2 = _G.CreateFrame("FontString", "GameTooltipTextLeft2")
_G.GameTooltipTextLeft3 = _G.CreateFrame("FontString", "GameTooltipTextLeft3")
_G.__unitNames = { player = "TestPlayer" }
_G.__unitGuids = {}
_G.__objectiveText = ""
_G.UnitName = function(unit) return _G.__unitNames[unit or "player"] or "TestPlayer" end
_G.UnitClass = function() return "战士", "WARRIOR" end
_G.UnitRace = function() return "Human", "Human" end
_G.UnitFactionGroup = function() return "Alliance" end
_G.UnitLevel = function() return 60 end
_G.UnitGUID = function(unit) return _G.__unitGuids[unit] end
_G.GetQuestID = function() return nil end
_G.GetQuestLogTitle = function() return nil end
_G.GetQuestLogQuestText = function() return "", "" end
_G.GetQuestLogLeaderBoard = function() return "", "", false end
_G.GetQuestLogCompletionText = function() return "" end
_G.GetAbandonQuestName = function() return "" end
_G.GetTitleText = function() return "" end
_G.GetQuestText = function() return "" end
_G.GetObjectiveText = function() return _G.__objectiveText or "" end
_G.GetRewardText = function() return "" end
_G.GetProgressText = function() return "" end
_G.GetGreetingText = function() return "" end
_G.GetNumQuestLogEntries = function() return 0 end
_G.GetQuestLogSelection = function() return 0 end
_G.GetNumQuestLeaderBoards = function() return 0 end
_G.GetTime = function() return 0 end
_G.time = function() return 0 end
_G.SendAddonMessage = function() end
_G.RegisterAddonMessagePrefix = function() end
_G.GetNumRaidMembers = function() return 0 end
_G.GetNumPartyMembers = function() return 0 end
_G.IsInGuild = function() return false end
_G.IsShiftKeyDown = function() return false end
_G.SlashCmdList = {}
_G.hooksecurefunc = function(target, hook)
  if type(target) ~= "string" or type(hook) ~= "function" then return end
  local original = _G[target] or function() end
  _G[target] = function(...)
    local results = { original(...) }
    hook(...)
    return unpack(results)
  end
end
_G.UIDropDownMenu_CreateInfo = function() return {} end
_G.UIDropDownMenu_AddButton = function() end
_G.UIDropDownMenu_Initialize = function() end
_G.ToggleDropDownMenu = function() end
_G.CloseDropDownMenus = function() end
_G.UIDropDownMenu_SetText = function() end
_G.EasyMenu = function() end
_G.GetCursorPosition = function() return 0, 0 end
_G.Minimap = _G.CreateFrame()
_G.WorldMapFrame = _G.CreateFrame()
_G.WorldMapButton = _G.CreateFrame()
_G.CharacterFrame = _G.CreateFrame("Frame", "CharacterFrame")
_G.FriendsFrame = _G.CreateFrame("Frame", "FriendsFrame")
_G.SkillFrame = _G.CreateFrame("Frame", "SkillFrame")
_G.ReputationFrame = _G.CreateFrame("Frame", "ReputationFrame")
_G.QuestFrame = _G.CreateFrame()
_G.QuestLogFrame = _G.CreateFrame()
_G.QuestInfoFrame = _G.CreateFrame()
_G.QuestFrameProgressPanel = _G.CreateFrame()
_G.QuestFrameRewardPanel = _G.CreateFrame()
_G.SpellBookFrame = _G.CreateFrame()
_G.WatchFrame_Update = function() end
_G.CharacterFrame_ShowSubFrame = function() end
_G.SkillFrame_Update = function() end
_G.ReputationFrame_Update = function() end
_G.ItemRefTooltip = _G.CreateFrame("GameTooltip", "ItemRefTooltip")
_G.ItemRefTooltipTextLeft1 = _G.CreateFrame("FontString", "ItemRefTooltipTextLeft1")
_G.TargetFrame = _G.CreateFrame()
_G.FocusFrame = _G.CreateFrame()
_G.WatchFrame = _G.CreateFrame()
_G.bit = { band = function(a, b) return a end }

-- Pack/unpack aliases
_G.unpack = unpack or table.unpack

-- 插件加载顺序直接读取 toc，确保测试与正式发布使用同一装载列表。
local files = {}
for line in io.lines("EpochCN.toc") do
  local trimmed = string.gsub(string.gsub(line, "^%s+", ""), "%s+$", "")
  if trimmed ~= "" and string.sub(trimmed, 1, 2) ~= "##" then
    local filePath = string.gsub(trimmed, "\\", "/")
    table.insert(files, filePath)
  end
end

for _, f in ipairs(files) do
  local ok, err = pcall(dofile, f)
  if not ok then
    print("LOAD FAIL: " .. f .. "\n  " .. tostring(err))
    os.exit(1)
  end
end
print("[1/3] All Data files parsed OK.")

local EpochCN = _G.EpochCN
if not EpochCN then
  print("FAIL: EpochCN global not set")
  os.exit(1)
end

_G.EpochCNDB = {}
_G.EpochCNCharDB = {}

local ok, err = pcall(function()
  EpochCN:Initialize()
end)
if not ok then
  print("[FAIL] Full addon init: " .. tostring(err))
  os.exit(1)
end
print("[2/3] Full addon init OK.")

-- Sanity checks
local function assertEq(desc, got, want)
  if got == want then
    print("  OK   " .. desc)
  else
    print("  FAIL " .. desc .. " got=" .. tostring(got) .. " want=" .. tostring(want))
    os.exit(1)
  end
end

assertEq("Overrides.maps[Dustwallow Marsh]", EpochCN_Overrides.maps["Dustwallow Marsh"], "尘泥沼泽")
assertEq("Overrides.maps[The Barrens]", EpochCN_Overrides.maps["The Barrens"], "贫瘠之地")
assertEq("Overrides.maps[Badlands]", EpochCN_Overrides.maps["Badlands"], "荒芜之地")
assertEq("Overrides.maps[Redridge Mountains]", EpochCN_Overrides.maps["Redridge Mountains"], "赤脊山")
assertEq("Overrides.maps[Durotar]", EpochCN_Overrides.maps["Durotar"], "杜隆塔尔")
assertEq("Overrides.maps[Swamp of Sorrows]", EpochCN_Overrides.maps["Swamp of Sorrows"], "悲伤沼泽")
assertEq("Overrides.maps[Felwood]", EpochCN_Overrides.maps["Felwood"], "费伍德森林")
assertEq("Overrides.maps[Deadwind Pass]", EpochCN_Overrides.maps["Deadwind Pass"], "逆风小径")
assertEq("Overrides.englishItems[Band of the Endless]", EpochCN_Overrides.englishItems["Band of the Endless"], "无尽指环")
assertEq("GAME_LOCALE forced to zhCN by default", GAME_LOCALE, "zhCN")

-- Load ItemNameMap and verify auction search reverse lookups
if LoadEpochCNItemNameMap then
  LoadEpochCNItemNameMap()
end
if not EpochCN_ItemNameMap then
  print("  FAIL EpochCN_ItemNameMap not loaded")
  os.exit(1)
end
local inm_count = 0
for _ in pairs(EpochCN_ItemNameMap) do inm_count = inm_count + 1 end
print("  OK   ItemNameMap entries: " .. inm_count)

-- Check key items are in the map
local function assertMap(key, want)
  local got = EpochCN_ItemNameMap[key]
  if got == want then
    print("  OK   ItemNameMap[" .. key .. "]: " .. got)
  else
    print("  FAIL ItemNameMap[" .. key .. "] got=" .. tostring(got) .. " want=" .. want)
    os.exit(1)
  end
end
assertMap("Arcanite Bar", "奥金锭")
assertMap("Copper Ore", "铜矿石")
assertMap("Black Lotus", "黑莲花")
assertMap("Runecloth", "符文布")
assertMap("Thunderfury, Blessed Blade of the Windseeker", "雷霆之怒，逐风者的祝福之剑")

assertEq("TranslateEnglishUnitName[Kobold Spellcaster]", EpochCN:TranslateEnglishUnitName("Kobold Spellcaster"), "狗头人施法者")
assertEq("TranslateEnglishUnitName[Forest Troll Berserker]", EpochCN:TranslateEnglishUnitName("Forest Troll Berserker"), "森林巨魔狂战士")
assertEq("TranslateEnglishUnitName[Lesser Felhunter]", EpochCN:TranslateEnglishUnitName("Lesser Felhunter"), "小型地狱猎手")
assertEq("TranslateEnglishUnitName[Defias Ambusher]", EpochCN:TranslateEnglishUnitName("Defias Ambusher"), "迪菲亚伏击者")
assertEq("TranslateEnglishUnitName[Infinite Assassin]", EpochCN:TranslateEnglishUnitName("Infinite Assassin"), "永恒刺客")
assertEq("TranslateEnglishUnitName[Captured Prisoner]", EpochCN:TranslateEnglishUnitName("Captured Prisoner"), "被俘虏")
assertEq("TranslateEnglishUnitName[Portal Guardian]", EpochCN:TranslateEnglishUnitName("Portal Guardian"), "传送门守护者")
assertEq("TranslateEnglishUnitName[Void Sentry]", EpochCN:TranslateEnglishUnitName("Void Sentry"), "虚空哨兵")
assertEq("TranslateEnglishUnitName[Quest Credit Marker]", EpochCN:TranslateEnglishUnitName("Quest Credit Marker"), nil)
assertEq("TranslateEnglishUnitName[Kanrethad]", EpochCN:TranslateEnglishUnitName("Kanrethad"), nil)
assertEq("GetUnitData[87] translated fallback", EpochCN:GetUnitData(87)[1], "森林巨魔狂战士")
assertEq("GetUnitData[283] translated fallback", EpochCN:GetUnitData(283)[1], "狗头人治疗者")
assertEq("GetUnitData[46679] translated fallback", EpochCN:GetUnitData(46679)[1], "被俘虏")
assertEq("GetItemData[110004] safe map fallback", EpochCN:GetItemData(110004)[1], "旅行者的背包")
assertEq("GetItemData[65371] duplicate name stays raw", EpochCN:GetItemData(65371)[1], "Satchel of Trade Goods")
assertEq("TranslateEnglishObjectName[Wooden Cage]", EpochCN:TranslateEnglishObjectName("Wooden Cage"), "木制牢笼")
assertEq("TranslateEnglishObjectName[Stone Obelisk]", EpochCN:TranslateEnglishObjectName("Stone Obelisk"), "石制方尖碑")
assertEq("TranslateEnglishObjectName[Prison Cage]", EpochCN:TranslateEnglishObjectName("Prison Cage"), "囚笼")
assertEq("TranslateEnglishObjectName[Quest Credit Marker]", EpochCN:TranslateEnglishObjectName("Quest Credit Marker"), nil)

GameTooltipTextLeft1:SetText("Forest Troll Berserker")
GameTooltip:FireScript("OnShow")
assertEq("tooltip title fallback on show", GameTooltipTextLeft1:GetText(), "森林巨魔狂战士")

GameTooltipTextLeft1:SetText("Wooden Cage")
GameTooltip:FireScript("OnShow")
assertEq("tooltip object fallback on show", GameTooltipTextLeft1:GetText(), "木制牢笼")

GameTooltip.GetItem = function()
  return "Traveler's Backpack", "|Hitem:110004:0:0:0:0:0:0:0|h[Traveler's Backpack]|h"
end
GameTooltipTextLeft1:SetText("Traveler's Backpack")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip item id fallback", GameTooltipTextLeft1:GetText(), "旅行者的背包")

GameTooltip.GetItem = function()
  return "Glowing Wax Stick", "|Hitem:1434:0:0:0:0:0:0:0|h[Glowing Wax Stick]|h"
end
GameTooltip.NumLines = function() return 2 end
GameTooltipTextLeft1:SetText("Glowing Wax Stick")
GameTooltipTextLeft2:SetText("Use: Decrease the armor of the target by 50 for 30 sec. While affected, the target cannot stealth or turn invisible.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip mixed exact effect cleanup", GameTooltipTextLeft2:GetText(), "使用：使目标的护甲降低 50 点，持续 30秒。在效果持续期间，目标无法潜行或隐形。")

GameTooltip.GetItem = function()
  return "Satchel of Trade Goods", "|Hitem:63491:0:0:0:0:0:0:0|h[Satchel of Trade Goods]|h"
end
GameTooltip.NumLines = function() return 3 end
GameTooltipTextLeft1:SetText("Satchel of Trade Goods")
GameTooltipTextLeft2:SetText("Binds when picked up")
GameTooltipTextLeft3:SetText('"A small satchel containing various trade goods."')
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip quoted effect cleanup", GameTooltipTextLeft3:GetText(), "一个装有各种贸易物资的小挎包。")

GameTooltip.GetItem = function()
  return "Arena Defender", "|Hitem:18854:0:0:0:0:0:0:0|h[Arena Defender]|h"
end
GameTooltip.NumLines = function() return 2 end
GameTooltipTextLeft1:SetText("Arena Defender")
GameTooltipTextLeft2:SetText("Equip: Decreases your damage taken from other players by 1%.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip pvp damage reduction", GameTooltipTextLeft2:GetText(), "装备：受到其他玩家的伤害降低 1%。")

GameTooltipTextLeft2:SetText("Set: Decreases your damage taken from other players by 2%.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip plain set bonus", GameTooltipTextLeft2:GetText(), "套装：受到其他玩家的伤害降低 2%。")

GameTooltipTextLeft2:SetText("Random Enchantment")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip random enchantment", GameTooltipTextLeft2:GetText(), "随机附魔")

GameTooltipTextLeft2:SetText("Use: Teaches you how to summon this mount.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip mount teaching", GameTooltipTextLeft2:GetText(), "使用：教你学会召唤这种坐骑。")

GameTooltipTextLeft2:SetText("Equip: Restores 4 mana per 5 sec.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip mana per 5 sec", GameTooltipTextLeft2:GetText(), "装备：每5秒恢复 4 点法力值。")

GameTooltipTextLeft2:SetText("(4) Set: Reduces the casting time of your Immolate spell by 0.2 sec.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set spell", GameTooltipTextLeft2:GetText(), "(4) 套装：献祭的施法时间缩短 0.2 秒。")

GameTooltipTextLeft2:SetText("(2) Set: +10 Frost and Fire Resistance.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set dual resistance", GameTooltipTextLeft2:GetText(), "(2) 套装：冰霜抗性和火焰抗性提高 10 点。")

GameTooltipTextLeft2:SetText("(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set cooldown", GameTooltipTextLeft2:GetText(), "(4) 套装：震荡射击的冷却时间缩短 1 秒。")

GameTooltipTextLeft2:SetText("(6) Set: Chance on melee attack to heal you for 88 to 132.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set melee heal proc", GameTooltipTextLeft2:GetText(), "(6) 套装：近战攻击命中时有几率为你恢复 88 到 132 点生命值。")

GameTooltipTextLeft2:SetText("(6) Set: Increases the critical strike chance of Shield Slam by 10%.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set crit ability", GameTooltipTextLeft2:GetText(), "(6) 套装：盾牌猛击的爆击几率提高 10%。")

GameTooltipTextLeft2:SetText("(8) Set: Thunder Clap generates 20% more threat.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip indexed set threat", GameTooltipTextLeft2:GetText(), "(8) 套装：雷霆一击产生的威胁值提高 20%。")

GameTooltipTextLeft2:SetText("Chance on hit: Grants 1 extra attack on your next swing.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip extra attack proc", GameTooltipTextLeft2:GetText(), "击中时可能：你的下一次攻击额外获得 1 次攻击。")

GameTooltipTextLeft2:SetText("Chance on hit: Smites an enemy for 30 Holy damage.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip holy proc exact", GameTooltipTextLeft2:GetText(), "击中时可能：惩击敌人，造成 30 点神圣伤害。")

GameTooltipTextLeft2:SetText("Equip: Allows underwater breathing.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip underwater breathing exact", GameTooltipTextLeft2:GetText(), "装备：允许在水下呼吸。")

GameTooltipTextLeft2:SetText("Use: Change the school of magic that this wand fires.")
GameTooltip:FireScript("OnTooltipSetItem")
assertEq("tooltip wand school exact", GameTooltipTextLeft2:GetText(), "使用：改变这根魔杖发射的魔法学派。")

GameTooltipTextLeft1:SetText("Kobold Healer")
GameTooltip.GetUnit = function() return "Kobold Healer", "mouseover" end
__unitNames.mouseover = "Kobold Healer"
__unitGuids.mouseover = "0xF13000011B"
GameTooltip:FireScript("OnTooltipSetUnit")
assertEq("tooltip title fallback on unit", GameTooltipTextLeft1:GetText(), "狗头人治疗者")

assertEq("objective object fallback", EpochCN:TranslateObjective("Wooden Cage: 1/3"), "木制牢笼: 1/3")
assertEq("objective freeform use object fallback", EpochCN:TranslateObjective("Use the Wooden Cage"), "使用木制牢笼")
assertEq("objective freeform activate object fallback", EpochCN:TranslateObjective("Activate the Stone Obelisk"), "激活石制方尖碑")
assertEq("objective freeform escort unit fallback", EpochCN:TranslateObjective("Escort the Kobold Healer"), "护送狗头人治疗者")
assertEq("objective freeform rescue unit fallback", EpochCN:TranslateObjective("Rescue the Kobold Healer"), "营救狗头人治疗者")
assertEq("objective freeform free unit fallback", EpochCN:TranslateObjective("Free the Captured Prisoner"), "解救被俘虏")
assertEq("objective freeform defend object fallback", EpochCN:TranslateObjective("Defend the Wooden Cage"), "保卫木制牢笼")
assertEq("objective freeform protect object fallback", EpochCN:TranslateObjective("Protect the Wooden Cage"), "保护木制牢笼")
assertEq("objective freeform destroy object fallback", EpochCN:TranslateObjective("Destroy the Stone Obelisk"), "摧毁石制方尖碑")
assertEq("objective freeform speak unit fallback", EpochCN:TranslateObjective("Speak to the Kobold Healer"), "与狗头人治疗者交谈")
assertEq("objective freeform speak-with unit fallback", EpochCN:TranslateObjective("Speak with the Kobold Healer"), "与狗头人治疗者交谈")
assertEq("objective freeform report unit fallback", EpochCN:TranslateObjective("Report to the Kobold Healer"), "向狗头人治疗者复命")
assertEq("objective freeform report-back unit fallback", EpochCN:TranslateObjective("Report back to the Kobold Healer"), "回去向狗头人治疗者复命")
assertEq("objective freeform bring-to fallback", EpochCN:TranslateObjective("Bring the Wooden Cage to the Kobold Healer"), "将木制牢笼带给狗头人治疗者")
assertEq("objective freeform deliver-to fallback", EpochCN:TranslateObjective("Deliver the Wooden Cage to the Kobold Healer"), "将木制牢笼交给狗头人治疗者")
assertEq("objective freeform collect-for fallback", EpochCN:TranslateObjective("Collect the Wooden Cage for the Kobold Healer"), "为狗头人治疗者收集木制牢笼")
assertEq("objective freeform gather-for fallback", EpochCN:TranslateObjective("Gather the Wooden Cage for the Kobold Healer"), "为狗头人治疗者收集木制牢笼")
assertEq("objective freeform collect-from fallback", EpochCN:TranslateObjective("Collect the Wooden Cage from the Kobold Healer"), "从狗头人治疗者处收集木制牢笼")
assertEq("objective freeform retrieve-from fallback", EpochCN:TranslateObjective("Retrieve the Wooden Cage from the Kobold Healer"), "从狗头人治疗者处取回木制牢笼")
assertEq("objective freeform recover-from fallback", EpochCN:TranslateObjective("Recover the Wooden Cage from the Kobold Healer"), "从狗头人治疗者处取回木制牢笼")
assertEq("objective freeform bring-me fallback", EpochCN:TranslateObjective("Bring me the Wooden Cage"), "带回木制牢笼")
assertEq("objective freeform return object fallback", EpochCN:TranslateObjective("Return to the Wooden Cage"), "返回木制牢笼")

__objectiveText = "Use the Wooden Cage"
assertEq("questframe objective text fallback", GetObjectiveText(), "使用木制牢笼")

local watchLine = _G.CreateFrame("Frame", "WatchFrameLine1")
local watchRegion = _G.CreateFrame("FontString", "WatchFrameLine1Text")
watchRegion:SetText("Escort the Kobold Healer")
watchLine.GetRegions = function() return watchRegion end
WatchFrame_Update()
assertEq("watchframe objective fallback", watchRegion:GetText(), "护送狗头人治疗者")

CharacterFrame.IsVisible = function() return true end
SkillFrame.IsVisible = function() return true end
ReputationFrame.IsVisible = function() return true end

local characterTab2 = _G.CreateFrame("Button", "CharacterFrameTab2")
characterTab2.IsShown = function() return true end
characterTab2:SetText("Skills")
local characterTab3 = _G.CreateFrame("Button", "CharacterFrameTab3")
characterTab3.IsShown = function() return true end
characterTab3:SetText("Reputation")

CharacterFrame_ShowSubFrame("SkillFrame")
assertEq("character tab dynamic skills label", characterTab2:GetText(), "技能")
assertEq("character tab dynamic reputation label", characterTab3:GetText(), "声望")

FriendsFrame.IsVisible = function() return true end
local uiRow = _G.CreateFrame("Frame", "EpochCNTestUIRow")
uiRow.IsVisible = function() return true end
local uiRowText = _G.CreateFrame("FontString", "EpochCNTestUIRowText")
uiRowText:SetText("Friendly")
uiRow.GetRegions = function() return uiRowText end
uiRow.GetChildren = function() return end
FriendsFrame.GetChildren = function() return uiRow end

EpochCN:LocalizeUI()
uiRowText:SetText("Friendly")
FriendsFrame:FireScript("OnShow")
assertEq("ui frame onshow immediate relocalize", uiRowText:GetText(), "友方")

-- Check slash command routing still preserves module subcommands and core commands.
local function assertChatContains(desc, needle)
  for _, msg in ipairs(chatMessages) do
    if string.find(msg, needle, 1, true) then
      print("  OK   " .. desc)
      return
    end
  end
  print("  FAIL " .. desc .. " missing=" .. tostring(needle))
  os.exit(1)
end

EpochCNDB.lastKnownRemoteVersion = "9.9.9"
SlashCmdList["EPOCHCN"]("update")
SlashCmdList["EPOCHCN"]("status")
assertChatContains("slash update command", "当前版本")
assertChatContains("slash status command", "已加载 " .. tostring(EpochCN.version))

-- Check DBC raw spell names can bridge English client text back to translated spell data.
local heroicStrikeTalent = EpochCN:GetSpellDataByName("Improved Heroic Strike")
if not heroicStrikeTalent or heroicStrikeTalent[1] ~= "强化英勇打击" then
  print("  FAIL DBC 英文法术名反查失败: " .. tostring(heroicStrikeTalent and heroicStrikeTalent[1]))
  os.exit(1)
end
print("  OK   DBC 英文法术名反查: Improved Heroic Strike -> " .. heroicStrikeTalent[1])

local heroicStrikeTalentRank = EpochCN:GetSpellDataByName("Improved Heroic Strike Rank 1")
if not heroicStrikeTalentRank or heroicStrikeTalentRank[1] ~= "强化英勇打击" then
  print("  FAIL DBC 英文法术名+等级反查失败: " .. tostring(heroicStrikeTalentRank and heroicStrikeTalentRank[1]))
  os.exit(1)
end
print("  OK   DBC 英文法术名+等级反查: Improved Heroic Strike Rank 1 -> " .. heroicStrikeTalentRank[1])

-- Check spell sanitization
local spell32509 = TPCN_SpellData_52[32509] and TPCN_SpellData_52[32509][2]
if spell32509 and string.find(spell32509, "/1000;s1") then
  print("  FAIL spell 32509 还包含 DBC token /1000;s1: " .. tostring(spell32509))
  os.exit(1)
end
if spell32509 and string.find(spell32509, "411139s1") then
  print("  FAIL spell 32509 还包含法术ID token 411139s1: " .. tostring(spell32509))
  os.exit(1)
end
if spell32509 and string.find(spell32509, "冷却时间秒", 1, true) then
  print("  FAIL spell 32509 仍存在残句 冷却时间秒: " .. tostring(spell32509))
  os.exit(1)
end
if spell32509 and not string.find(spell32509, "若干秒", 1, true) then
  print("  FAIL spell 32509 未保留时间占位: " .. tostring(spell32509))
  os.exit(1)
end
if spell32509 and not string.find(spell32509, "一定百分比的法术急速", 1, true) then
  print("  FAIL spell 32509 未保留百分比占位: " .. tostring(spell32509))
  os.exit(1)
end
print("  OK   SpellData_52[32509] DBC tokens cleaned: " .. tostring(spell32509))

-- 检查 UnitData[6] 正常存在
if not TPCN_UnitData[6] then
  print("  FAIL TPCN_UnitData[6] 不存在")
  os.exit(1)
end
print("  OK   TPCN_UnitData[6] = " .. TPCN_UnitData[6][1])

-- 检查 ItemData[17]
if not TPCN_ItemData[17] then
  print("  FAIL TPCN_ItemData[17] 不存在")
  os.exit(1)
end
print("  OK   TPCN_ItemData[17] = " .. TPCN_ItemData[17][1])

-- 检查 EpochHeadData 合并后 ObjectiveNameData 含 Marshal McBride
if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData["Marshal McBride"] then
  print("  OK   EpochHeadData 合并 NPC 映射: " .. EpochCN_ObjectiveNameData["Marshal McBride"])
else
  print("  FAIL EpochHeadData 未合并到 ObjectiveNameData")
  os.exit(1)
end

print("[3/3] All sanity checks passed.")
print("\nEpochCN v" .. tostring(EpochCN.version) .. " plugin integrity OK.")
