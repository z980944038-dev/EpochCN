EpochCN:RegisterModule("SpellBook", function(E)
  -- 职业天赋树 / 技能书标签页汉化对照表
  local tabNameMap = {
    -- 通用
    ["General"]           = "通用",
    ["Passive"]           = "被动",
    -- 战士
    ["Arms"]              = "武器",
    ["Fury"]              = "狂怒",
    ["Protection"]        = "防护",
    -- 圣骑士
    ["Holy"]              = "神圣",
    ["Retribution"]       = "惩戒",
    -- 猎人
    ["Beast Mastery"]     = "兽王",
    ["Marksmanship"]      = "射击",
    ["Survival"]          = "生存",
    -- 盗贼
    ["Assassination"]     = "刺杀",
    ["Combat"]            = "战斗",
    ["Subtlety"]          = "敏锐",
    -- 牧师
    ["Discipline"]        = "戒律",
    ["Shadow"]            = "暗影",
    -- 萨满
    ["Elemental"]         = "元素",
    ["Enhancement"]       = "增强",
    ["Restoration"]       = "恢复",
    -- 法师
    ["Arcane"]            = "奥术",
    ["Fire"]              = "火焰",
    ["Frost"]             = "冰霜",
    -- 术士
    ["Affliction"]        = "痛苦",
    ["Demonology"]        = "恶魔学识",
    ["Destruction"]       = "毁灭",
    -- 德鲁伊
    ["Balance"]           = "平衡",
    ["Feral Combat"]      = "野性战斗",
    ["Feral"]             = "野性",
    -- 死亡骑士
    ["Blood"]             = "鲜血",
    ["Unholy"]            = "邪恶",
    ["Runeforging"]       = "符文锻造",
    -- 技能分类
    ["Spells"]            = "法术",
    ["Skills"]            = "技能",
    ["Abilities"]         = "能力",
    ["Professions"]       = "专业",
    ["Pet"]               = "宠物",
  }

  local function PatchSpellBookTabText(tabButton)
    if not tabButton or tabButton.EpochCNTabPatched then return end
    local label = tabButton.GetText and tabButton:GetText()
    if label and label ~= "" then
      local cn = tabNameMap[label]
      if cn then
        tabButton:SetText(cn)
        tabButton.EpochCNTabPatched = true
      end
    end
  end

  local function PatchAllSpellBookTabs()
    -- SpellBookSkillLineTab（技能树标签）
    local maxTabs = MAX_SKILLLINE_TABS or 8
    for i = 1, maxTabs do
      local tab = getglobal("SpellBookSkillLineTab" .. i)
      if tab then
        local ok, name = pcall(GetSpellTabInfo, i)
        if ok and name and tabNameMap[name] then
          -- 内部 tooltip label
          tab.tooltip = tabNameMap[name]
        end
      end
    end
    -- SpellBookFrameTabButton（法术/宠物 tab 按钮）
    for i = 1, 3 do
      local tab = getglobal("SpellBookFrameTabButton" .. i)
      PatchSpellBookTabText(tab)
    end
  end

  local function PatchSkillLineTabTooltip()
    local maxTabs = MAX_SKILLLINE_TABS or 8

    for i = 1, maxTabs do
      local tab = getglobal("SpellBookSkillLineTab" .. i)
      if tab and not tab.EpochCNTooltipPatched then
        tab.EpochCNTooltipPatched = true
        tab:SetScript("OnEnter", function(self)
          local text = self.tooltip

          if (not text or text == "") and GetSpellTabInfo and self.GetID then
            local ok, name = pcall(GetSpellTabInfo, self:GetID())
            if ok then text = name end
          end

          if not text or text == "" then
            return
          end

          GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
          GameTooltip:SetText(text)
        end)
        tab:SetScript("OnLeave", function()
          GameTooltip:Hide()
        end)
      end
    end

    for i = 1, 3 do
      local tab = getglobal("SpellBookFrameTabButton" .. i)
      if tab and not tab.EpochCNTooltipPatched then
        tab.EpochCNTooltipPatched = true
        tab:SetScript("OnEnter", function(self)
          local label = self.GetText and self:GetText()
          local text

          if label and label ~= "" and MicroButtonTooltipText then
            text = MicroButtonTooltipText(label, self.binding)
          end

          if not text or text == "" then
            text = label
          end

          if not text or text == "" then
            return
          end

          GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
          GameTooltip:SetText(text, 1.0, 1.0, 1.0)
        end)
        tab:SetScript("OnLeave", function()
          GameTooltip:Hide()
        end)
      end
    end
  end

  local function LocalizeLater()
    PatchAllSpellBookTabs()
    PatchSkillLineTabTooltip()
    if C_Timer and C_Timer.After then
      C_Timer.After(0.05, function()
        PatchAllSpellBookTabs()
        PatchSkillLineTabTooltip()
      end)
    end
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:SetScript("OnEvent", LocalizeLater)

  if SpellBookFrame and SpellBookFrame.HookScript then
    SpellBookFrame:HookScript("OnShow", LocalizeLater)
  end

  LocalizeLater()
end)
