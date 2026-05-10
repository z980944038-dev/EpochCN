-- Incremental data confirmed from EpochHead.
-- Keep this file small and override-oriented so runtime lookup stays O(1).

function LoadEpochCNEpochHeadData()
  local names = {
    ["Berserker's Pale Chest Tattoos"] = "狂战士苍白胸前纹身",
    ["Blue Lumberjack Shirt"] = "蓝色伐木工衬衣",
    ["Green Lumberjack Shirt"] = "绿色伐木工衬衣",
    ["Red Lumberjack Shirt"] = "红色伐木工衬衣",
    ["Bronze Whelpling"] = "青铜雏龙",
    ["Dalaran Mage's Bracers"] = "达拉然法师护腕",
    ["Elemental Manifestation"] = "元素化身",
    ["Faction Transmutation Potion (Horde)"] = "阵营转换药水（部落）",
    ["Faction Transmutation Potion (Alliance)"] = "阵营转换药水（联盟）",
    ["Gaze of Infernal Control"] = "地狱控制之凝视",
    ["Gaze of Mystic Control"] = "秘法控制之凝视",
    ["Gaze of Relentless Control"] = "无情控制之凝视",
    ["Martin Fury"] = "马丁之怒",
    ["Mount Voucher"] = "坐骑兑换券",
    ["Savage Blood Troll Chest Wraps"] = "野蛮血巨魔裹胸",
    ["Savage Blood Troll Leg Wraps"] = "野蛮血巨魔腿部裹布",
    ["Savage Raptor"] = "野蛮迅猛龙",
    ["Sealed Title Scroll"] = "封印的头衔卷轴",
    ["Swift Shorestrider's Reins"] = "迅捷海滨陆行鸟缰绳",
    ["Band of the Endless"] = "无尽指环",
    ["Bottle of Northshire Wine"] = "一瓶北郡葡萄酒",
    ["A Brother's Disgust"] = "兄弟的厌恶",
    ["Stack of Barrels"] = "一堆木桶",
    ["Brother Neals"] = "尼尔斯修士",
    ["Melika Isenstrider"] = "梅莉卡·伊森斯特瑞德",
    ["Lion's Pride Inn"] = "狮王之傲旅店",
    ["Northshire Abbey"] = "北郡修道院",

    -- 高流量 NPC（塔纳利斯 / 安戈洛 / 其他经典区域）
    ["Revil Kost"] = "雷维尔·科斯特",
    ["Karlain"] = "卡兰恩",
    ["Farmer Furlbrow"] = "弗尔布罗农夫",
    ["Yorba Screwspigot"] = "约尔巴·螺旋旋塞",
    ["Sprinkle"] = "斯普林科",
    ["Tooga"] = "图加",
    ["Muigin"] = "穆金",
    ["Petra Grossen"] = "佩特拉·格罗森",
    ["Pozzik"] = "波兹克",
    ["Leakey Cartspark"] = "利基·卡茨帕克",

    -- Project Epoch 主要城镇 / 据点常见 NPC（避免对话框英文残留）
    ["Marshal McBride"] = "治安官玛克布莱德",
    ["Falkhaan Isenstrider"] = "法卡恩·伊森斯特瑞德",
    ["Deputy Willem"] = "威廉副官",
    ["Godric Rothgar"] = "戈德里克·罗斯加",
    ["Rallic Finn"] = "拉里克·芬恩",
    ["Gryan Stoutmantle"] = "格里安·斯托曼",
    ["Salma Saldean"] = "萨尔玛·萨丁",
    ["Farmer Saldean"] = "农夫萨丁",
    ["Innkeeper Farley"] = "旅店老板法利",
    ["Magistrate Solomon"] = "马瑞斯治安官",
    ["Magistrate Henry Maleb"] = "法官亨利·马雷布",
    ["Deputy Rainer"] = "瑞尼尔副队长",
    ["Marshal Dughan"] = "杜甘元帅",

    -- pfQuest-epoch × classic zhCN 同步 + 词根派生翻译
    ["Alexandra Blazen"] = "亚历山大·布拉森",
    ["Barkeep Dobbins"] = "酒吧老板杜宾斯",
    ["Bingles Blastenheimer"] = "宾格斯·雷管",
    ["Brother Wilhelm"] = "威尔海姆修士",
    ["Chromie"] = "克罗米",
    ["Cork Gizelton"] = "考克·基泽尔顿",
    ["Defias Rogue"] = "迪菲亚潜行者",
    ["Draenei Exile"] = "德莱尼流放者",
    ["Garrick Padfoot"] = "加瑞克·帕德弗特",
    ["Hemet Nesingwary"] = "赫米特·奈辛瓦里",
    ["Hinterlands Honey Ripple"] = "辛特兰蜜糖",
    ["Illiyana"] = "伊莉亚娜",
    ["Jailor Eston"] = "狱卒埃斯顿",
    ["Jeziba"] = "耶兹巴",
    ["Junder Brokk"] = "祖德尔·布鲁克",
    ["Kobold Geomancer"] = "狗头人地卜师",
    ["Kobold Miner"] = "狗头人矿工",
    ["Layo Starstrike"] = "莱耶·星击",
    ["Lesser Felhunter"] = "次级魔犬",
    ["Lesser Infernal"] = "次级地狱火",
    ["Lesser Succubus"] = "次级魅魔",
    ["Lesser Voidwalker"] = "次级虚空行者",
    ["Lilyn Darkriver"] = "莉琳·暗河",
    ["Magtoor"] = "玛格图尔",
    ["Masat T'andr"] = "马萨特·坦德",
    ["Master Smith Burninate"] = "大铁匠博恩奈特",
    ["Merissa Stilwell"] = "梅里萨·斯蒂维尔",
    ["Mild Spices"] = "甜香料",
    ["Mine Spider"] = "矿洞蜘蛛",
    ["Murloc Hunter"] = "鱼人猎人",
    ["Nek'rosh's Head"] = "纳克罗什的头颅",
    ["Painted Gnoll Armband"] = "彩色豺狼人臂章",
    ["Patrick Mills"] = "帕特里克·米尔斯",
    ["Protector Gariel"] = "守卫者加瑞尔",
    ["Putrid Gargoyle"] = "腐烂的石像鬼",
    ["Raene Wolfrunner"] = "莱恩·狼行者",
    ["Remen Marcot"] = "雷门·玛考特",
    ["Remy \"Two Times\""] = "雷米",
    ["Rigger Gizelton"] = "里格·基泽尔顿",
    ["Riverpaw Outrunner"] = "河爪豺狼人前锋",
    ["Riverpaw Runt"] = "矮小的河爪豺狼人",
    ["Scarlet Foreman"] = "血色工头",
    ["Scarlet Ghost"] = "血色幽灵",
    ["Scarlet Miner"] = "血色矿工",
    ["Second Mate Shandril"] = "大副杉德里尔",
    ["Sentinel Melyria Frostshadow"] = "哨兵梅丽瑞亚·霜影",
    ["Smith Argus"] = "铁匠阿古斯",
    ["Sten Stoutarm"] = "斯登·粗臂",
    ["Stormpike Mountaineer"] = "雷矛巡山人",
    ["Syndicate Mage"] = "辛迪加法师",
    ["Syndicate Overseer"] = "辛迪加监工",
    ["Syndicate Priest"] = "辛迪加牧师",
    ["Tharynn Bouden"] = "萨瑞恩·博丁",
    ["Theocritus"] = "塞欧克瑞图斯",
    ["Vincent Hyal"] = "文森特·海厄尔",
    ["William Pestle"] = "威廉·匹斯特",
    ["Zaldimar Wefhellt"] = "扎尔迪玛·维夫希尔特",
    ["Zannok Hidepiercer"] = "扎诺克",

    -- Epoch 专属降级套装（Ashen 系列）
    ["Ashen Belt of Might"] = "灰烬·力量腰带",
    ["Ashen Earthfury Belt"] = "灰烬·大地之怒腰带",
    ["Ashen Earthfury Bracers"] = "灰烬·大地之怒护腕",
    ["Ashen Giantstalker's Belt"] = "灰烬·巨魔猎手腰带",
    ["Ashen Nightslayer Belt"] = "灰烬·暗夜屠手腰带",
    ["Ashen Cenarion Belt"] = "灰烬·塞纳里奥腰带",
    ["Ashen Arcanist Belt"] = "灰烬·奥术师腰带",
    ["Ashen Lawbringer Belt"] = "灰烬·法律制裁者腰带",
    ["Ashen Vestments of Prophecy Belt"] = "灰烬·预言者长袍腰带",
    ["Ashen Stormrage Belt"] = "灰烬·怒风腰带",
    ["Ashen Nemesis Belt"] = "灰烬·宿敌腰带",
    ["Ashen Nemesis Bracers"] = "灰烬·宿敌护腕",
    ["Ashen Shadowcraft Belt"] = "灰烬·暗影工艺腰带",
    ["Ashen Magister's Belt"] = "灰烬·魔导师腰带",
    ["Ashen Dreadmist Belt"] = "灰烬·梦魇腰带",

    -- Epoch 专属炼金配方（可制造物品名）
    ["Balefire Draught"] = "厄火汤剂",
    ["Elixir of Dazzling Light"] = "耀目之光灵药",
    ["Elixir of Iron Diplomacy"] = "钢铁外交灵药",
    ["Elixir of Luring"] = "诱敌灵药",
    ["Elixir of Pure Arcane Power"] = "纯粹奥术之力灵药",
    ["Elixir of Valorous Diplomacy"] = "英勇外交灵药",
    ["Elixir of Virtuous Diplomacy"] = "崇德外交灵药",
    ["Elixir of Whirling Wind"] = "旋风灵药",

    -- Epoch 专属炼金配方卷轴名
    ["Recipe: Balefire Draught"] = "配方：厄火汤剂",
    ["Recipe: Elixir of Dazzling Light"] = "配方：耀目之光灵药",
    ["Recipe: Elixir of Iron Diplomacy"] = "配方：钢铁外交灵药",
    ["Recipe: Elixir of Luring"] = "配方：诱敌灵药",
    ["Recipe: Elixir of Pure Arcane Power"] = "配方：纯粹奥术之力灵药",
    ["Recipe: Elixir of Valorous Diplomacy"] = "配方：英勇外交灵药",
    ["Recipe: Elixir of Virtuous Diplomacy"] = "配方：崇德外交灵药",
    ["Recipe: Elixir of Whirling Wind"] = "配方：旋风灵药",

    -- Project Epoch 通用系统 UI 文本
    ["Bounty Board"] = "赏金公告板",
    ["Call Board"] = "召唤板",
    ["Call to Arms"] = "紧急召集",
    ["Epoch"] = "纪元",
    ["Project Epoch"] = "纪元计划",
    ["Ascension"] = "飞升",
    ["Realmkeeper"] = "领域守护者",
    ["Realmlist"] = "服务器列表",
    ["Loremaster"] = "博学者",
    ["The Dreamer"] = "梦旅者",
  }

  EpochCN_ObjectiveNameData = EpochCN_ObjectiveNameData or {}
  for english, chinese in pairs(names) do
    if not EpochCN_ObjectiveNameData[english] or EpochCN_ObjectiveNameData[english] == english then
      EpochCN_ObjectiveNameData[english] = chinese
    end
  end

  TPCN_ItemData = TPCN_ItemData or {}
  local items = {
    [17] = { "马丁之怒", "", "EpochHead" },
    [41248] = { "红色伐木工衬衣", "", "EpochHead" },
    [41249] = { "蓝色伐木工衬衣", "", "EpochHead" },
    [41250] = { "绿色伐木工衬衣", "", "EpochHead" },
    [62603] = { "一瓶北郡葡萄酒", "", "EpochHead" },
    [64950] = { "坐骑兑换券", "", "EpochHead" },
    [64951] = { "青铜雏龙", "", "EpochHead" },
    [90070] = { "元素化身", "", "EpochHead" },
    [90549] = { "无尽指环", "", "EpochHead" },
    [100003] = { "封印的头衔卷轴", "", "EpochHead" },
    [110000] = { "迅捷海滨陆行鸟缰绳", "", "EpochHead" },
    [110001] = { "野蛮迅猛龙", "", "EpochHead" },
    [110002] = { "野蛮血巨魔裹胸", "", "EpochHead" },
    [110003] = { "野蛮血巨魔腿部裹布", "", "EpochHead" },
    [110006] = { "狂战士苍白胸前纹身", "", "EpochHead" },
    [110014] = { "地狱控制之凝视", "", "EpochHead" },
    [110015] = { "无情控制之凝视", "", "EpochHead" },
    [110019] = { "秘法控制之凝视", "", "EpochHead" },
    [110030] = { "阵营转换药水（部落）", "", "EpochHead" },
    [110048] = { "达拉然法师护腕", "", "EpochHead" },
  }
  for id, data in pairs(items) do
    local current = TPCN_ItemData[id] and TPCN_ItemData[id][1]
    if not current or current == "" or current == data[1] or not string.find(current, "[\128-\255]") then
      TPCN_ItemData[id] = data
    end
  end

  EpochCN_EpochQuestData = EpochCN_EpochQuestData or {}
  if not EpochCN_EpochQuestData[26779] then
    EpochCN_EpochQuestData[26779] = {
      "兄弟的厌恶",
      "将一堆木桶带给狮王之傲旅店的梅莉卡·伊森斯特瑞德。",
      "<尼尔斯修士看着木桶，皱起了眉。>\n\n恶心的劣酒！这里可是酒庄，$N！奥斯沃思小姐种出了整个东部王国最好的葡萄，我和其他修士负责酿酒。这里没人喝麦酒。\n\n如果你真想知道这东西从哪里来，就去金郡的狮王之傲旅店，把你发现的东西拿给梅莉卡·伊森斯特瑞德看。她熟悉本地的常客和酿酒商。\n\n哦！如果你正要去那里，也请顺便把我们最新一批葡萄酒带给她。",
      "EpochHead",
      "A Brother's Disgust",
    }
  end
end
