-- EpochCN WorldMap Module
-- 独立世界地图任务标记：只依赖 EpochCN 自带 MapData，不需要 pfQuest。

EpochCN:RegisterModule("WorldMap", function(E)
  if not EpochCNDB.worldMap and not EpochCNDB.minimapQuestPins then return end
  if not EpochCN_MapData then
    E:Debug("世界地图任务标记缺少 MapData")
    return
  end

  E:InitWorldMap()
end)

local mapData = {
  [1429] = {3470.84, 2314.62, 1535.42, -7939.58},
  [1436] = {3500.00, 2333.33, 3016.67, -9400.00},
  [1433] = {2170.84, 1447.92, -1570.83, -8575.00},
  [1431] = {2700.00, 1800.00, 833.33, -9716.67},
  [1434] = {6381.25, 4254.17, 2220.83, -11168.75},
  [1453] = {1737.50, 1158.34, 1722.92, -7995.83},
  [1426] = {4925.00, 3283.34, 1802.08, -3877.08},
  [1455] = {790.63, 527.61, -713.591, -4569.24},
  [1432] = {2758.33, 1839.58, -1993.75, -4487.50},
  [1437] = {4135.42, 2756.25, -389.583, -2147.92},
  [1424] = {3200.00, 2133.33, 1066.67, 400.00},
  [1416] = {2800.00, 1866.67, 783.333, 1500.00},
  [1417] = {3600.00, 2400.00, -866.667, -133.333},
  [1425] = {3850.00, 2566.67, -1575.00, 1466.67},
  [1420] = {4518.75, 3012.50, 3033.33, 3837.50},
  [1421] = {4200.00, 2800.00, 3450.00, 1666.67},
  [1458] = {959.38, 640.10, 873.193, 1877.94},
  [1422] = {4300.00, 2866.67, 416.667, 3366.67},
  [1423] = {4031.25, 2687.50, -2287.50, 3704.17},
  [1418] = {2487.50, 1658.34, -2079.17, -5889.58},
  [1427] = {2231.25, 1487.50, -322.917, -6100.00},
  [1428] = {2929.17, 1952.08, -266.667, -7031.25},
  [1435] = {2293.75, 1529.17, -2222.92, -9620.83},
  [1419] = {3350.00, 2233.30, -1241.67, -10566.70},
  [1430] = {2500.00, 1666.63, -833.333, -9866.67},
  [1438] = {5091.66, 3393.75, 3814.58, 11831.20},
  [1457] = {1058.33, 705.71, 2938.36, 10238.30},
  [1439] = {6550.00, 4366.66, 2941.67, 8333.33},
  [1440] = {5766.67, 3843.75, 1700.00, 4672.92},
  [1442] = {4883.33, 3256.25, 3245.83, 2916.67},
  [1413] = {10133.34, 6756.25, 2622.92, 1612.50},
  [1411] = {5287.50, 3525.00, -1962.50, 1808.33},
  [1454] = {1402.61, 935.42, -3680.60, 2273.88},
  [1412] = {5137.50, 3425.00, 2047.92, -272.917},
  [1456] = {1043.75, 695.83, 516.667, -850.00},
  [1443] = {4495.83, 2997.91, 4233.33, 452.083},
  [1444] = {6950.00, 4633.33, 5441.67, -2366.67},
  [1441] = {4400.00, 2933.33, -433.333, -3966.67},
  [1446] = {6900.00, 4600.00, -218.75, -5875.00},
  [1449] = {3700.00, 2466.66, 533.333, -5966.67},
  [1451] = {3483.33, 2322.92, 2537.50, -5958.33},
  [1445] = {5250.00, 3500.00, -975.00, -2033.33},
  [1452] = {7100.00, 4733.33, -316.667, 8533.33},
  [1447] = {5070.84, 3381.25, -3277.08, 5341.67},
  [1448] = {5750.00, 3833.33, 1641.67, 7133.33},
  [1450] = {2308.33, 1539.59, -1381.25, 8491.67},
  [1415] = {40741.18, 27149.69, 18171.97, 11176.34},
  [1414] = {36799.81, 24533.20, 17066.60, 12799.90},
}

local zoneToUiMapID = {
  [12]=1429,[40]=1436,[44]=1433,[10]=1431,[33]=1434,[1519]=1453,
  [1]=1426,[1537]=1455,[38]=1432,[11]=1437,[267]=1424,[36]=1416,
  [45]=1417,[47]=1425,[85]=1420,[130]=1421,[1497]=1458,[28]=1422,
  [139]=1423,[3]=1418,[51]=1427,[46]=1428,[8]=1435,[4]=1419,[41]=1430,
  [141]=1438,[1657]=1457,[148]=1439,[331]=1440,[406]=1442,[17]=1413,
  [14]=1411,[1637]=1454,[215]=1412,[1638]=1456,[405]=1443,[357]=1444,
  [400]=1441,[440]=1446,[490]=1449,[1377]=1451,[15]=1445,[618]=1452,
  [16]=1447,[361]=1448,[493]=1450,
}

local mapFileToZoneID = {
  Alterac = 36,
  AlteracMountains = 36,
  Arathi = 45,
  ArathiHighlands = 45,
  Ashenvale = 331,
  Azshara = 16,
  Badlands = 3,
  BlastedLands = 4,
  BurningSteppes = 46,
  Darkshore = 148,
  Darnassis = 1657,
  Darnassus = 1657,
  DeadwindPass = 41,
  Desolace = 405,
  DunMorogh = 1,
  Durotar = 14,
  Duskwood = 10,
  Dustwallow = 15,
  DustwallowMarsh = 15,
  EasternPlaguelands = 139,
  Elwynn = 12,
  ElwynnForest = 12,
  Felwood = 361,
  Feralas = 357,
  Hillsbrad = 267,
  HillsbradFoothills = 267,
  Hinterlands = 47,
  TheHinterlands = 47,
  Ironforge = 1537,
  LochModan = 38,
  Moonglade = 493,
  Mulgore = 215,
  Ogrimmar = 1637,
  Orgrimmar = 1637,
  Redridge = 44,
  RedridgeMountains = 44,
  SearingGorge = 51,
  Silithus = 1377,
  Silverpine = 130,
  SilverpineForest = 130,
  StonetalonMountains = 406,
  Stormwind = 1519,
  StormwindCity = 1519,
  Stranglethorn = 33,
  StranglethornVale = 33,
  SwampOfSorrows = 8,
  Tanaris = 440,
  Teldrassil = 141,
  TheBarrens = 17,
  ThousandNeedles = 400,
  ThunderBluff = 1638,
  Tirisfal = 85,
  TirisfalGlades = 85,
  UngoroCrater = 490,
  UnGoroCrater = 490,
  Undercity = 1497,
  WesternPlaguelands = 28,
  Westfall = 40,
  Wetlands = 11,
  Winterspring = 618,
}

local zoneNameToID = {
  ["Alterac Mountains"] = 36,
  ["Arathi Highlands"] = 45,
  ["Ashenvale"] = 331,
  ["Azshara"] = 16,
  ["Badlands"] = 3,
  ["Blasted Lands"] = 4,
  ["Burning Steppes"] = 46,
  ["Darkshore"] = 148,
  ["Darnassus"] = 1657,
  ["Deadwind Pass"] = 41,
  ["Desolace"] = 405,
  ["Dun Morogh"] = 1,
  ["Durotar"] = 14,
  ["Duskwood"] = 10,
  ["Dustwallow Marsh"] = 15,
  ["Eastern Plaguelands"] = 139,
  ["Elwynn Forest"] = 12,
  ["Felwood"] = 361,
  ["Feralas"] = 357,
  ["Hillsbrad Foothills"] = 267,
  ["Ironforge"] = 1537,
  ["Loch Modan"] = 38,
  ["Moonglade"] = 493,
  ["Mulgore"] = 215,
  ["Orgrimmar"] = 1637,
  ["Redridge Mountains"] = 44,
  ["Searing Gorge"] = 51,
  ["Silithus"] = 1377,
  ["Silverpine Forest"] = 130,
  ["Stonetalon Mountains"] = 406,
  ["Stormwind City"] = 1519,
  ["Stranglethorn Vale"] = 33,
  ["Swamp of Sorrows"] = 8,
  ["Tanaris"] = 440,
  ["Teldrassil"] = 141,
  ["The Barrens"] = 17,
  ["The Hinterlands"] = 47,
  ["Thousand Needles"] = 400,
  ["Thunder Bluff"] = 1638,
  ["Tirisfal Glades"] = 85,
  ["Un'Goro Crater"] = 490,
  ["Undercity"] = 1497,
  ["Western Plaguelands"] = 28,
  ["Westfall"] = 40,
  ["Wetlands"] = 11,
  ["Winterspring"] = 618,
}
local subZoneNameToID = {
  ["Deathknell"] = 85,
  ["丧钟镇"] = 85,
  ["Brill"] = 85,
  ["布瑞尔"] = 85,
  ["Cold Hearth Manor"] = 85,
  ["Night Web's Hollow"] = 85,
  ["Solliden Farmstead"] = 85,
  ["Agamand Mills"] = 85,
  ["Tirisfal Glades"] = 85,
  ["提瑞斯法林地"] = 85,
}

