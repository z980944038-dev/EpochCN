EpochCN:RegisterModule("PFQuestBridge", function(E)
  if not EpochCNDB.pfQuestBridge then return end

  local function ApplyConfigDefaults(reason)
    if not pfQuest_config then return end

    if EpochCNDB.disablePFQuestTracker then
      pfQuest_config["showtracker"] = "0"
    end

    local changed = false

    if EpochCNDB.forcePFQuestMap and pfQuest_config["trackingmethod"] ~= 1 then
      pfQuest_config["trackingmethod"] = 1
      changed = true
    end

    local required = {
      showspawn = "1",
      showspawnmini = "1",
      showcluster = "1",
      showclustermini = "0",
      allquestgivers = "1",
      currentquestgivers = "1",
      worldmapmenu = "1",
      minimapnodes = "1",
      questlogbuttons = "1",
      showtooltips = "1",
    }

    for key, value in pairs(required) do
      if pfQuest_config[key] ~= value then
        pfQuest_config[key] = value
        changed = true
      end
    end

    if not EpochCNCharDB.pfQuestBridgeApplied then
      EpochCNCharDB.pfQuestBridgeApplied = true
      changed = true
    end

    if changed then
      pfQuest_questcache = {}
      if pfQuest and pfQuest.ResetAll then pfQuest:ResetAll() end
      if pfQuest and pfQuest.mapButton and pfQuest.mapButton.UpdateMenu then
        pfQuest.mapButton.current = 1
        pfQuest.mapButton:UpdateMenu()
      end
      E:Debug("已修正 pfQuest 地图显示设置: " .. tostring(reason))
    end
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("WORLD_MAP_UPDATE")
  frame:SetScript("OnEvent", function(self, event)
    ApplyConfigDefaults(event)
  end)
end)
