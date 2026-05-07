EpochCN:RegisterModule("QuestSync", function(E)
  if not EpochCNDB.questAutoSync and not EpochCNDB.questProgressNotify then return end

  local prefix = "EPOCHCN_QSYNC"
  local frame = CreateFrame("Frame")
  local incoming = {}
  local remoteStates = {}
  local lastLocalState = {}
  local pendingBroadcast = false
  local pendingRequest = false
  local syncTimer = 0
  local initializedState = false

  local function Trim(text)
    if not text then return text end
    return (string.gsub(string.gsub(text, "^%s+", ""), "%s+$", ""))
  end

  local function StripRealmName(fullName)
    if fullName and string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)")
    end
    return fullName
  end

  local function GetGroupChannel()
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then return "RAID" end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then return "PARTY" end
  end

  local function ParseObjectiveProgress(text)
    local name, current, total = string.match(text or "", "^(.-):%s*([%-%d]+)%s*/%s*([%-%d]+)")
    if not name then return nil, nil, nil end
    return Trim(name), tonumber(current), tonumber(total)
  end

  local function CollectLocalState()
    local state = {}
    local entries = GetNumQuestLogEntries and GetNumQuestLogEntries() or 0
    -- 使用原始 API 避免触发翻译链（QuestSync 只需要数值，不需要翻译后的文本）
    local rawLeaderBoard = E.raw.GetQuestLogLeaderBoard or GetQuestLogLeaderBoard

    for questLogIndex = 1, entries do
      local title, _, _, _, isHeader, _, complete, _, questID = E.raw.GetQuestLogTitle(questLogIndex)
      if not isHeader then
        questID = E:GetQuestID(questLogIndex, questID)
        if questID then
          local questTitle = (E:GetQuestData(questID) and E:GetQuestData(questID)[1]) or title or ("任务 " .. tostring(questID))
          local questState = {
            title = questTitle,
            complete = complete == true or complete == 1,
            objectives = {},
          }

          local objectiveCount = GetNumQuestLeaderBoards and GetNumQuestLeaderBoards(questLogIndex) or 0
          local finishedCount = 0
          for objectiveIndex = 1, objectiveCount do
            local text, _, finished = rawLeaderBoard(objectiveIndex, questLogIndex)
            local _, current, total = ParseObjectiveProgress(text)
            if finished then finishedCount = finishedCount + 1 end
            table.insert(questState.objectives, {
              text = text or ("目标 " .. objectiveIndex),
              current = current or (finished and 1 or 0),
              total = total or 1,
              finished = finished and true or false,
            })
          end

          if objectiveCount > 0 and finishedCount >= objectiveCount then
            questState.complete = true
          end

          state[questID] = questState
        end
      end
    end

    return state
  end

  local function BuildStateDigest(state)
    local questIDs = {}
    for questID in pairs(state) do
      table.insert(questIDs, questID)
    end
    table.sort(questIDs)

    local parts = {}
    for _, questID in ipairs(questIDs) do
      local quest = state[questID]
      local objectiveParts = {}
      for index, objective in ipairs(quest.objectives or {}) do
        objectiveParts[index] = string.format("%d/%d/%d", objective.current or 0, objective.total or 0, objective.finished and 1 or 0)
      end
      table.insert(parts, string.format("%d:%d:%s", questID, quest.complete and 1 or 0, table.concat(objectiveParts, ",")))
    end

    return table.concat(parts, ";")
  end

  local function ParseObjectiveBlob(blob)
    local objectives = {}
    if not blob or blob == "" then return objectives end

    for token in string.gmatch(blob, "[^,]+") do
      local current, total, finished = string.match(token, "([%-%d]+)/([%-%d]+)/([01])")
      if current and total and finished then
        table.insert(objectives, {
          current = tonumber(current) or 0,
          total = tonumber(total) or 0,
          finished = finished == "1",
        })
      end
    end

    return objectives
  end

  local function CleanupRemoteStates()
    local allowed = {}
    allowed[StripRealmName(UnitName("player"))] = true

    if GetNumRaidMembers and GetNumRaidMembers() > 0 and GetRaidRosterInfo then
      for index = 1, GetNumRaidMembers() do
        local name = GetRaidRosterInfo(index)
        if name then allowed[StripRealmName(name)] = true end
      end
    elseif GetNumPartyMembers then
      for index = 1, GetNumPartyMembers() do
        local name = UnitName("party" .. index)
        if name then allowed[StripRealmName(name)] = true end
      end
    end

    for sender in pairs(remoteStates) do
      if not allowed[sender] then remoteStates[sender] = nil end
    end
  end

  local function SendState(force)
    if not EpochCNDB.questAutoSync or not SendAddonMessage then return end
    local channel = GetGroupChannel()
    if not channel then return end

    local state = CollectLocalState()
    local digest = BuildStateDigest(state)
    if not force and digest == frame.lastDigest then return end
    frame.lastDigest = digest
    lastLocalState = state

    local stamp = tostring(time()) .. tostring(math.random(1000, 9999))
    SendAddonMessage(prefix, "BEGIN:" .. stamp, channel)
    for questID, quest in pairs(state) do
      local objectiveParts = {}
      for index, objective in ipairs(quest.objectives or {}) do
        objectiveParts[index] = string.format("%d/%d/%d", objective.current or 0, objective.total or 0, objective.finished and 1 or 0)
      end
      SendAddonMessage(prefix, string.format("Q:%s:%d:%d:%s", stamp, questID, quest.complete and 1 or 0, table.concat(objectiveParts, ",")), channel)
    end
    SendAddonMessage(prefix, "END:" .. stamp, channel)
  end

  local function QueueBroadcast(force)
    if force then frame.forceBroadcast = true end
    pendingBroadcast = true
    syncTimer = 0
  end

  local function QueueSyncRequest()
    if not EpochCNDB.questAutoSync or not SendAddonMessage then return end
    pendingRequest = true
    syncTimer = 0
  end

  local function NotifyProgressChanges(newState)
    if not EpochCNDB.questProgressNotify then
      lastLocalState = newState
      return
    end

    for questID, quest in pairs(newState) do
      local oldQuest = lastLocalState[questID]
      for index, objective in ipairs(quest.objectives or {}) do
        local oldObjective = oldQuest and oldQuest.objectives and oldQuest.objectives[index]
        local oldCurrent = oldObjective and oldObjective.current or 0
        local newCurrent = objective.current or 0
        local progressed = newCurrent > oldCurrent
        local finishedNow = objective.finished and not (oldObjective and oldObjective.finished)

        if progressed or finishedNow then
          local message = string.format("%s - %s", quest.title or ("任务 " .. tostring(questID)), objective.text or ("目标 " .. index))
          if UIErrorsFrame and UIErrorsFrame.AddMessage then
            UIErrorsFrame:AddMessage(message, 1, 0.82, 0.2, 1.0)
          end
          if DEFAULT_CHAT_FRAME then
            DEFAULT_CHAT_FRAME:AddMessage("|cff33ffccEpoch|cffffffffCN: " .. message)
          end
          if EpochCNDB.questProgressPartyChat and GetGroupChannel() and SendChatMessage then
            SendChatMessage(message, GetGroupChannel())
          end
        end
      end
    end

    lastLocalState = newState
  end

  function E:GetSyncedQuestIDs()
    local synced = {}
    for _, data in pairs(remoteStates) do
      for questID in pairs(data.quests or {}) do
        synced[questID] = true
      end
    end
    return synced
  end

  function E:IsSyncedQuestComplete(questID)
    for _, data in pairs(remoteStates) do
      local quest = data.quests and data.quests[questID]
      if quest and quest.complete then return true end
    end
    return false
  end

  function E:GetQuestSyncTooltipLines(questIDs)
    local lines, seen = {}, {}
    for questID in pairs(questIDs or {}) do
      for sender, data in pairs(remoteStates) do
        local quest = data.quests and data.quests[questID]
        if quest and not seen[sender .. ":" .. tostring(questID)] then
          seen[sender .. ":" .. tostring(questID)] = true
          local objectiveTotal = #(quest.objectives or {})
          local objectiveDone = 0
          for _, objective in ipairs(quest.objectives or {}) do
            if objective.finished then objectiveDone = objectiveDone + 1 end
          end

          local status = quest.complete and "可交" or "进行中"
          if not quest.complete and objectiveTotal > 0 then
            status = string.format("进行中 %d/%d", objectiveDone, objectiveTotal)
          end

          table.insert(lines, sender .. "：" .. status)
        end
      end
    end
    table.sort(lines)
    return lines
  end

  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:RegisterEvent("PARTY_MEMBERS_CHANGED")
  frame:RegisterEvent("RAID_ROSTER_UPDATE")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("QUEST_LOG_UPDATE")
  frame:SetScript("OnEvent", function(_, event, ...)
    if event == "CHAT_MSG_ADDON" then
      local msgPrefix, message, _, sender = ...
      sender = StripRealmName(sender)
      if msgPrefix ~= prefix or not sender or sender == StripRealmName(UnitName("player")) then return end

      if message == "REQ" then
        QueueBroadcast(true)
        return
      end

      local stamp = string.match(message, "^BEGIN:(.+)$")
      if stamp then
        incoming[sender] = { stamp = stamp, quests = {} }
        return
      end

      stamp = string.match(message, "^END:(.+)$")
      if stamp and incoming[sender] and incoming[sender].stamp == stamp then
        remoteStates[sender] = { quests = incoming[sender].quests, updated = time() }
        incoming[sender] = nil
        if EpochCN and EpochCN.UpdateWorldMapPins then EpochCN:UpdateWorldMapPins() end
        return
      end

      local qStamp, questID, complete, objectiveBlob = string.match(message, "^Q:([^:]+):([^:]+):([^:]+):(.*)$")
      if qStamp and incoming[sender] and incoming[sender].stamp == qStamp then
        incoming[sender].quests[tonumber(questID)] = {
          complete = complete == "1",
          objectives = ParseObjectiveBlob(objectiveBlob),
        }
      end
      return
    end

    if event == "QUEST_LOG_UPDATE" then
      local state = CollectLocalState()
      if initializedState then
        NotifyProgressChanges(state)
      else
        lastLocalState = state
        initializedState = true
      end
      QueueBroadcast(false)
      return
    end

    if event == "PLAYER_ENTERING_WORLD" then
      CleanupRemoteStates()
      lastLocalState = CollectLocalState()
      initializedState = true
      QueueBroadcast(true)
      QueueSyncRequest()
      return
    end

    if event == "PARTY_MEMBERS_CHANGED" or event == "RAID_ROSTER_UPDATE" then
      CleanupRemoteStates()
      QueueBroadcast(true)
      QueueSyncRequest()
    end
  end)

  frame:SetScript("OnUpdate", function(_, elapsed)
    if not pendingBroadcast and not pendingRequest then return end
    syncTimer = syncTimer + elapsed
    if syncTimer < 0.5 then return end

    if pendingRequest then
      pendingRequest = false
      local channel = GetGroupChannel()
      if channel and SendAddonMessage then
        SendAddonMessage(prefix, "REQ", channel)
      end
    end

    if pendingBroadcast then
      pendingBroadcast = false
      SendState(frame.forceBroadcast)
      frame.forceBroadcast = nil
    end

    syncTimer = 0
  end)
end)