local zoneContinent = {
  [1]=2,[3]=2,[4]=2,[8]=2,[10]=2,[11]=2,[12]=2,[28]=2,[33]=2,[36]=2,
  [38]=2,[40]=2,[41]=2,[44]=2,[45]=2,[46]=2,[47]=2,[51]=2,[85]=2,
  [130]=2,[139]=2,[267]=2,[1497]=2,[1519]=2,[1537]=2,
  [14]=1,[15]=1,[16]=1,[17]=1,[141]=1,[148]=1,[215]=1,[331]=1,
  [357]=1,[361]=1,[400]=1,[405]=1,[406]=1,[440]=1,[490]=1,[493]=1,
  [618]=1,[1377]=1,[1637]=1,[1638]=1,[1657]=1,
}
local continentNameToID = {
  ["Kalimdor"] = 1,
  ["Eastern Kingdoms"] = 2,
  ["Lordaeron"] = 2,
  ["卡利姆多"] = 1,
  ["东部王国"] = 2,
  ["洛丹伦"] = 2,
}
local mapFileToContinentID = {
  Kalimdor = 1,
  Azeroth = 0,
  Lordaeron = 2,
  EasternKingdoms = 2,
}

local pins = {}
local minimapPins = {}
local maxPins = 300
local maxMinimapPins = 30
local mapCanvas
local lastDebug = {}
local lastMinimapDebug = {}
local minimapZoomYards = {
  outdoor = { [0] = 300, [1] = 240, [2] = 180, [3] = 120, [4] = 80, [5] = 50 },
  indoor = { [0] = 466.6667, [1] = 400, [2] = 333.3333, [3] = 266.3333, [4] = 200, [5] = 133.3333 },
}
local textures = {
  start = "Interface\\Icons\\INV_Letter_15",
  available = "Interface\\GossipFrame\\AvailableQuestIcon",
  finish = "Interface\\GossipFrame\\ActiveQuestIcon",
  node = "Interface\\COMMON\\Indicator-Green",
}
local pinSizes = {
  start = 16,
  available = 16,
  finish = 22,
  objective = 2,
}
local pinColors = {
  start = { 0.35, 0.8, 1.0 },
  available = { 1.0, 0.85, 0.1 },
  finish = { 1.0, 0.45, 0.15 },
  objective = { 0.2, 1.0, 0.25 },
}
local filterKeys = {
  start = "worldMapShowStartPins",
  available = "worldMapShowAvailablePins",
  finish = "worldMapShowFinishPins",
  objective = "worldMapShowObjectivePins",
}
local markerPriority = {
  finish = 4,
  objective = 3,
  available = 2,
  start = 1,
}

local function Mod(a, b)
  return a - math.floor(a / b) * b
end

local function StableNodeColor(text)
  text = tostring(text or "")
  local hash = 0
  for i = 1, string.len(text) do
    hash = Mod((hash * 33) + string.byte(text, i), 9973)
  end
  local r = 0.35 + (Mod(hash, 70) / 100)
  local g = 0.55 + (Mod(math.floor(hash / 7), 45) / 100)
  local b = 0.35 + (Mod(math.floor(hash / 13), 60) / 100)
  return math.min(r, 1), math.min(g, 1), math.min(b, 1)
end
local trackingModeText = {
  all = "全部任务",
  sync = "自动同步",
  tracked = "仅追踪任务",
  manual = "手动选择",
  off = "关闭",
}
local trackingModeShortText = {
  all = "全",
  sync = "同",
  tracked = "追",
  manual = "手",
  off = "关",
}
local raceBits = {
  Human = 1,
  Orc = 2,
  Dwarf = 4,
  NightElf = 8,
  Scourge = 16,
  Undead = 16,
  Tauren = 32,
  Gnome = 64,
  Troll = 128,
  BloodElf = 512,
  Draenei = 1024,
}
local classBits = {
  WARRIOR = 1,
  PALADIN = 2,
  HUNTER = 4,
  ROGUE = 8,
  PRIEST = 16,
  DEATHKNIGHT = 32,
  SHAMAN = 64,
  MAGE = 128,
  WARLOCK = 256,
  DRUID = 1024,
}

local moduleFrame
local menuFrame
local menuButton
local refreshPending = false
local refreshTimer = 0
local mapCacheKey, mapCacheMarkers
local refreshVersion = 0
local minimapCacheKey, minimapCacheMarkers
local minimapRefreshTimer = 0
local hoverPollTimer = 0
local hoverPin
local PrintMapDebug
local visibleWorldMapPins = 0   -- 当前世界地图实际显示的 pin 数量，供 PollPinTooltip 限定遍历范围
local visibleMinimapPins = 0    -- 当前小地图实际显示的 pin 数量，同上

local function Print(message)
  if DEFAULT_CHAT_FRAME then
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ffccEpoch|cffffffffCN: " .. tostring(message))
  end
end

local function Band(a, b)
  if bit and bit.band then return bit.band(a, b) end
  local result, bitval = 0, 1
  while a > 0 and b > 0 do
    local aa, bb = Mod(a, 2), Mod(b, 2)
    if aa == 1 and bb == 1 then result = result + bitval end
    a = math.floor(a / 2)
    b = math.floor(b / 2)
    bitval = bitval * 2
  end
  return result
end

local function ZoneToWorld(x, y, zoneID)
  local uid = zoneToUiMapID[zoneID]
  local d = uid and mapData[uid]
  if not d then return nil, nil end
  return d[3] - d[1] * (x / 100), d[4] - d[2] * (y / 100)
end

local function WorldToContinent(worldX, worldY, continent)
  local d = mapData[continent == 1 and 1414 or 1415]
  if not d then return nil, nil end
  return (d[3] - worldX) / d[1], (d[4] - worldY) / d[2]
end

local function GetMapAreaID()
  if GetCurrentMapAreaID then
    local id = GetCurrentMapAreaID()
    if id and id > 0 then return id end
  end
end

local function CleanMapText(text)
  if not text or text == "" then return nil end
  text = tostring(text)
  text = string.gsub(text, "|c%x%x%x%x%x%x%x%x", "")
  text = string.gsub(text, "|r", "")
  text = string.gsub(text, "^%s+", "")
  text = string.gsub(text, "%s+$", "")
  if text == "" then return nil end
  return text
end

local function GetFrameText(frame)
  if type(frame) == "string" then frame = getglobal(frame) end
  if frame and frame.GetText then
    return CleanMapText(frame:GetText())
  end
end

local function GetMapContextTexts()
  return {
    GetFrameText("WorldMapContinentDropDownText"),
    GetFrameText("WorldMapZoneDropDownText"),
    GetFrameText("WorldMapZoneMinimapDropDownText"),
    GetFrameText(WorldMapFrameAreaLabel),
  }
end

local localizedZoneNamesAdded = false
local function AddLocalizedZoneNames()
  -- 幂等保护：Overrides.maps 在整个会话期间不变，只需执行一次
  if localizedZoneNamesAdded then return end
  if not EpochCN_Overrides or not EpochCN_Overrides.maps then
    localizedZoneNamesAdded = true
    return
  end
  localizedZoneNamesAdded = true
  for english, localized in pairs(EpochCN_Overrides.maps) do
    local id = zoneNameToID[english]
    if id and localized then zoneNameToID[localized] = id end
  end
end

local function ZoneIDFromMapAreaID(areaID)
  if not areaID then return nil end
  if zoneToUiMapID[areaID] then return areaID end
  for zoneID, uiMapID in pairs(zoneToUiMapID) do
    if uiMapID == areaID then return zoneID end
  end
end

