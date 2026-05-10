-- 模拟 WoW 3.3.5 环境测试 EpochCN 插件加载
-- 运行: cd 到 EpochCN 根目录，然后 ./lua-5.1.5/src/lua Tools/test_load.lua

-- Stub WoW globals
_G.getglobal = function(k) return _G[k] end
_G.CreateFrame = function(frameType, name, parent, template)
  local f = {}
  local mt = {__index = function(_, key)
    return function() return nil end
  end}
  setmetatable(f, mt)
  f.RegisterEvent = function() end
  f.SetScript = function() end
  f.HookScript = function() end
  f.Show = function() end
  f.Hide = function() end
  f.IsShown = function() return false end
  f.IsVisible = function() return false end
  f.SetPoint = function() end
  f.SetSize = function() end
  f.SetWidth = function() end
  f.SetHeight = function() end
  f.SetText = function() end
  f.GetText = function() return "" end
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
  f.CreateFontString = function() return _G.CreateFrame() end
  f.CreateTexture = function() return _G.CreateFrame() end
  f.GetRegions = function() return end
  f.GetChildren = function() return end
  f.GetName = function() return name end
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
_G.DEFAULT_CHAT_FRAME = { AddMessage = function() end }
_G.UIParent = _G.CreateFrame()
_G.GameTooltip = _G.CreateFrame()
_G.UnitName = function() return "TestPlayer" end
_G.UnitClass = function() return "战士", "WARRIOR" end
_G.UnitRace = function() return "Human", "Human" end
_G.UnitFactionGroup = function() return "Alliance" end
_G.UnitLevel = function() return 60 end
_G.UnitGUID = function() return nil end
_G.GetQuestID = function() return nil end
_G.GetQuestLogTitle = function() return nil end
_G.GetQuestLogQuestText = function() return "", "" end
_G.GetQuestLogLeaderBoard = function() return "", "", false end
_G.GetQuestLogCompletionText = function() return "" end
_G.GetAbandonQuestName = function() return "" end
_G.GetTitleText = function() return "" end
_G.GetQuestText = function() return "" end
_G.GetObjectiveText = function() return "" end
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
_G.hooksecurefunc = function() end
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
_G.QuestFrame = _G.CreateFrame()
_G.QuestLogFrame = _G.CreateFrame()
_G.QuestInfoFrame = _G.CreateFrame()
_G.QuestFrameProgressPanel = _G.CreateFrame()
_G.QuestFrameRewardPanel = _G.CreateFrame()
_G.SpellBookFrame = _G.CreateFrame()
_G.ItemRefTooltip = _G.CreateFrame()
_G.TargetFrame = _G.CreateFrame()
_G.FocusFrame = _G.CreateFrame()
_G.WatchFrame = _G.CreateFrame()
_G.bit = { band = function(a, b) return a end }

-- Pack/unpack aliases
_G.unpack = unpack or table.unpack

-- 插件加载顺序（与 toc 一致）
local files = {
  "Data/Manifest.lua",
  "Data/FrameXMLStrings.lua",
  "Data/Glossary.lua",
  "Data/Overrides.lua",
  "Data/QuestCN_Data.lua",
  "Data/EpochQuestData.lua",
  "Data/MapData.lua",
  "Data/SpellData_52.lua",
  "Data/SpellData_Season.lua",
  "Data/SpellData_Epoch.lua",
  "Data/ItemData.lua",
  "Data/ItemNameMap.lua",
  "Data/EpochConsumableData.lua",
  "Data/UnitData.lua",
  "Data/ObjectiveNameData.lua",
  "Data/CallBoardData.lua",
  "Data/GlobalData.lua",
  "Data/EpochHeadData.lua",
  "Core.lua",
}

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
  EpochCN:CaptureRawAPI()
  EpochCN:LoadSeedData()
  EpochCN:BuildLookupTables()
end)
if not ok then
  print("[FAIL] Core init: " .. tostring(err))
  os.exit(1)
end
print("[2/3] Core init OK.")

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
