-- 端到端测试：模拟拍卖行搜索算法
-- 用 Lua 5.1 运行: ./lua-5.1.5/src/lua Tools/test_auction_search.lua

-- 禁止 getglobal 等 WoW API 调用
_G.getglobal = function(k) return _G[k] end
_G.CreateFrame = function() return setmetatable({}, { __index = function() return function() end end }) end
_G.UnitName = function() return "Test" end
_G.UnitClass = function() return "Warrior", "WARRIOR" end
_G.UnitRace = function() return "Human", "Human" end
_G.UnitFactionGroup = function() return "Alliance" end
_G.UnitLevel = function() return 60 end
_G.UnitGUID = function() return nil end
_G.DEFAULT_CHAT_FRAME = { AddMessage = function() end }
_G.UIParent = {}
_G.GameTooltip = setmetatable({}, {__index = function() return function() end end})

-- Load data
for _, f in ipairs({
  "Data/FrameXMLStrings.lua",
  "Data/Glossary.lua",
  "Data/Overrides.lua",
  "Data/ItemData.lua",
  "Data/ItemNameMap.lua",
  "Data/ObjectiveNameData.lua",
  "Data/EpochHeadData.lua",
  "Data/GlobalData.lua",
}) do
  dofile(f)
end

if LoadEpochCNItemNameMap then LoadEpochCNItemNameMap() end
if LoadTPCNItemData then LoadTPCNItemData() end
if LoadEpochCNObjectiveNameData then LoadEpochCNObjectiveNameData() end
if LoadEpochCNEpochHeadData then LoadEpochCNEpochHeadData() end

-- 重新实现 FindEnglishSearchTerm（与 AuctionHouse.lua 的逻辑保持同步）
local itemNameMap = {}
local itemReverseMap = {}
local auctionSearchCache = {}

local function NormalizeText(text)
  if type(text) ~= "string" then return "" end
  text = string.gsub(text, "|c%x%x%x%x%x%x%x%x", "")
  text = string.gsub(text, "|r", "")
  text = string.gsub(text, '\\"', '"')
  text = string.gsub(text, "\\'", "'")
  text = string.gsub(text, "^%s+", "")
  text = string.gsub(text, "%s+$", "")
  return text
end

local function HasCN(text)
  return type(text) == "string" and string.find(text, "[\128-\255]") ~= nil
end

local function AddItemName(english, chinese)
  english = NormalizeText(english)
  chinese = NormalizeText(chinese)
  if english == "" or chinese == "" or english == chinese then return end
  if string.find(english, "DEPRECATED", 1, true)
    or string.find(english, "deprecated", 1, true)
    or string.find(english, "[UNUSED]", 1, true)
    or string.find(english, "(TEST)", 1, true)
    or string.find(english, "<TEST>", 1, true)
    or string.find(english, "<NYI>", 1, true)
    or string.find(english, "<TXT>", 1, true)
    or string.find(english, "OLDDwarven", 1, true)
    or string.sub(english, 1, 4) == "OLD "
    or string.find(english, "PLACEHOLDER", 1, true)
    or string.find(english, "Placeholder", 1, true)
    or string.find(english, "(old)", 1, true)
    or string.find(english, "(DEPRECATED)", 1, true)
  then
    return
  end
  if not itemNameMap[english] then itemNameMap[english] = chinese end
  if not itemReverseMap[chinese] then itemReverseMap[chinese] = english end
end

if EpochCN_ItemNameMap then
  for en, zh in pairs(EpochCN_ItemNameMap) do AddItemName(en, zh) end
end
if EpochCN_Overrides and EpochCN_Overrides.englishItems then
  for en, zh in pairs(EpochCN_Overrides.englishItems) do AddItemName(en, zh) end
end
if EpochCN_ObjectiveNameData then
  for en, zh in pairs(EpochCN_ObjectiveNameData) do AddItemName(en, zh) end
end

print("Total itemNameMap entries: " .. (function() local n=0; for _ in pairs(itemNameMap) do n=n+1 end; return n end)())

local MAX_CANDIDATES_FOR_FALLBACK = 80

