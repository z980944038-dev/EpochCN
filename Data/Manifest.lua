EpochCN_DataManifest = {
  version = "0.8.0-core",
  generated = "2026-08-06",
  designer = "EpochCN",
  sources = {
    {
      name = "local FrameXML",
      path = "FrameXML/GlobalStrings.lua",
      role = "Chinese client global strings for settings and base UI",
    },
    {
      name = "EpochDB",
      url = "https://epochdb.net/",
      role = "Current Project Epoch item, quest, NPC, loot, and vendor verification source",
    },
    {
      name = "EpochHead",
      url = "https://epochhead.com/",
      role = "Project Epoch community database, item/quest detail source, and incremental EpochHeadData coverage source",
    },
    {
      name = "pfQuest-epoch",
      url = "https://github.com/Bennylavaa/pfQuest-epoch",
      role = "Project Epoch quest coordinate seed data, embedded into EpochCN MapData",
    },
    {
      name = "Maczuga/pfQuest-Epoch",
      url = "https://github.com/Maczuga/pfQuest-Epoch",
      role = "Legacy Project Epoch coordinate reference for missing NPC markers",
    },
    {
      name = "pfQuest-wotlk",
      url = "https://github.com/akzkak/pfQuest-wotlk",
      role = "Base quest coordinate seed data, embedded into EpochCN MapData",
    },
    {
      name = "epochhead addon",
      url = "https://github.com/chrispl57/epochhead",
      role = "Community data collection reference",
    },
    {
      name = "local QuestCN",
      path = "QuestCN/Data/QustCN_Data_CN.lua",
      role = "Chinese quest text seed data",
    },
    {
      name = "local Tooltips_Chinese",
      path = "Tooltips_Chinese/Data",
      role = "Chinese tooltip, item, unit, spell, and Epoch talent seed data",
    },
  },
}
