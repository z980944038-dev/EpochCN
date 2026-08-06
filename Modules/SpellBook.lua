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
        tab:HookScript("OnEnter", function(self)
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
        tab:HookScript("OnLeave", function()
          GameTooltip:Hide()
        end)
      end
    end

    for i = 1, 3 do
      local tab = getglobal("SpellBookFrameTabButton" .. i)
      if tab and not tab.EpochCNTooltipPatched then
        tab.EpochCNTooltipPatched = true
        tab:HookScript("OnEnter", function(self)
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
        tab:HookScript("OnLeave", function()
          GameTooltip:Hide()
        end)
      end
    end
  end

  -- 等级 / 子标签翻译对照
  local rankMap = {
    ["Rank 1"] = "等级 1", ["Rank 2"] = "等级 2", ["Rank 3"] = "等级 3",
    ["Rank 4"] = "等级 4", ["Rank 5"] = "等级 5", ["Rank 6"] = "等级 6",
    ["Rank 7"] = "等级 7", ["Rank 8"] = "等级 8", ["Rank 9"] = "等级 9",
    ["Rank 10"] = "等级 10", ["Rank 11"] = "等级 11", ["Rank 12"] = "等级 12",
    ["Rank 13"] = "等级 13", ["Rank 14"] = "等级 14", ["Rank 15"] = "等级 15",
    ["Passive"] = "被动",
    ["Racial"] = "种族",
    ["Racial Passive"] = "种族被动",
    ["Cosmetic Racial"] = "外观种族",
    ["Apprentice"] = "初级",
    ["Journeyman"] = "中级",
    ["Expert"] = "高级",
    ["Artisan"] = "大师级",
    ["Master"] = "宗师级",
    ["Grand Master"] = "超级大师级",
    ["Shapeshift"] = "变形",
    ["Summon"] = "召唤",
    ["Knowledge"] = "知识",
  }

  local function TranslateRank(text)
    if not text or text == "" then return end
    local cn = rankMap[text]
    if cn then return cn end
    -- Dynamic "Rank N" pattern
    local n = string.match(text, "^Rank (%d+)$")
    if n then return "等级 " .. n end
    return nil
  end

  local function GetBookType()
    return (SpellBookFrame and SpellBookFrame.bookType) or BOOKTYPE_SPELL
  end

  local function GetSpellBookSlot(button)
    if not button or not button.GetID then return end
    local buttonID = button:GetID()
    if not buttonID then return end

    if SpellBook_GetSpellID then
      local ok, slot = pcall(SpellBook_GetSpellID, buttonID)
      if ok and type(slot) == "number" and slot > 0 then
        return slot
      end
    end

    local page = 1
    local bookType = GetBookType()
    local offset = 0
    if SpellBookFrame then
      page = SpellBookFrame.currentPage or SpellBookFrame.page or 1
      if bookType == BOOKTYPE_SPELL and SpellBookFrame.selectedSkillLine and GetSpellTabInfo then
        local ok, name, texture, spellOffset = pcall(GetSpellTabInfo, SpellBookFrame.selectedSkillLine)
        if ok and type(spellOffset) == "number" then
          offset = spellOffset
        end
      end
    end
    return offset + buttonID + ((page - 1) * (SPELLS_PER_PAGE or 12))
  end

  local function PatchSpellButtons()
    if not SpellBookFrame or not SpellBookFrame:IsShown() then return end
    local numButtons = SPELLS_PER_PAGE or 12

    for i = 1, numButtons do
      local buttonName = "SpellButton" .. i
      local button = getglobal(buttonName)
      if button and button.GetID then
        local slot = GetSpellBookSlot(button)
        local bookType = GetBookType()

        -- Get spell info from the button
        local spellName, subSpellName, id

        if slot and GetSpellBookItemInfo and bookType then
          local ok, sType, spellID = pcall(GetSpellBookItemInfo, slot, bookType)
          if ok then id = spellID end
        end

        -- Use GetSpellBookItemName for name/subtext
        if slot and GetSpellBookItemName and bookType then
          local ok, sn, ss = pcall(GetSpellBookItemName, slot, bookType)
          if ok then
            spellName = sn
            subSpellName = ss
          end
        end

        if not spellName and slot and GetSpellName and bookType then
          local ok, sn, ss = pcall(GetSpellName, slot, bookType)
          if ok then
            spellName = sn
            subSpellName = subSpellName or ss
          end
        end

        -- Last-resort fallback only when the real spellbook slot cannot be resolved.
        if not spellName and not slot then
          local nameRegion = getglobal(buttonName .. "SpellName")
          if nameRegion and nameRegion.GetText then
            spellName = nameRegion:GetText()
          end
        end
        if not subSpellName and not slot then
          local subRegion = getglobal(buttonName .. "SubSpellName")
          if subRegion and subRegion.GetText then
            subSpellName = subRegion:GetText()
          end
        end

        -- Get translation data
        local data
        if id then
          data = E:GetSpellData(id)
        end
        if not data and spellName and E.GetSpellDataByName then
          data = E:GetSpellDataByName(spellName)
        end

        -- Translate spell name
        if data and data[1] then
          local nameRegion = getglobal(buttonName .. "SpellName")
          if nameRegion and nameRegion.SetText and nameRegion.GetText then
            local currentName = nameRegion:GetText()
            if currentName and currentName ~= "" and data[1] ~= currentName then
              nameRegion:SetText(data[1])
            end
          end
        end

        -- Translate rank/subtext
        if subSpellName then
          local cnRank = (data and data[4]) or TranslateRank(subSpellName)
          if cnRank then
            local subRegion = getglobal(buttonName .. "SubSpellName")
            if subRegion and subRegion.SetText then
              subRegion:SetText(cnRank)
            end
          end
        end
      end
    end
  end

  local function PatchSpellButtonsSoon()
    PatchSpellButtons()
    E:After(0.05, PatchSpellButtons)
  end

  local function LocalizeLater()
    PatchAllSpellBookTabs()
    PatchSkillLineTabTooltip()
    PatchSpellButtons()
    E:After(0.05, function()
      PatchAllSpellBookTabs()
      PatchSkillLineTabTooltip()
      PatchSpellButtons()
    end)
  end

  local frame = CreateFrame("Frame")
  frame:RegisterEvent("PLAYER_ENTERING_WORLD")
  frame:RegisterEvent("SPELLS_CHANGED")
  frame:SetScript("OnEvent", LocalizeLater)

  if SpellBookFrame and SpellBookFrame.HookScript then
    SpellBookFrame:HookScript("OnShow", LocalizeLater)
  end

  -- Hook page turning for spell button updates
  if SpellBookPrevPageButton and SpellBookPrevPageButton.HookScript then
    SpellBookPrevPageButton:HookScript("OnClick", PatchSpellButtonsSoon)
  end
  if SpellBookNextPageButton and SpellBookNextPageButton.HookScript then
    SpellBookNextPageButton:HookScript("OnClick", PatchSpellButtonsSoon)
  end

  -- Hook skill line tab clicks for spell button updates
  local maxTabs = MAX_SKILLLINE_TABS or 8
  for i = 1, maxTabs do
    local tab = getglobal("SpellBookSkillLineTab" .. i)
    if tab and tab.HookScript then
      tab:HookScript("OnClick", PatchSpellButtonsSoon)
    end
  end

  LocalizeLater()
end)