local function GetSelectedZoneID()
  AddLocalizedZoneNames()

  local areaID = GetMapAreaID()
  local zoneID = ZoneIDFromMapAreaID(areaID)
  if zoneID then return zoneID end

  if GetMapInfo then
    local mapFile = GetMapInfo()
    if mapFile and mapFileToZoneID[mapFile] then return mapFileToZoneID[mapFile] end
  end

  if GetCurrentMapContinent and GetCurrentMapZone and GetMapZones then
    local continent = GetCurrentMapContinent()
    local zone = GetCurrentMapZone()
    if continent and zone and zone > 0 then
      local zones = { GetMapZones(continent) }
      local zoneName = zones[zone]
      if zoneName and zoneNameToID[zoneName] then return zoneNameToID[zoneName] end
    end
  end

  for _, text in ipairs(GetMapContextTexts()) do
    if text and zoneNameToID[text] then return zoneNameToID[text] end
  end
end

local function GetSelectedContinentID(selectedZoneID)
  if selectedZoneID and zoneContinent[selectedZoneID] then return zoneContinent[selectedZoneID] end

  if GetCurrentMapContinent then
    local continent = GetCurrentMapContinent()
    if continent and continent >= 1 and continent <= 2 then return continent end
  end

  local areaID = GetMapAreaID()
  if areaID == 1414 then return 1 end
  if areaID == 1415 then return 2 end

  if GetMapInfo then
    local mapFile = GetMapInfo()
    if mapFile and mapFileToContinentID[mapFile] and mapFileToContinentID[mapFile] > 0 then
      return mapFileToContinentID[mapFile]
    end
  end

  for _, text in ipairs(GetMapContextTexts()) do
    if text then
      if continentNameToID[text] then return continentNameToID[text] end
      if zoneNameToID[text] and zoneContinent[zoneNameToID[text]] then
        return zoneContinent[zoneNameToID[text]]
      end
    end
  end
end

local function BuildMapSignature()
  local parts = {
    tostring(GetMapAreaID() or 0),
    tostring(GetMapInfo and GetMapInfo() or ""),
  }

  for _, text in ipairs(GetMapContextTexts()) do
    table.insert(parts, tostring(text or ""))
  end

  return table.concat(parts, "|")
end

local function GetTrackingMode()
  local mode = EpochCNDB and EpochCNDB.worldMapTrackingMode
  if mode == "sync" or mode == "tracked" or mode == "manual" or mode == "off" then return mode end
  return "all"
end

local function IsMarkerTypeEnabled(markerType)
  local key = filterKeys[markerType]
  if not key then return true end
  return EpochCNDB[key] ~= false
end

local function GetManualSelection()
  EpochCNCharDB.worldMapManualSelection = EpochCNCharDB.worldMapManualSelection or {}
  return EpochCNCharDB.worldMapManualSelection
end

local function GetHiddenQuests()
  EpochCNCharDB.worldMapHiddenQuests = EpochCNCharDB.worldMapHiddenQuests or {}
  return EpochCNCharDB.worldMapHiddenQuests
end

local function GetMarkerName(marker)
  local kind, id = marker[4], marker[5]
  if EpochCN_MapNames and EpochCN_MapNames[kind] and EpochCN_MapNames[kind][id] then
    return EpochCN_MapNames[kind][id]
  end
  if kind == "U" and EpochCN.GetUnitData then
    local data = EpochCN:GetUnitData(id)
    if data and data[1] then return data[1] end
  elseif kind == "I" and EpochCN.GetItemData then
    local data = EpochCN:GetItemData(id)
    if data and data[1] then return data[1] end
  end
  return kind .. " " .. tostring(id)
end

local function MarkerTypeText(markerType)
  if markerType == "available" then return "可接任务" end
  if markerType == "start" then return "接取任务" end
  if markerType == "finish" then return "交还任务" end
  return "任务目标"
end

local function CountQuestIDs(questIDs)
  local count, last = 0, nil
  for questID in pairs(questIDs or {}) do
    count = count + 1
    last = questID
  end
  return count, last
end

local function GetInverseMapScale()
  local canvas = mapCanvas or WorldMapButton
  if not canvas or not canvas.GetEffectiveScale then return 1 end
  local scale = canvas:GetEffectiveScale()
  if not scale or scale <= 0 then return 1 end
  return 1 / scale
end

local function GetWorldMapCanvas()
  if mapCanvas and mapCanvas.IsShown and mapCanvas:IsShown() and mapCanvas.GetWidth and mapCanvas:GetWidth() and mapCanvas:GetWidth() > 0 then
    return mapCanvas
  end

  local candidates = {
    WorldMapButton,
    WorldMapDetailFrame,
    WorldMapFrameScrollFrameChild,
    WorldMapFrameScrollFrame,
    WorldMapFrame,
  }
  for _, frame in ipairs(candidates) do
    if frame and frame.GetWidth and frame.GetHeight then
      local width, height = frame:GetWidth() or 0, frame:GetHeight() or 0
      if width > 100 and height > 100 then
        mapCanvas = frame
        return frame
      end
    end
  end

  return WorldMapButton
end

local function GetPinSize(markerType)
  if markerType == "finish" then return pinSizes.finish end
  if markerType == "objective" then
    local size = tonumber(EpochCNDB.worldMapObjectivePinSize) or pinSizes.objective
    if size < 2 then size = 2 end
    if size > 3 then size = 3 end
    return size
  end
  local size = tonumber(EpochCNDB.worldMapPinSize) or pinSizes[markerType] or pinSizes.start
  return math.max(size, pinSizes[markerType] or pinSizes.start)
end

local function ApplyNodeAppearance(pin, markerType, scale, distance, edgeRadius)
  local size = GetPinSize(markerType) * (scale or 1)
  local visualSize = size
  if pin.clusterCount and pin.clusterCount > 1 then
    visualSize = markerType == "objective" and math.min(size + 0.5 * (scale or 1), 3.5 * (scale or 1)) or math.max(size, 22 * (scale or 1))
  end

  local color = pinColors[markerType] or pinColors.start
  if markerType == "objective" then
    color = { StableNodeColor(pin.sourceName or pin.questTitle) }
  end

  if markerType == "objective" then
    local hitSize = math.max(12 * (scale or 1), visualSize)
    pin:SetWidth(hitSize)
    pin:SetHeight(hitSize)
    pin.icon:Hide()
    if pin.dot then pin.dot:Hide() end
    pin.glow:Show()
    pin.glow:ClearAllPoints()
    pin.glow:SetPoint("CENTER", pin, "CENTER", 0, 0)
    pin.glow:SetWidth(visualSize + 2)
    pin.glow:SetHeight(visualSize + 2)
    pin.glow:SetTexture("Interface\\Buttons\\WHITE8X8")
    pin.glow:SetBlendMode("ADD")
    pin.glow:SetVertexColor(color[1], color[2], color[3], 0.18)
    pin.core:Show()
    pin.core:ClearAllPoints()
    pin.core:SetPoint("CENTER", pin, "CENTER", 0, 0)
    pin.core:SetWidth(visualSize)
    pin.core:SetHeight(visualSize)
    pin.core:SetTexture("Interface\\Buttons\\WHITE8X8")
    pin.core:SetBlendMode("ADD")
    pin.core:SetVertexColor(color[1], color[2], color[3], 0.85)
  else
    pin:SetWidth(visualSize)
    pin:SetHeight(visualSize)
    pin.glow:Hide()
    pin.core:Hide()
    if pin.dot then pin.dot:Hide() end
    pin.icon:Show()
    pin.icon:ClearAllPoints()
    pin.icon:SetAllPoints(pin)
    pin.icon:SetTexture(textures[markerType] or textures.available)
    pin.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    pin.icon:SetVertexColor(color[1], color[2], color[3])
  end

  if distance and edgeRadius and edgeRadius > 0 then
    local fadeIn = edgeRadius * 0.72
    local fadeOut = edgeRadius * 0.80
    local alpha = 1
    if distance > fadeIn then
      alpha = 1 - ((distance - fadeIn) / (fadeOut - fadeIn))
      if alpha < 0 then alpha = 0 end
      if alpha > 1 then alpha = 1 end
    end
    pin:SetAlpha(alpha)
  else
    pin:SetAlpha(1)
  end

  if pin.countText then
    pin.countText:SetText("")
    pin.countText:Hide()
  end
end

local function ApplyPinAppearance(pin, markerType)
  ApplyNodeAppearance(pin, markerType, GetInverseMapScale())
end

local function ApplyMinimapPinAppearance(pin, markerType)
  ApplyNodeAppearance(pin, markerType, 1)
end

local function GetSyncedTooltipLines(questIDs)
  if not EpochCN or not EpochCN.GetQuestSyncTooltipLines then return nil end
  return EpochCN:GetQuestSyncTooltipLines(questIDs)
end