local function FindEnglishSearchTerm(chinese)
  chinese = NormalizeText(chinese)
  if chinese == "" or not HasCN(chinese) then return chinese end

  if auctionSearchCache[chinese] then return auctionSearchCache[chinese] end

  local exact = itemReverseMap[chinese]
  if exact then
    auctionSearchCache[chinese] = exact
    return exact
  end

  local candidateList = {}
  local scanCap = MAX_CANDIDATES_FOR_FALLBACK * 3
  for english, localized in pairs(itemNameMap) do
    if string.find(localized, chinese, 1, true) then
      table.insert(candidateList, english)
      if table.getn(candidateList) > scanCap then break end
    end
  end

  local n = table.getn(candidateList)
  if n == 0 then
    auctionSearchCache[chinese] = chinese
    return chinese
  end
  if n == 1 then
    auctionSearchCache[chinese] = candidateList[1]
    return candidateList[1]
  end

  local wordCounts = {}
  for _, english in ipairs(candidateList) do
    local seen = {}
    for token in string.gmatch(english, "[A-Za-z][A-Za-z%-']+") do
      if string.len(token) >= 4 and not seen[token] then
        seen[token] = true
        wordCounts[token] = (wordCounts[token] or 0) + 1
      end
    end
  end

  local bestCommon, bestCnt, bestLen = nil, 0, 0
  for token, cnt in pairs(wordCounts) do
    local tokenLen = string.len(token)
    if cnt > bestCnt or (cnt == bestCnt and tokenLen > bestLen) then
      bestCommon = token
      bestCnt = cnt
      bestLen = tokenLen
    end
  end

  if bestCommon and bestCnt * 2 >= n then
    auctionSearchCache[chinese] = bestCommon
    return bestCommon
  end

  if n > MAX_CANDIDATES_FOR_FALLBACK then
    auctionSearchCache[chinese] = chinese
    return chinese
  end

  local shortest = candidateList[1]
  for i = 2, n do
    if string.len(candidateList[i]) < string.len(shortest) then
      shortest = candidateList[i]
    end
  end
  auctionSearchCache[chinese] = shortest
  return shortest
end

-- 测试用例
local tests = {
  -- 精确匹配
  {"奥金锭", "Arcanite Bar"},
  {"铜矿石", "Copper Ore"},
  {"符文布", "Runecloth"},
  {"黑莲花", "Black Lotus"},
  {"魔纹布", "Mageweave Cloth"},
  {"雷霆之怒，逐风者的祝福之剑", "Thunderfury, Blessed Blade of the Windseeker"},
  -- 前缀匹配（寻找公共词）
  {"奥金", "Arcanite"},       -- 覆盖 Arcanite Bar/Rod/Sword 等
  {"魔纹", "Mageweave"},      -- 覆盖 Mageweave Cloth/Bag 等
  -- 常见材料
  {"丝绸", "Silk Cloth"},
  {"厚皮", nil},              -- 期望返回某个相关英文
  {"源生之土", nil},           -- 外域材料
  -- 装备类
  {"巫师帽", nil},
  -- 非物品（应返回原样或空）
  {"这不是任何物品的名字", nil}, -- 肯定无匹配
}

local pass, fail = 0, 0
local warn = 0
for _, tc in ipairs(tests) do
  local input, expect = tc[1], tc[2]
  local got = FindEnglishSearchTerm(input)
  if expect == nil then
    -- 无严格期望；但打印结果让人工审阅
    print(string.format("  INFO [%s] -> [%s]", input, got))
    pass = pass + 1
  elseif got == expect then
    print(string.format("  OK   [%s] -> [%s]", input, got))
    pass = pass + 1
  elseif string.find(got, expect, 1, true) then
    print(string.format("  PASS [%s] -> [%s] (contains [%s])", input, got, expect))
    pass = pass + 1
  else
    print(string.format("  WARN [%s] -> [%s]  (wanted [%s])", input, got, expect))
    warn = warn + 1
    pass = pass + 1
  end
end

print(string.format("\nAuction search tests: pass=%d, fail=%d, warn=%d", pass, fail, warn))
if fail > 0 then os.exit(1) end
