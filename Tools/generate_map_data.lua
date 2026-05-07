local ROOT = "/Users/macos/Desktop/EpochCN"
local PFQUEST = "/Users/macos/Desktop/pfQuest-wotlk"
local PFQUEST_EPOCH = "/Users/macos/Desktop/pfQuest-epoch"

pfDB = { quests = {}, units = {}, objects = {}, items = {}, zones = {}, areatrigger = {} }

local function load(path)
  local ok, err = pcall(dofile, path)
  if not ok then io.stderr:write("skip ", path, ": ", tostring(err), "\n") end
end

local files = {
  PFQUEST .. "/db/quests.lua",
  PFQUEST .. "/db/units.lua",
  PFQUEST .. "/db/objects.lua",
  PFQUEST .. "/db/items.lua",
  PFQUEST .. "/db/areatrigger.lua",
  PFQUEST .. "/db/enUS/quests.lua",
  PFQUEST .. "/db/zhCN/units.lua",
  PFQUEST .. "/db/zhCN/objects.lua",
  PFQUEST .. "/db/zhCN/items.lua",
  PFQUEST_EPOCH .. "/db/quests-epoch.lua",
  PFQUEST_EPOCH .. "/db/units-epoch.lua",
  PFQUEST_EPOCH .. "/db/objects-epoch.lua",
  PFQUEST_EPOCH .. "/db/items-epoch.lua",
  PFQUEST_EPOCH .. "/db/areatrigger-epoch.lua",
  PFQUEST_EPOCH .. "/db/enUS/quests-epoch.lua",
  PFQUEST_EPOCH .. "/db/zhCN/quests-epoch.lua",
  PFQUEST_EPOCH .. "/db/zhCN/units-epoch.lua",
  PFQUEST_EPOCH .. "/db/zhCN/objects-epoch.lua",
  PFQUEST_EPOCH .. "/db/zhCN/items-epoch.lua",
}

for _, path in ipairs(files) do load(path) end

local quests = {}
local names = { U = {}, O = {}, I = {}, A = {} }
local seenNames = { U = {}, O = {}, I = {}, A = {} }
local MAX_POINTS_PER_SOURCE_ZONE = 8
local MAX_ITEM_SOURCES = 12

-- Small, traceable corrections for Project Epoch entries that are present in
-- quest text but missing coordinates from the current pfQuest-epoch database.
local MANUAL_NAMES = {
  U = {
    [27705] = "洛林·狐火",
  },
}

local MANUAL_COORDS = {
  U = {
    -- Maczuga/pfQuest-Epoch db/units-tbc.lua: Lorrin Foxfire, Stonard.
    [27705] = { coords = { { 47.9, 55.5, 8, 120 } }, fac = "H", lvl = "41" },
  },
}

local QUEST_MARKER_OVERRIDES = {
  -- pfQuest-epoch quest text asks the player to take the tailoring order to
  -- Tyraeth Morningshade at Mirage Raceway, but the quest row lacks end.U.
  [28711] = {
    e = { U = { 45976 } },
  },
}

local function escape(s)
  s = tostring(s or "")
  s = string.gsub(s, "\\", "\\\\")
  s = string.gsub(s, "\"", "\\\"")
  s = string.gsub(s, "\n", "\\n")
  s = string.gsub(s, "\r", "\\r")
  return s
end

local function addName(kind, id)
  if not id or seenNames[kind][id] then return end
  seenNames[kind][id] = true
  local source = MANUAL_NAMES[kind] and MANUAL_NAMES[kind][id]
  if kind == "U" then
    source = source or (pfDB.units["zhCN-epoch"] and pfDB.units["zhCN-epoch"][id]) or (pfDB.units.zhCN and pfDB.units.zhCN[id])
  elseif kind == "O" then
    source = source or (pfDB.objects["zhCN-epoch"] and pfDB.objects["zhCN-epoch"][id]) or (pfDB.objects.zhCN and pfDB.objects.zhCN[id])
  elseif kind == "I" then
    source = source or (pfDB.items["zhCN-epoch"] and pfDB.items["zhCN-epoch"][id]) or (pfDB.items.zhCN and pfDB.items.zhCN[id])
  end
  if source then names[kind][id] = source end
end