-- 从任务日志读取指定 questID 的目标进度行
local function GetQuestLogProgress(questID)
  if not questID or not GetNumQuestLogEntries then return nil end
  local entries = GetNumQuestLogEntries()
  for i = 1, entries do
    local _, _, _, _, isHeader, _, _, _, rawID = EpochCN.raw.GetQuestLogTitle(i)
    if not isHeader then
      local resolvedID = EpochCN:GetQuestID(i, rawID)
      if resolvedID == questID then
        local objCount = GetNumQuestLeaderBoards and GetNumQuestLeaderBoards(i) or 0
        if objCount == 0 then return nil end
        local lines = {}
        for j = 1, objCount do
          local text, _, finished = EpochCN.raw.GetQuestLogLeaderBoard(j, i)
          if text and text ~= "" then
            if EpochCN.TranslateObjective then
              text = EpochCN:TranslateObjective(text) or text
            end
            table.insert(lines, { text = text, done = finished })
          end
        end
        return #lines > 0 and lines or nil
      end
    end
  end
  return nil
end

local function ShowPinTooltip(pin)
  if not pin or not pin:IsShown() then return end
  GameTooltip:SetOwner(pin, "ANCHOR_RIGHT")
  if pin.clusterCount and pin.clusterCount > 1 then
    GameTooltip:SetText(pin.questTitle or "任务地点", 1, .82, 0)
    GameTooltip:AddLine(string.format("%s：聚合了 %d 个标记", MarkerTypeText(pin.markerType), pin.clusterCount), .85, .85, .85, true)
    local shownTitles = {}
    for _, entry in ipairs(pin.entries or {}) do
      if not shownTitles[entry.questTitle] then
        shownTitles[entry.questTitle] = true
        GameTooltip:AddLine("- " .. (entry.questTitle or "未知任务"), .9, .9, .9, true)
      end
    end
    if pin.clusterCount > #(pin.entries or {}) then
      GameTooltip:AddLine(string.format("另有 %d 个标记未展开", pin.clusterCount - #(pin.entries or {})), .7, .7, .7)
    end
    if pin.sourceName and pin.sourceName ~= "" then
      GameTooltip:AddLine("主要来源: " .. pin.sourceName, .6, .8, 1, true)
    end
  else
    GameTooltip:SetText(pin.questTitle or "任务地点", 1, .82, 0)
    GameTooltip:AddLine(MarkerTypeText(pin.markerType) .. ": " .. (pin.sourceName or ""), .85, .85, .85, true)
    -- 显示任务目标进度（仅当任务已在日志中且为目标/交还类型标记时）
    if pin.markerType == "objective" or pin.markerType == "finish" then
      for questID in pairs(pin.questIDs or {}) do
        local progress = GetQuestLogProgress(questID)
        if progress then
          GameTooltip:AddLine(" ")
          GameTooltip:AddLine("任务进度:", 1, 0.9, 0.4)
          for _, obj in ipairs(progress) do
            local r, g, b = obj.done and 0.2 or 0.85, obj.done and 0.9 or 0.85, obj.done and 0.2 or 0.85
            GameTooltip:AddLine("  " .. obj.text, r, g, b, true)
          end
        end
      end
    end
    if pin.marker then
      GameTooltip:AddLine(string.format("坐标: %.1f, %.1f", pin.marker[1], pin.marker[2]), .6, .8, 1)
    end
  end
  local syncedLines = GetSyncedTooltipLines(pin.questIDs)
  if syncedLines and #syncedLines > 0 then
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine("队伍同步", .4, .9, 1)
    for _, line in ipairs(syncedLines) do
      GameTooltip:AddLine(line, .8, .9, 1, true)
    end
  end
  GameTooltip:AddLine("左键: 手动模式下切换任务", .7, 1, .8)
  GameTooltip:AddLine("Shift+左键: 隐藏该任务标记", .7, 1, .8)
  GameTooltip:AddLine("右键: 打开地图标记菜单", .7, 1, .8)
  GameTooltip:Show()
end

local function IsCursorOverFrame(frame)
  if not frame or not frame:IsShown() then return false end
  local x, y = GetCursorPosition()
  local scale = frame:GetEffectiveScale() or 1
  x = x / scale
  y = y / scale

  local left, right, top, bottom = frame:GetLeft(), frame:GetRight(), frame:GetTop(), frame:GetBottom()
  return left and right and top and bottom and x >= left and x <= right and y >= bottom and y <= top
end

local function PollPinTooltip(list, count)
  for i = 1, count do
    local pin = list[i]
    if IsCursorOverFrame(pin) then
      return pin
    end
  end
end

local function UpdateHoveredPinTooltip()
  local pin
  if WorldMapFrame and WorldMapFrame:IsShown() then
    pin = PollPinTooltip(pins, visibleWorldMapPins)
  end
  if not pin and Minimap then
    pin = PollPinTooltip(minimapPins, visibleMinimapPins)
  end

  if pin ~= hoverPin then
    if hoverPin then GameTooltip:Hide() end
    hoverPin = pin
    if hoverPin then ShowPinTooltip(hoverPin) end
  elseif hoverPin and GameTooltip and not GameTooltip:IsShown() then
    ShowPinTooltip(hoverPin)
  end
end

local function CreatePin(index)
  if not pins[index] then
    local pin = CreateFrame("Button", "EpochCNWorldMapPin" .. index, GetWorldMapCanvas() or WorldMapButton or WorldMapFrame)
    pin:SetWidth(18)
    pin:SetHeight(18)
    local parent = pin:GetParent()
    pin:SetFrameLevel((parent and parent.GetFrameLevel and parent:GetFrameLevel() or 1) + 50)
    pin:SetFrameStrata("DIALOG")
    pin:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    pin.glow = pin:CreateTexture(nil, "BORDER")
    pin.glow:Hide()
    pin.icon = pin:CreateTexture(nil, "OVERLAY")
    pin.icon:SetAllPoints(pin)
    pin.core = pin:CreateTexture(nil, "OVERLAY")
    pin.core:Hide()
    pin.dot = pin:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    pin.dot:Hide()
    pin.countText = pin:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    pin.countText:SetPoint("BOTTOMRIGHT", pin, "BOTTOMRIGHT", 3, -2)
    pin.countText:SetTextColor(1, 0.95, 0.3)
    pin.countText:Hide()
    pin:EnableMouse(true)
    pin:SetScript("OnEnter", ShowPinTooltip)
    pin:SetScript("OnLeave", function() GameTooltip:Hide() end)
    pins[index] = pin
  end
  local canvas = GetWorldMapCanvas()
  if canvas and pins[index]:GetParent() ~= canvas then
    pins[index]:SetParent(canvas)
    pins[index]:SetFrameLevel((canvas.GetFrameLevel and canvas:GetFrameLevel() or 1) + 50)
  end
  return pins[index]
end

local function HidePins()
  if hoverPin then
    hoverPin = nil
    GameTooltip:Hide()
  end
  for i = 1, maxPins do
    if pins[i] then
      pins[i]:ClearAllPoints()
      if WorldMapButton then
        pins[i]:SetParent(WorldMapButton)
        pins[i]:SetPoint("CENTER", WorldMapButton, "TOPLEFT", -1000, 1000)
      end
      pins[i]:Hide()
    end
  end
  visibleWorldMapPins = 0
end

local function CreateMinimapPin(index)
  if not minimapPins[index] then
    local pin = CreateFrame("Frame", nil, Minimap)
    pin:SetFrameLevel((Minimap.GetFrameLevel and Minimap:GetFrameLevel() or 1) + 50)
    pin:SetFrameStrata("HIGH")
    pin.glow = pin:CreateTexture(nil, "BORDER")
    pin.glow:Hide()
    pin.icon = pin:CreateTexture(nil, "OVERLAY")
    pin.icon:SetAllPoints(pin)
    pin.core = pin:CreateTexture(nil, "OVERLAY")
    pin.core:Hide()
    pin.dot = pin:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    pin.dot:Hide()
    pin:EnableMouse(true)
    pin:SetScript("OnEnter", ShowPinTooltip)
    pin:SetScript("OnLeave", function() GameTooltip:Hide() end)
    minimapPins[index] = pin
  end
  minimapPins[index]:SetParent(Minimap)
  minimapPins[index]:SetFrameLevel((Minimap.GetFrameLevel and Minimap:GetFrameLevel() or 1) + 50)
  return minimapPins[index]
end

local function HideMinimapPins()
  if hoverPin then
    hoverPin = nil
    GameTooltip:Hide()
  end
  for i = 1, maxMinimapPins do
    if minimapPins[i] then
      minimapPins[i]:ClearAllPoints()
      minimapPins[i]:SetParent(Minimap)
      minimapPins[i]:SetPoint("CENTER", Minimap, "CENTER", 0, 0)
      minimapPins[i]:Hide()
    end
  end
  visibleMinimapPins = 0
end

local function MarkerInMapScope(marker, continent, zone, selectedZoneID)
  local markerZone = marker and marker[3]
  if not markerZone then return false end
  if zone and zone > 0 then return selectedZoneID and markerZone == selectedZoneID end
  if continent == 0 then return true end
  return zoneContinent[markerZone] == continent
end

local function MarkerToMapXY(marker, continent, zone)
  local x, y, markerZone = marker[1], marker[2], marker[3]

  if zone and zone > 0 then
    local currentZoneID = GetSelectedZoneID()
    if currentZoneID and markerZone == currentZoneID then
      return x / 100, y / 100
    end
    return nil, nil
  end

  if continent == 0 then
    local markerContinent = zoneContinent[markerZone]
    local wx, wy = ZoneToWorld(x, y, markerZone)
    if not wx or not markerContinent then return nil, nil end
    local cx, cy = WorldToContinent(wx, wy, markerContinent)
    if not cx or cx < 0 or cx > 1 or cy < 0 or cy > 1 then return nil, nil end
    if markerContinent == 1 then
      return cx * 0.90 - 0.22, cy * 0.85 + 0.05
    end
    return 0.33 + (cx * 0.90), cy * 0.90 - 0.04
  end

  if continent < 1 or continent > 2 or zoneContinent[markerZone] ~= continent then return nil, nil end
  local wx, wy = ZoneToWorld(x, y, markerZone)
  if not wx then return nil, nil end
  return WorldToContinent(wx, wy, continent)
end

local function AddMarkers(list, questID, questTitle, markerType, out)
  for _, marker in ipairs(list or {}) do
    table.insert(out, {
      marker = marker,
      questID = questID,
      questTitle = questTitle,
      markerType = markerType,
      sourceName = GetMarkerName(marker),
      priority = markerPriority[markerType] or 0,
    })
  end
end

local function AddMarkersInScope(list, questID, questTitle, markerType, out, scope)
  for _, marker in ipairs(list or {}) do
    if not scope or not scope.minimap or MarkerInMapScope(marker, scope.continent, scope.zone, scope.selectedZoneID) then
      table.insert(out, {
        marker = marker,
        questID = questID,
        questTitle = questTitle,
        markerType = markerType,
        sourceName = GetMarkerName(marker),
        priority = markerPriority[markerType] or 0,
      })
    end
  end
end

local function GetCompletedQuests()
  EpochCNCharDB.completedQuests = EpochCNCharDB.completedQuests or {}
  return EpochCNCharDB.completedQuests
end

local function IsQuestCompleted(questID)
  if not questID then return false end
  local completed = EpochCNCharDB and EpochCNCharDB.completedQuests
  if completed and completed[questID] then return true end
  if pfQuest_history and pfQuest_history[questID] then return true end
  return false
end

local function IsQuestActive(active, questID)
  return active and questID and active[questID]
end

local function AllObjectivesFinished(questLogIndex)
  local objectives = GetNumQuestLeaderBoards and GetNumQuestLeaderBoards(questLogIndex) or 0
  if objectives == 0 then return true end
  for objectiveIndex = 1, objectives do
    local _, _, finished = EpochCN.raw.GetQuestLogLeaderBoard(objectiveIndex, questLogIndex)
    if not finished then return false end
  end
  return true
end

local function PlayerRaceBit()
  local _, race = UnitRace("player")
  local faction = UnitFactionGroup("player")
  return raceBits[race] or (faction == "Alliance" and 77 or 178)
end

local function PlayerClassBit()
  local _, class = UnitClass("player")
  return classBits[class] or 0
end

local function PlayerHasSkill(skillID)
  if not skillID or not GetNumSkillLines or not GetSkillLineInfo then return true end
  return true
end

local function HasPrerequisite(quest)
  if not quest.p or #(quest.p) == 0 then return true end
  for _, prequest in ipairs(quest.p) do
    if IsQuestCompleted(prequest) then return true end
  end
  return false
end

-- playerInfo 缓存结构：{ level, raceBit, classBit, highRange, lowRange, hideLow }
-- 在 CollectMapMarkers 中一次性计算，避免每个任务重复调用 API
local function IsQuestEligible(questID, quest, active, playerInfo)
  if not quest or IsQuestActive(active, questID) or IsQuestCompleted(questID) then return false end
  if not quest.s or #(quest.s) == 0 then return false end

  local plevel = playerInfo.level

  -- 高等级过滤
  if quest.m and quest.m > plevel + playerInfo.highRange then return false end

  -- 低等级过滤
  if playerInfo.hideLow then
    if quest.l and quest.l < plevel - playerInfo.lowRange then return false end
  end

  -- 不可接：最低接取等级高于角色等级
  if quest.m and quest.m > plevel then return false end

  if quest.r and Band(quest.r, playerInfo.raceBit) ~= playerInfo.raceBit then return false end
  if quest.c and Band(quest.c, playerInfo.classBit) ~= playerInfo.classBit then return false end
  if quest.sk and not PlayerHasSkill(quest.sk) then return false end
  if quest.ev then return false end
  if not HasPrerequisite(quest) then return false end

  return true
end

local function GetQuestTitle(E, questID, fallback)
  local data = E:GetQuestData(questID)
  return (data and data[1]) or fallback or (EpochCN_MapData[questID] and EpochCN_MapData[questID].t) or ("任务 " .. tostring(questID))
end

local function CollectQuestState(E)
  local state = { active = {}, watched = {}, complete = {} }
  local entries = GetNumQuestLogEntries and GetNumQuestLogEntries() or 0
  for i = 1, entries do
    local _, _, _, _, isHeader, _, complete, _, questID = E.raw.GetQuestLogTitle(i)
    if not isHeader then
      questID = E:GetQuestID(i, questID)
      if questID then
        state.active[questID] = true
        if IsQuestWatched and IsQuestWatched(i) then state.watched[questID] = true end
        if complete == true or complete == 1 or AllObjectivesFinished(i) then
          state.complete[questID] = true
        end
      end
    end
  end
  return state
end

local function ShouldShowQuest(questID, state)
  if not questID or GetHiddenQuests()[questID] then return false end
  local mode = GetTrackingMode()
  if mode == "off" then return false end
  if mode == "sync" then return state.active[questID] == true or state.watched[questID] == true end
  if mode == "tracked" then return state.watched[questID] == true end
  if mode == "manual" then return GetManualSelection()[questID] == true end
  return true
end

local function ClusterMarkers(markers, continent, zone)
  local clusters, ordered = {}, {}
  local radius = tonumber(EpochCNDB.worldMapClusterRadius) or 0.018
  if radius < 0.005 then radius = 0.005 end
  if radius > 0.05 then radius = 0.05 end

  for _, data in ipairs(markers) do
    local mx, my = MarkerToMapXY(data.marker, continent, zone)
    if mx and my and mx >= 0 and mx <= 1 and my >= 0 and my <= 1 then
      local bucketX = math.floor(mx / radius)
      local bucketY = math.floor(my / radius)
      local key = data.markerType .. ":" .. tostring(bucketX) .. ":" .. tostring(bucketY)
      local cluster = clusters[key]
      if not cluster then
        cluster = {
          mx = mx,
          my = my,
          count = 0,
          entries = {},
          markerType = data.markerType,
          questTitle = data.questTitle,
          sourceName = data.sourceName,
          questIDs = {},
          marker = data.marker,
          priority = data.priority or 0,
        }
        clusters[key] = cluster
        table.insert(ordered, cluster)
      else
        local nextCount = cluster.count + 1
        cluster.mx = ((cluster.mx * cluster.count) + mx) / nextCount
        cluster.my = ((cluster.my * cluster.count) + my) / nextCount
        if (data.priority or 0) >= (cluster.priority or 0) then
          cluster.questTitle = data.questTitle
          cluster.sourceName = data.sourceName
          cluster.marker = data.marker
          cluster.priority = data.priority or 0
        end
      end

      cluster.count = cluster.count + 1
      cluster.questIDs[data.questID] = true
      if #cluster.entries < 6 then
        table.insert(cluster.entries, data)
      end
    end
  end

  table.sort(ordered, function(a, b)
    if (a.priority or 0) == (b.priority or 0) then
      return (a.count or 0) > (b.count or 0)
    end
    return (a.priority or 0) > (b.priority or 0)
  end)

  return ordered
end

local function UpdateMenuButtonText()
  if not menuButton then return end
  local text
  if not EpochCNDB.worldMapPins or GetTrackingMode() == "off" then
    text = "任务:关"
  else
    text = "任务:" .. (trackingModeShortText[GetTrackingMode()] or "全")
  end
  menuButton:SetText(text)
end

local function RequestRefresh()
  refreshPending = true
  refreshTimer = 0
  refreshVersion = refreshVersion + 1
  mapCacheKey = nil
  mapCacheMarkers = nil
  minimapCacheKey = nil
  minimapCacheMarkers = nil
end

local function SetTrackingMode(mode)
  EpochCNDB.worldMapTrackingMode = mode
  UpdateMenuButtonText()
  RequestRefresh()
  Print("世界地图标记模式已切换为：" .. (trackingModeText[mode] or trackingModeText.all))
end

local function ToggleManualQuest(questID)
  if not questID then return end
  local manual = GetManualSelection()
  manual[questID] = not manual[questID] or nil
  RequestRefresh()
  Print(string.format("任务 %d 已%s手动列表", questID, manual[questID] and "加入" or "移出"))
end

local function HideQuestPins(questIDs)
  local hidden = GetHiddenQuests()
  local count = 0
  for questID in pairs(questIDs or {}) do
    hidden[questID] = true
    count = count + 1
  end
  if count > 0 then
    RequestRefresh()
    Print(string.format("已隐藏 %d 个任务的世界地图标记", count))
  end
end

local function ClearHiddenQuests()
  EpochCNCharDB.worldMapHiddenQuests = {}
  RequestRefresh()
  Print("已清空隐藏任务标记列表")
end

local function ClearManualSelection()
  EpochCNCharDB.worldMapManualSelection = {}
  RequestRefresh()
  Print("已清空手动选择任务列表")
end

local function CreateMenuEntries()
  local entries = {
    { text = "EpochCN 任务标记", isTitle = 1, notCheckable = 1 },
    {
      text = "启用世界地图标记",
      checked = EpochCNDB.worldMapPins,
      keepShownOnClick = 1,
      func = function()
        EpochCNDB.worldMapPins = not EpochCNDB.worldMapPins
        UpdateMenuButtonText()
        RequestRefresh()
      end,
    },
    { text = "追踪模式", isTitle = 1, notCheckable = 1 },
  }

  for _, mode in ipairs({ "all", "sync", "tracked", "manual", "off" }) do
    table.insert(entries, {
      text = trackingModeText[mode],
      checked = GetTrackingMode() == mode,
      func = function() SetTrackingMode(mode) end,
    })
  end

  table.insert(entries, { text = "标记类型", isTitle = 1, notCheckable = 1 })
  for _, markerType in ipairs({ "objective", "finish", "available", "start" }) do
    table.insert(entries, {
      text = MarkerTypeText(markerType),
      checked = IsMarkerTypeEnabled(markerType),
      keepShownOnClick = 1,
      func = function()
        local key = filterKeys[markerType]
        EpochCNDB[key] = not EpochCNDB[key]
        RequestRefresh()
      end,
    })
  end

  table.insert(entries, {
    text = "清空手动选择",
    notCheckable = 1,
    func = ClearManualSelection,
  })
  table.insert(entries, {
    text = "清空隐藏任务",
    notCheckable = 1,
    func = ClearHiddenQuests,
  })
  table.insert(entries, {
    text = "立即刷新",
    notCheckable = 1,
    func = RequestRefresh,
  })

  return entries
end

local function ShowMapMenu(anchor)
  if not menuFrame then return end
  EasyMenu(CreateMenuEntries(), menuFrame, anchor or "cursor", 0, 0, "MENU", 2)
end

local function HandlePinClick(pin, button)
  if button == "RightButton" then
    ShowMapMenu(pin)
    return
  end

  if IsShiftKeyDown() then
    HideQuestPins(pin.questIDs)
    return
  end

  if GetTrackingMode() ~= "manual" then return end

  local count, questID = CountQuestIDs(pin.questIDs)
  if count ~= 1 then
    Print("该聚合标记包含多个任务，请缩放或切换区域后再选择。")
    return
  end

  ToggleManualQuest(questID)
end

local function CreateMenuButton()
  if menuButton or not WorldMapFrame then return end
  menuButton = CreateFrame("Button", "EpochCNWorldMapMenuButton", WorldMapFrame, "UIPanelButtonTemplate")
  menuButton:SetWidth(72)
  menuButton:SetHeight(20)
  menuButton:SetPoint("TOPRIGHT", WorldMapFrame, "TOPRIGHT", -92, -34)
  menuButton:SetScript("OnClick", function(self) ShowMapMenu(self) end)
  UpdateMenuButtonText()
end

local function GetSelectedQuestLogQuestID()
  if not GetQuestLogSelection then return nil end
  local index = GetQuestLogSelection()
  if not index or index <= 0 then return nil end
  local _, _, _, _, isHeader, _, _, _, questID = EpochCN.raw.GetQuestLogTitle(index)
  if isHeader then return nil end
  return EpochCN:GetQuestID(index, questID)
end

local function HandleSlashCommand(msg)
  local command, rest = string.match(msg or "", "^(%S*)%s*(.-)$")
  command = string.lower(command or "")
  rest = string.lower(rest or "")

  if command == "" or command == "help" then
    Print("/ecmap mode all|sync|tracked|manual|off")
    Print("/ecmap toggle")
    Print("/ecmap show objective|finish|available|start")
    Print("/ecmap hide objective|finish|available|start")
    Print("/ecmap quest <id|current>")
    Print("/ecmap clear hidden|manual")
    return
  end

  if command == "mode" then
    if trackingModeText[rest] then
      SetTrackingMode(rest)
    else
      Print("可用模式：all、sync、tracked、manual、off")
    end
    return
  end

  if command == "toggle" then
    EpochCNDB.worldMapPins = not EpochCNDB.worldMapPins
    UpdateMenuButtonText()
    RequestRefresh()
    Print("世界地图标记已" .. (EpochCNDB.worldMapPins and "开启" or "关闭"))
    return
  end

  if command == "show" or command == "hide" then
    if filterKeys[rest] then
      EpochCNDB[filterKeys[rest]] = command == "show"
      RequestRefresh()
      Print(string.format("%s %s 标记", command == "show" and "显示" or "隐藏", MarkerTypeText(rest)))
    else
      Print("可用类型：objective、finish、available、start")
    end
    return
  end

  if command == "clear" then
    if rest == "hidden" then
      ClearHiddenQuests()
    elseif rest == "manual" then
      ClearManualSelection()
    else
      Print("可清空的列表：hidden、manual")
    end
    return
  end

  if command == "quest" then
    local questID = rest == "current" and GetSelectedQuestLogQuestID() or tonumber(rest)
    if questID then
      ToggleManualQuest(questID)
    else
      Print("请输入有效任务 ID，或使用 /ecmap quest current")
    end
    return
  end

  if command == "menu" then
    ShowMapMenu(menuButton or "cursor")
    return
  end

  if command == "debug" then
    EpochCN:UpdateWorldMapPins()
    PrintMapDebug()
    return
  end

  Print("未知命令，输入 /ecmap help 查看帮助")
end

function EpochCN:CollectMapMarkers(scope)
  local results = {}
  local state = CollectQuestState(self)
  local seen = {}
  local entries = GetNumQuestLogEntries and GetNumQuestLogEntries() or 0
  local mode = GetTrackingMode()
  local minimapOnly = scope and scope.minimap

  for i = 1, entries do
    local title, _, _, _, isHeader, _, complete, _, questID = self.raw.GetQuestLogTitle(i)
    if not isHeader then
      questID = self:GetQuestID(i, questID)
      local quest = questID and EpochCN_MapData[questID]
      if quest and (minimapOnly or ShouldShowQuest(questID, state)) then
        seen[questID] = true
        local questTitle = GetQuestTitle(self, questID, title)
        local isComplete = complete == true or complete == 1 or state.complete[questID]
        if isComplete then
          if IsMarkerTypeEnabled("finish") then
            AddMarkersInScope(quest.e, questID, questTitle, "finish", results, scope)
          end
          if #(quest.e or {}) == 0 and IsMarkerTypeEnabled("start") then
            AddMarkersInScope(quest.s, questID, questTitle, "start", results, scope)
          end
        else
          if #(quest.o or {}) > 0 then
            if IsMarkerTypeEnabled("objective") then
              AddMarkersInScope(quest.o, questID, questTitle, "objective", results, scope)
            end
          elseif #(quest.e or {}) > 0 then
            if IsMarkerTypeEnabled("objective") then
              AddMarkersInScope(quest.e, questID, questTitle, "objective", results, scope)
            end
          elseif IsMarkerTypeEnabled("objective") then
            AddMarkersInScope(quest.s, questID, questTitle, "objective", results, scope)
          end
        end
      end
    end
  end

  if not minimapOnly and mode ~= "sync" and EpochCNDB.availableQuestPins and IsMarkerTypeEnabled("available") then
    -- 缓存玩家信息，避免在循环中重复调用 API
    local playerInfo = {
      level = UnitLevel("player") or 1,
      raceBit = PlayerRaceBit(),
      classBit = PlayerClassBit(),
      highRange = tonumber(EpochCNDB.availableQuestLevelRange) or 3,
      lowRange = tonumber(EpochCNDB.availableQuestLowLevelRange) or 4,
      hideLow = EpochCNDB.hideLowLevelAvailableQuestPins ~= false,
    }
    for questID, quest in pairs(EpochCN_MapData) do
      if IsQuestEligible(questID, quest, state.active, playerInfo) and ShouldShowQuest(questID, state) then
        seen[questID] = true
        AddMarkersInScope(quest.s, questID, GetQuestTitle(self, questID, quest.t), "available", results, scope)
      end
    end
  end

  if not minimapOnly and mode == "sync" and self.GetSyncedQuestIDs then
    for questID in pairs(self:GetSyncedQuestIDs()) do
      if not seen[questID] and not GetHiddenQuests()[questID] and not IsQuestCompleted(questID) then
        local quest = EpochCN_MapData[questID]
        if quest then
          local questTitle = GetQuestTitle(self, questID, quest.t)
          if self.IsSyncedQuestComplete and self:IsSyncedQuestComplete(questID) then
            if IsMarkerTypeEnabled("finish") then
              AddMarkersInScope(#(quest.e or {}) > 0 and quest.e or quest.s, questID, questTitle, "finish", results, scope)
            end
          elseif IsMarkerTypeEnabled("objective") then
            if #(quest.o or {}) > 0 then
              AddMarkersInScope(quest.o, questID, questTitle, "objective", results, scope)
            elseif #(quest.e or {}) > 0 then
              AddMarkersInScope(quest.e, questID, questTitle, "objective", results, scope)
            else
              AddMarkersInScope(quest.s, questID, questTitle, "objective", results, scope)
            end
          end
        end
      end
    end
  end

  if not minimapOnly and mode == "manual" and IsMarkerTypeEnabled("start") then
    for questID in pairs(GetManualSelection()) do
      if not seen[questID] and not GetHiddenQuests()[questID] and not IsQuestCompleted(questID) then
        local quest = EpochCN_MapData[questID]
        if quest then
          AddMarkersInScope(quest.s, questID, GetQuestTitle(self, questID, quest.t), "start", results, scope)
        end
      end
    end
  end

  return results
end

function EpochCN:UpdateWorldMapPins()
  CreateMenuButton()
  UpdateMenuButtonText()

  local canvas = GetWorldMapCanvas()
  HidePins()
  if not EpochCNDB.worldMap or not canvas or not WorldMapFrame or not WorldMapFrame:IsShown() then return end

  if not EpochCNDB.worldMapPins or GetTrackingMode() == "off" then return end

  local continent = GetCurrentMapContinent and GetCurrentMapContinent() or 0
  local zone = GetCurrentMapZone and GetCurrentMapZone() or 0
  local selectedZoneID = GetSelectedZoneID()
  local cacheKey = BuildMapSignature() .. ":" .. tostring(continent) .. ":" .. tostring(zone) .. ":" .. tostring(selectedZoneID) .. ":" .. tostring(GetTrackingMode())
  local markers
  if mapCacheKey == cacheKey and mapCacheMarkers then
    markers = mapCacheMarkers
  else
    markers = self:CollectMapMarkers({ continent = continent, zone = zone, selectedZoneID = selectedZoneID })
    mapCacheKey = cacheKey
    mapCacheMarkers = markers
  end
  local clusters = ClusterMarkers(markers, continent, zone)
  lastDebug = {
    continent = continent,
    zone = zone,
    selectedZoneID = selectedZoneID,
    markers = #(markers or {}),
    clusters = #(clusters or {}),
    canvas = canvas.GetName and canvas:GetName() or tostring(canvas),
    width = canvas.GetWidth and canvas:GetWidth() or 0,
    height = canvas.GetHeight and canvas:GetHeight() or 0,
  }

  for index, cluster in ipairs(clusters) do
    if index > maxPins then break end
    local pin = CreatePin(index)
    pin.marker = cluster.marker
    pin.questTitle = cluster.questTitle
    pin.markerType = cluster.markerType
    pin.sourceName = cluster.sourceName
    pin.entries = cluster.entries
    pin.questIDs = cluster.questIDs
    pin.clusterCount = cluster.count
    ApplyPinAppearance(pin, cluster.markerType)
    pin:SetScript("OnClick", HandlePinClick)
    pin:ClearAllPoints()
    pin:SetPoint("CENTER", canvas, "TOPLEFT", cluster.mx * canvas:GetWidth(), -cluster.my * canvas:GetHeight())
    pin:Show()
  end
  -- 精确记录世界地图可见 pin 数量（供 PollPinTooltip 限定遍历范围，避免遍历 300 个 slot）
  visibleWorldMapPins = math.min(#clusters, maxPins)
end

PrintMapDebug = function()
  Print("worldMap=" .. tostring(EpochCNDB.worldMap) .. " worldMapPins=" .. tostring(EpochCNDB.worldMapPins) .. " mode=" .. tostring(GetTrackingMode()))
  Print("map continent=" .. tostring(lastDebug.continent) .. " zone=" .. tostring(lastDebug.zone) .. " selectedZoneID=" .. tostring(lastDebug.selectedZoneID))
  Print("markers=" .. tostring(lastDebug.markers) .. " clusters=" .. tostring(lastDebug.clusters) .. " canvas=" .. tostring(lastDebug.canvas) .. " size=" .. tostring(lastDebug.width) .. "x" .. tostring(lastDebug.height))
  Print("minimap reason=" .. tostring(lastMinimapDebug.reason) .. " zoneID=" .. tostring(lastMinimapDebug.zoneID) .. " raw=" .. tostring(lastMinimapDebug.rawX) .. "," .. tostring(lastMinimapDebug.rawY) .. " markers=" .. tostring(lastMinimapDebug.markers) .. " sameZone=" .. tostring(lastMinimapDebug.sameZone) .. " shown=" .. tostring(lastMinimapDebug.shown) .. " zoom=" .. tostring(lastMinimapDebug.zoom) .. " size=" .. tostring(lastMinimapDebug.size))
  if lastMinimapDebug.realZone or lastMinimapDebug.zoneText or lastMinimapDebug.minimapZone then
    Print("minimap zones real=" .. tostring(lastMinimapDebug.realZone) .. " zone=" .. tostring(lastMinimapDebug.zoneText) .. " mini=" .. tostring(lastMinimapDebug.minimapZone))
  end
  Print("WorldMapFrame shown=" .. tostring(WorldMapFrame and WorldMapFrame:IsShown()) .. " WorldMapButton=" .. tostring(WorldMapButton and WorldMapButton:GetWidth()) .. "x" .. tostring(WorldMapButton and WorldMapButton:GetHeight()))
end

local function GetZoneIDByName(name)
  AddLocalizedZoneNames()
  name = CleanMapText(name)
  return name and (zoneNameToID[name] or subZoneNameToID[name])
end

local function GetCurrentMapZoneID()
  local areaID = GetMapAreaID()
  local zoneID = ZoneIDFromMapAreaID(areaID)
  if zoneID then return zoneID end

  if GetCurrentMapContinent and GetCurrentMapZone and GetMapZones then
    local continent = GetCurrentMapContinent()
    local zone = GetCurrentMapZone()
    if continent and zone and zone > 0 then
      local zones = { GetMapZones(continent) }
      return GetZoneIDByName(zones[zone])
    end
  end
end

local function RefreshCurrentZoneMap()
  if SetMapToCurrentZone and (not WorldMapFrame or not WorldMapFrame:IsShown()) then
    SetMapToCurrentZone()
  end
end

local function GetCurrentPlayerMapContext()
  RefreshCurrentZoneMap()
  local zoneID = GetZoneIDByName(GetRealZoneText and GetRealZoneText()) or GetZoneIDByName(GetZoneText and GetZoneText())
  local x, y
  if GetPlayerMapPosition then
    x, y = GetPlayerMapPosition("player")
  end

  if not zoneID or zoneID == 0 then
    zoneID = GetZoneIDByName(GetMinimapZoneText and GetMinimapZoneText()) or GetCurrentMapZoneID() or GetSelectedZoneID()
  end

  if not zoneID or zoneID == 0 or not x or not y or x <= 0 or y <= 0 then
    return nil, x, y, zoneID
  end
  return zoneID, x * 100, y * 100
end

local function GetMinimapZoomYards()
  local zoom = Minimap and Minimap.GetZoom and Minimap:GetZoom() or tonumber(GetCVar and GetCVar("minimapZoom")) or 3
  if zoom < 0 then zoom = 0 end
  if zoom > 5 then zoom = 5 end

  local inside = false
  if GetCVar then
    inside = tostring(GetCVar("minimapZoom")) == tostring(GetCVar("minimapInsideZoom"))
  end

  local tableName = inside and "indoor" or "outdoor"
  return minimapZoomYards[tableName][zoom] or minimapZoomYards.outdoor[3]
end

function EpochCN:UpdateMinimapQuestPins()
  if not EpochCNDB.minimapQuestPins or not Minimap then
    HideMinimapPins()
    return
  end

  local zoneID, playerX, playerY, rawZoneID = GetCurrentPlayerMapContext()
  if not zoneID then
    lastMinimapDebug = {
      reason = "no player map context",
      zoneID = rawZoneID,
      rawX = playerX,
      rawY = playerY,
      realZone = GetRealZoneText and GetRealZoneText(),
      zoneText = GetZoneText and GetZoneText(),
      minimapZone = GetMinimapZoneText and GetMinimapZoneText(),
    }
    HideMinimapPins()
    return
  end

  local d = mapData[zoneToUiMapID[zoneID] or zoneID]
  if not d then
    lastMinimapDebug = { reason = "missing map data", zoneID = zoneID }
    HideMinimapPins()
    return
  end

  local minimapKey = tostring(zoneID)
    .. ":" .. tostring(refreshVersion)
    .. ":" .. tostring(EpochCNDB.minimapQuestObjectivesOnly)
    .. ":" .. tostring(GetTrackingMode())
    .. ":" .. tostring(EpochCNDB.worldMapShowObjectivePins)
    .. ":" .. tostring(EpochCNDB.worldMapShowFinishPins)
  local markers
  if minimapCacheKey == minimapKey and minimapCacheMarkers then
    markers = minimapCacheMarkers
  else
    markers = self:CollectMapMarkers({ continent = zoneContinent[zoneID] or 0, zone = 1, selectedZoneID = zoneID, minimap = true })
    table.sort(markers, function(a, b)
      return (a.priority or 0) > (b.priority or 0)
    end)
    minimapCacheKey = minimapKey
    minimapCacheMarkers = markers
  end

  local mapZoom = GetMinimapZoomYards()
  local minimapWidth = Minimap.GetWidth and Minimap:GetWidth() or 140
  local minimapHeight = Minimap.GetHeight and Minimap:GetHeight() or minimapWidth
  if not minimapWidth or minimapWidth < 30 then minimapWidth = 140 end
  if not minimapHeight or minimapHeight < 30 then minimapHeight = minimapWidth end
  local xDraw = minimapWidth / (mapZoom / d[1]) / 100
  local yDraw = minimapHeight / (mapZoom / d[2]) / 100
  local displayRadius = math.min(minimapWidth, minimapHeight) / 2
  local shown = 0
  local sameZone = 0
  for _, data in ipairs(markers) do
    if shown >= maxMinimapPins then break end
    if not EpochCNDB.minimapQuestObjectivesOnly or data.markerType == "objective" or data.markerType == "finish" then
      local marker = data.marker
      if marker and marker[3] == zoneID then
        sameZone = sameZone + 1
        local xPos = (marker[1] - playerX) * xDraw
        local yPos = (marker[2] - playerY) * yDraw
        local distance = math.sqrt((xPos * xPos) + (yPos * yPos))
        if distance <= displayRadius - 5 then
          shown = shown + 1
          local pin = CreateMinimapPin(shown)
          pin.marker = marker
          pin.questTitle = data.questTitle
          pin.markerType = data.markerType
          pin.sourceName = data.sourceName
          pin.entries = { data }
          pin.questIDs = { [data.questID] = true }
          pin.clusterCount = 1
          ApplyNodeAppearance(pin, data.markerType, 1, distance, displayRadius)
          pin:ClearAllPoints()
          pin:SetPoint("CENTER", Minimap, "CENTER", xPos, -yPos)
          pin:Show()
        end
      end
    end
  end

  lastMinimapDebug = {
    reason = "ok",
    zoneID = zoneID,
    rawX = playerX and (playerX / 100),
    rawY = playerY and (playerY / 100),
    playerX = playerX,
    playerY = playerY,
    markers = #(markers or {}),
    sameZone = sameZone,
    shown = shown,
    zoom = mapZoom,
    size = tostring(minimapWidth) .. "x" .. tostring(minimapHeight),
  }

  for i = shown + 1, maxMinimapPins do
    if minimapPins[i] then minimapPins[i]:Hide() end
  end
  -- 精确记录小地图可见 pin 数量（供 PollPinTooltip 限定遍历范围）
  visibleMinimapPins = shown
end

function EpochCN:InitWorldMap()
  if moduleFrame then return end

  menuFrame = CreateFrame("Frame", "EpochCNWorldMapMenuFrame", UIParent, "UIDropDownMenuTemplate")

  moduleFrame = CreateFrame("Frame")
  moduleFrame:RegisterEvent("WORLD_MAP_UPDATE")
  moduleFrame:RegisterEvent("QUEST_LOG_UPDATE")
  moduleFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
  moduleFrame:RegisterEvent("ZONE_CHANGED")
  moduleFrame:RegisterEvent("ZONE_CHANGED_NEW_AREA")
  moduleFrame:RegisterEvent("MINIMAP_ZONE_CHANGED")
  moduleFrame:RegisterEvent("QUEST_TURNED_IN")
  moduleFrame:RegisterEvent("QUEST_WATCH_UPDATE")
  moduleFrame:RegisterEvent("QUEST_WATCH_LIST_CHANGED")
  moduleFrame:SetScript("OnEvent", function(_, event, questID)
    if event == "QUEST_TURNED_IN" and questID then
      GetCompletedQuests()[questID] = { time(), UnitLevel("player") }
    end
    if event == "PLAYER_ENTERING_WORLD" or event == "ZONE_CHANGED" or event == "ZONE_CHANGED_NEW_AREA" or event == "MINIMAP_ZONE_CHANGED" then
      RefreshCurrentZoneMap()
    end
    RequestRefresh()
  end)
  moduleFrame:SetScript("OnUpdate", function(_, elapsed)
    if refreshPending then
      refreshTimer = refreshTimer + elapsed
      if refreshTimer >= 0.20 then
        refreshPending = false
        refreshTimer = 0
        EpochCN:UpdateWorldMapPins()
        EpochCN:UpdateMinimapQuestPins()
      end
    end

    minimapRefreshTimer = minimapRefreshTimer + elapsed
    if minimapRefreshTimer >= 0.75 then
      minimapRefreshTimer = 0
      if not WorldMapFrame or not WorldMapFrame:IsShown() then HidePins() end
      EpochCN:UpdateMinimapQuestPins()
    end

    hoverPollTimer = hoverPollTimer + elapsed
    if hoverPollTimer >= 0.08 then
      hoverPollTimer = 0
      -- 快速退出：无可见 pin 且地图未打开时跳过悬停检测，避免每帧轮询
      if visibleWorldMapPins > 0 or visibleMinimapPins > 0 or (WorldMapFrame and WorldMapFrame:IsShown()) then
        UpdateHoveredPinTooltip()
      elseif hoverPin then
        hoverPin = nil
        GameTooltip:Hide()
      end
    end
  end)

  if WorldMapFrame and EpochCNDB.worldMap then
    WorldMapFrame:HookScript("OnShow", function()
      CreateMenuButton()
      RequestRefresh()
    end)
    WorldMapFrame:HookScript("OnHide", HidePins)
  end

  SLASH_EPOCHCNMAP1 = "/epochcnmap"
  SLASH_EPOCHCNMAP2 = "/ecmap"
  SlashCmdList["EPOCHCNMAP"] = HandleSlashCommand

  HidePins()
  HideMinimapPins()
  RequestRefresh()
  self:Debug("世界地图任务标记核心已加载")
end
