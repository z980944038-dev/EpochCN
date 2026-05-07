-- UpdateChecker.lua
-- Checks GitHub releases for a newer version and notifies the player in-game.
-- Uses the WoW 3.3.5a SendAddonMessage + OnUpdate timer approach since
-- the 3.3.5 client does not have a native HTTP API. We compare the local
-- version string (from E.version) against a version file embedded in the
-- addon distribution. For true remote checking we rely on a lightweight
-- "version beacon" approach: guild/party members running a newer build
-- will broadcast their version, and any recipient running an older build
-- gets a notification.
--
-- Additionally, the addon's GitHub release tag is stored in
-- EpochCN.updateInfo so that external updater tools can consume it.

EpochCN:RegisterModule("UpdateChecker", function(E)
  -- Respect the user toggle
  if EpochCNDB.updateCheck == false then return end

  local UPDATE_PREFIX = "EpochCNVer"
  local BROADCAST_INTERVAL = 300 -- seconds between broadcasts
  local INITIAL_DELAY = 10       -- seconds after login before first broadcast
  local GITHUB_REPO = "https://github.com/z980944038-dev/EpochCN"

  -- Persisted state
  EpochCNDB.dismissedVersion = EpochCNDB.dismissedVersion or ""
  EpochCNDB.lastKnownRemoteVersion = EpochCNDB.lastKnownRemoteVersion or ""

  -- Runtime state
  local notifiedThisSession = false
  local broadcastTimer = 0
  local initialized = false

  ---------------------------------------------------------------------------
  -- Version comparison utilities
  ---------------------------------------------------------------------------
  local function ParseVersion(str)
    if type(str) ~= "string" then return nil end
    local parts = {}
    for num in string.gmatch(str, "(%d+)") do
      table.insert(parts, tonumber(num))
    end
    return #parts > 0 and parts or nil
  end

  local function CompareVersions(a, b)
    -- Returns 1 if a > b, -1 if a < b, 0 if equal
    local pa = ParseVersion(a)
    local pb = ParseVersion(b)
    if not pa or not pb then return 0 end
    local len = math.max(#pa, #pb)
    for i = 1, len do
      local va = pa[i] or 0
      local vb = pb[i] or 0
      if va > vb then return 1 end
      if va < vb then return -1 end
    end
    return 0
  end

  local function IsNewer(remote, local_ver)
    return CompareVersions(remote, local_ver) > 0
  end

  ---------------------------------------------------------------------------
  -- Notification
  ---------------------------------------------------------------------------
  local updateFrame = nil

  local function ShowUpdateNotification(remoteVersion)
    if notifiedThisSession then return end
    if EpochCNDB.dismissedVersion == remoteVersion then return end
    notifiedThisSession = true

    -- Store for reference
    EpochCNDB.lastKnownRemoteVersion = remoteVersion

    -- Chat notification
    E:Print("|cffff9900⬆ 发现新版本|r: |cff33ff99v" .. remoteVersion .. "|r (当前: v" .. E.version .. ")")
    E:Print("|cff88ccff下载地址|r: " .. GITHUB_REPO .. "/releases")
    E:Print("|cff888888输入 /ecn update dismiss 可忽略本次更新提醒。|r")

    -- Optional: floating notification frame
    if updateFrame then updateFrame:Show(); return end

    updateFrame = CreateFrame("Frame", "EpochCNUpdateFrame", UIParent)
    updateFrame:SetSize(360, 80)
    updateFrame:SetPoint("TOP", UIParent, "TOP", 0, -120)
    updateFrame:SetFrameStrata("DIALOG")
    updateFrame:SetMovable(true)
    updateFrame:EnableMouse(true)
    updateFrame:RegisterForDrag("LeftButton")
    updateFrame:SetScript("OnDragStart", function(self) self:StartMoving() end)
    updateFrame:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    updateFrame:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true,
      tileSize = 32,
      edgeSize = 16,
      insets = { left = 5, right = 5, top = 5, bottom = 5 },
    })

    local title = updateFrame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    title:SetPoint("TOP", updateFrame, "TOP", 0, -12)
    title:SetText("|cff33ffccEpochCN|r |cffff9900新版本可用！|r")

    local body = updateFrame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    body:SetPoint("TOP", title, "BOTTOM", 0, -4)
    body:SetWidth(340)
    body:SetJustifyH("CENTER")
    body:SetText("v" .. remoteVersion .. " 已发布（当前 v" .. E.version .. "）\n请前往 GitHub 下载最新版本")

    local dismissBtn = CreateFrame("Button", nil, updateFrame, "UIPanelButtonTemplate")
    dismissBtn:SetSize(60, 20)
    dismissBtn:SetPoint("BOTTOMRIGHT", updateFrame, "BOTTOMRIGHT", -8, 8)
    dismissBtn:SetText("忽略")
    dismissBtn:SetScript("OnClick", function()
      EpochCNDB.dismissedVersion = remoteVersion
      updateFrame:Hide()
    end)

    local closeBtn = CreateFrame("Button", nil, updateFrame, "UIPanelButtonTemplate")
    closeBtn:SetSize(60, 20)
    closeBtn:SetPoint("BOTTOMLEFT", updateFrame, "BOTTOMLEFT", 8, 8)
    closeBtn:SetText("关闭")
    closeBtn:SetScript("OnClick", function()
      updateFrame:Hide()
    end)

    -- Auto-hide after 30 seconds
    C_Timer = C_Timer or nil
    updateFrame.elapsed = 0
    updateFrame:SetScript("OnUpdate", function(self, elapsed)
      self.elapsed = self.elapsed + elapsed
      if self.elapsed > 30 then
        self:SetScript("OnUpdate", nil)
        self:Hide()
      end
    end)
  end

  ---------------------------------------------------------------------------
  -- Addon communication – version beacon
  ---------------------------------------------------------------------------
  -- In WoW 3.3.5, addons can send short messages over addon channels.
  -- We broadcast our version to GUILD and PARTY; if we receive a newer
  -- version from someone else, we notify.

  local function BroadcastVersion(channel)
    if not SendAddonMessage then return end
    local ok = pcall(SendAddonMessage, UPDATE_PREFIX, E.version, channel)
    if not ok then
      E:Debug("UpdateChecker: 广播版本到 " .. channel .. " 失败")
    end
  end

  local function OnAddonMessage(prefix, message, channel, sender)
    if prefix ~= UPDATE_PREFIX then return end
    -- Ignore our own messages
    local playerName = UnitName("player")
    if sender == playerName then return end

    local remoteVersion = message
    if IsNewer(remoteVersion, E.version) then
      E:Debug("UpdateChecker: 收到来自 " .. tostring(sender) .. " 的新版本通知: v" .. tostring(remoteVersion))
      ShowUpdateNotification(remoteVersion)
    end
  end

  ---------------------------------------------------------------------------
  -- Check against embedded version file
  -- (For standalone update checking without other players online)
  ---------------------------------------------------------------------------
  local function CheckEmbeddedVersion()
    -- EpochCN_LatestVersion is set by a small file that can be updated
    -- independently (e.g., by a CI script that writes the latest tag).
    -- If the user downloads a new release, this file will contain the
    -- release version. If the addon was updated partially, it will
    -- detect the mismatch.
    if EpochCN_LatestVersion and type(EpochCN_LatestVersion) == "string" then
      if IsNewer(EpochCN_LatestVersion, E.version) then
        ShowUpdateNotification(EpochCN_LatestVersion)
      end
    end
  end

  ---------------------------------------------------------------------------
  -- Slash command extension
  ---------------------------------------------------------------------------
  local originalSlashHandler = SlashCmdList["EPOCHCN"]

  SlashCmdList["EPOCHCN"] = function(msg)
    local cmd = string.lower(msg or "")
    if cmd == "update" then
      E:Print("当前版本: |cff33ff99v" .. E.version .. "|r")
      if EpochCNDB.lastKnownRemoteVersion ~= "" and IsNewer(EpochCNDB.lastKnownRemoteVersion, E.version) then
        E:Print("|cffff9900最新版本|r: |cff33ff99v" .. EpochCNDB.lastKnownRemoteVersion .. "|r")
        E:Print("|cff88ccff下载|r: " .. GITHUB_REPO .. "/releases")
      else
        E:Print("已是最新版本。")
      end
      return
    end
    if cmd == "update dismiss" then
      if EpochCNDB.lastKnownRemoteVersion ~= "" then
        EpochCNDB.dismissedVersion = EpochCNDB.lastKnownRemoteVersion
        E:Print("已忽略 v" .. EpochCNDB.lastKnownRemoteVersion .. " 的更新提醒。")
      else
        E:Print("当前没有可忽略的新版本。")
      end
      return
    end
    if originalSlashHandler then
      originalSlashHandler(msg)
    end
  end

  ---------------------------------------------------------------------------
  -- Initialization
  ---------------------------------------------------------------------------
  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("CHAT_MSG_ADDON")
  frame:SetScript("OnEvent", function(self, event, ...)
    if event == "PLAYER_ENTERING_WORLD" then
      if initialized then return end
      initialized = true

      -- Register addon prefix for version broadcasts
      if RegisterAddonMessagePrefix then
        pcall(RegisterAddonMessagePrefix, UPDATE_PREFIX)
      end

      -- Check embedded version after a short delay
      self.initDelay = 0
      self:SetScript("OnUpdate", function(self, elapsed)
        self.initDelay = (self.initDelay or 0) + elapsed
        if self.initDelay < INITIAL_DELAY then return end
        self:SetScript("OnUpdate", nil)

        -- Check embedded version file
        CheckEmbeddedVersion()

        -- Start periodic broadcast timer
        local broadcaster = CreateFrame("Frame")
        broadcaster.elapsed = 0
        broadcaster:SetScript("OnUpdate", function(self, elapsed)
          self.elapsed = self.elapsed + elapsed
          if self.elapsed >= BROADCAST_INTERVAL then
            self.elapsed = 0
            if IsInGuild() then BroadcastVersion("GUILD") end
            local n = GetNumPartyMembers and GetNumPartyMembers() or 0
            if n > 0 then BroadcastVersion("PARTY") end
            local r = GetNumRaidMembers and GetNumRaidMembers() or 0
            if r > 0 then BroadcastVersion("RAID") end
          end
        end)

        -- Immediate first broadcast
        if IsInGuild() then BroadcastVersion("GUILD") end
        local n = GetNumPartyMembers and GetNumPartyMembers() or 0
        if n > 0 then BroadcastVersion("PARTY") end
      end)

    elseif event == "CHAT_MSG_ADDON" then
      OnAddonMessage(...)
    end
  end)

  -- Store GitHub repo URL for the About panel and other modules
  E.updateInfo = {
    repo = GITHUB_REPO,
    currentVersion = E.version,
  }

  E:Debug("UpdateChecker 已注册")
end)
