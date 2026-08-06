EpochCN:RegisterModule("NamePlates", function(E)
  EpochCNDB.nameplates = EpochCNDB.nameplates or {}
  if EpochCNDB.nameplates.keepFriendlyAndEnemyNames == nil then
    EpochCNDB.nameplates.keepFriendlyAndEnemyNames = true
  end

  local nameMap = {}
  local nameMapBuilt = false
  local elvHooked = false
  local elvHookAttempts = 0

  local function AddName(english, chinese)
    if type(english) ~= "string" or type(chinese) ~= "string" then return end
    if english == "" or chinese == "" or english == chinese then return end
    nameMap[english] = chinese
  end

  local function AddCatalog(en, cn)
    if type(en) ~= "table" or type(cn) ~= "table" then return end
    for id, english in pairs(en) do
      AddName(english, cn[id])
    end
  end

  local function BuildNameMap()
    if nameMapBuilt then return end
    nameMapBuilt = true

    if EpochCN_Overrides and EpochCN_Overrides.englishUnits then
      for english, chinese in pairs(EpochCN_Overrides.englishUnits) do
        AddName(english, chinese)
      end
    end

    if pfDB and pfDB.units then
      AddCatalog(pfDB.units.enUS, pfDB.units.loc)
      AddCatalog(pfDB.units["enUS-epoch"], pfDB.units["zhCN-epoch"])
    end
  end

  local function TranslateText(text)
    if not text or text == "" then return end
    BuildNameMap()

    local direct = nameMap[text]
      or (E.nameMap and E.nameMap[text])
      or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[text])
    if direct then return direct end
    if E.nameMap and E.nameMap[text] then
      AddName(text, E.nameMap[text])
      return E.nameMap[text]
    end

    -- Nameplates sometimes append level/classification text or spaces.
    local trimmed = string.gsub(string.gsub(text, "^%s+", ""), "%s+$", "")
    if trimmed ~= text then
      direct = nameMap[trimmed]
        or (E.nameMap and E.nameMap[trimmed])
        or (EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[trimmed])
      if direct then return direct end
    end

    if E.TranslateEnglishUnitName then
      local translated = E:TranslateEnglishUnitName(trimmed)
      if translated and translated ~= trimmed then
        AddName(trimmed, translated)
        return translated
      end
    end
  end

  local function GetCreatureIDFromGUID(guid)
    if not guid then return end
    local id = string.match(guid, "^0xF130(%x%x%x%x%x%x)")
    if id then return tonumber(id, 16) end
    return tonumber(string.sub(guid, 8, 12), 16)
  end

  local function GetChineseByID(id)
    local data = E:GetUnitData(id)
    if data and data[1] and data[1] ~= "" then
      return data[1]
    end
  end

  local function GetChineseByEnglish(english)
    if not english or english == "" then return end
    return TranslateText(english)
  end

  local function LearnUnit(unit)
    if not unit or not UnitName then return end
    local english = UnitName(unit)
    if not english or english == "" then return end

    local id
    if UnitGUID then
      local guid = UnitGUID(unit)
      if guid then
        if GetCreatureIDFromUnit then
          id = GetCreatureIDFromUnit(unit)
        else
          id = GetCreatureIDFromGUID(guid)
        end
      end
    end

    local chinese = GetChineseByID(id) or GetChineseByEnglish(english)
    if chinese then
      E:RegisterEnglishUnitName(english, chinese)
      AddName(english, chinese)
    end
  end

  local function TranslateFontString(region)
    if not region or not region.GetObjectType or region:GetObjectType() ~= "FontString" then return end
    if not region.GetText or not region.SetText then return end

    local text = region:GetText()
    local translated = TranslateText(text)
    if translated and translated ~= text then
      region:SetText(translated)
    end
  end

  local function TranslateFrame(frame, depth)
    if not frame or not frame.GetRegions then return end
    depth = depth or 0

    for _, region in pairs({ frame:GetRegions() }) do
      TranslateFontString(region)
    end

    if depth < 3 and frame.GetChildren then
      for _, child in pairs({ frame:GetChildren() }) do
        TranslateFrame(child, depth + 1)
      end
    end
  end

  local function TranslateElvUIFrame(frame)
    if not frame then return end
    if frame.UnitType == "FRIENDLY_PLAYER" or frame.UnitType == "ENEMY_PLAYER" then return end

    local chinese
    if frame.guid then
      chinese = GetChineseByID(GetCreatureIDFromGUID(frame.guid))
    end

    if not chinese and frame.unit and UnitGUID then
      chinese = GetChineseByID(GetCreatureIDFromGUID(UnitGUID(frame.unit)))
    end

    if not chinese and frame.UnitName then
      chinese = GetChineseByEnglish(frame.UnitName)
    end

    if chinese and frame.Name and frame.Name.SetText then
      frame.Name:SetText(chinese)
      if frame.UnitName then
        AddName(frame.UnitName, chinese)
      end
    else
      TranslateFrame(frame)
    end
  end

  local function TryHookElvUI()
    if elvHooked then return true end
    elvHookAttempts = elvHookAttempts + 1

    if not ElvUI or type(ElvUI) ~= "table" then return false end
    local ok, Elv = pcall(function() return unpack(ElvUI) end)
    if not ok or not Elv or not Elv.GetModule then return false end

    local moduleOk, NP = pcall(Elv.GetModule, Elv, "NamePlates")
    if not moduleOk or not NP then return false end

    if hooksecurefunc then
      pcall(hooksecurefunc, NP, "Update_Name", function(_, frame)
        TranslateElvUIFrame(frame)
      end)
      pcall(hooksecurefunc, NP, "UpdateElement_All", function(_, frame)
        TranslateElvUIFrame(frame)
      end)
      pcall(hooksecurefunc, NP, "OnShow", function(plate)
        if plate and plate.UnitFrame then
          TranslateElvUIFrame(plate.UnitFrame)
        end
      end)
    else
      local oldUpdateName = NP.Update_Name
      NP.Update_Name = function(self, frame, ...)
        oldUpdateName(self, frame, ...)
        TranslateElvUIFrame(frame)
      end
    end

    elvHooked = true
    E:Debug("已接管 ElvUI 姓名板名字汉化")
    return true
  end

  local elapsedSinceScan = 0
  local worldFrameScanTimer = 0
  local elvRefreshTimer = 0
  local cvarGuardTimer = 0
  local cachedElvNP  -- 缓存 ElvUI NamePlates 模块引用，避免每帧 pcall

  local nameDisplayCVars = {
    "UnitNameEnemyPlayerName",
    "UnitNameFriendlyPlayerName",
    "UnitNameEnemyPetName",
    "UnitNameFriendlyPetName",
    "UnitNameEnemyGuardianName",
    "UnitNameFriendlyGuardianName",
    "UnitNameEnemyTotemName",
    "UnitNameFriendlyTotemName",
  }

  local function EnsureFriendlyAndEnemyNames()
    if not EpochCNDB.nameplates or EpochCNDB.nameplates.keepFriendlyAndEnemyNames == false then return end
    if not SetCVar then return end

    for _, cvar in ipairs(nameDisplayCVars) do
      if not GetCVar or tostring(GetCVar(cvar)) ~= "1" then
        pcall(SetCVar, cvar, "1")
      end
    end
  end

  -- 判断一个 WorldFrame 子 frame 是否为姓名板（3.3.5 原版姓名板结构检测）
  -- 姓名板特征：有 GetRegions 返回的第一个 region 是 StatusBar 或含有 HealthBar 子 frame
  local function IsNamePlateFrame(frame)
    if not frame or not frame.IsShown or not frame:IsShown() then return false end
    if not frame.GetChildren then return false end
    -- 3.3.5 原版姓名板的子 frame 中包含一个 StatusBar（血条）
    local children = { frame:GetChildren() }
    for _, child in pairs(children) do
      if child and child.GetObjectType and child:GetObjectType() == "StatusBar" then
        return true
      end
    end
    return false
  end

  local scanner = CreateFrame("Frame")
  scanner:RegisterEvent("PLAYER_ENTERING_WORLD")
  scanner:RegisterEvent("UPDATE_MOUSEOVER_UNIT")
  scanner:RegisterEvent("PLAYER_TARGET_CHANGED")
  scanner:RegisterEvent("PLAYER_REGEN_ENABLED")
  scanner:RegisterEvent("PLAYER_REGEN_DISABLED")
  scanner:RegisterEvent("ZONE_CHANGED_NEW_AREA")
  scanner:RegisterEvent("CVAR_UPDATE")
  scanner:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_ENTERING_WORLD"
      or event == "PLAYER_REGEN_ENABLED"
      or event == "PLAYER_REGEN_DISABLED"
      or event == "ZONE_CHANGED_NEW_AREA"
      or event == "CVAR_UPDATE" then
      EnsureFriendlyAndEnemyNames()
    end
    LearnUnit("mouseover")
    LearnUnit("target")
    LearnUnit("focus")
    elapsedSinceScan = 1
  end)
  scanner:SetScript("OnUpdate", function(_, elapsed)
    elapsedSinceScan = elapsedSinceScan + elapsed
    if elapsedSinceScan < 0.5 then return end
    elapsedSinceScan = 0

    cvarGuardTimer = cvarGuardTimer + 0.5
    if cvarGuardTimer >= 5.0 then
      cvarGuardTimer = 0
      EnsureFriendlyAndEnemyNames()
    end

    -- ElvUI hook 尝试（仅在未成功且尝试次数合理时）
    if not elvHooked and elvHookAttempts < 20 then
      TryHookElvUI()
      if elvHooked then
        -- 缓存 NP 模块引用
        local ok, Elv = pcall(function() return unpack(ElvUI) end)
        if ok and Elv and Elv.GetModule then
          local moduleOk, NP = pcall(Elv.GetModule, Elv, "NamePlates")
          if moduleOk and NP then cachedElvNP = NP end
        end
      end
    end

    -- ElvUI 已 hook 时，降低补充刷新频率（每 2 秒一次，hook 本身已实时触发）
    if ElvUI and elvHooked then
      elvRefreshTimer = elvRefreshTimer + 0.5
      if elvRefreshTimer < 2.0 then return end
      elvRefreshTimer = 0
      if cachedElvNP and cachedElvNP.VisiblePlates then
        for frame in pairs(cachedElvNP.VisiblePlates) do
          TranslateElvUIFrame(frame)
        end
      end
      return
    end

    -- 非 ElvUI 环境：仅扫描姓名板 frame（而非 WorldFrame 全部子 frame）
    -- 降低扫描频率至每 3 秒一次
    worldFrameScanTimer = worldFrameScanTimer + 0.5
    if worldFrameScanTimer < 3.0 then return end
    worldFrameScanTimer = 0

    if WorldFrame and WorldFrame.GetChildren then
      local children = { WorldFrame:GetChildren() }
      for _, child in pairs(children) do
        if IsNamePlateFrame(child) then
          TranslateFrame(child)
        end
      end
    end
  end)

  E:Debug("姓名板汉化模块已加载，ElvUI hook: " .. tostring(elvHooked))
end)
