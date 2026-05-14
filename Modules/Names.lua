EpochCN:RegisterModule("Names", function(E)
  local function GetUnitID(unit)
    if not unit or not UnitGUID then return end

    local guid = UnitGUID(unit)
    if not guid then return end

    if GetCreatureIDFromUnit then
      return GetCreatureIDFromUnit(unit)
    end

    local id = string.match(guid, "^0xF130(%x%x%x%x%x%x)")
    if id then return tonumber(id, 16) end
    return tonumber(string.sub(guid, 8, 12), 16)
  end

  local function GetCNName(unit)
    local id = GetUnitID(unit)
    local data = E:GetUnitData(id)
    if data and data[1] then return data[1] end

    local english = UnitName and UnitName(unit)
    if english and english ~= "" then
      if E.nameMap and E.nameMap[english] then return E.nameMap[english] end
      if EpochCN_ObjectiveNameData and EpochCN_ObjectiveNameData[english] then
        return EpochCN_ObjectiveNameData[english]
      end
      if E.TranslateEnglishUnitName then
        return E:TranslateEnglishUnitName(english)
      end
    end
  end

  local function SetText(widget, text)
    if widget and widget.SetText and text and text ~= "" then
      widget:SetText(text)
    end
  end

  local function UpdateUnitFrame(unit)
    local name = GetCNName(unit)
    if not name then return end
    E:RegisterEnglishUnitName(UnitName(unit), name)

    if unit == "target" then
      SetText(TargetFrameTextureFrameName, name)
      if TargetFrame and TargetFrame.name then
        SetText(TargetFrame.name, name)
      end
      -- TargetFrameNameBackground.Text 在 3.3.5 不存在；保留空值安全检查
      if TargetFrameNameBackground and TargetFrameNameBackground.Text then
        SetText(TargetFrameNameBackground.Text, name)
      end
    elseif unit == "focus" then
      SetText(FocusFrameTextureFrameName, name)
      if FocusFrame and FocusFrame.name then
        SetText(FocusFrame.name, name)
      end
    elseif unit == "mouseover" then
      if GameTooltip and GameTooltip:IsShown() then
        local title = getglobal("GameTooltipTextLeft1")
        SetText(title, name)
      end
    end
  end

  local function UpdateAll()
    UpdateUnitFrame("target")
    UpdateUnitFrame("focus")
    UpdateUnitFrame("mouseover")
  end

  if TargetFrame_Update then
    hooksecurefunc("TargetFrame_Update", function() UpdateUnitFrame("target") end)
  end

  if FocusFrame_Update then
    hooksecurefunc("FocusFrame_Update", function() UpdateUnitFrame("focus") end)
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_TARGET_CHANGED")
  frame:RegisterEvent("PLAYER_FOCUS_CHANGED")
  frame:RegisterEvent("UPDATE_MOUSEOVER_UNIT")
  frame:RegisterEvent("UNIT_TARGET")
  frame:SetScript("OnEvent", function(_, event, unit)
    if event == "UNIT_TARGET" and unit ~= "player" then return end
    UpdateAll()
  end)

  UpdateAll()
end)