local function coordSource(kind, id)
  if MANUAL_COORDS[kind] and MANUAL_COORDS[kind][id] then
    return MANUAL_COORDS[kind][id]
  end

  if kind == "U" then
    return (pfDB.units["data-epoch"] and pfDB.units["data-epoch"][id]) or (pfDB.units.data and pfDB.units.data[id])
  elseif kind == "O" then
    return (pfDB.objects["data-epoch"] and pfDB.objects["data-epoch"][id]) or (pfDB.objects.data and pfDB.objects.data[id])
  elseif kind == "A" then
    return (pfDB.areatrigger["data-epoch"] and pfDB.areatrigger["data-epoch"][id]) or (pfDB.areatrigger.data and pfDB.areatrigger.data[id])
  end
end

local function appendCoords(markers, kind, id)
  local source = coordSource(kind, id)
  if not source or not source.coords then return end
  addName(kind, id)

  local byZone = {}
  for _, c in pairs(source.coords) do
    local x, y, zone = tonumber(c[1]), tonumber(c[2]), tonumber(c[3])
    if x and y and zone then
      if not byZone[zone] then byZone[zone] = {} end
      table.insert(byZone[zone], { x, y })
    end
  end

  for zone, list in pairs(byZone) do
    local step = math.max(1, math.floor(table.getn(list) / MAX_POINTS_PER_SOURCE_ZONE))
    local added = 0
    for i = 1, table.getn(list), step do
      table.insert(markers, { list[i][1], list[i][2], zone, kind, id })
      added = added + 1
      if added >= MAX_POINTS_PER_SOURCE_ZONE then break end
    end
  end
end

local function appendItemSources(markers, item)
  addName("I", item)
  local data = (pfDB.items["data-epoch"] and pfDB.items["data-epoch"][item]) or (pfDB.items.data and pfDB.items.data[item])
  if not data then return end

  local candidates = {}
  for kind, coordsKind in pairs({ U = "U", O = "O" }) do
    if data[kind] then
      for id, rate in pairs(data[kind]) do
        table.insert(candidates, { kind = coordsKind, id = id, rate = tonumber(rate) or 0 })
      end
    end
  end

  table.sort(candidates, function(a, b) return a.rate > b.rate end)
  for i = 1, math.min(table.getn(candidates), MAX_ITEM_SOURCES) do
    appendCoords(markers, candidates[i].kind, candidates[i].id)
  end
end

local function addQuest(id, quest)
  if not quest then return end
  local q = { l = tonumber(quest.lvl) or 0, m = tonumber(quest.min) or 0, s = {}, e = {}, o = {} }
  local loc = (pfDB.quests["enUS-epoch"] and pfDB.quests["enUS-epoch"][id]) or (pfDB.quests.enUS and pfDB.quests.enUS[id])
  if loc and loc.T then q.t = loc.T end
  if quest.race then q.r = tonumber(quest.race) end
  if quest["class"] then q.c = tonumber(quest["class"]) end
  if quest.skill then q.sk = tonumber(quest.skill) end
  if quest.event then q.ev = tonumber(quest.event) or 1 end
  if quest.pre then
    q.p = {}
    for _, prequest in pairs(quest.pre) do
      if tonumber(prequest) then table.insert(q.p, tonumber(prequest)) end
    end
    table.sort(q.p)
  end

  if quest.start then
    if quest.start.U then for _, id in pairs(quest.start.U) do appendCoords(q.s, "U", id) end end
    if quest.start.O then for _, id in pairs(quest.start.O) do appendCoords(q.s, "O", id) end end
  end

  if quest["end"] then
    if quest["end"].U then for _, id in pairs(quest["end"].U) do appendCoords(q.e, "U", id) end end
    if quest["end"].O then for _, id in pairs(quest["end"].O) do appendCoords(q.e, "O", id) end end
  end

  local override = QUEST_MARKER_OVERRIDES[id]
  if override and override.e then
    if override.e.U then for _, id in pairs(override.e.U) do appendCoords(q.e, "U", id) end end
    if override.e.O then for _, id in pairs(override.e.O) do appendCoords(q.e, "O", id) end end
  end

  if quest.obj then
    if quest.obj.U then for _, id in pairs(quest.obj.U) do appendCoords(q.o, "U", id) end end
    if quest.obj.O then for _, id in pairs(quest.obj.O) do appendCoords(q.o, "O", id) end end
    if quest.obj.A then for _, id in pairs(quest.obj.A) do appendCoords(q.o, "A", id) end end
    if quest.obj.I then for _, id in pairs(quest.obj.I) do appendItemSources(q.o, id) end end
  end

  if table.getn(q.s) > 0 or table.getn(q.e) > 0 or table.getn(q.o) > 0 then
    quests[id] = q
  end
