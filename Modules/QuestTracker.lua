-- EpochCN QuestTracker Module
-- 任务追踪汉化：将 WoW 3.3.5 内置任务追踪框（WatchFrame）的显示内容汉化

EpochCN:RegisterModule("QuestTracker", function(E)
  if not EpochCNDB.questTracker then return end

  -- WoW 3.3.5 (WotLK) 使用 WatchFrame 显示追踪中的任务
  -- GetQuestLogTitle / GetQuestLogLeaderBoard 已被 QuestLog 模块全局钩挂，
  -- WatchFrame 调用这些函数时会自动获取汉化文本。
  -- 本模块负责：
  --   1. 翻译 WatchFrame 中因缓存产生的英文残留
  --   2. 汉化"Zoom Out"等地图按钮
  --   3. 提供 /epochcn track 开关命令

  -- -------------------------------------------------------
  -- 辅助：扫描 Frame 及子 Frame，对 FontString 尝试翻译
  -- -------------------------------------------------------
  local function TranslateFrame(frame, depth)
    if not frame or (depth and depth > 6) then return end
    depth = (depth or 0) + 1

    if frame.GetRegions then
      for _, region in pairs({ frame:GetRegions() }) do
        if region and region.GetText and region.SetText then
          local text = region:GetText()
          if text and text ~= "" then
            -- 优先查翻译缓存
            local translated = E.localizedTextByRaw and E.localizedTextByRaw[text]
            if not translated and EpochCN_Overrides and EpochCN_Overrides.maps then
              translated = EpochCN_Overrides.maps[text]
            end
            if translated and translated ~= text then
              region:SetText(translated)
            end
          end
        end
      end
    end

    if frame.GetChildren then
      for _, child in pairs({ frame:GetChildren() }) do
        TranslateFrame(child, depth)
      end
    end
  end

  -- -------------------------------------------------------
  -- 汉化世界地图上的 UI 按钮文字
  -- -------------------------------------------------------
  local mapButtonStrings = {
    ["Zoom Out"]   = "缩小",
    ["Zone Map"]   = "地区地图",
    ["Continent"]  = "大陆",
    ["Zone"]       = "地区",
    ["Show All"]   = "总是显示",
    ["Track"]      = "追踪",
    ["Show"]       = "显示",
    ["Hide"]       = "隐藏",
    ["Clean"]      = "清除",
    ["Reset"]      = "重置",
  }

  local function TranslateWorldMapButtons()
    if not WorldMapFrame then return end
    for _, child in pairs({ WorldMapFrame:GetChildren() }) do
      if child and child.GetRegions then
        for _, region in pairs({ child:GetRegions() }) do
          if region and region.GetText and region.SetText then
            local text = region:GetText()
            if text and mapButtonStrings[text] then
              region:SetText(mapButtonStrings[text])
            end
          end
        end
      end
    end
    -- DropDown 按钮文字
    local dropdowns = {
      WorldMapZoneMinimapDropDown,
      WorldMapContinentDropDown,
      WorldMapZoneDropDown,
    }
    for _, dd in pairs(dropdowns) do
      if dd then TranslateFrame(dd) end
    end
  end

  -- -------------------------------------------------------
  -- WatchFrame 汉化修正
  -- 由于 WatchFrame_Update 调用全局 GetQuestLogTitle / GetQuestLogLeaderBoard，
  -- EpochCN 的 QuestLog 模块已钩挂这两个函数，WatchFrame 会自动获得汉化内容。
  -- 此处额外修正：有时 WatchFrame 显示的标题残留了一级英文缓存，
  -- 我们在 WatchFrame_Update 执行后再做一次强制刷新。
  -- -------------------------------------------------------
  local function FixWatchFrameText()
    if not WatchFrame then return end
    -- 遍历 WatchFrameLines（WotLK 3.3.5 结构：WatchFrameLine1 ~ WatchFrameLine20）
    for i = 1, (WATCHFRAME_MAXQUESTS or 10) * 3 do
      local line = getglobal("WatchFrameLine" .. i)
      if line then
        -- 检查 FontString 子区域
        for _, region in pairs({ line:GetRegions() }) do
          if region and region.GetText and region.SetText then
            local text = region:GetText()
            if text and text ~= "" then
              local cn = E.localizedTextByRaw and E.localizedTextByRaw[text]
              if cn and cn ~= text then region:SetText(cn) end
            end
          end
        end
      end
    end
  end

  -- -------------------------------------------------------
  -- 钩挂 WatchFrame_Update（如果存在）
  -- -------------------------------------------------------
  if WatchFrame_Update then
    hooksecurefunc("WatchFrame_Update", function()
      FixWatchFrameText()
    end)
  end

  -- -------------------------------------------------------
  -- pfQuest Tracker 标签汉化
  -- pfQuest 有自己的追踪面板（pfQuestTracker），其文字引用 pfQuest_Loc 表。
  -- 我们在此添加中文条目覆盖。
  -- -------------------------------------------------------
  local function PatchPfQuestLocale()
    if not pfQuest_Loc then return end
    local cn = {
      ["Quest"]        = "任务",
      ["Level"]        = "等级",
      ["Required"]     = "所需",
      ["Objectives"]   = "目标",
      ["Explore"]      = "探索",
      ["Loot"]         = "战利品",
      ["Buy"]          = "购买",
      ["Vendor"]       = "商人",
      ["Respawn"]      = "刷新",
      ["Type"]         = "类型",
      ["Use <Shift>-Click To Remove Nodes"]   = "Shift+点击 移除标记",
      ["Use <Shift>-Click To Mark Quest As Done"] = "Shift+点击 标记已完成",
      ["Hold <Ctrl> To Hide Cluster"]         = "按住 Ctrl 隐藏聚合",
      ["Hold <Ctrl> To Hide Minimap Nodes"]   = "按住 Ctrl 隐藏小地图节点",
      ["Click Node To Change Color"]          = "点击节点更改颜色",
      ["Show"]         = "显示",
      ["Hide"]         = "隐藏",
      ["Clean"]        = "清除",
      ["Reset"]        = "重置",
      ["All Quests"]   = "全部任务",
      ["Tracked"]      = "追踪中",
      ["Manual"]       = "手动",
      ["Disabled"]     = "禁用",
    }
    for k, v in pairs(cn) do
      if pfQuest_Loc[k] == nil or pfQuest_Loc[k] == k then
        pfQuest_Loc[k] = v
      end
    end
  end

  -- -------------------------------------------------------
  -- 事件注册
  -- -------------------------------------------------------
  local frame = CreateFrame("Frame")
  frame:RegisterEvent("WORLD_MAP_UPDATE")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("VARIABLES_LOADED")
  frame:SetScript("OnEvent", function(self, event)
    TranslateWorldMapButtons()
    if event == "VARIABLES_LOADED" then
      PatchPfQuestLocale()
    end
  end)

  -- 初始执行
  PatchPfQuestLocale()
  TranslateWorldMapButtons()

  E:Debug("任务追踪汉化模块已加载")
end)
