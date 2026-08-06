-- Verified against https://epochdb.net/ public API snapshot (2026-08-06).
-- This file only contains records missing from the bundled EpochCN datasets.
function LoadEpochCNEpochDBSupplementData()
  EpochCN_ItemOverlayData = EpochCN_ItemOverlayData or {}
  EpochCN_ItemNameMap = EpochCN_ItemNameMap or {}
  TPCN_UnitData = TPCN_UnitData or {}

  local items = {
    [90726] = {"竞争者的战斗法师头冠", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Crown"},
    [90727] = {"竞争者的战斗法师衬肩", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Mantle"},
    [90728] = {"竞争者的战斗法师长袍", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Robe"},
    [90729] = {"竞争者的战斗法师手套", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Gloves"},
    [90730] = {"竞争者的战斗法师护腿", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Leggings"},
    [90731] = {"竞争者的战斗法师长靴", "", "EpochDB 物品", "item", {}, "Contender's Battlemage Boots"},
    [90732] = {"竞争者的施法腰带", "", "EpochDB 物品", "item", {}, "Contender's Waistband of Spellcasting"},
    [90733] = {"竞争者的施法腕轮", "", "EpochDB 物品", "item", {}, "Contender's Bands of Spellcasting"},
    [90734] = {"对手的战斗法师头冠", "", "EpochDB 物品", "item", {}, "Rival's Battlemage Crown"},
    [90736] = {"对手的战斗法师长袍", "", "EpochDB 物品", "item", {}, "Rival's Battlemage Robe"},
    [90737] = {"对手的战斗法师手套", "", "EpochDB 物品", "item", {}, "Rival's Battlemage Gloves"},
    [90739] = {"对手的战斗法师长靴", "", "EpochDB 物品", "item", {}, "Rival's Battlemage Boots"},
  }

  for id, data in pairs(items) do
    EpochCN_ItemOverlayData[id] = data
    EpochCN_ItemNameMap[data[6]] = data[1]
  end

  TPCN_UnitData[90070] = {"吉利吉姆地雷", "", "EpochDB", "吉利吉姆岛", "纳迦遗迹", "Gillijim Land Mine"}

  -- Some EpochDB quest uploads contain only a title. These aliases restore
  -- the classic quest ID so the already translated QuestCN row can be used.
  EpochCN_EpochDBQuestAliases = {
    ["A Crumpled Up Note"] = 4264,
    ["Rocknot's Ale"] = 4295,
    ["Cuergo's Gold"] = 2882,
    ["The Medallion of Faith"] = 5122,
  }
end