end

for id, quest in pairs(pfDB.quests.data or {}) do addQuest(id, quest) end
for id, quest in pairs(pfDB.quests["data-epoch"] or {}) do addQuest(id, quest) end

local out = assert(io.open(ROOT .. "/Data/MapData.lua", "w"))
out:write("-- Generated by Tools/generate_map_data.lua. Do not edit by hand.\n")
out:write("function LoadEpochCNMapData()\n")
out:write("  EpochCN_MapData = {\n")

local ids = {}
for id in pairs(quests) do table.insert(ids, id) end
table.sort(ids)

local function writeMarkers(markers)
  out:write("{")
  for _, marker in ipairs(markers) do
    out:write(string.format("{%.2f,%.2f,%d,\"%s\",%d},", marker[1], marker[2], marker[3], marker[4], marker[5]))
  end
  out:write("}")
end

for _, id in ipairs(ids) do
  local q = quests[id]
  out:write("    [", id, "]={")
  out:write("l=", q.l, ",m=", q.m, ",")
  if q.r then out:write("r=", q.r, ",") end
  if q.c then out:write("c=", q.c, ",") end
  if q.sk then out:write("sk=", q.sk, ",") end
  if q.ev then out:write("ev=", q.ev, ",") end
  if q.p and table.getn(q.p) > 0 then
    out:write("p={")
    for _, prequest in ipairs(q.p) do out:write(prequest, ",") end
    out:write("},")
  end
  if q.t then out:write("t=\"", escape(q.t), "\",") end
  out:write("s="); writeMarkers(q.s); out:write(",")
  out:write("e="); writeMarkers(q.e); out:write(",")
  out:write("o="); writeMarkers(q.o)
  out:write("},\n")
end
out:write("  }\n")

out:write("  EpochCN_MapNames = {\n")
for _, kind in ipairs({ "U", "O", "I", "A" }) do
  out:write("    ", kind, "={")
  local keys = {}
  for id in pairs(names[kind]) do table.insert(keys, id) end
  table.sort(keys)
  for _, id in ipairs(keys) do out:write("[", id, "]=\"", escape(names[kind][id]), "\",") end
  out:write("},\n")
end
out:write("  }\n")
out:write("end\n")
out:close()

print(string.format("Generated %d quests into %s/Data/MapData.lua", table.getn(ids), ROOT))

local questOut = assert(io.open(ROOT .. "/Data/EpochQuestData.lua", "w"))
questOut:write("-- Generated by Tools/generate_map_data.lua. Do not edit by hand.\n")
questOut:write("function LoadEpochCNQuestData()\n")
questOut:write("  EpochCN_EpochQuestData = {\n")

local zhQuest = pfDB.quests["zhCN-epoch"] or {}
local enQuest = pfDB.quests["enUS-epoch"] or {}
local questTextIDs = {}
for id in pairs(zhQuest) do table.insert(questTextIDs, id) end
table.sort(questTextIDs)

for _, id in ipairs(questTextIDs) do
  local zh = zhQuest[id] or {}
  local en = enQuest[id] or {}
  local title = zh.T or ""
  local objective = zh.O or ""
  local description = zh.D or ""
  local enTitle = en.T or ""
  if title ~= "" or objective ~= "" or description ~= "" then
    questOut:write("    [", id, "]={")
    questOut:write("\"", escape(title), "\",")
    questOut:write("\"", escape(objective), "\",")
    questOut:write("\"", escape(description), "\",")
    questOut:write("\"pfQuest-epoch zhCN\",")
    questOut:write("\"", escape(enTitle), "\"")
    questOut:write("},\n")
  end
end

questOut:write("  }\n")
questOut:write("end\n")
questOut:close()

print(string.format("Generated %d Epoch quest texts into %s/Data/EpochQuestData.lua", table.getn(questTextIDs), ROOT))
